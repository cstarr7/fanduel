# -*- coding: utf-8 -*-
# @Author: Charlie
# @Date:   2017-12-28 20:54:09
# @Last Modified by:   charl
# @Last Modified time: 2019-01-11 21:37:12

from lxml import html
import requests
import sqlite3
import pandas as pd
import os
import player
import numpy as np


class ProcessCSV(object):
	#generic class and functions for processing both DraftKings and fanduel CSVs

	def __init__(self, daily_player_CSV):

		self.daily_player_CSV = daily_player_CSV
		self.player_table = self.open_CSV()
		self.player_db_conn = self.open_player_db()

	def open_player_db(self):

		conn = sqlite3.connect('player_db.sqlite')

		return conn

	def open_CSV(self):

		player_table = pd.read_csv(self.daily_player_CSV)

		return player_table


class FanduelCSV(ProcessCSV):


	def __init__(self, daily_player_CSV):

		super(FanduelCSV, self).__init__(daily_player_CSV)
		self.fire_rows = self.retrieve_numberfire()
		self.grinder_table = self.retrieve_rotogrinders()
		self.baller_rows = self.retrieve_rotoballer()
		self.update_player_db()
		self.pool = self.create_pool()
		

	def update_player_db(self):
		
		cursor = self.player_db_conn.cursor()

		cursor.execute(
			'''CREATE TABLE IF NOT EXISTS players
			(fd_position TEXT,
			fd_first TEXT,
			fd_last TEXT,
			fd_nickname TEXT PRIMARY KEY,
			team TEXT, 
			dk_name TEXT,
			dk_position TEXT,
			bref_url TEXT,
			nf_name TEXT,
			grinder_name TEXT,
			baller_name TEXT)'''
			)
		existing_players = [player[0] for player in 
			cursor.execute('''SELECT fd_nickname from players''').fetchall()
			]


		for index, player in self.player_table.iterrows():
			if player['Nickname'] not in existing_players:
				payload = (
					player['Position'], player['First Name'], player['Last Name'],
					player['Nickname'], player['Team']
					)
				cursor.execute(
					'''INSERT INTO players 
					(fd_position, fd_first, fd_last, fd_nickname, team)
					VALUES (?, ?, ?, ?, ?)''', payload)
				self.player_db_conn.commit()

				index_letter = player['Last Name'][0].lower()
				name_index_url = (
					'https://www.basketball-reference.com/players/' 
					+ index_letter +'/'
					)
				index_tree = html.fromstring(requests.get(name_index_url).text)
				player_table = index_tree.xpath('.//table[@id="players"]')[0]
				for entry in player_table.xpath('./tbody/tr'):

					try:
						if entry.xpath('./th[1]/strong/a/text()')[0] == player['Nickname']:
							bref_url = entry.xpath('./th[1]/strong/a/@href')[0]
							cursor.execute(
								'''UPDATE players SET bref_url = ?
								WHERE fd_nickname = ?''', 
								(bref_url, player['Nickname'])
								)
							self.player_db_conn.commit()
							break

					except:
						continue
			nf_name = self.player_db_conn.execute(
				'''SELECT nf_name from players 
				WHERE fd_nickname = ?''',(player['Nickname'],)).fetchall()[0][0]
			if not nf_name:
				self.update_numberfire_name(player)

			grinder_name = self.player_db_conn.execute(
				'''SELECT grinder_name from players 
				WHERE fd_nickname = ?''',(player['Nickname'],)).fetchall()[0][0]
			if not grinder_name:
				self.update_grinder_name(player)
			baller_name = self.player_db_conn.execute(
				'''SELECT baller_name from players 
				WHERE fd_nickname = ?''',(player['Nickname'],)).fetchall()[0][0]
			if not baller_name:
				self.update_baller_name(player)
			else:
				continue

	def update_numberfire_name(self, player):
		cursor = self.player_db_conn.cursor()
		for row in self.fire_rows:
			if player['Nickname'] == row.xpath("./text()")[0].strip():
				cursor.execute(
					'''UPDATE players SET nf_name = ?
					WHERE fd_nickname = ?''', 
					(player['Nickname'], player['Nickname'])
					)
				self.player_db_conn.commit()
				break

	def update_grinder_name(self, player):
		cursor = self.player_db_conn.cursor()
		for row in self.grinder_table.index:
			if player['Nickname'] == row:
				cursor.execute(
					'''UPDATE players SET grinder_name = ?
					WHERE fd_nickname = ?''', 
					(player['Nickname'], player['Nickname'])
					)
				self.player_db_conn.commit()
				break

	def update_baller_name(self, player):
		cursor = self.player_db_conn.cursor()
		for row in self.baller_rows:
			if player['Nickname'] == row.xpath('./td/a[@target="blank"]/text()')[0].strip():
				cursor.execute(
					'''UPDATE players SET baller_name = ?
					WHERE fd_nickname = ?''', 
					(player['Nickname'], player['Nickname'])
					)
				self.player_db_conn.commit()
				break

	def retrieve_numberfire(self):

		url = 'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections'

		fire_tree  = html.fromstring(requests.get(url).text)
		fire_table = fire_tree.xpath('.//tbody[@class="stat-table__body"]')[0]

		fire_rows = fire_table.xpath('./tr/td/span/a')

		return fire_rows

	def retrieve_rotogrinders(self):

		grinders_csv = pd.read_csv('grinders.csv', index_col = 'Name')
		return grinders_csv

	def retrieve_rotoballer(self):

		url = 'https://www.rotoballer.com/nba-dfs-lineups-projections-daily-fantasy-basketball-matchups-fanduel-draftkings/562583?src=bar3'

		baller_tree  = html.fromstring(requests.get(url).text)
		baller_table = baller_tree.xpath('.//tbody[@id="fbody"]')[0]

		baller_rows = baller_table.xpath('./tr')

		return baller_rows

	def create_pool(self):

		players = self.create_players()
		valid_players = self.filter_players(players)
		pool = PlayerPool(valid_players)

		return pool

	def create_players(self):
		#create player objects
		players = []
		cursor = self.player_db_conn.cursor()
		for index, baller in self.player_table.iterrows():
			payload = list(cursor.execute(
				'''SELECT fd_nickname, fd_position, bref_url, nf_name, grinder_name,
				baller_name from players WHERE fd_nickname = ?''',
				(baller['Nickname'],)).fetchall()[0])
			payload.extend([baller['Salary'], baller['Opponent']])
			new_player = player.Player(*payload)
			if baller['Injury Indicator'] != 'O':
				players.append(new_player)
		return players

	def filter_players(self, players):

		valid_players = []
		for baller in players:
			baller.pull_numberfire(self.fire_rows)
			baller.pull_grinders(self.grinder_table)
			baller.pull_ballers(self.baller_rows)
			baller.make_projection()
			baller.projected = baller.nf_projection
			print baller.projected
			if baller.projected > 0.0:
				valid_players.append(baller)
			else:
				print baller.nickname
		projection_out(valid_players)
		return valid_players

	def average_projections(self, player):
		
		projections = [player.nf_projection, player.grinder_projection, player.baller_projection]
		valid_proj = [x for x in projections if x != 0.0]
		if len(valid_proj) > 0:
			return np.mean(valid_proj)
		else:
			return 0.0

class PlayerPool(object):
	#assemble pool of players for the slate
	
	def __init__(self, player_pool):

		self.valid_players = player_pool

def projection_out(valid_players):

	outframe = pd.DataFrame(
		0.0, index = [], columns = ['NF Projection', 'Charles Projection', 'Price'])
	for player in valid_players:
		outframe.loc[player.nickname] = (
			[player.nf_projection, player.charles_projection, player.price]
			)

	writer = pd.ExcelWriter('projection_compare.xlsx')
	outframe.to_excel(writer)
	writer.save()