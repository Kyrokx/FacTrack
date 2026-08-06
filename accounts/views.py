from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login

from accounts.forms import RegisterForm


def login_view(request):
    return render(request, 'registration/login.html')

def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('setup')
    else:
        form = RegisterForm()
    return render(request, 'registration/signup.html', {'form': form})