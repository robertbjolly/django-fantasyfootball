from django.urls import path
from . import views

urlpatterns = [
	path('', views.draft, name='draft'),
    path('setup/', views.draft_setup, name='draft_setup'),
    path('previous/', views.previous_draft, name='previous_draft'),
    path('teams/', views.draft_teams, name='draft_teams'),
    path('order/', views.draft_order, name='draft_order'),
    path('live/<slug>', views.draft_live, name='draft_live'),
]