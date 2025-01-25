from django.shortcuts import render
from django.http import HttpResponse



def manager_dashboard(request):
    return render(request, "dashboard/manager-dashboard.html")


def user_dashboard(request):
    return render(request, "dashboard/user-dashboard.html")


def test(request):
    context = {
        'names': ['Hriday', 'Sarder', 'Talha']
    }
    return render(request, "test.html", context)
