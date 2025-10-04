from django.contrib import admin
from .models import Department, Outcome

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
