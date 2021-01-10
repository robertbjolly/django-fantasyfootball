from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from .models import *





class PLayerAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(FootballPlayer, PLayerAdmin)
admin.site.register(NflTeam)
admin.site.register(NflMatchup)
admin.site.register(NflWeek)
admin.site.register(NflPlayerStat)