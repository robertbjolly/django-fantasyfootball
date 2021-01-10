from django.db import models
from django.contrib.auth.models import User
from fantasyleagues.models import League
from django.contrib import messages
from django.shortcuts import render, redirect
from nflinfo.models import FootballPlayer, NflTeam, NflMatchup

# https://docs.djangoproject.com/en/3.1/ref/models/fields/
# https://www.revsys.com/tidbits/tips-using-djangos-manytomanyfield/


class DraftTeam(models.Model):
	league = models.ForeignKey(League, on_delete=models.CASCADE, null=True, blank=True)
	team_name = models.CharField(max_length=20, blank=False)
	draft_spot = models.SmallIntegerField(null=True, blank=True)
	team_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	commissioner = models.BooleanField(default = False, null=True, blank=False)

	def __str__(self):
		team_name = str(self.team_name)
		league = str(self.league).split('-')[-1]
		return f"{team_name}"

	def available_draft_nums(draft_players):
		draft_nums_taken = [i.draft_spot for i in draft_players if i.draft_spot != None]
		available_draft_nums = [i for i in range(1, len(draft_players)+1) if i not in draft_nums_taken]
		return available_draft_nums

	def draft_order_incomplete_list(user, draft_players, available_draft_nums):
		draft_players = draft_players.order_by('draft_spot')
		incomplete_draft_list = available_draft_nums[:]
		for i in range(len(incomplete_draft_list)):
			incomplete_draft_list[i] = ''
		for i in draft_players:
			if i.draft_spot != None:
				spot = int(i.draft_spot)
				team_name = i.team_name
				incomplete_draft_list.insert(spot-1, team_name)
		return incomplete_draft_list


	def get_draft_order(league_name, league_amount):
		draft_players = DraftTeam.objects.filter(league__league_name=str(league_name), league__completed=False)
		for i in draft_players:
			if i.draft_spot == None:
				return None
		draft_order = draft_players.order_by('draft_spot')
		draft_order = [str(draft_order[i]) for i in range(len(draft_order))]
		return draft_order

	def updated_draft_order(draft_order, amount_players_drafted):
		updated_draft_order = []
		for i in range(8):
			forward_order = draft_order[:]
			for drafter in forward_order:
				updated_draft_order.append(drafter)
			backwards_order = draft_order[:]
			backwards_order.reverse()
			for drafter in backwards_order:
				updated_draft_order.append(drafter)
		for i in range(amount_players_drafted):
			del updated_draft_order[0]
			updated_draft_order.append('Draft Finished')
		return updated_draft_order




class FootballPlayerDraftSpot(models.Model):
	league = models.ForeignKey(League, on_delete=models.CASCADE, null=True, blank=True)
	draft_team = models.ForeignKey(DraftTeam, on_delete=models.CASCADE, null=True, blank=True)
	football_player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE, null=True, blank=True)
	player_position = models.CharField(max_length=3, null=True, blank=True)
	player_team = models.ForeignKey(NflTeam, on_delete=models.CASCADE, null=True, blank=True)
	draft_spot = models.IntegerField(null=True, blank=True)
	starter = models.BooleanField(default = False, null=True, blank=False)
	flex = models.BooleanField(default = False, null=True, blank=False) 
	rostered = models.BooleanField(default = False, blank=False)

	def __str__(self):
		football_player = str(self.football_player).replace(' ', '')
		draft_spot = str(self.draft_spot).replace(' ', '')
		draft_team = str(self.draft_team).replace(' ', '')
		league = str(self.league).replace(' ', '')
		return f"{football_player} #{draft_spot} {draft_team} {league}"


	def store_drafted_player(league, draft_team, football_player, position, current_pick_num, request, slug, team):
		drafters_picks = FootballPlayerDraftSpot.objects.filter(league=league, draft_team=draft_team)
		drafters_picks_positions = [i.player_position for i in drafters_picks]
		drafters_flex_player = [i for i in drafters_picks if i.flex == True]
		flex_count = len(drafters_flex_player)

		pick = 'Valid'
		qb_count = drafters_picks_positions.count('QB')
		if position == 'QB':
			if qb_count >= 4:	pick = 'Invalid'
		rb_count = drafters_picks_positions.count('RB')
		if position == 'RB':
			if rb_count >= 8:	pick = 'Invalid'
		wr_count = drafters_picks_positions.count('WR')
		if position == 'WR':
			if wr_count >= 8:	pick = 'Invalid'
		te_count = drafters_picks_positions.count('TE')
		if position == 'TE':
			if te_count >= 3:	pick = 'Invalid'
		def_count = drafters_picks_positions.count('DEF')
		if position == 'DEF':
			if def_count >= 3:	pick = 'Invalid'
		k_count = drafters_picks_positions.count('K')
		if position == 'K':
			if k_count >= 3:	pick = 'Invalid'

		if pick == 'Invalid':
			messages.info(request, f"{draft_team} Has Attempted To Draft Too Many {position}'s.")
			messages.info(request, 'Please Draft A Player From A Different Position.')
			return redirect('draft_live', slug=slug)

		all_positions = ['QB', 'RB', 'WR', 'TE', 'DEF', 'K']
		needed_positions = [position for position in all_positions if position not in drafters_picks_positions]
		total_picks = len(drafters_picks_positions)
		picks_left = 16 - total_picks
		string_needed_positions = ", ".join(needed_positions)

		rb_count = drafters_picks_positions.count('RB')
		wr_count = drafters_picks_positions.count('WR')

		if picks_left == len(needed_positions):
			if position not in needed_positions:
				messages.info(request, f"{draft_team} Must Draft At Least One Player From Every Position")
				messages.info(request, 'Please Draft A Player From One Of The Following Positions:')
				messages.info(request, f'{string_needed_positions}')
				return redirect('draft_live', slug=slug)

		starter = False
		if position == 'QB':
			if qb_count == 0:
				starter = True
		elif position == 'RB':
			if rb_count < 2:
				starter = True
		elif position == 'WR':
			if wr_count < 2:
				starter = True
		elif position == 'TE':
			if te_count == 0:
				starter = True
		elif position == 'DEF':
			if def_count == 0:
				starter = True
		elif position == 'K':
			if k_count == 0:
				starter = True

		flex = False
		if starter == False and flex_count == 0:
			if position == 'RB' and rb_count == 2:
				starter = True
				flex = True
			elif position == 'WR' and wr_count == 2:
				starter = True
				flex = True
			elif position == 'TE' and te_count == 1:
				starter = True
				flex = True

		player_team = NflTeam.objects.get(franchise=team)

		store_player = FootballPlayerDraftSpot.objects.create(league=league, 
			draft_team=draft_team, football_player=football_player, player_position=position,
			draft_spot=current_pick_num, starter=starter, flex=flex, rostered=True, player_team=player_team)

		return store_player
		

	def get_drafted_players(league_name):
		league = League.objects.get(league_name=league_name, completed=False)
		players = league.footballplayerdraftspot_set.all()
		players.order_by('draft_spot')
		drafted_players = [str(player.football_player) for player in players]
		return drafted_players


	def get_drafted_players_with_postitions(league_name):
		league = League.objects.get(league_name=league_name, completed=False)
		players = league.footballplayerdraftspot_set.all()
		players.order_by('draft_spot')
		drafted_players_with_postitions = [f"{player.player_position} {player.football_player}" for player in players]
		return drafted_players_with_postitions


	def make_draft_board_picks(drafted_players_with_postitions, max_draft_amount, league_amount):
		empty_strings_needed = max_draft_amount - len(drafted_players_with_postitions)
		for i in range(empty_strings_needed):
			drafted_players_with_postitions.append(f"Player Not Selected")			
		snake_draft_board = []
		for i in range(16):
			snake = drafted_players_with_postitions[0:league_amount]
			if i % 2 != 0:
				snake.reverse()
			snake_draft_board.append(snake)
			for i in range(league_amount):
				del drafted_players_with_postitions[0]
		return snake_draft_board

	def make_snake(drafted_order, league_amount):
		make_snake = []
		for i in range(16):
			snake = drafted_order[0:league_amount]
			if i % 2 != 0:
				snake.reverse()
			make_snake.append(snake)
			for i in range(league_amount):
				del drafted_order[0]
		return make_snake



