from django.urls import path
from . import views


urlpatterns = [
	path('team_roster/<slug>/', views.team_roster, name='team_roster'),
	path('<slug>/draft_results/', views.draft_results, name='draft_results'),
]