# main/views.py

# -------------------- Imports -------------------- #

# Django Core Imports
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Count

# Third-party Libraries
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import openpyxl

# Local App Imports
from .models import Workshop, WorkshopRegistration, WorkshopFeedback
from .forms import WorkshopForm, WorkshopRegistrationForm, WorkshopFeedbackForm

# -------------------- Public Views -------------------- #

def home_view(request):
    return render(request, 'main/home.html')


def register_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, pk=workshop_id)

    if request.method == 'POST':
        form = WorkshopRegistrationForm(request.POST, workshop=workshop)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.workshop = workshop
            registration.save()

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
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [registration.email], fail_silently=False)

            messages.success(request, 'Thank you for registering! A confirmation email has been sent.')
            return redirect('register_workshop', workshop_id=workshop_id)
    else:
        form = WorkshopRegistrationForm(workshop=workshop)

    return render(request, 'main/register_workshop.html', {
        'form': form,
        'workshop': workshop,
    })


def workshop_feedback_view(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if request.method == 'POST':
        form = WorkshopFeedbackForm(request.POST, workshop=workshop)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.workshop = workshop
            feedback.save()

            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.setFont("Helvetica-Bold", 24)
            p.drawCentredString(300, 700, "Certificate of Participation")
            p.setFont("Helvetica", 18)
            p.drawCentredString(300, 650, f"Presented to {feedback.name}")
            p.setFont("Helvetica", 14)
            p.drawCentredString(300, 600, f"For attending the workshop: {workshop.title}")
            p.showPage()
            p.save()
            buffer.seek(0)

            email = EmailMessage(
                subject='Your Workshop Certificate',
                body=f"Hi {feedback.name},\n\nThank you for attending the workshop. Find your certificate attached.",
                to=[feedback.email],
            )
            email.attach(f'{feedback.name}_certificate.pdf', buffer.read(), 'application/pdf')
            email.send()

            messages.success(request, 'Thank you for your feedback! Your certificate has been emailed.')
    else:
        form = WorkshopFeedbackForm(workshop=workshop)

    return render(request, 'main/workshop_feedback.html', {
        'form': form,
        'workshop': workshop
    })

# -------------------- Authentication Views -------------------- #

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
    context = {
        'workshop_count': Workshop.objects.count(),
        'participant_count': WorkshopRegistration.objects.count(),
        'feedback_count': WorkshopFeedback.objects.count(),
        'recent_workshops': Workshop.objects.order_by('-date')[:5],
        'recent_participants': WorkshopRegistration.objects.order_by('-registered_at')[:5],
        'recent_feedbacks': WorkshopFeedback.objects.order_by('-submitted_at')[:5],
    }
    return render(request, 'main/dashboard.html', context)

# -------------------- Workshop Management Views -------------------- #

@login_required
def manage_workshops(request):
    today = timezone.now().date()
    workshops = Workshop.objects.annotate(
        registration_count=Count('workshopregistration')
    ).order_by('-date')

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

# -------------------- Participant Views -------------------- #

@login_required
def participants_view(request):
    workshop_id = request.GET.get('workshop')
    registrations = WorkshopRegistration.objects.select_related('workshop')

    if workshop_id:
        registrations = registrations.filter(workshop_id=workshop_id)

    workshops = Workshop.objects.all().order_by('-date')

    return render(request, 'main/participants.html', {
        'registrations': registrations,
        'workshops': workshops,
        'selected_workshop': int(workshop_id) if workshop_id else None,
    })

@login_required
def export_participants_excel(request):
    workshop_id = request.GET.get('workshop')
    registrations = WorkshopRegistration.objects.all()

    if workshop_id:
        registrations = registrations.filter(workshop__id=workshop_id)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Participants"
    headers = ['Name', 'Email', 'Phone', 'Participant Type', 'Registered At', 'Extra Info']
    ws.append(headers)

    for reg in registrations:
        if reg.participant_type == 'student':
            extra_info = f"{reg.college}, {reg.course} ({reg.year_of_study})"
        elif reg.participant_type == 'employee':
            extra_info = f"{reg.company_name}, {reg.designation}"
        else:
            extra_info = 'N/A'

        row = [
            reg.name,
            reg.email,
            reg.phone or 'N/A',
            reg.get_participant_type_display(),
            reg.registered_at.strftime('%Y-%m-%d %H:%M'),
            extra_info
        ]
        ws.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=participants.xlsx'
    wb.save(response)
    return response

# -------------------- Feedback List -------------------- #
@login_required
def feedback_list(request):
    workshops = Workshop.objects.all()
    selected_workshop_id = request.GET.get('workshop_id')

    feedbacks = []
    selected_workshop = None

    if selected_workshop_id:
        selected_workshop = Workshop.objects.get(id=selected_workshop_id)
        feedbacks = WorkshopFeedback.objects.filter(workshop=selected_workshop)

    return render(request, 'main/feedbacks.html', {
        'workshops': workshops,
        'selected_workshop': selected_workshop,
        'feedbacks': feedbacks
    })
