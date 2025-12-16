from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def contact(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        
        if email and message:
            # Compose the email
            subject = f'New Contact Form Message from {email}'
            full_message = f'From: {email}\n\nMessage:\n{message}'
            
            try:
                # Send email
                send_mail(
                    subject,
                    full_message,
                    email,  # From email
                    ['rijmenbaskara@gmail.com'],  # To email
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
            except Exception as e:
                messages.error(request, f'Failed to send message. Please try again later.')
            
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'contact.html')

def home(request):
    return render(request, 'home.html')

def works(request):
    return render(request, 'works.html')

def articles(request):
    return render(request, 'articles.html')

def about(request):
    return render(request, 'about.html')
