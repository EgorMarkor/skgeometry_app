# myapp/utils.py
import datetime
from django.db.models import Sum
from django.utils import timezone
from .models import Project, DailyOutput, Expense, Assignment, Tool

def dashboard_callback(request, context):
    today = timezone.localdate()
    # --- Базовые счётчики ---
    stats = {
        "total_projects": Project.objects.count(),
        "total_output": DailyOutput.objects.aggregate(sum=Sum("volume"))["sum"] or 0,
        "total_expenses": Expense.objects.aggregate(sum=Sum("amount"))["sum"] or 0,
        "active_assignments": Assignment.objects.filter(end_date__gte=today).count(),
        "missing_tools": Tool.objects.filter(status="absent").count(),
    }
    context["stats"] = stats

    # --- Данные для графиков за последнюю неделю ---
    start = today - datetime.timedelta(days=6)

    # Выработка по дням
    qs_out = (
        DailyOutput.objects
        .filter(date__range=(start, today))
        .values("date")
        .annotate(sum=Sum("volume"))
        .order_by("date")
    )
    context["chart_output_data"] = [
        {"x": obj["date"].strftime("%Y-%m-%d"), "y": float(obj["sum"] or 0)}
        for obj in qs_out
    ]

    # Затраты по дням
    qs_exp = (
        Expense.objects
        .filter(date__range=(start, today))
        .values("date")
        .annotate(sum=Sum("amount"))
        .order_by("date")
    )
    context["chart_expense_data"] = [
        {"x": obj["date"].strftime("%Y-%m-%d"), "y": float(obj["sum"] or 0)}
        for obj in qs_exp
    ]

    return context
