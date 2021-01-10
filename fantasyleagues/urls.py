from django.urls import path
from . import views

urlpatterns = [
	path('createdleagues/', views.join_created_leagues, name='join_created_leagues'), 
	path('createdleagues/claimteam/<slug>/', views.claim_team, name='claim_team'),
]