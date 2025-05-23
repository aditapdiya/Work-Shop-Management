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


# views.py
def register_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, pk=workshop_id)

    if request.method == 'POST':
        form = WorkshopRegistrationForm(request.POST, workshop=workshop)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.workshop = workshop
            registration.save()

            # Email sending logic (as you already have)
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

from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMessage
from django.contrib import messages
from .forms import WorkshopFeedbackForm
from .models import Workshop, WorkshopFeedback
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def workshop_feedback_view(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if request.method == 'POST':
        form = WorkshopFeedbackForm(request.POST, workshop=workshop)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.workshop = workshop
            feedback.save()

            # Generate certificate as PDF
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

            # Send email with certificate
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

from django.db.models import Count

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


from .models import WorkshopRegistration  # already imported

@login_required
def participants_view(request):
    workshop_id = request.GET.get('workshop')

    # Get all registrations, filter if a workshop is selected
    registrations = WorkshopRegistration.objects.select_related('workshop')
    if workshop_id:
        registrations = registrations.filter(workshop_id=workshop_id)

    # For dropdown list
    workshops = Workshop.objects.all().order_by('-date')

    return render(request, 'main/participants.html', {
        'registrations': registrations,
        'workshops': workshops,
        'selected_workshop': int(workshop_id) if workshop_id else None,
    })

import openpyxl
from django.http import HttpResponse
from .models import WorkshopRegistration, Workshop

def export_participants_excel(request):
    workshop_id = request.GET.get('workshop')
    registrations = WorkshopRegistration.objects.all()

    if workshop_id:
        registrations = registrations.filter(workshop__id=workshop_id)

    # Create Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Participants"

    # Headers
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

    # Response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = 'participants.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response
