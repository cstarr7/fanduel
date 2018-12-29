# -*- coding: utf-8 -*-
# @Author: charl
# @Date:   2018-12-28 19:39:33
# @Last Modified by:   charl
# @Last Modified time: 2018-12-29 17:51:42
import pandas as pd 
import numpy as np
import copy


class GeneticSearch(object):

    def __init__(
    	self, player_pool, gen_size, gen_count, survival_rate, mutation_rate,
    	inversion_rate, budget, chromosomes, positions
    	):

    	self.player_pool = player_pool
    	self.gen_size = gen_size
    	self.gen_count = gen_count
    	self.survival_rate = survival_rate
    	self.mutation_rate = mutation_rate
    	self.inversion_rate = inversion_rate
    	self.budget = budget
    	self.chromosomes = chromosomes
    	self.positions = positions
    	self.position_pools = self.build_player_pools(positions)
    	self.gene_pool = self.initialize_rosters()
    	self.evolve_rosters()

    def build_player_pools(self):

    	position_pools = {}
    	#create a dataframe for each position
    	for position in positions:
    		position_pools[position] = pd.DataFrame(
    			0, columns = 'Nickname', 'Price', 'Projected'
    			)
    	#add players to appropriate dataframe
    	for player in self.player_pool:
    		position_pools[player.position].append(
    			[player.nickname, player.price, player.projected]
    			)

    	return position_pools

    def initialize_rosters(self):

    	rosters = []
		#create unique roster equal to generation count
		while len(rosters) < self.gen_size:
			roster = copy.deepcopy(self.chromosomes)
			roster = self.generate_roster()
			if self.validate_roster(roster):
				rosters.append(roster)

		return rosters

	def generate_roster(self):
		pass

    def run_generation(self):
    	#perform operations associated with a generation of roster evolution

    	self.bottleneck()
    	self.repopulate()
    	self.rank_rosters()

    def remove_invalids(self):

    	#remove rosters if they exceed budget or have duplicate players
    	for roster in self.gene_pool:
    		valid = False
    		valid = self.validate_roster(roster)
    		while not valid:
    			roster = self.generate_roster()
    			valid = self.validate_roster(roster)

    def validate_roster(self, roster):
    	pass

    def rank_rosters(self):

		rank_array = []

		for roster in self.gene_pool:
			fitness_points = self.point_tally(roster)
			rank_array.append(fitness_points)

		self.gene_pool = [
			x for _, x in sorted(zip(rank_array, self.gene_pool), reverse = True)
			]

		return

	def point_tally(self, roster):
		#tally points for a roster
		fitness_points = 0.0
		for players, position in zip(roster, self.positions):
			for player in players:
				fitness_points += self.position_pools[position].loc(player, 'Projected')
		return fitness_points

	def salary_tally(self, roster):
		#tally salary for a roster
		salary = 0
		for players, position in zip(roster, self.positions):
			for player in players:
				salary += self.position_pools[position].loc(player, 'Price')
		return salary

	def bottleneck(self):

		truncation = int(round(self.gen_size * self.survival_rate))
		self.gene_pool = self.gene_pool[:truncation]
		return

	def repopulate(self):
		#generate new lineup variations through mating, mutation, and inversion
		while len(self.gene_pool) < self.gen_size:
			offspring = []
			mom, dad = np.random.choice(self.gene_pool, 2)
			for mom_pos, dad_pos, position in zip(mom, dad self.positions):
				offspring_position = []
				#mating
				for players in zip(mom_pos, dad_pos):
					offspring_player = np.random.choice(players)
					#mutation
					if np.random.random < self.mutation_rate:
						offspring_player = np.random.choice(
							self.position_pools[position].index
							)
					offspring_position.append(offspring_player)
				#inversion
				if np.random.random < self.inversion_rate:
					offspring_position = offspring_position[::-1]
				
				offspring.append(offspring_position)
			#validate new roster
			if self.validate_roster(offspring):
				self.gene_pool.append(offspring)
		return

	def evolve_rosters(self):
		#controls and reports on roster evolution
		writer = pd.ExcelWriter('ga_generation_report.xlsx')
		for i in range(self.gen_count):
			self.run_generation()
			report = self.generation_report()
			report.to_excel(writer, sheet_name = 'Generation' + str(i))
		writer.save()

	def generation_report(self):
		#pandas data frame for top 100 rosters per generation
		report = pd.DataFrame(0, columns = 
			['PG1', 'PG2', 'SG1', 'SG2', 'SF1', 'SF2', 'PF1', 'PF2', 'C', 'Points', 'Salary']
			)
		for roster in self.gene_pool[:100]:
			payload = []
			points = self.point_tally(roster)
			salary = self.salary_tally(roster)
			for players, position in zip(roster, self.positions):
				for player in players:
					payload.append(
						self.position_pools[position].loc(player, 'Nickname')
						)
			payload.append(points)
			payload.append(salary)
			report.append(payload)
		return report






class FanduelNBA(GeneticSearch):

    def __init__(self):

	    super(FanduelNBA, self).__init__(
	        player_pool, gen_size, gen_count, survival_rate, mutation_rate,
	    	inversion_rate, budget, [[], [], [], [], []], ['PG', 'SG', 'SF', 'PF', 'C']
	        )

	def generate_roster(self):
		#randomly sample index of position dataframe
		roster = copy.deepcopy(self.chromosomes)
		for slot, position in enumerate(self.positions):
			#center only has one slot, others have two
			if position == 'C':
				roster[slot].append(
					np.random.choice(self.position_pools.index, 1)
					)
			else:
				roster[slot].append(
					np.random.choice(self.position_pools.index, 2)
					)
		return roster

    def validate_roster(self, roster):
    	#check whether there are duplicate players or roster exceeds budget
    	valid == True
		payroll = 0
		for players, position in zip(roster, self.positions):
			if position != 'C':
				seen = set()
				for player in players:
					if player in seen:
						valid = False
						break
					payroll += self.position_pools[position].loc(player, 'Price')
					seen.append(player)
				if valid == False:
					break
			else:
				payroll += self.position_pools[position].loc(player, 'Price')
		
		if payroll > self.budget:
			valid = False

		return valid













