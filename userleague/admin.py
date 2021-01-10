from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from .models import *


class LeagueAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)






admin.site.register(LeagueMatchup, LeagueAdmin)   