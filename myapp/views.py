from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from datetime import date




# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirige a la vista del dashboard
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
            return redirect('login')

    return render(request, 'login.html')

# Vista para el dashboard
def dashboard_view(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    else:
        return redirect('login')  # Si no está autenticado, redirige al login
    
def ingreso(request):
    return render(request, 'ingreso.html')

def gasto(request):
    return render(request, 'gasto.html')

def rendicion(request):
    today = date.today().isoformat()  # Formato YYYY-MM-DD
    return render(request, 'rendicion.html', {'today': today})