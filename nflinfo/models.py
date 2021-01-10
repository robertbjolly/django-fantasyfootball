from django.db import models
from django.contrib.auth.models import User
from fantasyleagues.models import League
from django.contrib import messages
from django.shortcuts import render, redirect



# https://www.cbssports.com/fantasy/football/stats/posvsdef/QB/all/avg/standard
# https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Football_League/National_Football_League_team_abbreviations
class NflTeam(models.Model):
	franchise = models.CharField(max_length=25)
	abbreviation = models.CharField(max_length=10)
	bye = models.IntegerField(null=True, blank=True)
	rank_against_qb = models.IntegerField(null=True, blank=True)
	rank_against_rb = models.IntegerField(null=True, blank=True)
	rank_against_wr = models.IntegerField(null=True, blank=True)
	rank_against_te = models.IntegerField(null=True, blank=True)
	rank_against_dst = models.IntegerField(null=True, blank=True)
	rank_against_k = models.IntegerField(null=True, blank=True)
	
	def __str__(self):
		return self.franchise



class NflMatchup(models.Model):
	week = models.IntegerField()
	day_of_week = models.CharField(max_length=10)
	date = models.CharField(null=True, blank=True, max_length=20)
	time = models.CharField(max_length=10, blank=True, null=True)
	home_team = models.ForeignKey(NflTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='home_team')
	away_team = models.ForeignKey(NflTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='away_team')

	def __str__(self):
		return f"Week {self.week} - {self.away_team} @ {self.home_team}"





class FootballPlayer(models.Model):
	rank = models.IntegerField(unique=True, null=True, blank=True)
	name = models.CharField(max_length=25)
	position = models.CharField(max_length=3)
	team = models.ForeignKey(NflTeam, on_delete=models.SET_NULL, null=True, blank=True)
	projection = models.DecimalField(default=0, decimal_places=1, max_digits=3)
	status = models.CharField(max_length=20, default='Healthy')
	injury_detail = models.CharField(max_length=1000, blank=True, null=True)

	def __str__(self):
		return self.name 



class NflWeek(models.Model):
	week_number = models.IntegerField(unique=True)
	week_start = models.DateTimeField(blank=True, unique=True)
	week_end = models.DateTimeField(blank=True, unique=True)

	def __str__(self):
		week_start = str(self.week_start).split('+')[0]
		week_end = str(self.week_end).split('+')[0]
		return f"{str(self.week_number)} {week_start} - {week_end} "






class NflPlayerStat(models.Model):
	week = models.IntegerField()
	player = models.ForeignKey(FootballPlayer, on_delete=models.SET_NULL, null=True, blank=True)
	opponent = models.ForeignKey(NflTeam, on_delete=models.SET_NULL, null=True, blank=True)
	carries = models.IntegerField()
	rushing_yards = models.IntegerField()
	rushing_tds = models.IntegerField()
	passing_yards = models.IntegerField()
	passing_tds = models.IntegerField()
	interceptions = models.IntegerField()
	targets = models.IntegerField()
	receptions = models.IntegerField()
	receiving_yards = models.IntegerField()
	receiving_tds = models.IntegerField()
	field_goals_made = models.IntegerField()
	field_goals_attempted = models.IntegerField()
	extra_points_made = models.IntegerField()
	total_points = models.IntegerField()


	def __str__(self):
		week = str(self.week)
		player = str(self.player)
		return f"Week {week} - {player} Stats"