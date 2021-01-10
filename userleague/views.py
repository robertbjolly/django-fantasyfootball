from django.shortcuts import render, redirect
from django.http import HttpResponse
from draft.models import FootballPlayer, League, DraftTeam, FootballPlayerDraftSpot
from django.contrib import messages
from .models import LeagueMatchup
from django.utils import timezone
from nflinfo.models import NflWeek, NflTeam



def team_roster(request, slug):
	# Get users league, football players, team
	user = request.user
	team = DraftTeam.objects.get(id=slug)
	players = FootballPlayerDraftSpot.objects.filter(draft_team=team)

	league = team.league
	team_manager = DraftTeam.objects.get(league=league, team_name=team).team_owner
	if team_manager == None:
		team_manager = 'Team Not Claimed'
	league_id = league.id
	league_name = league.league_name

	teams = DraftTeam.objects.filter(league=league)
	league_managers = [team.team_owner for team in teams]
	user_league_draft_team_id = [str(i.id) for i in teams if i.team_owner == user][0]
	if user not in league_managers:
		team = 'NotFound'
	starters = [player for player in players if player.starter == True]
	bench = [player for player in players if player.starter == False]
	
	# Order Starters And Bench Players
	order_starters = LeagueMatchup.order_starters(starters)
	order_bench = LeagueMatchup.order_bench(bench)

	if request.method == 'POST':
		player_1_id = request.POST['player_1'].split('_')
		player_2_id = request.POST['player_2'].split('_')
		edit_lineup = LeagueMatchup.edit_lineup(player_1_id, player_2_id, league, team)
		return redirect('team_roster', slug=slug)

	context = {'team':team, 'league_name':league_name, 'order_starters':order_starters, 
	'user_league_draft_team_id':user_league_draft_team_id, 'league_id':league_id, 'team_manager':team_manager,
	'order_bench':order_bench}

	return render(request, 'team_roster.html', context)



def draft_results(request, slug):
	user = request.user
	try:
		league = League.objects.get(id=slug)
	except:
		return redirect('team_roster', slug=slug)
	league_id = league.id
	draft_teams = DraftTeam.objects.filter(league=league)
	draft_team_owners = [team.team_owner for team in draft_teams]
	if user not in draft_team_owners:
		return redirect('team_roster', slug=slug)
	league_name = league.league_name
	league_amount = league.league_amount
	football_players = FootballPlayerDraftSpot.objects.filter(league=league).order_by('draft_spot')
	league_members = DraftTeam.objects.filter(league=league).order_by('draft_spot')
	league_draft_order =  [member.team_name for member in league_members]
	drafted_order = [f"{football_players[i].player_position} {football_players[i].football_player}" for i in range(len(football_players))]
	order_snake = FootballPlayerDraftSpot.make_snake(drafted_order, league_amount)

	context = {'league_name':league_name, 'league_draft_order':league_draft_order, 'order_snake':order_snake, 'slug':slug, 
	'league_id':league_id}
	return render(request, 'draft_results.html', context)




def league_draft_board(request):
	user = request.user
	context = {'user': user, 'league':league}
	return render(request, 'league_draft_board.html', context)
