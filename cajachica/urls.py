
from django.contrib import admin
from django.urls import path
from myapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login_view, name='login'),
    path('dashboard/',dashboard_view, name='dashboard'),
    path('ingreso/', ingreso, name='ingreso'),
    path('gasto/', gasto, name='gasto'),
    path('rendicion/', rendicion, name='rendicion'),
]
