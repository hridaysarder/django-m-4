from django import forms
from tasks.models import Task


class TaskForm(forms.Form):
    title = forms.CharField(max_length=250, label='Task Title')
    description = forms.CharField(
        widget=forms.Textarea, label='Task Description')
    due_date = forms.DateField(widget=forms.SelectDateWidget, label='Due Date')
    assigned_to = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=[], label='Assigned To')

    def __init__(self, *args, **kwargs):
        employees = kwargs.pop("employees", [])
        print(employees)
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].choices = [
            (emp.id, emp.name) for emp in employees]


class TaskModelForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'assigned_to']

        # exclude=['project','is_completed','created_at','updated_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': "border-2 border-gray-300 w-full rounded-lg shadow-md focus:border-rose-500 focus:ring-rose-500",
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': "border-2 border-gray-300 w-full rounded-lg shadow-md focus:border-rose-500 focus:ring-rose-500",
                'placeholder': 'Describe the task'
            }),
            'due_date': forms.SelectDateWidget(attrs={
                'class': "border-2 border-gray-300 rounded-lg shadow-md focus:border-rose-500 focus:ring-rose-500",

            }),
            'assigned_to': forms.CheckboxSelectMultiple(attrs={
                'class': "border-gray-300 rounded-lg shadow-md focus:border-rose-500 focus:ring-rose-500",
            })
        }
