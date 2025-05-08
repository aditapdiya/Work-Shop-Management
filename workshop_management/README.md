# Workshop Management System

A Django-based application for managing workshop details, including user authentication, workshop scheduling, and more.

## Features

- **User Authentication**: Login, Registration, Password Reset
- **Workshop Scheduling**: Create and manage workshops
- **Admin Panel**: Admin users can manage workshops, view users, etc.
- **Email Integration**: Forgot password functionality using Gmail's SMTP

## Requirements

- Python 3.x
- Django 3.x or higher
- sqlite
- Python-dotenv (for environment variables)


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aditapdiya/Work-Shop-Management.git
   cd Work-Shop-Management


## Email Configuration (Gmail SMTP)
Django requires an SMTP server to send emails, including password reset emails. If you’re using Gmail, you need to configure Gmail's SMTP settings.

🔐 Step 1: Enable 2-Step Verification
Go to Google Account Security Settings
https://myaccount.google.com/security

Enable 2-Step Verification if it’s not already enabled.

🔐 Step 2: Generate an App Password
Go to App Passwords
https://myaccount.google.com/apppasswords

Log in to your Google account and select:

App: "Mail"

Device: "Other" and name it "Django App"

Google will generate a 16-character password, such as abcd efgh ijkl mnop.

🛠️ Step 3: Use This App Password in Your Django settings.py
Update your settings.py with the following configuration:

python
Copy
Edit
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'  # Replace with your Gmail address
EMAIL_HOST_PASSWORD = 'your_app_specific_password'  # Paste the 16-character password here
Make sure there are no spaces when copying the 16-character password.

Step 4: Verify Email Sending Functionality
After completing the setup, Django will be able to send password reset emails successfully. You can test this by using the Forgot Password functionality in the login page.

Usage
Login Page: Access the login page to enter your credentials and log in.

Forgot Password: If you forget your password, use the "Forgot Password" link to reset your password via email.

Admin Panel: Access the Django admin panel at http://127.0.0.1:8000/admin (only if you are an admin). Use the superuser credentials created earlier to log in.