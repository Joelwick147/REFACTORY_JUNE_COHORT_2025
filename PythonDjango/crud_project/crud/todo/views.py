from django.shortcuts import render,redirect
#import the model
from .models import Task
# Create your views here.

def index(request):
    tasks=Task.objects.all()
    total=tasks.count()
    completed=tasks.filter(is_complete =True).count()
    pending=tasks.filter(is_complete =False).count()
    
    context ={
        'tasks':tasks,
        'total':total,
        'completed':completed,
        'pending':pending,
    }
    return render(request,'index.html',context)


def add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Task.objects.create(title=title)
            return redirect('index')
        
def status(request, task_id):
    task =Task.objects.get(id=task_id)
    task.is_complete =not task.is_complete
    task.save()
    return redirect('index')

def delete(request, task_id):
    task =Task.objects.get(id=task_id).delete()
    return redirect('index')