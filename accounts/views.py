from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

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

@login_required
def profile_view(request):
    try:
        membership = request.user.membership
    except:
        membership = None
    return render(request, 'accounts/profile.html', {
        'membership': membership,
    })