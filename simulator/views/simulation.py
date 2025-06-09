import os
import uuid
import random
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from simulator.models import Simulation, InvestmentPlan
from simulator.utils import get_historical_data


def monte_carlo_simulation_with_historical_data(
    initial, monthly, expense, income,
    years=30, simulations=500,
    symbol="^GSPC", start_date="2010-01-01", end_date="2025-01-01",
    risk_level="medium"):

    historical_data = get_historical_data(symbol, start_date, end_date)

    if ('Close', symbol) in historical_data.columns:
        historical_data['Daily Return'] = historical_data[('Close', symbol)].pct_change()
    else:
        raise ValueError("Nu am găsit o coloană 'Close' în datele istorice")

    # ✅ Calcul corect al randamentelor anuale compuse
    annual_returns = historical_data['Daily Return'].resample('YE').apply(lambda x: (1 + x).prod() - 1)

    # 📊 DEBUG – Statistici despre randamente
    print("========== DEBUG: Randamente anuale compuse ==========")
    print(annual_returns.describe())
    print("======================================================")

    mean_return = annual_returns.mean()
    std_dev = annual_returns.std()

    print(f"[DEBUG] Media randamentelor anuale (mean): {mean_return:.4f}")
    print(f"[DEBUG] Deviația standard anuală (std): {std_dev:.4f}")

    # Definim șocurile bazate pe nivelul de risc
    if risk_level == "low":
        shock_neg = -0.03  # -3%
        shock_pos = 0.02   # +2%
        shock_prob = 0.05  # 5% șansă de șoc
    elif risk_level == "medium":
        shock_neg = -0.05  # -5%
        shock_pos = 0.03   # +3%
        shock_prob = 0.10  # 10% șansă de șoc
    else:  # high
        shock_neg = -0.08  # -8%
        shock_pos = 0.05   # +5%
        shock_prob = 0.15  # 15% șansă de șoc

    results = []
    for _ in range(simulations):
        value = initial
        scenario = []
        annual_expense = expense * 12
        annual_contribution = monthly * 12
        annual_income = income * 12

        for year in range(years):
            # Generate random inflation for this year
            inflation = np.random.normal(0.03, 0.01)
            
            current_expense = annual_expense * (1 + inflation) ** year
            current_contribution = annual_contribution * (1 + inflation) ** year
            current_income = annual_income * (1.02) ** year

            # cashflow = (current_income - current_expense - current_contribution)
            shock = np.random.normal(mean_return, std_dev)

            # Aplicăm șocurile bazate pe probabilitate și nivelul de risc
            if random.random() < shock_prob:
                # 50% șansă pentru șoc pozitiv sau negativ
                if random.random() < 0.5:
                    shock = shock_pos
                else:
                    shock = shock_neg

            # ✅ Actualizare valoare corectă
            value = (value + current_contribution) * (1 + shock)
            scenario.append(value)

        results.append(scenario)

    return np.array(results)


def plot_simulation_as_html(scenarios, annual_contribution, initial=0):
    arr = np.array(scenarios)
    mean = np.mean(arr, axis=0)
    p10 = np.percentile(arr, 10, axis=0)
    p90 = np.percentile(arr, 90, axis=0)

    years = len(mean)
    years_range = list(range(1, years + 1))
    contribution_line = [annual_contribution * (i + 1) for i in range(years)]

    valoare_finala = mean[-1]
    total_contributii = initial + contribution_line[-1]
    if total_contributii > 0:
        cagr = ((valoare_finala / total_contributii) ** (1 / years) - 1) * 100
    else:
        cagr = 0.0
    cagr_formatted = f"{cagr:.2f}%"
    
    # Calculate estimated profit
    profit_estimat = valoare_finala - total_contributii
    profit_formatted = f"{profit_estimat:,.2f} RON"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years_range, y=p90, fill=None, mode='lines', line_color='rgba(0, 100, 255, 0.2)', name='90%'))
    fig.add_trace(go.Scatter(x=years_range, y=p10, fill='tonexty', mode='lines', line_color='rgba(0, 100, 255, 0.2)', name='10%'))
    fig.add_trace(go.Scatter(x=years_range, y=mean, mode='lines', name='Valoare simulată', line=dict(color='blue', width=2),
                             hovertemplate='An: %{x}<br>Valoare: %{y:,.2f} RON<extra></extra>'))
    fig.add_trace(go.Scatter(x=years_range, y=contribution_line, mode='lines', name='Contribuții totale',
                             line=dict(color='green', width=2, dash='dash'),
                             hovertemplate='An: %{x}<br>Contribuții: %{y:,.2f} RON<extra></extra>'))

    fig.update_layout(
        title=f'Evoluție simulată vs. contribuții (Randament mediu: {cagr_formatted}/an | Profit estimat: {profit_formatted})',
        xaxis_title='Ani',
        yaxis_title='Valoare (RON)',
        hovermode='x unified',
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def start_simulation(request, plan_id):
    plan = get_object_or_404(InvestmentPlan, id=plan_id, user=request.user)

    start = plan.start_date
    end = plan.end_date
    years = (end - start).days // 365

    symbol = "^GSPC"
    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

    scenarios = monte_carlo_simulation_with_historical_data(
        float(plan.initial_investment),
        float(plan.monthly_contribution),
        float(plan.monthly_expense),
        float(plan.monthly_income),
        years=years,
        simulations=500,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        risk_level=plan.risk_level
    )

    annual_contribution = float(plan.monthly_contribution) * 12
    chart_html = plot_simulation_as_html(scenarios, annual_contribution, initial=float(plan.initial_investment))

    sim = Simulation.objects.create(
        investment_plan=plan,
        user=request.user,
        initial_investment=plan.initial_investment,
        risk_level=plan.risk_level,
        years=years,
        result_image_path="",
        simulations_run=500
    )

    return render(request, 'simulator/simulare_resultate.html', {
        'plan': plan,
        'simulare': sim,
        'chart_html': chart_html
    })


@login_required
def istoric_simulari(request, plan_id):
    plan = get_object_or_404(InvestmentPlan, id=plan_id, user=request.user)
    simulari = Simulation.objects.filter(investment_plan=plan).order_by('-created_at')
    
    return render(request, 'simulator/istoric_simulari.html', {
        'plan': plan,
        'simulari': simulari,
        'MEDIA_URL': settings.MEDIA_URL,
    })

@require_POST
def sterge_simulare(request, simulare_id):
    simulare = get_object_or_404(Simulation, id=simulare_id, user=request.user)

    # șterge fișierul grafic dacă există
    if simulare.result_image_path:
        image_path = os.path.join(settings.MEDIA_ROOT, simulare.result_image_path)
        if os.path.exists(image_path):
            os.remove(image_path)

    plan_id = simulare.investment_plan.id
    simulare.delete()

    return redirect('istoric_simulari', plan_id=plan_id)