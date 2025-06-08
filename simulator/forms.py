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
            'name', 'plan_type', 'payment_frequency', 'initial_investment',
            'monthly_contribution', 'risk_level', 'currency', 'start_date', 'end_date',
            'monthly_expense', 'monthly_income'
        ]
        labels = {
            'name': 'Numele Planului',
            'plan_type': 'Tipul Planului',
            'payment_frequency': 'Frecventa Contributiilor',
            'initial_investment': 'Investitie Initială',
            'monthly_contribution': 'Contributie lunară',
            'risk_level': 'Nivel de risc',
            'currency': 'Monedă',
            'start_date': 'Data Începerii',
            'end_date': 'Data Finalizării',
            'monthly_expense': 'Cheltuieli lunare',
            'monthly_income': 'Venit lunar',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'plan_type': forms.Select(),
            'payment_frequency': forms.Select(),
            'risk_level': forms.Select(),
            'currency': forms.Select(),
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
        fields = ['initial_investment', 'risk_level', 'years', 'simulations_run']