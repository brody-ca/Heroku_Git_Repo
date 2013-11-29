from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email

from django.core.urlresolvers import reverse

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, Http404

from mimetypes import guess_type

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator

from django.core.mail import send_mail

from application.models import *
from application.forms import *

def home(request):
    return render(request, "home.html")
    
def login(request):
    return render(request, "login.html")
    
def view_request(request):
    return render(request, "request_page.html")

def view_profile(request):
    return render(request, "profile.html")

def get_followed_user_requests(request):
    return render(request, "follows.html")

def view_my_requests(request):
    return render(request, "my_requests.html")

def new_request(request):
    return render(request, "new_request.html")
