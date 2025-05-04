from django.db import models
from django.contrib.auth.models import User

class InvestmentPlan(models.Model):
    PLAN_TYPE_CHOICES = [
        ('investitii', 'Plan de Investiții'),
    ]

    PAYMENT_FREQUENCY_CHOICES = [
        ('monthly', 'Lunar'),
        ('quarterly', 'Trimestrial'),
        ('semiannual', 'Semestrial'),
        ('annual', 'Anual'),
    ]

    RISK_LEVEL_CHOICES = [
        ('low', 'Scăzut'),
        ('medium', 'Mediu'),
        ('high', 'Ridicat'),
    ]

    CURRENCY_CHOICES = [
        ('RON', 'RON'),
        ('EUR', 'EUR'),
        ('USD', 'USD'),
    ]

    user = models.ForeignKey(User, related_name="investment_plans", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Numele Planului")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='investitii')
    payment_frequency = models.CharField(max_length=20, choices=PAYMENT_FREQUENCY_CHOICES)
    initial_investment = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Investiție Inițială")
    monthly_contribution = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Contribuție lunară")
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, verbose_name="Nivel de risc")
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='RON', verbose_name="Monedă")
    start_date = models.DateField(verbose_name="Data Începerii")
    end_date = models.DateField(verbose_name="Data Finalizării")

    def __str__(self):
        return f"{self.name} - {self.user.username}"
