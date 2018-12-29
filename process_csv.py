# -*- coding: utf-8 -*-
# @Author: Charlie
# @Date:   2017-12-28 20:54:09
# @Last Modified by:   charl
# @Last Modified time: 2018-12-29 18:28:48

from lxml import html
import requests
import sqlite3
import pandas as pd
import os
import player


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
		self.update_player_db()

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
			bref_url TEXT)'''
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

			else:
				continue

	def create_players(self):
		#create player objects
		players = []
		cursor = self.player_db_conn.cursor()
		for index, player in self.player_table.iterrows():
			payload = cursor.execute(
				'''SELECT fd_nickname, fd_position, bref_url from players 
				WHERE fd_nickname = ?''',(player['Nickname'],)).fetchall()
			payload.extend([player['Salary'], player['Opponent']])
			
			player = Player(payload)
			players.append(player)
		return players

			





		
				

FanduelCSV('fanduel.csv')