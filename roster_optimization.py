# -*- coding: utf-8 -*-
# @Author: charl
# @Date:   2018-12-29 18:31:18
# @Last Modified by:   charl
# @Last Modified time: 2019-01-12 23:52:00

import pandas as pd 
import requests
from lxml import html
import numpy as np
import os
import sqlite3
import copy
import process_csv
import player
import genetic_algorithm
'''
def leave_one_out():
	processed_csv = process_csv.FanduelCSV('fanduel.csv')
	player_pool = processed_csv.pool
	ga = genetic_algorithm.FanduelNBA(player_pool, 1000, 25, 0.25, 0.10, 0.05, 60000,'best_roster')
	for baller in ga.top_lineup.values:
		print baller
		missing_baller = None
		for index, playa in enumerate(player_pool.valid_players):
			if baller == playa.nickname:
				missing_baller = player_pool.valid_players.pop(index)
				break
		sub_ga = genetic_algorithm.FanduelNBA(
			player_pool, 1000, 25, 0.25, 0.10, 0.05, 60000,'best_roster-' + baller)
		player_pool.valid_players.append(missing_baller)
'''

def projection_sources():

	processed_csv = process_csv.FanduelCSV('fanduel.csv', 'player_db.sqlite', 2019)
	player_pool = processed_csv.pool
	ga = genetic_algorithm.FanduelNBA(
		player_pool, 10000, 50, 0.25, 0.20, 0.05, 60000,'best_roster'
		)

projection_sources()
