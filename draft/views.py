from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import DraftTeam, FootballPlayerDraftSpot
from fantasyleagues.models import League
from .forms import DraftSetupForm, DraftTeamsForm
from django.forms import formset_factory 
from django.contrib import messages
import random
from nflinfo.models import FootballPlayer

from userleague.models import LeagueMatchup


def draft(request):
	return redirect('draft_setup')


def draft_setup(request):
	if request.user.is_authenticated == False:
		return redirect('login')
	user = request.user
	league = League.objects.filter(commissioner=user, completed=False)
	league_count = league.count()
	if league_count >= 1:
		return redirect('previous_draft')

	if request.method == 'POST':
		form = DraftSetupForm(request.POST)
		desired_league_name = form['league_name'].value()
		desired_league_key = form['league_key'].value()
		if len(desired_league_key) == 0:
			messages.info(request, f"League Key Can Not Be Left Blank.")
			return redirect('draft_setup')
		if desired_league_key.count(' ') == len(desired_league_key):
			messages.info(request, f"Invalid League Key. Try Again")
			return redirect('draft_setup')

		leagues = League.objects.filter(commissioner=user, completed=True)
		for info in leagues:
			if info.league_name == desired_league_name:
				messages.info(request, f"You are already commissioner of a league called {desired_league_name}. Please choose another league name.")
				return redirect('draft_setup')
			
		if form.is_valid():
			form = form.save()
			form.commissioner = request.user
			form.league_amount = request.POST['send'] # Number of league buttons
			form.save()
			return redirect('draft_teams')
	else:
		form = DraftSetupForm()
		context = {'form':form, 'user':user}

	return render(request, 'draft_setup.html', context)



def draft_teams(request):
	if request.user.is_authenticated == False:
		return redirect('login')
	user = request.user
	league = League.objects.filter(commissioner=user, completed=False)
	try:
		league_amount = league.values_list('league_amount', flat=True)[0] # Link above
	except IndexError:
		return redirect('draft_setup')
	str_league = League.objects.filter(commissioner=user, completed=False)[0]
	draft_players = DraftTeam.objects.filter(league=str_league)
	if len(draft_players) == league_amount:
		return redirect('draft_order')
	DraftTeamSet = formset_factory(DraftTeamsForm, min_num=league_amount, max_num=league_amount, 
		validate_min=True, validate_max=True)
	formset = DraftTeamSet(request.POST or None)
	if formset.is_valid():
		duplicate_check = []
		for form in formset:
			form = form.save(commit=False)	
			duplicate_check.append(form.team_name)
		if len(duplicate_check) == len(set(duplicate_check)):
			for form in formset:
				form = form.save(commit=False)
				form.league = League.objects.get(commissioner=user, completed=False)
				form.save()
			commissioner = formset[0].save(commit=False)
			commish_team = DraftTeam.objects.get(league=league[0], team_name=commissioner)
			commish_team.team_owner = user
			commish_team.commissioner = True
			commish_team.save()
			return redirect('draft_order')
		else:
			messages.info(request, '*Duplicate names found')
			#return redirect('draft_teams')	
	context = {'league': league, 'formset':formset}
	return render(request, 'draft_teams.html', context)




def draft_order(request):
	if request.user.is_authenticated == False:
		return redirect('login')
	try:
		user = request.user
		league = League.objects.filter(commissioner=user, completed=False)
		for info in league:
			league_id = info.id
			league_amount = info.league_amount
			str_league = info.league_name
		draft_players = DraftTeam.objects.filter(league__league_name=str_league, league__completed=False)
		if len(draft_players) == 0:		
			return redirect('draft_teams')		
		drafters_no_draft_spot = [drafter.team_name for drafter in draft_players if drafter.draft_spot == None]
		if len(drafters_no_draft_spot) == 0:	
			return redirect('draft_live', slug='RANK')

		random_drafter = drafters_no_draft_spot[random.randint(0, len(drafters_no_draft_spot)-1)]
		available_draft_nums = DraftTeam.available_draft_nums(draft_players)
		draft_order_incomplete_list = DraftTeam.draft_order_incomplete_list(user, draft_players, available_draft_nums)

	except IndexError:
		return redirect('draft_setup')

	if request.method == 'POST':
		drafter_info = request.POST['send']
		team_name, draft_spot = drafter_info.split('-')
		league = League.objects.get(commissioner=request.user, completed=False)
		draft_team = DraftTeam.objects.get(league=league, team_name=team_name)
		draft_team.draft_spot = int(draft_spot)
		draft_team.save()
		return redirect('draft_order')

	context = {'draft_players':draft_players, 'str_league':str_league, 'random_drafter':random_drafter, 
	'available_draft_nums':available_draft_nums, 'draft_order_incomplete_list':draft_order_incomplete_list}
	return render(request, 'draft_order.html', context)




def draft_live(request, slug):
	if request.user.is_authenticated == False:
		return redirect('login')

	possible_slugs = ['rank', 'qb', 'rb', 'wr', 'te', 'def', 'k']
	if slug not in possible_slugs:
		slug = 'rank'

	user = request.user
	league = League.objects.filter(commissioner=user, completed=False)
	if len(league) == 0:
		return redirect('draft_setup')
	else:
		for info in league:
			league_name = info.league_name
			league_amount = info.league_amount
			league_id = info.id
	draft_order = DraftTeam.get_draft_order(league_name, league_amount)
	if draft_order == None:
		return redirect('draft_order')
	drafted_players = FootballPlayerDraftSpot.get_drafted_players(league_name)
	drafted_players_with_postitions = FootballPlayerDraftSpot.get_drafted_players_with_postitions(league_name)
	players = FootballPlayer.objects.all().order_by('rank')
	available_players = [player for player in players if player.name not in drafted_players]

	if slug != 'rank':
		available_players = [player for player in available_players if player.position == slug.upper()]
	
	max_draft_amount = league_amount * 16
	amount_players_drafted = len(drafted_players)
	updated_draft_order = DraftTeam.updated_draft_order(draft_order, amount_players_drafted)
	try:
		current_drafter = updated_draft_order[0]
	except IndexError:
		return redirect('draft_order')
	upcoming_drafters = updated_draft_order[1:6]
	current_pick_num = updated_draft_order.count('Draft Finished')+1
	upcoming_picks_nums = [current_pick_num + pick for pick in range(1,6)]
	make_draft_board_picks = FootballPlayerDraftSpot.make_draft_board_picks(drafted_players_with_postitions, max_draft_amount, league_amount)


	# Draft Complete
	if current_pick_num > max_draft_amount:
		league = League.objects.get(commissioner=user, completed=False)
		league.completed = True
		league.save()
		return redirect('draft_results', slug=league_id)
	# User selects a player
	if request.method == 'POST':
		post = request.POST
		try:
			sort_position = post['sort'].lower()
			if sort_position == 'd/st':
				sort_position = 'def'
			return redirect('draft_live', slug=sort_position)
		except KeyError:
			pass
		player_info = request.POST['send']
		player, rank, position, team = player_info.split(',')
		if player in drafted_players:
			return redirect('draft_live', slug='rank')
		league = League.objects.get(commissioner=request.user, completed=False)
		draft_team = DraftTeam.objects.get(league=league, team_name=current_drafter)
		football_player = FootballPlayer.objects.get(name=player, rank=rank)
		store_drafted_player = FootballPlayerDraftSpot.store_drafted_player(league, draft_team, football_player, 
			position, current_pick_num, request, slug, team)
		return redirect('draft_live', slug=slug)
		
	context = {'available_players': available_players, 'league_name': league_name, 
				'current_drafter': current_drafter, 'upcoming_drafters': upcoming_drafters,
				'current_pick_num':current_pick_num, 'upcoming_picks_nums':upcoming_picks_nums,
				'draft_order':draft_order, 'make_draft_board_picks':make_draft_board_picks, 'slug':slug}
				
	return render(request, 'draft_live.html', context)




def previous_draft(request):
	user = request.user
	league = League.objects.filter(commissioner=user, completed=False)
	league_count = league.count()
	if league_count == 0:
		return redirect('draft_setup')
	if request.method == 'POST':
		user_choice = request.POST['send']
		if user_choice == "Continue Previous Draft":
			return redirect('draft_live', slug='rank')
		if user_choice == "Delete Previous Draft":
			print(league)
			league.delete()
			return redirect('draft_setup')

	context = {'league': league}
	return render(request, 'previous_draft.html', context)
