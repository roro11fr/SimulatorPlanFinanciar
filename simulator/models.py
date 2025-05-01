from django.db import models

class UserFinancialProfile(models.Model):
    JOB_CHOICES = [
        ('medic', 'Medic'),
        ('freelancer', 'Freelancer'),
        ('corporatist', 'Corporatist'),
        ('student', 'Student'),
        ('altul', 'Altul'),
    ]

    job = models.CharField(max_length=20, choices=JOB_CHOICES)
    venit_lunar = models.DecimalField(max_digits=10, decimal_places=2)
    cheltuieli_lunare = models.DecimalField(max_digits=10, decimal_places=2)
    economii_lunare = models.DecimalField(max_digits=10, decimal_places=2)
    planuri = models.TextField(blank=True)  # de ex: "investitii, pensie, planuri de studiu"

    def __str__(self):
        return f"{self.job} - {self.venit_lunar} RON"

