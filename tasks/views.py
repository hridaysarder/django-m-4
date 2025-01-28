from django.shortcuts import render
from django.http import HttpResponse
from tasks.forms import TaskModelForm
from tasks.models import Employee, Task


def manager_dashboard(request):
   

    return render(request, "dashboard/manager-dashboard.html")


def user_dashboard(request):
    return render(request, "dashboard/user-dashboard.html")


def test(request):
    context = {
        'names': ['Hriday', 'Sarder', 'Talha']
    }
    return render(request, "test.html", context)


def create_task(request):
    employees = Employee.objects.all()
    form = TaskModelForm()  # For GET

    if request.method == "POST":
        form = TaskModelForm(request.POST)
        if form.is_valid():

            '''For Model Form Data'''
            form.save()

            return render(request, 'task_form.html', {"form": form, "message": "Task added sucessfully"})

            """For Django Form data"""
        # data = form.cleaned_data
        # title = data.get("title")
        # description = data.get("description")
        # due_date = data.get("due_date")
        # assigned_to = data.get("assigned_to")

        # task = Task.objects.create(
        #     title=title, description=description, due_date=due_date)
        # for emp_id in assigned_to:
        #     employee = Employee.objects.get(id=emp_id)
        #     task.assigned_to.add(employee)

            return HttpResponse('Task added sucessfully')
    context = {"form": form}
    return render(request, "task_form.html", context)


def view_task(request):
    tasks = Task.objects.all()

    task3 = Task.objects.get(id=1)

    first_task = Task.objects.first()
    return render(request, "show_task.html", {"tasks": tasks, "task3": task3, "first_task": first_task})
