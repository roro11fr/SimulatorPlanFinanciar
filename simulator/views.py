from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from .forms import UserFinancialProfileForm


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # După înregistrare, redirecționează la login
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def create_profile(request):
    if request.method == 'POST':
        form = UserFinancialProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Salvează profilul asociat utilizatorului
            profile.save()
            return redirect('success')
    else:
        form = UserFinancialProfileForm()
    return render(request, 'simulator/create_profile.html', {'form': form})