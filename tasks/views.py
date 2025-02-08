from django.shortcuts import render, redirect
from django.http import HttpResponse
from tasks.forms import TaskModelForm, TaskDetailModelForm
from tasks.models import Employee, Task,Project
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required


def is_manager(user):
    return user.groups.filter(name='Manager').exists()
def is_employee(user):
    return user.groups.filter(name='Employee').exists()

@user_passes_test(is_manager,login_url='no-permission')
def manager_dashboard(request):

    # total_task = tasks.count()
    # completed_task = Task.objects.filter(status="COMPLETED").count()
    # in_progress_task = Task.objects.filter(status="IN_PROGRESS").count()
    # pending_task = Task.objects.filter(status="PENDING").count()

    counts = Task.objects.aggregate(
        total=Count('id'),
        completed_task=Count('id', filter=Q(status='COMPLETED')),
        in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
        pending_task=Count('id', filter=Q(status='PENDING'))
    )

    type = request.GET.get('type', 'all')

    base_query = Task.objects.select_related(
        'details').prefetch_related('assigned_to')

    if type == 'completed':
        tasks = base_query.filter(status='COMPLETED')
    elif type == 'in_progress':
        tasks = base_query.filter(status='IN_PROGRESS')
    elif type == 'pending':
        tasks = base_query.filter(status='PENDING')
    elif type == 'all':
        tasks = base_query.all()

    context = {
        "tasks": tasks,
        "counts": counts
    }

    return render(request, "dashboard/manager-dashboard.html", context)

@user_passes_test(is_employee,login_url='no-permission')
def employee_dashboard(request):
    return render(request, "dashboard/user-dashboard.html")


@login_required
@permission_required('tasks.add_task',login_url='no-permission')
def create_task(request):
    employees = Employee.objects.all()
    task_form = TaskModelForm()  # For GET
    task_detail_form = TaskDetailModelForm()

    if request.method == "POST":
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST)
        if task_form.is_valid() and task_detail_form.is_valid():

            '''For Model Form Data'''
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, 'Task created successfully')
            return redirect('create-task')

    context = {"task_form": task_form, "task_detail_form": task_detail_form}
    return render(request, "task_form.html", context)

@login_required
@permission_required('tasks.change_task',login_url='no-permission')
def update_task(request, id):
    task = Task.objects.get(id=id)
    task_form = TaskModelForm(instance=task)  # For GET

    if task.details:
        task_detail_form = TaskDetailModelForm(instance=task.details)

    if request.method == "POST":
        task_form = TaskModelForm(request.POST,instance=task)
        task_detail_form = TaskDetailModelForm(request.POST,instance=task.details)
        if task_form.is_valid() and task_detail_form.is_valid():

            '''For Model Form Data'''
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, 'Task updated successfully')
            return redirect('update-task',id)

    context = {"task_form": task_form, "task_detail_form": task_detail_form}
    return render(request, "task_form.html", context)


@login_required
@permission_required('tasks.delete_task',login_url='no-permission')
def delete_task(request,id):
    if request.method=="POST":
        tasks=Task.objects.get(id=id)
        tasks.delete()
        messages.success(request,'Task Deleted Successfully')
        return redirect('manager-dashboard')
    else:
        messages.error(request,'Something went wrong')
        return redirect('manager-dashboard')


@login_required
@permission_required('tasks.view_task',login_url='no-permission')
def view_task(request):
    projects=Project.objects.annotate(
        num_task=Count('task')).order_by('num_task')
    return render(request,'show-task.html',{"projects":projects})