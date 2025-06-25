from django import forms
from django.contrib.auth.models import User
from .models import InvestmentPlan, Simulation
from django.core.exceptions import ValidationError


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class InvestmentPlanForm(forms.ModelForm):
    class Meta:
        model = InvestmentPlan
        fields = [
            'name', 'stock_index', 'payment_frequency', 'initial_investment',
            'monthly_contribution', 'currency', 'start_date', 'end_date',
            'monthly_expense', 'monthly_income'
        ]
        labels = {
            'name': 'Numele Planului',
            'stock_index': 'Indexul bursier',
            'payment_frequency': 'Frecventa Contributiilor',
            'initial_investment': 'Investitie Initială',
            'monthly_contribution': 'Contributie lunară',
            'currency': 'Monedă',
            'start_date': 'Data Începerii',
            'end_date': 'Data Finalizării',
            'monthly_expense': 'Cheltuieli lunare',
            'monthly_income': 'Venit lunar',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),    
            'stock_index': forms.Select(attrs={'class': 'form-control'}),
            'payment_frequency': forms.Select(attrs={'class': 'form-control'}),
            'initial_investment': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_contribution': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monthly_expense': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        monthly_contribution = cleaned_data.get("monthly_contribution")
        monthly_income = cleaned_data.get("monthly_income")
        monthly_expense = cleaned_data.get("monthly_expense")

        if start and end and start >= end:
            raise ValidationError("Data finalizării trebuie să fie după data începerii.")
        
        if monthly_contribution and monthly_income and monthly_expense:
            available_income = monthly_income - monthly_expense
            if monthly_contribution > available_income:
                raise ValidationError("Contribuția lunară nu poate depăși venitul disponibil după cheltuieli.")
        
        return cleaned_data
    

class SimulationForm(forms.ModelForm):
    class Meta:
        model = Simulation
        fields = ['initial_investment', 'years', 'simulations_run']