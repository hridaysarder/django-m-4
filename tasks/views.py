from django.shortcuts import render, redirect
from tasks.forms import TaskModelForm, TaskDetailModelForm
from tasks.models import Task,Project
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from users.views import is_admin
from django.http import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.base import ContextMixin
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import UpdateView


# class base view
class Greetings(View):
    greetings='Hello World'
    
    def get(self,request):
        return HttpResponse(self.greetings)
    
class HiGreetings(Greetings):
    greetings='Hi, How are you'

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

    type = request.GET.get('type', 'all')

    counts = Task.objects.aggregate(
        total=Count('id'),
        completed_task=Count('id', filter=Q(status='COMPLETED')),
        in_progress=Count('id', filter=Q(status='IN_PROGRESS')),
        pending_task=Count('id', filter=Q(status='PENDING'))
    )


    base_query = Task.objects.select_related(
        'details').prefetch_related('assigned_to')

    if type == 'completed':
        tasks = base_query.filter(status='COMPLETED')
    elif type == 'in-progress':
        tasks = base_query.filter(status='IN_PROGRESS')
    elif type == 'pending':
        tasks = base_query.filter(status='PENDING')
    elif type == 'all':
        tasks = base_query.all()

    context = {
        "tasks": tasks,
        "counts": counts,
        "role":'manager'
    }

    return render(request, "dashboard/manager-dashboard.html", context)

@user_passes_test(is_employee)
def employee_dashboard(request):
    return render(request, "dashboard/user-dashboard.html")


@login_required
@permission_required('tasks.add_task',login_url='no-permission')
def create_task(request):
    # employees = Employee.objects.all()
    task_form = TaskModelForm()  # For GET
    task_detail_form = TaskDetailModelForm()

    if request.method == "POST":
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST,request.FILES)
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

# vaiable for list of decorators
create_decorators=[login_required,permission_required('tasks.add_task',login_url='no-permission')]

# @method_decorator(create_decorators, name="dispatch")
class CreateTask(ContextMixin,LoginRequiredMixin,PermissionRequiredMixin,View):
    
    permission_required='tasks.add_task'
    login_url='sign-in'
    template_name="task_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_form"]=kwargs.get("task_from",TaskModelForm())
        context["task_detail_form"]=kwargs.get("task_detail_form",TaskDetailModelForm)
        return context

    def get(self,request,*args, **kwargs):
         task_form = TaskModelForm()  # For GET
         task_detail_form = TaskDetailModelForm()
         context=self.get_context_data()
         return render(request,self.template_name,context)

    def post(self,request,*args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST,request.FILES)
        if task_form.is_valid() and task_detail_form.is_valid():

            '''For Model Form Data'''
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, 'Task created successfully')
            context=self.get_context_data(task_form=task_form,task_detail_form=task_detail_form)
            return render(request,self.template_name,context)
        


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
            return redirect('task-details',id)

    context = {"task_form": task_form, "task_detail_form": task_detail_form}
    return render(request, "task_form.html", context)



class UpdateTask(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = 'task_form.html'
    context_object_name = 'task'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_form'] = self.get_form()
        print(context)
        if hasattr(self.object, 'details') and self.object.details:
            context['task_detail_form'] = TaskDetailModelForm(
                instance=self.object.details)
        else:
            context['task_detail_form'] = TaskDetailModelForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)

        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=getattr(self.object, 'details', None))

        if task_form.is_valid() and task_detail_form.is_valid():

            """ For Model Form Data """
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task Updated Successfully")
            return redirect('update-task', self.object.id)
        return redirect('update-task', self.object.id)



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


view_project_decorators=[login_required,permission_required('projects.view-task',login_url='no-permission')]

@method_decorator(view_project_decorators, name="dispatch")
class ViewProject(ListView):
    model=Project
    context_object_name="projects"
    template_name="show_task.html"

    def get_queryset(self):
        queryset=Project.objects.annotate(num_task=Count('task')).order_by('num_task')
        return queryset

@login_required
@permission_required('tasks.view_task',login_url='no-permission')
def task_details(request,task_id):
    task=Task.objects.get(id=task_id)
    status_choices=Task.STATUS_CHOICES

    if request.method=='POST':
        selected_status=request.POST.get('task_status')
        task.status=selected_status
        task.save()
        return redirect('task-details',task.id)
    return render(request,'task_details.html',{'task':task,'status_choices':status_choices})

class TaskDetail(DetailView):
    model=Task
    template_name="task_details.html"
    context_object_name="task"
    pk_url_kwarg="task_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices']=Task.STATUS_CHOICES
        return context

    def post(self,request,*args, **kwargs):
        task=self.get_object()
        selected_status=request.POST.get('task_status')
        task.status=selected_status
        task.save()
        return redirect('task-details',task.id)


@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect('manager-dashboard')
    elif is_employee(request.user):
        return redirect('user-dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')
    
    return redirect('no-permission')