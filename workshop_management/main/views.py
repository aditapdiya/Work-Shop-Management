# main/views.py

# Standard & Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

# Local imports
from .models import Workshop
from .forms import WorkshopForm, WorkshopRegistrationForm


# ------------------ Public Views ------------------ #

def home_view(request):
    return render(request, 'main/home.html')


def register_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, pk=workshop_id)

    if request.method == 'POST':
        form = WorkshopRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.workshop = workshop
            registration.save()
            # Send confirmation email
            subject = f"Workshop Registration Confirmation: {workshop.title}"
            message = (
                f"Dear {registration.name},\n\n"
                f"Thank you for registering for the workshop \"{workshop.title}\".\n\n"
                f"📅 Date: {workshop.date}\n"
                f"🕒 Time: {workshop.time}\n"
                f"⏳ Duration: {workshop.duration}\n"
                f"🎤 Speaker: {workshop.speaker}\n"
                f"📍 Location: {'Online' if workshop.location == 'online' else 'Offline'}\n"
                f"{'🔗 Meeting Link: ' + workshop.meeting_link if workshop.location == 'online' else '🏢 Address: ' + workshop.address}\n\n"
                f"Feel free to reach out if you have any questions.\n\n"
                f"Best regards,\nEvent Team"
            )
            recipient = registration.email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)

            messages.success(request, 'Thank you for registering! A confirmation email has been sent.')
    else:
        form = WorkshopRegistrationForm()

    return render(request, 'main/register_workshop.html', {
        'form': form,
        'workshop': workshop,
    })


# ------------------ Authentication Views ------------------ #

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'main/login.html')


@login_required
def dashboard_view(request):
    return render(request, 'main/dashboard.html')


# ------------------ Workshop Management Views ------------------ #

@login_required
def manage_workshops(request):
    today = timezone.now().date()
    workshops = Workshop.objects.all().order_by('-date')

    # Update status dynamically without saving to DB
    for workshop in workshops:
        workshop.is_active = workshop.date >= today

    return render(request, 'main/manage_workshops.html', {'workshops': workshops})


@login_required
def add_workshop(request):
    if request.method == 'POST':
        form = WorkshopForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Workshop added successfully.')
            return redirect('manage_workshops')
        else:
            print("Form errors:", form.errors)
            messages.error(request, "There were errors in the form. Please fix them.")
    else:
        form = WorkshopForm()

    return render(request, 'main/add_edit_workshop.html', {
        'form': form,
        'title': 'Add Workshop',
    })


@login_required
def edit_workshop(request, id):
    workshop = get_object_or_404(Workshop, id=id)

    if request.method == 'POST':
        form = WorkshopForm(request.POST, instance=workshop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Workshop updated successfully.')
            return redirect('manage_workshops')
    else:
        form = WorkshopForm(instance=workshop)

    return render(request, 'main/add_edit_workshop.html', {
        'form': form,
        'title': 'Edit Workshop',
    })


@login_required
def delete_workshop(request, id):
    workshop = get_object_or_404(Workshop, id=id)
    workshop.delete()
    messages.success(request, 'Workshop deleted successfully.')
    return redirect('manage_workshops')