import os
import uuid
import random
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings

from simulator.models import Simulation
from simulator.models import InvestmentPlan
from django.views.decorators.http import require_POST


def monte_carlo_simulation(initial, monthly, years=30, simulations=500, risk_factor=0.1):
    results = []
    for _ in range(simulations):
        value = initial
        scenario = []
        for _ in range(years):
            annual_contribution = monthly * 12
            shock = random.gauss(0, risk_factor)
            growth = 0.03 + shock
            value = (value + annual_contribution) * (1 + growth)
            scenario.append(value)
        results.append(scenario)
    return results

def plot_simulation(scenarios):
    arr = np.array(scenarios)
    mean = np.mean(arr, axis=0)
    p10 = np.percentile(arr, 10, axis=0)
    p90 = np.percentile(arr, 90, axis=0)

    plt.figure(figsize=(10, 5))
    plt.fill_between(range(len(mean)), p10, p90, color='lightblue', alpha=0.4, label='10%-90%')
    plt.plot(mean, color='blue', label='Medie')
    plt.title("Evoluție simulată")
    plt.xlabel("Ani")
    plt.ylabel("Valoare (RON)")
    plt.legend()
    plt.grid(True)

    filename = f"simulation_{uuid.uuid4().hex}.png"
    path = os.path.join(settings.MEDIA_ROOT, 'simulations', filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path)
    plt.close()
    return f"simulations/{filename}"

def start_simulation(request, plan_id):
    plan = get_object_or_404(InvestmentPlan, id=plan_id, user=request.user)

    start = plan.start_date
    end = plan.end_date
    years = (end - start).days // 365

    risk_map = {'low': 0.05, 'medium': 0.10, 'high': 0.20}
    risk_factor = risk_map.get(plan.risk_level, 0.10)

    scenarios = monte_carlo_simulation(
        float(plan.initial_investment),
        float(plan.monthly_contribution),
        years=years,
        simulations=500,
        risk_factor=risk_factor
    )
    image_path = plot_simulation(scenarios)

    sim = Simulation.objects.create(
        investment_plan=plan,
        user=request.user,
        initial_investment=plan.initial_investment,
        risk_level=plan.risk_level,
        years=years,
        result_image_path=image_path,
        simulations_run=500
    )

    return render(request, 'simulator/simulare_resultate.html', {'simulare': sim})

def istoric_simulari(request):
    simulari = Simulation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'simulator/istoric_simulari.html', {
        'simulari': simulari,
        'MEDIA_URL': settings.MEDIA_URL,
    })

@require_POST
def sterge_simulare(request, simulare_id):
    simulare = get_object_or_404(Simulation, id=simulare_id, user=request.user)
    
    # Șterge fișierul grafic, dacă există
    image_path = os.path.join(settings.MEDIA_ROOT, simulare.result_image_path)
    if os.path.exists(image_path):
        os.remove(image_path)

    simulare.delete()
    return redirect('istoric_simulari')  # asigură-te că numele URL-ului e corect
