from django.shortcuts import render, redirect
from simulator.forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Autentificare utilizator
            user = form.get_user()
            login(request, user)
            # Redirect după login
            next_url = request.GET.get('next', 'dashboard')  # sau altă pagină dorită
            return redirect(next_url)  
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # După înregistrare, redirectionează la login
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})