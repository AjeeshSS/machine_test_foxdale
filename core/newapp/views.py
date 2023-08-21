from django.shortcuts import render, redirect
import requests

from django.views import View  
from newapp.models import*
from datetime import datetime
from django.http import HttpResponse
from django.core.mail import send_mail
import math, random
from django.contrib import messages
from twilio.rest import Client
from django.urls import reverse
import string

    
class register(View):
    """view for register a new user."""
    
    def get(self, request):
        return render(request, "register.html")
    
    def post(self, request):
        error_msg = None
        PostData = request.POST
        name = PostData.get('name')
        dob = PostData.get('dob')
        dob2 =datetime.strptime(PostData.get('dob'), '%Y-%m-%d')
        today = datetime.now().date()
        age = today.year - dob2.year
        ph = PostData.get('ph')
        email = PostData.get('email')
        about = PostData.get('about')
        userid = random.randint(1001, 9999)
        
        
        if (not ph) and len(ph) < 10:
            error_msg = "phone number required or should be 10 digit !"
            
        if len(about)<5 and (not about):
            error_msg = "about must be at least 5 long"
        
        if not error_msg:
            user = Customer(userid=userid, name=name, dob=dob, ph=ph, age=age, email=email,about=about)
            user.save()
            request.session['email'] = email
            request.session['phone'] = ph
        context = {'user': user}
        return render(request, "welcomepage.html", context=context)
    
  
def generateOTP() :
    """function to generate otp."""
    
    digits = "0123456789"
    OTP = ""
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def send_otp(request):
    """view function to send a otp."""
    
    phone = int(request.session.get('phone'))
    email=request.session.get('email')
    print(email, phone)
    o=generateOTP()
    request.session['otp'] = o
    print('otp is ',o)
    
    
    """send otp code to mobile using fastsms (paid)."""
    
    # url = 'https://www.fast2sms.com/dev/bulkV2'
    # message = o
    # numbers = phone
    # payload = f'sender_id=TXTIND&message={message}&route=v3&language=english&numbers={numbers}'
    # headers = {
    # 'authorization': "xoiObB7WLa4GvY0uPZ6J9KmS1kXQCA2MeRhpzfTHN5sy8dctVDo5mkyeX9CRJxBKzu8M7FZ0stfh2gdi",
    # 'Content-Type': "application/x-www-form-urlencoded"
    # }
    # response = requests.request("POST", url, data=payload, headers=headers)
    # print(response.text)
    
    
    """send otp code to mobile using twilio api(free)"""
    
    account_sid = 'ACcfb38987cad487ee45167fbea77496aa'
    auth_token = '3925fffbb92e15edc121b839c5ccee1f'
    TWILIO_PHONE_NUMBER = +12518422935
    
    client = Client(account_sid, auth_token)
    to_phone_number = phone
    
    message = client.messages.create(
        body=f'Your OTP is: {o}',
        from_=TWILIO_PHONE_NUMBER,
        to='+91' + str(to_phone_number)
    )
    
    
    """send otp code for mail"""
    htmlgen =  f'<p>Your OTP is <strong>{o}</strong></p>'
    send_mail('OTP request',o,'email',[email], fail_silently=False, html_message=htmlgen)
    
    return render(request, "otp.html", {'email': email, 'phone': phone})

 
def otp_verification(request):
    """View function for otp verification."""
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
    if otp == request.session["otp"]:
        messages.info(request,'signed in successfully...')
        email=request.session.get('email')
        user = Customer.objects.get(email=email)
        return render(request,"userdetails.html",{'user': user})
    else:
        messages.error(request,'otp does not match')
        return render(request,"otp.html")
        
    
def decision(request):
    """Decision after manual verification."""
    
    if request.method == 'POST':  
        decision = request.POST.get('decision')
        email = request.session.get('email')
        user = Customer.objects.get(email=email)
        
        """send success mail when accepted"""
        if decision == 'Accept':
            """generate a password if accepted"""
            characters = string.ascii_letters + string.digits + string.punctuation
            new_password = ''.join(random.choice(characters) for _ in range(8))
            Customer.objects.update(password=new_password)
            
            message = f"Successfully registered. Your user ID: {user.userid}."
            html_content = f"<p>Successfully registered with user ID:<strong>{user.userid}</strong><br><br>Password is: <b>{new_password}</b></p>"

            send_mail(
                subject='Registration Successful',
                message=message,
                from_email='email', 
                recipient_list=[email],
                fail_silently=False,
                html_message=html_content,
            )
            
            """send rejection mail when rejected."""
        elif decision == 'Reject':
            edit_url = request.build_absolute_uri(reverse('edit_user', args=[user.userid]))
            htmlgen = f'''<p>Application rejected for user ID: {user.userid}. Please <a href="{edit_url}">edit your application</a>.</p>'''
            
            send_mail(
                subject='Application Rejected',
                message="Your application has been rejected. Please edit your application.",
                from_email='email', 
                recipient_list=[email],
                fail_silently=False,
                html_message=htmlgen,
            )
        return HttpResponse("Decision processed successfully")
    else:
        # Handle cases where the request method is not POST
        return HttpResponse("Invalid request method")
    
def edit_user(request, user_id):
    """edit user if rejected by admin."""
    
    user = Customer.objects.get(userid=user_id)
    
    if request.method == 'POST':
        # Retrieve updated data from the POST request
        new_username = request.POST.get('name')
        new_dob = request.POST.get('dob')
        new_age = request.POST.get('age')
        new_ph = request.POST.get('ph')
        new_email = request.POST.get('email')
        new_about = request.POST.get('about')
        
        # Update the user's information
        user.name = new_username
        user.dob = new_dob
        user.age = new_age
        user.ph = new_ph
        user.email = new_email
        user.about = new_about
        user.save()
        
        return redirect('user_detail', user_id=user.userid)  # Redirect to user detail page
    
    return render(request, 'edit_user.html', {'user': user})
    
def user_detail(request, user_id):
    """user detail page after edit."""
    
    user = Customer.objects.get(userid=user_id)
    return render(request, 'user_detail.html', {'user': user})
    
