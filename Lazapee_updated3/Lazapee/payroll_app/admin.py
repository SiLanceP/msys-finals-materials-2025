from django.contrib import admin
from .models import Employee, Payslip, Account

# Register your models here.
admin.site.register(Employee)
admin.site.register(Payslip)
admin.site.register(Account)
