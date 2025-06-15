# myapp/admin.py
from django.contrib import admin
from .models import Role, UserProfile, Project, Employee, DailyOutput, Expense, Assignment, WorkSchedule, Tool, FinancialRecord

admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(Employee)

@admin.register(DailyOutput)
class DailyOutputAdmin(admin.ModelAdmin):
    list_display = ("date", "project", "employee", "volume")
    list_filter = ("project", "date")

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "project", "category", "amount")
    list_filter = ("project", "date")

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("project", "employee", "shift", "start_date", "end_date")
    list_filter = ("project", "shift")

@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ("project", "work_type", "start_date", "end_date")
    list_filter = ("project",)

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ("project", "name", "status")
    list_filter = ("project", "status")

@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ("date", "project", "record_type", "amount")
    list_filter = ("project", "record_type", "date")
