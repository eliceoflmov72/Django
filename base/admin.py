from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created',) # esto es para un campo solo de lectura
# Register your models here.

admin.site.register(Task, TaskAdmin) # con esto podemos añadir la tarea en el admin