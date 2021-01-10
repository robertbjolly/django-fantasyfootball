from django.shortcuts import render, redirect
from django.http import HttpResponse
from draft.models import FootballPlayer, League, DraftTeam, FootballPlayerDraftSpot
from django.contrib import messages




def join_created_leagues(request):
	if request.user.is_authenticated == False:
		return redirect('login')
	user = request.user
	leagues = League.objects.filter(completed=True)
	leagues = [league for league in leagues if league.amount_joined != league.league_amount]
	context = {'user': user, 'leagues':leagues}
	return render(request, 'join_created_leagues.html', context)





def claim_team(request, slug):
	if request.user.is_authenticated == False:
		return redirect('login')
	league = League.objects.get(id=slug)
	league_name = str(league).split(' -')[0]
	teams = DraftTeam.objects.filter(league=league)
	context = {'teams':teams, 'league_name':league_name}

	if request.method == 'POST':
		guessed_league_key = request.POST['league_key']
		team_name = request.POST['team_name']
		correct_league_key = league.league_key
		user = request.user
		team_owners = [team.team_owner for team in teams]
		valid = True
		if user in team_owners:
			messages.info(request, f"* You already manage a team in {league_name}.")
			valid = False
		if guessed_league_key != correct_league_key:
			messages.info(request, f"* Incorrect League Key")
			valid = False
		if valid != False:
			league.amount_joined += 1
			league.save()
			team = DraftTeam.objects.get(league=league, team_name=team_name)
			team.team_owner = user
			team.save()
			messages.info(request, f"* Successfully took ownership of {team_name}.")
			return redirect('claim_team', slug=slug)
	return render(request, 'claim_team.html', context)

	


