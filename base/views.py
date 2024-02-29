from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required # con esto colocamos a cada funcion, indicando que esta protegida por el login
# Create your views here.

def home(request):
    return render(request, 'home.html')


def loginup(request):
    if request.method == 'GET':
        return render(request, 'loginup.html',{
            'form': UserCreationForm()
            })# con esto estamos creando un formulario
    else:
        if request.POST['password1'] == request.POST['password2']:
            #register user
            # try lo que hace es que intenta guardar la base de datos, pero si falla va a capturar el error
            try:
                user= User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user) # con esto podemos saber si las tareas o cualquier cosa lo ha hecho el usuario
                return redirect('tasks') # con esto redireccionamos a la pagina que queremos ir
            except IntegrityError:
                return render(request, 'loginup.html',{
                    'form': UserCreationForm(),
                    'error': 'El usuario ya existe'
                })
    return render(request, 'loginup.html',{
            'form': UserCreationForm(),
            'error': 'Las contraseñas no coinciden'
            })

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True) # con esto marcamos que solo nos trae las tareas que no esten completadas
    return render(request, 'tasks.html', {'tasks': tasks})
@login_required
def loginout(request):
    logout(request)
    return redirect('home')

def loginin(request):
    if request.method == 'GET':
        return render(request, 'loginin.html',
            {'form': AuthenticationForm()})
    else:
        User = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if User is None:
            return render(request, 'loginin.html',
                {'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrectos'})
        else:
            login(request, User)
            return redirect('tasks')

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html',
        {'form': TaskForm()})
    else:
        #print(request.POST) con esto podemos ver la informacion que estamos enviando en la consola
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False) # con esto nos va a devolver los datos del formulario
            new_task.user = request.user
            new_task.save() # con esto guardamos en la base de datos
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html',{
                'form': TaskForm(),
                'error': 'Por favor, proporcione datos validos'
            })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task =get_object_or_404(Task, pk=task_id)# con esto mandamos a buscar la tarea y si buscamos una tarea que no esta no saldra el error 404
        form = TaskForm(instance=task) 
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task =get_object_or_404(Task, pk=task_id, user=request.user)# con esto mandamos a buscar la tarea y si buscamos una tarea que no esta no saldra el error 404. Y solo buscara las tareas del usuario
            form =TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error al actualizar la tarea'})

@login_required    
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now() # con esto marcamos la fecha de completado
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted') # con esto vemos la tareas que ya estan hechas
    return render(request, 'tasks.html', {'tasks': tasks})