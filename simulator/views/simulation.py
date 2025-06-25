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

from fredapi import Fred
import pandas as pd
from decimal import Decimal

def get_historical_inflation(api_key: str) -> pd.Series:
    """
    Returnează inflația anuală reală (YOY) din FRED pentru perioada fixă 1994–2023.
    """
    fred = Fred(api_key=api_key)
    cpi = fred.get_series('CPIAUCNS', observation_start="1993-12-01", observation_end="2023-12-31")

    cpi.index = pd.to_datetime(cpi.index)
    cpi_annual = cpi.to_frame(name="CPI").resample('YE').last()
    inflation = cpi_annual.pct_change().dropna()

    if inflation.empty:
        raise ValueError("Inflația istorică nu a putut fi calculată.")

    return inflation.squeeze()
# ======================================
# Simulare Monte Carlo
# ======================================


def monte_carlo_simulation_with_historical_data(
    initial, monthly, expense, income,
    years=30, simulations=500,
    symbol="^GSPC", start_date="1994-01-01", end_date="2024-12-31",
    api_key=None):

    if api_key is None:
        raise ValueError("Trebuie să furnizezi api_key pentru FRED.")

    # Conversii
    initial = float(initial)
    monthly = float(monthly)
    expense = float(expense)
    income = float(income)

    # Date istorice
    historical_data = get_historical_data(symbol, start_date, end_date)
    if ('Close', symbol) not in historical_data.columns:
        raise ValueError("Nu am găsit o coloană 'Close' în datele istorice")

    historical_data['Daily Return'] = historical_data['Close'].pct_change()
    annual_returns = historical_data['Daily Return'].resample('YE').apply(lambda x: (1 + x).prod() - 1).dropna().values
    inflation_series = get_historical_inflation(api_key).dropna().values

    results = []

    for _ in range(simulations):
        value = initial
        scenario = []

        annual_expense = expense * 12
        annual_contribution = monthly * 12
        annual_income = income * 12

        sampled_inflation = [random.choice(inflation_series) for _ in range(years)]
        sampled_returns = [random.choice(annual_returns) for _ in range(years)]

        for year in range(years):
            shock = sampled_returns[year]
            inf_cumul = np.prod([1 + sampled_inflation[i] for i in range(year + 1)])

            current_expense = annual_expense * inf_cumul
            current_contribution = annual_contribution * inf_cumul
            current_income = annual_income * inf_cumul

            value = (value + current_contribution) * (1 + shock)
            scenario.append(value)

        results.append(scenario)

    return np.array(results)


def monte_carlo_clasic(
    initial, monthly, expense, income,
    years=30, simulations=500,
    mean_return=0.07, std_dev=0.15):

    initial = float(initial)
    monthly = float(monthly)
    expense = float(expense)
    income = float(income)

    results = []

    for _ in range(simulations):
        value = initial
        scenario = []

        annual_contribution = monthly * 12

        for year in range(years):
            shock = np.random.normal(loc=mean_return, scale=std_dev)
            inflation = np.random.normal(0.025, 0.01)
            inf_cumul = (1 + inflation) ** year

            current_contribution = annual_contribution * inf_cumul
            value = (value + current_contribution) * (1 + shock)
            scenario.append(value)

        results.append(scenario)

    return np.array(results)



def monte_carlo_gbm(
    initial, monthly, expense, income,
    years=30, simulations=500,
    mean_return=0.07, std_dev=0.15):

    initial = float(initial)
    monthly = float(monthly)
    expense = float(expense)
    income = float(income)

    results = []

    for _ in range(simulations):
        value = initial
        scenario = []

        annual_contribution = monthly * 12

        for year in range(years):
            Z = np.random.normal()
            shock = np.exp((mean_return - 0.5 * std_dev ** 2) + std_dev * Z) - 1
            inflation = np.random.normal(0.025, 0.01)
            inf_cumul = (1 + inflation) ** year

            current_contribution = annual_contribution * inf_cumul
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

def run_all_simulations_and_compare(plan, years, symbol, start_date, end_date, api_key):
    methods = {}

    # Bootstrapping
    scenarios_boot = monte_carlo_simulation_with_historical_data(
        initial=plan.initial_investment,
        monthly=plan.monthly_contribution,
        expense=plan.monthly_expense,
        income=plan.monthly_income,
        years=years, simulations=500,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        api_key=api_key
    )
    methods["Bootstrapping"] = (scenarios_boot, evaluate_monte_carlo_error(scenarios_boot))

    # Clasic
    scenarios_norm = monte_carlo_clasic(
        initial=plan.initial_investment,
        monthly=plan.monthly_contribution,
        expense=plan.monthly_expense,
        income=plan.monthly_income,
        years=years, simulations=500
    )
    methods["Clasic"] = (scenarios_norm, evaluate_monte_carlo_error(scenarios_norm))

    # GBM
    scenarios_gbm = monte_carlo_gbm(
        initial=plan.initial_investment,
        monthly=plan.monthly_contribution,
        expense=plan.monthly_expense,
        income=plan.monthly_income,
        years=years, simulations=500
    )
    methods["GBM"] = (scenarios_gbm, evaluate_monte_carlo_error(scenarios_gbm))

    return methods


def start_simulation(request, plan_id):
    plan = get_object_or_404(InvestmentPlan, id=plan_id, user=request.user)

    start = plan.start_date
    end = plan.end_date
    years = (end - start).days // 365

    symbol = plan.stock_index
    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")
    fred_api_key = settings.FRED_API_KEY

    # Rulăm toate cele 3 simulări și comparăm
    methods = run_all_simulations_and_compare(plan, years, symbol, start_date, end_date, fred_api_key)

    print("\n=========== COMPARAȚIE ERORI MONTE CARLO ===========")
    for name, (scenarios, metrics) in methods.items():
        mean = metrics["mean"]
        std = metrics["std_dev"]
        se = metrics["standard_error"]
        ci_low, ci_high = metrics["confidence_interval_95"]

        std_pct = (std / mean) * 100
        se_pct = (se / mean) * 100
        ci_pct = ((ci_high - mean) / mean) * 100

        print(f"🔸 {name}")
        print(f"   Medie finală: {mean:,.2f} RON")
        print(f"   Std Dev: {std:,.2f} RON ({std_pct:.2f}%)")
        print(f"   SE: {se:,.2f} RON ({se_pct:.2f}%)")
        print(f"   CI 95%: [{ci_low:,.2f} ... {ci_high:,.2f}] (±{ci_pct:.2f}%)")
        print("-----------------------------------------------------")

    
    chart_htmls = {}
    annual_contribution = float(plan.monthly_contribution) * 12
    initial = float(plan.initial_investment)

    for name, (scenarios, metrics) in methods.items():
        chart_htmls[name] = plot_simulation_as_html(
            scenarios,
            annual_contribution=annual_contribution,
            initial=initial
        )

    # alegem și metoda cu eroarea standard cea mai mică
    best_method = min(methods.items(), key=lambda x: x[1][1]['standard_error'])
    best_name = best_method[0]

    # Salvăm doar rezultatul final + metoda aleasă
    sim = Simulation.objects.create(
        investment_plan=plan,
        user=request.user,
        initial_investment=plan.initial_investment,
        years=years,
        result_image_path="",
        simulations_run=500
    )

    return render(request, 'simulator/simulare_resultate.html', {
        'plan': plan,
        'simulare': sim,
        'chart_htmls': chart_htmls,
        'metoda_aleasa': best_name
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


def evaluate_monte_carlo_error(scenarios: np.ndarray) -> dict:
    """
    Calculează erorile estimării Monte Carlo:
    - media valorii finale
    - deviația standard
    - standard error (SE)
    - interval de încredere 95%
    """
    final_values = scenarios[:, -1]
    n = len(final_values)

    mean_final = np.mean(final_values)
    std_final = np.std(final_values)
    se_final = std_final / np.sqrt(n)
    ci_lower = mean_final - 1.96 * se_final
    ci_upper = mean_final + 1.96 * se_final

    return {
        "mean": mean_final,
        "std_dev": std_final,
        "standard_error": se_final,
        "confidence_interval_95": (ci_lower, ci_upper)
    }
