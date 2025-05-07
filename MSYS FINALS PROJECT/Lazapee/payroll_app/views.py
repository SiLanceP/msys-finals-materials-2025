from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Payslip, Account
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            account = Account.objects.get(username=username)
            if account.password == password:
                # Stores the User info in a session (makes sure that the user is logged in when looking at the pages)
                request.session['user_id'] = account.id
                request.session['username'] = account.username
                return redirect('view_employee')# Change this if needed
            else:
                return render(request, 'payroll_app/login.html', {'error': 'Invalid login'}) # Change this if needed
        except Account.DoesNotExist:
            return render(request, 'payroll_app/login.html', {'error': 'Invalid login'}) # Change this if needed
        
    return render(request, 'payroll_app/login.html') # Change this if needed

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if Account.objects.filter(username=username).exists():
            return render(request, 'payroll_app/signup.html', {'error': 'Account already exists'}) # Change this if needed
        
        #creation of new account
        Account.objects.create(username=username, password=password)
        messages.success(request, 'Account created successfully')
        return redirect('login')
    return render(request, 'payroll_app/signup.html') # Change this if needed
        
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    return redirect('login')

def aunthentication(request):
    return 'user_id' in request.session

