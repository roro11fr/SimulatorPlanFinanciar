from django import forms
from django.contrib.auth.models import User
from .models import InvestmentPlan
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
            'monthly_contribution', 'risk_level', 'currency', 'start_date', 'end_date'
        ]
        labels = {
            'name': 'Numele Planului',
            'plan_type': 'Tipul Planului',
            'payment_frequency': 'Frecvența Contribuțiilor',
            'initial_investment': 'Investiție Inițială',
            'monthly_contribution': 'Contribuție lunară',
            'risk_level': 'Nivel de risc',
            'currency': 'Monedă',
            'start_date': 'Data Începerii',
            'end_date': 'Data Finalizării',
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
        if start and end and start >= end:
            raise ValidationError("Data finalizării trebuie să fie după data începerii.")
        return cleaned_data