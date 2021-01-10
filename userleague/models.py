from django.db import models
from django.contrib.auth.models import User
from fantasyleagues.models import League
from django.contrib import messages
from django.shortcuts import render, redirect
from draft.models import DraftTeam
from fantasyleagues.models import League
import numpy as np
from draft.models import FootballPlayer, League, DraftTeam, FootballPlayerDraftSpot
from nflinfo.models import NflWeek, NflTeam, NflMatchup, NflPlayerStat
from django.utils import timezone
from django.template.defaulttags import register
from . import *


class LeagueMatchup(models.Model):
	league = models.ForeignKey(League, on_delete=models.CASCADE, null=True, blank=True)  
	week = models.IntegerField(null=True, blank=True)
	team_1 = models.ForeignKey(DraftTeam, on_delete=models.CASCADE, null=True, blank=True, related_name='team_1')
	team_2 = models.ForeignKey(DraftTeam, on_delete=models.CASCADE, null=True, blank=True, related_name='team_2')

	def __str__(self):
		league = str(self.league).split(' -')[0]
		week = str(self.week)
		team_1 = str(self.team_1)
		team_2 = str(self.team_2)
		return f"{league} - Week: {week} - {team_1} vs {team_2}"


	def edit_lineup(player_1_id, player_2_id, league, team):
		class Players:
			def __init__(self, starter, name, flex):
				self.starter = starter
				self.name = name
				self.flex = flex	
		player_1 = Players(True, '', False)
		player_2 = Players(False, '', False)
		if 'FLEX' in player_1_id:
			player_1.flex = True
		if player_1_id[1] != '':
			player_1.name = player_1_id[1]
		if 'starter' in player_2_id:
			player_2.starter = True
		if 'Empty' in player_2_id[0]:
			pass
		else:
			player_2.name = player_2_id[1]
		if 'FLEX' in player_2_id:
			player_2.flex = True
		if player_1.name != '':
			football_player = FootballPlayer.objects.get(name=player_1.name)
			football_player_draft_spot = FootballPlayerDraftSpot.objects.get(league=league, draft_team=team, football_player=football_player)
			football_player_draft_spot.flex = player_2.flex
			football_player_draft_spot.starter = player_2.starter
			football_player_draft_spot.save()
			if player_2.starter == True and player_2.flex == True:
				player_1.starter = False
		if player_2.name != '':
			football_player = FootballPlayer.objects.get(name=player_2.name)
			football_player_draft_spot = FootballPlayerDraftSpot.objects.get(league=league, draft_team=team, football_player=football_player)
			football_player_draft_spot.flex = player_1.flex
			football_player_draft_spot.starter = player_1.starter
			football_player_draft_spot.save()	
		return None





	def order_starters(starters):
		order_starters = ['' for i in range(9)]

		for i in range(len(starters)):
			player_info = {}
			player_info['player'] = starters[i]
			
			if starters[i].flex == True:
				player_info['table_position'] = 'FLEX'
			else:
				if starters[i].player_position == 'DEF':
					player_info['table_position'] = 'D/ST'
				else:
					player_info['table_position'] = starters[i].player_position

			# Player Injury Status
			injury_status = starters[i].football_player.status
			player_info['injury_status'] = injury_status

			# Player Projection
			player_info['player_projection'] = starters[i].football_player.projection

			# Player Score
			player_info['player_score'] = 0
			football_player = starters[i].football_player
			

			# Order table positions for starters
			table_position = player_info['table_position']
			
			if player_info['table_position'] == 'QB':
				order_starters[0] = player_info

			if player_info['table_position'] == 'RB':
				if order_starters[1] == '':
					order_starters[1] = player_info
				else:
					order_starters[2] = player_info

			if player_info['table_position'] == 'WR':
				if order_starters[3] == '':
					order_starters[3] = player_info
				else:
					order_starters[4] = player_info

			if player_info['table_position'] == 'TE':
				order_starters[5] = player_info

			if player_info['table_position'] == 'FLEX':
				order_starters[6] = player_info

			if player_info['table_position'] == 'D/ST':
				order_starters[7] = player_info

			if player_info['table_position'] == 'K':
				order_starters[8] = player_info

		
		# Putting table position in dictionary if there is an empty starters spot
		if order_starters.count('') > 0:
			order_starters = fill_empty_starters(order_starters)

		return order_starters


	def order_bench(bench):
		order_bench = []
		for i in range(len(bench)):
			player_info = {}
			player_info['player'] = bench[i]
			player_team = bench[i].player_team

			# Bench Player Injury Status
			injury_status = bench[i].football_player.status
			player_info['injury_status'] = injury_status

			# Player Projection
			player_info['player_projection'] = bench[i].football_player.projection

			# Player Score
			player_info['player_score'] = 0
			order_bench.append(player_info)

		return order_bench



