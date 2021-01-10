from django.db import models
from django.contrib.auth.models import User




class League(models.Model):
	league_name = models.CharField(max_length=20)
	commissioner = models.ForeignKey(User, on_delete=models.SET_NULL, null = True, blank = True)
	completed = models.BooleanField(default = False, null=True, blank=False)
	league_amount = models.IntegerField(null=True, blank=True)
	amount_joined = models.IntegerField(default=1)
	league_key = models.CharField(max_length=20, null=True, blank=True)

	def __str__(self):
		league_name = str(self.league_name) 
		id = str(self.id)
		return f"{league_name} - {id}"

	def teamnames_leagues_id(user_teams):
		teamnames_leagues_id = []
		for i in user_teams:
			team_name = i.team_name
			league = str(i.league)
			league = league.split(' -')[0]
			team_id = i.id
			teamnames_leagues_id.append([team_name, league, team_id])
		return teamnames_leagues_id




