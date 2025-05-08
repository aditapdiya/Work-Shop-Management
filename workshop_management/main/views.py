from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Workshop
from .forms import WorkshopRegistrationForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .forms import WorkshopRegistrationForm
from .models import Workshop


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')   # change 'home' to your home view name
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'main/login.html')


from django.shortcuts import render

def home_view(request):
    return render(request, 'main/home.html')


def dashboard_view(request):
    return render(request, 'main/dashboard.html')


from django.shortcuts import render, redirect, get_object_or_404
from .models import Workshop
from .forms import WorkshopForm

def manage_workshops(request):
    workshops = Workshop.objects.all()
    return render(request, 'main/manage_workshops.html', {'workshops': workshops})

def add_workshop(request):
    if request.method == 'POST':
        form = WorkshopForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_workshops')
    else:
        form = WorkshopForm()
    return render(request, 'main/add_edit_workshop.html', {'form': form, 'action': 'Add'})

def edit_workshop(request, id):
    workshop = get_object_or_404(Workshop, id=id)
    if request.method == 'POST':
        form = WorkshopForm(request.POST, instance=workshop)
        if form.is_valid():
            form.save()
            return redirect('manage_workshops')
    else:
        form = WorkshopForm(instance=workshop)
    return render(request, 'main/add_edit_workshop.html', {'form': form, 'action': 'Edit'})

def delete_workshop(request, id):
    workshop = get_object_or_404(Workshop, id=id)
    workshop.delete()
    return redirect('manage_workshops')






def register_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, pk=workshop_id)

    if request.method == 'POST':
        form = WorkshopRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.workshop = workshop
            registration.save()
            # Show success message and stay on the same page
            messages.success(request, 'Thank you for registering! You will receive a confirmation email soon.')
    else:
        form = WorkshopRegistrationForm()

    return render(request, 'main/register_workshop.html', {
        'form': form,
        'workshop': workshop,
    })

