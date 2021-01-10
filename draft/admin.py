from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from .models import *
from fantasyleagues.models import League


# Register your models here.


class LeagueAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)




admin.site.register(League, LeagueAdmin)
admin.site.register(DraftTeam, LeagueAdmin)
admin.site.register(FootballPlayerDraftSpot, LeagueAdmin)




