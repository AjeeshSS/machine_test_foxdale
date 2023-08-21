"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from newapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path("",views.home,name="home"),
    path('register/', views.register.as_view(), name='register'), 
    path("register/send_otp/",views.send_otp,name="send otp"),
    path("register/send_otp/otp_verification",views.otp_verification,name="verify"),
    path('register/send_otp/decision/', views.decision, name='decision'), 
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('user_detail/<int:user_id>/', views.user_detail, name='user_detail'),
]