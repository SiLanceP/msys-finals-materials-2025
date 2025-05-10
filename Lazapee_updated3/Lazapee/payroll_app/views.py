from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Payslip, Account
from django.contrib import messages
from django.urls import reverse

# Create your views here.

def authentication(function):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, "You must be logged in to view the page.")
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrapper

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            account = Account.objects.get(username=username)
            if account.password == password:
                request.session['user_id'] = account.id
                request.session['username'] = account.username
                return redirect('employee_list')
            else:
                return render(request, 'payroll_app/login.html', {'error': 'Invalid login, Incorrect Username/Password.'})
        except Account.DoesNotExist:
            return render(request, 'payroll_app/login.html', {'error': 'Invalid login, Account does not exist.'})
        
    return render(request, 'payroll_app/login.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if Account.objects.filter(username=username).exists():
            return render(request, 'payroll_app/signup.html', {'error': 'Account already exists'})
        
        #creation of new account
        Account.objects.create(username=username, password=password)
        messages.success(request, 'Account created successfully')
        return redirect('login')
    return render(request, 'payroll_app/signup.html')
        
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    messages.info(request, "You have been logged out.")
    return redirect('login')

def manage_acc(request, pk):
    if not authentication(request):
        messages.error(request, "You must be logged in to view the page.")
        return redirect('login')

    if request.session.get('user_id') != pk:
        return redirect('employee_list')
    
    account = get_object_or_404(Account, pk=pk)
    return render(request, 'payroll_app/manage_acc.html', {'account': account})

def update_acc(request, pk):
    if not authentication(request):
        messages.error(request, "You must be logged in to view the page.")
        return redirect('login')

    if request.session.get('user_id') != pk:
        return redirect('employee_list')
    
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        current_password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if account.password != current_password:
            return render(request, 'payroll_app/update_acc.html',{'error': 'Current password is incorrect', 'account':account})
        
        if current_password == new_password:
            account = get_object_or_404(Account, pk=pk)
            return render(request, 'payroll_app/update_acc.html',{'error': 'New password cannot be the same as current password', 'account':account})
        elif new_password == confirm_password:
            Account.objects.filter(pk=pk).update(password=new_password)
            return redirect('manage_acc',pk=pk)
        else:
            account = get_object_or_404(Account, pk=pk)
            return render(request, 'payroll_app/update_acc.html', {'error': 'Passwords do not match', 'account':account})
    else:
        account = get_object_or_404(Account, pk=pk)
        return render(request, 'payroll_app/update_acc.html', {'account': account})

def delete_acc(request, pk):
    if not authentication(request):
        return redirect('login')
    
    # Ensure user can only delete their own account
    if request.session.get('user_id') != pk:
        return redirect('employee_list')
    
    account = get_object_or_404(Account, pk=pk)
    account.delete()
    
    # Clear session
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    
    return redirect('login')


@authentication
def employee_list(request):
    employees = Employee.objects.all()
    context = {'employees': employees}
    return render(request, 'payroll_app/employee_list.html', context)

@authentication
def employee_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        id_number = request.POST.get('id_number')
        rate_str = request.POST.get('rate')
        allowance_str = request.POST.get('allowance', '0') #default to '0' if not provided

        #basic validation for rate
        try:
            rate = float(rate_str if rate_str else 0)
        except ValueError:
            messages.error(request, "Invalid input for rate.")
            return render(request, 'payroll_app/employee_form.html', {'action': 'Create'})

        allowance = float(allowance_str if allowance_str else 0)


        if not name or not id_number or rate_str is None :
             messages.error(request, "Name, ID Number, and Rate are required.")
             return render(request, 'payroll_app/employee_form.html', {'action': 'Create', 'employee': request.POST})


        if Employee.objects.filter(id_number=id_number).exists():
            messages.error(request, f"Employee with ID {id_number} already exists.")
        else:
            Employee.objects.create(
                name=name,
                id_number=id_number,
                rate=rate,
                allowance=allowance,
                overtime_pay=0.0
            )
            messages.success(request, "Employee added successfully.")
            return redirect('employee_list')
    return render(request, 'payroll_app/employee_form.html', {'action': 'Create'})

@authentication
def employee_update(request, id_number):
    employee = get_object_or_404(Employee, id_number=id_number)
    if request.method == 'POST':
        employee.name = request.POST.get('name')
        
        rate_str = request.POST.get('rate')
        allowance_str = request.POST.get('allowance', '0')

        try:
            employee.rate = float(rate_str if rate_str else 0)
        except ValueError:
            messages.error(request, "Invalid input for rate.")
            context = {'employee': employee, 'action': 'Update'}
            return render(request, 'payroll_app/employee_form.html', context)
            
        employee.allowance = float(allowance_str if allowance_str else 0)

        if not employee.name or rate_str is None:
            messages.error(request, "Name and Rate are required.")
            context = {'employee': employee, 'action': 'Update'}
            return render(request, 'payroll_app/employee_form.html', context)

        employee.save()
        messages.success(request, "Employee updated successfully.")
        return redirect('employee_list')
    context = {'employee': employee, 'action': 'Update'}
    return render(request, 'payroll_app/employee_form.html', context)

@authentication
def employee_delete(request, id_number):
    employee = get_object_or_404(Employee, id_number=id_number)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, "Employee deleted successfully.")
    return redirect('employee_list')


@authentication
def employee_add_overtime(request, id_number):
    employee = get_object_or_404(Employee, id_number=id_number)
    if request.method == 'POST':
        try:
            overtime_hours_str = request.POST.get('overtime_hours')
            if not overtime_hours_str: #check if string is empty or none
                 messages.error(request, "Overtime hours cannot be empty.")
                 return redirect('employee_list')

            overtime_hours = float(overtime_hours_str)

            if overtime_hours > 0:
                if employee.rate is None:
                    messages.error(request, f"Cannot calculate overtime for {employee.name} as rate is not set.")
                    return redirect('employee_list')
                
                #overtime = (rate/160) x 1.5 x overtime hours
                calculated_overtime_pay = (employee.rate / 160) * 1.5 * overtime_hours
                employee.overtime_pay = (employee.overtime_pay or 0.0) + calculated_overtime_pay
                employee.save()
                messages.success(request, f"Overtime added for {employee.name}.")
            elif overtime_hours == 0:
                messages.info(request, "Overtime hours entered was 0. No overtime added.")
            else: #overtime_hours < 0
                messages.error(request, "Overtime hours must be a positive value.")
        except ValueError:
            messages.error(request, "Invalid input for overtime hours. Please enter a number.")
        except TypeError:
            messages.error(request, "Error in overtime calculation due to missing employee data (rate or previous overtime).")

    return redirect('employee_list')


def daterange(month, year, cycle):
    if cycle == 1:
        return f"{month} 1-15, {year}"
    elif month == 'February' and cycle == 2:
        return f"{month} 16-28, {year}"
    else:
        return f"{month} 16-30, {year}"
    
@authentication
def payslip_list(request):
    employees = Employee.objects.all()
    payslips = Payslip.objects.all()

    if request.method == 'POST':
        payroll_for = request.POST.get('payroll')
        month = request.POST.get('month')
        year = request.POST.get('year')
        cycle = request.POST.get('cycle')

        if not (payroll_for and month and year and cycle):
            messages.error(request, "All fields are required.")
            return redirect('payslip_list')
        
        cycle = int(cycle)

        if payroll_for == 'all':
            selected = employees
        else:
            selected = employees.filter(id_number=payroll_for)
        
        for employee in selected:
            if Payslip.objects.filter(id_number=employee, month=month, year=year, pay_cycle=cycle).exists():
                messages.error(request, f"Payslip already exists for ID: {employee.id_number}, Month: {month}, Year: {year}, Cycle: {cycle}.")
                continue
            half_rate = employee.getRate() / 2
            allowance = employee.getAllowance()
            overtime = employee.getOvertime()
            if cycle == 1:
                pagibig = 100
                sss = 0
                philhealth = 0
                gross = half_rate + allowance + overtime - pagibig
            else:
                pagibig = 0
                philhealth = employee.getRate() * 0.04
                sss = employee.getRate() * 0.045
                gross = half_rate + allowance + overtime - philhealth - sss
            
            tax = gross * 0.2
            total_pay = gross - tax
            date_range = daterange(month, year, cycle)

            Payslip.objects.create(
                id_number=employee,
                month=month,
                date_range = date_range,
                year=year,
                pay_cycle=cycle,
                rate=employee.getRate(),
                earnings_allowance=allowance,
                deductions_tax=tax,
                deductions_health=philhealth,
                pag_ibig=pagibig,
                sss=sss,
                overtime=overtime,
                total_pay=total_pay
            )

            employee.resetOvertime()
            messages.success(request, f"Payslip created for ID: {employee.id_number}")
        return redirect('payslip_list')
    
    return render(request, 'payroll_app/payslips.html', {'employees': employees, 'payslips': payslips})

def payslip_delete(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    if request.method == 'POST':
        payslip.delete()
        messages.success(request, "Payslip deleted successfully.")
    return redirect('payslip_list')
