"""
URL configuration for Lazapee project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name='login'),
    path('signup/',views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('accounts/<int:pk>/', views.manage_acc, name='manage_acc'),
    path('accounts/<int:pk>/change_password/', views.update_acc, name='update_acc'),
    path('accounts/<int:pk>/delete/', views.delete_acc, name='delete_acc'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_add'),
    path('employees/<str:id_number>/update/', views.employee_update, name='employee_update'),
    path('employees/<str:id_number>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/<str:id_number>/add_overtime/', views.employee_add_overtime, name='employee_add_overtime'),
]
