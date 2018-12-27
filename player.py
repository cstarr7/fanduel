# -*- coding: utf-8 -*-
# @Author: Charles Starr
# @Date:   2018-01-28 21:26:02
# @Last Modified by:   charl
# @Last Modified time: 2018-12-26 19:00:11

import pandas as pd 
import requests
from lxml import html

class Player(object):

	def __init__(self, nickname, position, price, opponent, bref_url):

		self.nickname = nickname
		self.position = position
		self.price = price
		self.opponent = opponent
		self.bref_url = bref_url
		self.stats = pd.Series(
			data = [[] for i in range(0,8)], index = [
			'Points', 'Rebounds', 'Assists', 'Blocks', 'Steals', 'Minutes',
			'Turnovers', 'Opponent'
			]
			)
		self.stat_rates = pd.Series(data = 0.0, index = [
			'Points', 'Rebounds', 'Assists', 'Blocks', 'Steals', 'Minutes', 'Turnovers'
			]
			)
		self.number_fire = pd.Series(data = 0.0, index = [
			'Fanduel Points', 'Value', 'Minutes', 'Points', 'Rebounds', 'Assists',
			'Steals', 'Blocks', 'Turnovers'])

	def pull_stats(self, year):

		url = (
			'https://www.basketball-reference.com' + self.bref_url[:-5] 
			+ '/gamelog/' + str(year)
			)

		game_log_tree = html.fromstring(requests.get(url).text)
		game_log_table = game_log_tree.xpath('.//table[@id="pgl_basic"]')[0]
		
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
		print minutes_played
		for stat in self.stat_rates.index:
			print sum(self.stats[stat])
			self.stat_rates[stat] = sum(self.stats[stat])/minutes_played

		return

	def pull_numberfire(self):

		url = 'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections'

		fire_tree = game_log_tree = html.fromstring(requests.get(url).text)
		fire_table = game_log_tree.xpath('.//tbody[@class="stat-table__body"]')[0]

		fire_rows = fire_table.xpath('./tr/td/span/a')
		for row in fire_rows:
			if self.nickname == row.xpath("./text()")[0].strip():
				true_row = row.xpath('./../..')[0]
				stats = true_row.xpath('./following-sibling::*/text()')
				self.number_fire = [x.strip() for x in stats]
				print self.number_fire




test_p = Player('Myles Turner', 'PF', '$7300', 'ATL', '/players/t/turnemy01.html')
test_p.pull_stats(2019)
test_p.calculate_rates()
test_p.pull_numberfire()
print test_p.stats
print test_p.stat_rates




