from django.contrib import admin
from apps.employee.models import Employee

# Register your models here.


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id',
        'name',
        'department',
        'position'
    )
