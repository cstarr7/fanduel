# -*- coding: utf-8 -*-
# @Author: Charles Starr
# @Date:   2018-01-28 21:26:02
# @Last Modified by:   charl
# @Last Modified time: 2019-01-12 23:41:55

import pandas as pd
from lxml import html
import requests

point_values = [1.0, 1.2, 1.5, 3.0, 3.0, -1.0]

class Player(object):

	def __init__(self, nickname, position, bref_url, nf_name, grinder_name, 
		baller_name, price, opponent, year):

		self.nickname = nickname
		self.position = position
		self.price = price
		self.opponent = opponent
		self.nf_name = nf_name
		self.grinder_name = grinder_name
		self.baller_name = baller_name
		self.bref_url = bref_url
		self.year = year
		self.stats = pd.Series(
			data = [[] for i in range(0,8)], index = [
			'Points', 'Rebounds', 'Assists', 'Blocks', 'Steals',
			'Turnovers','Minutes', 'Opponent'
			]
			)
		self.stat_rates = pd.Series(data = 0.0, index = [
			'Points', 'Rebounds', 'Assists', 'Blocks', 'Steals', 'Turnovers'
			]
			)
		self.number_fire = pd.Series(data = 0.0, index = [
			'Fanduel Points', 'Cost', 'Value', 'Minutes', 'Points', 'Rebounds', 'Assists',
			'Steals', 'Blocks', 'Turnovers'])
		self.pull_stats(2019)
		self.calculate_rates()
		self.projected = 0.0
		self.nf_projection = 0.0
		self.grinder_projection = 0.0
		self.baller_projection = 0.0
		self.charles_projection = 0.0

	def pull_stats(self, year):
		url = (
			'https://www.basketball-reference.com' + self.bref_url[:-5] 
			+ '/gamelog/' + str(self.year)
			)

		game_log_tree = html.fromstring(requests.get(url).text)
		try:
			game_log_table = game_log_tree.xpath('.//table[@id="pgl_basic"]')[0]
		except:
			return
		for game in game_log_table.xpath('./tbody/tr'):
			if game.xpath('./td[@data-stat="game_season"]/strong/text()'):
				minutes_string = game.xpath(
					'./td[@data-stat="mp"]/text()'
					)[0].split(':')
				minutes_float = (
					float(minutes_string[0]) + float(minutes_string[1])/60
					)
				self.stats['Minutes'].append(minutes_float)
				self.stats['Points'].append(
					int(game.xpath('./td[@data-stat="pts"]/text()')[0])
					)
				self.stats['Rebounds'].append(
					int(game.xpath('./td[@data-stat="trb"]/text()')[0])
					)
				self.stats['Assists'].append(
					int(game.xpath('./td[@data-stat="ast"]/text()')[0])
					)
				self.stats['Blocks'].append(
					int(game.xpath('./td[@data-stat="blk"]/text()')[0])
					)
				self.stats['Steals'].append(
					int(game.xpath('./td[@data-stat="stl"]/text()')[0])
					)
				self.stats['Turnovers'].append(
					int(game.xpath('./td[@data-stat="tov"]/text()')[0])
					)
				self.stats['Opponent'].append(
					game.xpath('./td[@data-stat="opp_id"]/a/text()')[0])
		return

	def calculate_rates(self):

		minutes_played = sum(self.stats['Minutes'])

		if minutes_played == 0.0:
			return

		for stat in self.stat_rates.index:

			self.stat_rates[stat] = sum(self.stats[stat])/minutes_played

		return

	def pull_numberfire(self, fire_rows):
		found = False
		for row in fire_rows:
			#print self.nf_name
			if self.nf_name == row.xpath("./text()")[0].strip():
				found = True
				true_row = row.xpath('./../..')[0]
				stats = true_row.xpath('./following-sibling::*/text()')
				self.number_fire[:] = [x.strip() for x in stats]
				self.nf_projection = float(self.number_fire['Fanduel Points'])
				break
		if found == False:
			print 'nf' + self.nickname

		return

	def pull_grinders(self, grinder_table):

		found = False
		for row in grinder_table.index:
			if self.grinder_name == row:
				self.grinder_projection = grinder_table.loc[row, 'Fantasy Points']
				found = True
		if found == False:
			#print 'grinder' + self.nickname
			pass

		return

	def pull_ballers(self, baller_rows):

		found = False
		for row in baller_rows:
			if self.baller_name == row.xpath('./td/a[@target="blank"]/text()')[0].strip():
				found = True
				points_perK = float(row.xpath('./td[4]/text()')[0])
				self.baller_projection = self.price * points_perK / 1000.0
		if found == False:
			#print 'baller' + self.nickname
			pass

		return

	def make_projection(self):

		projected_total = 0.0

		if self.number_fire['Minutes'] != 0.0:
			projected_minutes = self.number_fire['Minutes']
		else:
			projected_minutes = 0.0
			#projected_minutes = np.mean(self.stats['Minutes'])
		for index, stat in enumerate(self.stat_rates.values):
			category_score = float(projected_minutes) * float(stat) * float(point_values[index])
			projected_total += category_score

		self.charles_projection = projected_total

		return

class PlayerPool(object):
	#assemble pool of players for the slate
	
	def __init__(self, players):

		self.valid_players = self.filter_players(players)

	def filter_players(self, players):

		valid_players = []
		for baller in players:
			if baller.projected > 0.0:
				valid_players.append(baller)
			else:
				print baller.nickname
		projection_out(valid_players)
		return valid_players

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









