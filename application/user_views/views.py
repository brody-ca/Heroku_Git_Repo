from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email

from django.core.urlresolvers import reverse

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, Http404, HttpResponseRedirect

from mimetypes import guess_type

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import * 

from django.core.mail import send_mail

from application.models import *
from application.forms import *

def register(request):
    context = {}
    errors = []
    
    username = request.POST['username']
    if not username:
        errors.append("You must enter username!")
        context['errors'] = errors
        return render(request, 'login.html', context)
    email = request.POST['email']
    if not email:
        errors.append("You must enter email!")
        context['errors'] = errors
        return render(request, 'login.html', context)
    
    password1 = request.POST['password1']
    password2 = request.POST['password2']
    if not password1 or not password2:
        errors.append("You must enter passwords!")
        context['errors'] = errors
        return render(request, 'login.html', context)
    
    if password1 and password2 and password1 != password2:
        errors.append("Passwords don't match.")
        context['errors'] = errors
        return render(request, 'login.html', context)
   
    if User.objects.filter(username__exact=username):
        errors.append("Username already exists.")
        context['errors'] = errors
        return render(request, 'login.html', context)
  
    if User.objects.filter(email__exact=email):
        errors.append("Email already in use.")
        context['errors'] = errors
        return render(request, 'login.html', context)
    try:
        validate_email(request.POST['email'])
    except ValidationError:
        errors.append('Email is invalid.')
        context['errors'] = errors
        return render(request, 'login.html', context)
        
    #Creating new User object
    new_user = User.objects.create_user(username=username, \
                                        password=password1, \
                                        email=request.POST['email'])
    new_user.save()
    
    user = authenticate(username=username, password=password1)
    login(request, user)
     
    #Create AppUser obj for the new User
    #TODO: Add more stuff to AppUser
    new_app_user = AppUser(user = new_user)
    new_app_user.save()
    
    return redirect('/')


def logout_user(request):
    logout(request)
    return redirect('/') 

def view_profile(request):
    context = {}
    context['appuser'] = get_user_from_request(request)
    if request.method == 'POST' or not request.GET.get('id'):
        thisuser = get_user_from_request(request)
        if not thisuser:
            raise Http404
        
        context['tags'] = thisuser.expertise.all() 
        thisid = thisuser.id
        context['profileuser'] = get_object_or_404(AppUser, id=thisid)
        if not context['profileuser']:
            raise Http404
        if thisid==request.user.id:
            context['self']="true";
        else:
            context['self']="false";
        return HttpResponseRedirect('profile?id=' + str(thisid))
        
    thisid = request.GET['id']
    thisuser = get_object_or_404(AppUser, id=thisid)
    context['profileuser'] = thisuser 
    if not context['profileuser']:
        raise Http404
     
    context['tags'] = thisuser.expertise.all()
    if thisid==request.user.id:
        context['self']="true";
    else:
        context['self']="false";
        
    profileuser = context['profileuser']
    context['request_list'] = Request.objects.filter(user=profileuser).order_by('-date')    
    context['response_list'] = []
    responses = Response.objects.filter(user=profileuser).order_by('-date')
    for r in responses:
        if (r.request not in context['request_list']) and (r.request not in context['response_list']):
            context['response_list'].append(r.request)
    
    return render(request, 'profile.html', context)

def edit_profile(request):
    context = {}
    context['appuser'] = get_user_from_request(request)
    thisuser = get_user_from_request(request)
    if request.method == 'GET':
        thisid = thisuser.id
        context['profileuser'] = get_object_or_404(AppUser, id=thisid)
        context['rep'] = context['profileuser'].reversevote.all().count() 
        context['tags'] = thisuser.expertise.all()
        return render(request, 'edit_profile.html', context)

    profile = get_object_or_404(AppUser, id=thisuser.id)
    
    education = request.POST['education']
    if education:
        profile.education=education
    career = request.POST['career']
    if career:
        profile.career = career
    expertise = request.POST['expertise']
    if expertise:
        new_tag = Tag(text=expertise)
        new_tag.save()
        profile.expertise.add(new_tag)
    profile.save() 
    
    form = AppUserForm(request.POST, request.FILES, instance=profile)
    if not form.is_valid():
        print "Error in form" 
        print form.errors
        return redirect('/profile') 
    
    form.save()

    return redirect('/profile')

def follow_user(request):
    follow_id = request.GET['target_id']
    appuser = get_user_from_request(request)
    follow_user = get_object_or_404(AppUser, id=follow_id)

    if len(appuser.followed_users.filter(user=follow_user.user)) == 0:
        appuser.followed_users.add(follow_user)
    
    return HttpResponseRedirect('profile?id=' + str(follow_id))

def change_password(request):
    context = {}
    errors = []
    context['errors'] = errors
    context['appuser'] = get_user_from_request(request)
    thisuser = get_user_from_request(request)
    
    thisid = thisuser.id
    context['profileuser'] = get_object_or_404(AppUser, id=thisid)
    if request.method == 'GET':
        return render(request, 'change_password.html', context)

    old_pw = request.POST['old_password']
    new_pw1 = request.POST['password1']
    new_pw2 = request.POST['password2']
    if (not new_pw1 or not new_pw2) or (new_pw1 != new_pw2):
        errors.append("password error.")
        return render(request, 'change_password.html', context)

    if not check_password(old_pw,request.user.password):
        errors.append("password error. old password did not match!")
        return render(request, 'change_password.html', context)
   
    request.user.password = make_password(new_pw1)
    request.user.save()
   
    thisid = thisuser.id
    return HttpResponseRedirect('profile?id=' + str(thisid))

# helper function to get the AppUser from the post/get request
def get_user_from_request(request):
    if request.user and request.user.is_authenticated():
        return AppUser.objects.get(user=request.user)
    else:
        return None
