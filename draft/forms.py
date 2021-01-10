from django import forms
from .models import DraftTeam
from fantasyleagues.models import League


# https://www.youtube.com/watch?v=6-XXvUENY_8

class DraftSetupForm(forms.ModelForm):
	class Meta:
		model = League
		fields = ('league_name', 'league_key')
		widgets = {
			'league_name': forms.TextInput(attrs={'class':'form-control'}),
			'league_key': forms.TextInput(attrs={'class':'form-control'})
		}


class DraftTeamsForm(forms.ModelForm):
	class Meta:
		model = DraftTeam
		fields = ('team_name', )
		widgets = {
			'team_name': forms.TextInput(attrs={'class':'form-control'})
		}