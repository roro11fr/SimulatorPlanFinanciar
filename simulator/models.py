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
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default='low', verbose_name="Nivel de risc")
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='RON', verbose_name="Monedă")
    start_date = models.DateField(verbose_name="Data Începerii")
    end_date = models.DateField(verbose_name="Data Finalizării")
    monthly_expense = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cheltuieli lunare", default=0.00)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Venit lunar", default=0.00)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Simulation(models.Model):
    investment_plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE, related_name="simulations")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    initial_investment = models.DecimalField(max_digits=12, decimal_places=2)
    risk_level = models.CharField(max_length=10)
    years = models.PositiveIntegerField()
    simulations_run = models.PositiveIntegerField(default=500)

    result_image_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Simulare #{self.id} - {self.user.username} ({self.created_at.date()})"