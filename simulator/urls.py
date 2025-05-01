from django.urls import path
from . import views
from django.http import HttpResponse
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'),
    path('profil/', views.create_profile, name='create_profile'),
    path('success/', lambda r: HttpResponse("Profil salvat!"), name='success'),
    path('register/', views.register, name='register'),  # Ruta de înregistrare
]
