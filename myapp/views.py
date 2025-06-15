# myapp/views.py (фрагмент)
import hashlib, hmac, time, json
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from .models import User, UserProfile, Role
# myapp/views.py (основные представления)
from django.shortcuts import render, redirect
from .models import Project, Employee, DailyOutput, Expense, Assignment, WorkSchedule, Tool, FinancialRecord

def reporting(request):
    """Вкладка 'Отчётность': ежедневная выработка."""
    projects = Project.objects.all()
    employees = Employee.objects.all()
    if request.method == "POST":
        # Получаем данные формы выработки
        proj_id = request.POST.get("project")
        emp_id = request.POST.get("employee")
        date = request.POST.get("date")
        volume = request.POST.get("volume")
        if proj_id and emp_id and date and volume:
            project = Project.objects.get(id=proj_id)
            employee = Employee.objects.get(id=emp_id)
            DailyOutput.objects.create(project=project, employee=employee, date=date, volume=volume)
            # После сохранения перенаправляем обратно (во избежание повторного POST при обновлении страницы)
            return redirect("reporting")
    return render(request, "reporting.html", {"projects": projects, "employees": employees})

def schedules(request):
    """Вкладка 'Графики': назначение сотрудников на смены и график работ."""
    projects = Project.objects.all()
    employees = Employee.objects.all()
    if request.method == "POST":
        if request.POST.get("shift"):
            # Обработка формы назначения смен (Assignment)
            proj_id = request.POST.get("project")
            emp_id = request.POST.get("employee")
            shift = request.POST.get("shift")
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            if proj_id and emp_id and shift and start_date and end_date:
                project = Project.objects.get(id=proj_id)
                employee = Employee.objects.get(id=emp_id)
                Assignment.objects.create(project=project, employee=employee, shift=shift,
                                           start_date=start_date, end_date=end_date)
                return redirect("schedules")
        elif request.POST.get("work_type"):
            # Обработка формы графика работ (WorkSchedule)
            proj_id = request.POST.get("project")
            work_type = request.POST.get("work_type")
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            if proj_id and work_type and start_date and end_date:
                project = Project.objects.get(id=proj_id)
                WorkSchedule.objects.create(project=project, work_type=work_type,
                                             start_date=start_date, end_date=end_date)
                return redirect("schedules")
    return render(request, "schedules.html", {"projects": projects, "employees": employees})

def finances(request):
    """
    Вкладка «Финансы»: добавление расходов и операций (доход/расход),
    а также табличный вывод последних записей.
    """
    projects = Project.objects.all()
    # берём последние 20 записей
    expenses = Expense.objects.order_by('-date')[:20]
    records = FinancialRecord.objects.order_by('-date')[:20]

    if request.method == "POST":
        # добавление расхода
        if request.POST.get("category"):
            proj = Project.objects.get(id=request.POST["project"])
            Expense.objects.create(
                project=proj,
                category=request.POST["category"],
                amount=request.POST["amount"],
                date=request.POST["date"]
            )
            return redirect("finances")
        # добавление дохода/расхода
        if request.POST.get("record_type"):
            proj = Project.objects.get(id=request.POST["project"])
            FinancialRecord.objects.create(
                project=proj,
                record_type=request.POST["record_type"],
                amount=request.POST["amount"],
                date=request.POST["date"]
            )
            return redirect("finances")

    return render(request, "finances.html", {
        "projects": projects,
        "expenses": expenses,
        "records": records,
    })


def tools(request):
    """
    Вкладка «Инструменты»: добавление/обновление инструментов
    и табличный вывод текущего списка.
    """
    projects = Project.objects.all()
    tools_list = Tool.objects.select_related('project').order_by('project__name', 'name')

    if request.method == "POST":
        proj = Project.objects.get(id=request.POST["project"])
        Tool.objects.update_or_create(
            project=proj,
            name=request.POST["name"],
            defaults={"status": request.POST["status"]}
        )
        return redirect("tools")

    return render(request, "tools.html", {
        "projects": projects,
        "tools": tools_list,
    })


# функция валидации данных от Telegram WebApp
def verify_telegram_init_data(init_data: str) -> dict:
    """Проверяет подпись init_data. Возвращает dict с данными пользователя, если успешно, иначе {}."""
    try:
        # Разбираем строку вида key1=value1&key2=value2...
        data_pairs = dict(item.split('=', 1) for item in init_data.split('&'))
    except Exception:
        return {}
    hash_hex = data_pairs.pop('hash', None)
    if not hash_hex:
        return {}
    # Опционально: проверка не истёк ли срок (1 день)
    auth_date = int(data_pairs.get('auth_date', 0))
    if auth_date and time.time() - auth_date > 86400:
        return {}  # данные устарели, не доверяем
    # Формируем строку для подписи
    check_string = '\n'.join(f"{k}={v}" for k,v in sorted(data_pairs.items()))
    # Вычисляем секретный ключ из токена бота
    token = settings.TELEGRAM_BOT_TOKEN  # должен быть задан в settings.py
    secret_key = hmac.new(b"WebAppData", token.encode('utf-8'), hashlib.sha256).digest()
    # Вычисляем контрольный хеш
    calc_hash = hmac.new(secret_key, check_string.encode('utf-8'), hashlib.sha256).hexdigest()
    # Сравнение с переданным хешем (с использованием compare_digest для безопасности)
    if not hmac.compare_digest(calc_hash, hash_hex):
        return {}
    # Если подпись верна – возвращаем разобранные данные (например, user)
    return json.loads(data_pairs.get('user', '{}'))

@csrf_exempt
def telegram_login(request):
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        init_data = body.get('initData', '')
        user_data = verify_telegram_init_data(init_data)
        if not user_data:
            return JsonResponse({"status": "error"}, status=403)
        # Данные валидны, выполняем вход пользователя
        telegram_id = user_data.get('id')
        username = user_data.get('username') or f"tg_user_{telegram_id}"
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        # Ищем или создаём пользователя Django
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name)
            # Назначаем роль "прораб" по умолчанию
            role, _ = Role.objects.get_or_create(name="прораб")
            UserProfile.objects.create(user=user, role=role)
        # Логиним пользователя (создаём сессию)
        login(request, user)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "bad request"}, status=400)
