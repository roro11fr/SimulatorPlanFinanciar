from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from simulator.models import InvestmentPlan

@login_required
def dashboard_view(request):
    investment_plans = InvestmentPlan.objects.filter(user=request.user)
    return render(request, 'simulator/dashboard.html', {'investment_plans': investment_plans})

