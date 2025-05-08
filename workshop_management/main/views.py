from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # change 'home' to your home view name
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'main/login.html')


from django.shortcuts import render

def home_view(request):
    return render(request, 'main/home.html')
