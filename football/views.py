from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from draft.models import DraftTeam
from fantasyleagues.models import League


def homepage(request):
    if request.user.is_authenticated:       
        user = request.user
        completed_drafts = League.objects.filter(completed=True)
        teams = DraftTeam.objects.filter(team_owner=user)
        user_teams = [i for i in teams if i.league in completed_drafts]
        teamnames_leagues_id = League.teamnames_leagues_id(user_teams)
        context = {'user': user, 'teamnames_leagues_id': teamnames_leagues_id}
        return render(request, 'homepage.html', context)
    else:
        context = {}
        return render(request, 'homepage.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form':form})



def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form':form})



