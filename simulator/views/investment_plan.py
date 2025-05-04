from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from simulator.forms import InvestmentPlanForm
from simulator.models import InvestmentPlan
from django.contrib import messages


@login_required
def create_investment_plan(request):
    if request.method == 'POST':
        form = InvestmentPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user  # Asociem planul cu utilizatorul curent
            plan.save()
            return redirect('dashboard')  # După salvare, redirecționăm la dashboard
    else:
        form = InvestmentPlanForm()
    return render(request, 'simulator/create_investment_plan.html', {'form': form})


@login_required
def edit_investment_plan(request, plan_id):
    plan = get_object_or_404(InvestmentPlan, id=plan_id, user=request.user)

    if request.method == 'POST':
        form = InvestmentPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = InvestmentPlanForm(instance=plan)

    return render(request, 'simulator/edit_investment_plan.html', {'form': form, 'plan': plan})


@login_required
def delete_investment_plan(request, plan_id):
    plan = get_object_or_404(InvestmentPlan, id=plan_id, user=request.user)

    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Planul a fost șters cu succes.')
        return redirect('dashboard')

    return render(request, 'simulator/delete_investment_plan_confirm.html', {'plan': plan})
