from django.urls import path
from .views import dashboard, investment_plan, auth
urlpatterns = [
    path('', dashboard.dashboard_view, name='dashboard'),
    
    # Autentificare și înregistrare
    path('login/', auth.login_view, name='login'),
    path('logout/', auth.logout_view, name='logout'),
    path('register/', auth.register_view, name='register'),
    # Investment Plan
    path('create_investment_plan/', investment_plan.create_investment_plan, name='create_investment_plan'),
    path('plan/<int:plan_id>/edit/', investment_plan.edit_investment_plan, name='edit_investment_plan'),
    path('plan/<int:plan_id>/delete/', investment_plan.delete_investment_plan, name='delete_investment_plan'),

]
