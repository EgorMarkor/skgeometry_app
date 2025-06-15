from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    name = models.CharField("Роль", max_length=50, unique=True)

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name="Роль")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} ({self.role.name})"

class Project(models.Model):
    name = models.CharField("Название объекта", max_length=100)
    location = models.CharField("Адрес/расположение", max_length=200, blank=True)

    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField("ФИО сотрудника", max_length=100)
    position = models.CharField("Должность", max_length=100, blank=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.name

class DailyOutput(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Объект")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Сотрудник")
    date = models.DateField("Дата")
    volume = models.FloatField("Объём работ")

    class Meta:
        verbose_name = "Ежедневная выработка"
        verbose_name_plural = "Ежедневные выработки"

    def __str__(self):
        return f"{self.project.name}: {self.date} - {self.volume}"

class Expense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Объект")
    category = models.CharField("Статья расхода", max_length=100)
    amount = models.DecimalField("Сумма", max_digits=12, decimal_places=2)
    date = models.DateField("Дата")

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"

    def __str__(self):
        return f"{self.project.name}: {self.category} - {self.amount}"

class Assignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Объект")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Сотрудник")
    shift = models.CharField("Смена", max_length=50)  # например, день/ночь или название смены
    start_date = models.DateField("Начало")
    end_date = models.DateField("Окончание")

    class Meta:
        verbose_name = "Назначение на смену"
        verbose_name_plural = "Назначения на смену"

    def __str__(self):
        return f"{self.project.name}: {self.employee.name} - {self.shift}"

class WorkSchedule(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Объект")
    work_type = models.CharField("Вид работ", max_length=100)
    start_date = models.DateField("Начало")
    end_date = models.DateField("Окончание")

    class Meta:
        verbose_name = "График работ"
        verbose_name_plural = "Графики работ"

    def __str__(self):
        return f"{self.project.name}: {self.work_type}"

class Tool(models.Model):
    STATUS_CHOICES = [
        ('present', "В наличии"),
        ('absent', "Отсутствует"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Объект")
    name = models.CharField("Инструмент", max_length=100)
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default='present')

    class Meta:
        unique_together = [('project', 'name')]
        verbose_name = "Инструмент"
        verbose_name_plural = "Инструменты"

    def __str__(self):
        return f"{self.project.name}: {self.name} ({self.status})"

class FinancialRecord(models.Model):
    TYPE_CHOICES = [
        ('income', "Доход"),
        ('expense', "Расход"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Объект")
    record_type = models.CharField("Тип", max_length=7, choices=TYPE_CHOICES)
    amount = models.DecimalField("Сумма", max_digits=12, decimal_places=2)
    date = models.DateField("Дата")

    class Meta:
        verbose_name = "Финансовая запись"
        verbose_name_plural = "Финансовые записи"

    def __str__(self):
        type_display = dict(TYPE_CHOICES).get(self.record_type, self.record_type)
        return f"{self.project.name}: {type_display} - {self.amount}"
