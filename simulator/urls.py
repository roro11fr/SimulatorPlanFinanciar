from django.urls import path
from .views import dashboard, investment_plan, auth, simulation

urlpatterns = [
    path('', dashboard.dashboard_view, name='dashboard'),
    # Autentificare si înregistrare
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),
    path('register/', auth.register_view, name='register'),
    # Investment Plan
    path('create_investment_plan/', investment_plan.create_investment_plan, name='create_investment_plan'),
    path('plan/<int:plan_id>/edit/', investment_plan.edit_investment_plan, name='edit_investment_plan'),
    path('plan/<int:plan_id>/delete/', investment_plan.delete_investment_plan, name='delete_investment_plan'),
    #Simulation
    path('simulare/<int:plan_id>/', simulation.start_simulation, name='start_simulation'),
    path('simulari/istoric/', simulation.istoric_simulari, name='istoric_simulari'),
    path('simulare/sterge/<int:simulare_id>/', simulation.sterge_simulare, name='sterge_simulare'),
]
