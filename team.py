# -*- coding: utf-8 -*-
# @Author: charl
# @Date:   2019-01-13 00:16:35
# @Last Modified by:   charl
# @Last Modified time: 2019-01-13 00:32:44

import numpy as np
import pandas as pd
from lxml import html
import sqlite3
import requests

class Team(object):

	def __init__(self, team_name, fd_abbr, bref_abbr, year):

		self.team_name = team_name
		self.fd_abbr = fd_abbr
		self.bref_abbr = bref_abbr
		self.year = year
		self.stats_for = pd.DataFrame(0.0, index = [], columns = 
			['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers']
			)
		self.stats_against = pd.DataFrame(0.0, index = [], columns = 
			['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers']
			)
		self.rates_for = pd.Series(0.0, index = 
			['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers']
			)
		self.rates_against = pd.Series(0.0, index = 
			['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers']
			)
		self.retrieve_stats()
		print self.stats_for
		print self.stats_against

	def retrieve_stats(self):

		url = (
			'https://www.basketball-reference.com/teams/' 
			+ self.bref_abbr + '/' + str(self.year) + '/gamelog/'
			)

		game_log_tree = html.fromstring(requests.get(url).text)
		game_log_table = game_log_tree.xpath('//table[@id="tgl_basic"]')[0]

		for game_row in game_log_table.xpath(
			'./tbody/tr[contains(@id, "tgl_basic")]'
			):
			
			date_index = game_row.xpath('./td[@data-stat="date_game"]/a/text()') [0]
			#populate for stats from bref table
			self.stats_for.loc[date_index, 'Points'] = (
				game_row.xpath('./td[@data-stat="pts"]/text()')
				)[0]
			self.stats_for.loc[date_index, 'Rebounds'] = (
				game_row.xpath('./td[@data-stat="trb"]/text()')
				)[0]
			self.stats_for.loc[date_index, 'Assists'] = (
				game_row.xpath('./td[@data-stat="ast"]/text()')
				)[0]
			self.stats_for.loc[date_index, 'Steals'] = (
				game_row.xpath('./td[@data-stat="stl"]/text()')
				)[0]
			self.stats_for.loc[date_index, 'Blocks'] = (
				game_row.xpath('./td[@data-stat="blk"]/text()')
				)[0]
			self.stats_for.loc[date_index, 'Turnovers'] = (
				game_row.xpath('./td[@data-stat="tov"]/text()')
				)[0]
			#populate against stats from bref table
			self.stats_against.loc[date_index, 'Points'] = (
				game_row.xpath('./td[@data-stat="opp_pts"]/text()')
				)[0]
			self.stats_against.loc[date_index, 'Rebounds'] = (
				game_row.xpath('./td[@data-stat="opp_trb"]/text()')
				)[0]
			self.stats_against.loc[date_index, 'Assists'] = (
				game_row.xpath('./td[@data-stat="opp_ast"]/text()')
				)[0]
			self.stats_against.loc[date_index, 'Steals'] = (
				game_row.xpath('./td[@data-stat="opp_stl"]/text()')
				)[0]
			self.stats_against.loc[date_index, 'Blocks'] = (
				game_row.xpath('./td[@data-stat="opp_blk"]/text()')
				)[0]
			self.stats_against.loc[date_index, 'Turnovers'] = (
				game_row.xpath('./td[@data-stat="opp_tov"]/text()')
				)[0]

		return

class TeamPool(object):

	def __init__(self, team_db, year):

		self.team_db_conn = self.open_team_db(team_db)
		self.year = year
		self.team_nomenclature = self.retrieve_nomenclature()
		self.teams = self.create_teams()

	def open_team_db(self, db_file):

		conn = sqlite3.connect(db_file)

		return conn

	def retrieve_nomenclature(self):

		cursor = self.team_db_conn.cursor()
		teams = cursor.execute(
				'''SELECT * from teams''').fetchall()
		return teams

	def create_teams(self):

		teams = []

		for names in self.team_nomenclature:

			new_team = Team(names[0], names[1], names[2], self.year)

TeamPool('player_db.sqlite', 2019)

