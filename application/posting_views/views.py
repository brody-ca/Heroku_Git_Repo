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
from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator

from django.core.mail import send_mail

from application.models import *
from application.forms import *

from itertools import chain

def home(request):
    context = {}
    appuser = get_user_from_request(request)
    context['appuser'] = appuser
    if not request.GET.__contains__('sort') or request.GET['sort'] == "unanswered":
        context['request_list'] = Request.get_unanswered_requests(appuser)
        context['sort'] = "unanswered"
        return render(request, "home.html", context)
    
    # else the sort value was given to us
    sort_method = request.GET['sort']
    if sort_method == "most_valuable":
        context['sort'] = "most_valuable"
        context['request_list'] = Request.get_valuable_requests(appuser)
    elif sort_method == "popular":
        context['sort'] = "popular"
        context['request_list'] = Request.get_popular_requests(appuser)
    elif sort_method == "from_top_users":
        context['sort'] = "from_top_users"
        context['request_list'] = Request.get_top_user_requests(appuser) 
    elif sort_method == "newest":
        context['sort'] = "newest"
        context['request_list'] = Request.get_newest_requests(appuser)
    elif sort_method == "search":
        print "searching"
        context['sort'] = "search"
        search_key = request.GET['search']
        if request.GET.__contains__('tag'):
            tag = True 
        else:
            tag = False
        if request.GET.__contains__('username'):
            username = True 
        else:
            username = False
        if request.GET.__contains__('followed'):
            followed = True 
        else:
            followed = False
        if (not tag) and (not username) and (not followed):
            name_filter_set = Request.objects.filter(name__contains=search_key)
            details_filter_set = Request.objects.filter(details__contains=search_key)
            context['request_list'] = list(chain(name_filter_set, details_filter_set))
        else:
            filter_set = Request.objects.all()
            if tag:
                filter_set = filter_set.filter(tags_string__contains=search_key)
            if username:
                filter_set = filter_set.filter(user__user__username=search_key)
            if followed:
                for req in filter_set:
                    if req.user not in appuser.followed_users.all():
                        filter_set = filter_set.exclude(id=req.id)
                if (not tag) and (not username):
                    name_filter_set = filter_set.filter(name__contains=search_key)
                    details_filter_set = filter_set .filter(details__contains=search_key)
                    context['request_list'] = list(chain(name_filter_set, details_filter_set))
            context['request_list'] = filter_set
            
    else:
        print "undefined sort_method"
    return render(request, "home.html", context)
    

    
def view_request(request):
    context = {}
    context['appuser'] = get_user_from_request(request)
    
    if request.method == 'POST' or not request.GET.get('id'):
        raise Http404
    
    thisid = request.GET['id']
    
    if not Request.objects.filter(id=thisid).exists():
        raise Http404
    
    context['request'] = Request.objects.get(id=thisid)
    return render(request, "request_page.html", context)
    
@login_required
def dislike_request(request, id):
    context = {}
    appuser = get_user_from_request(request)
    context['appuser'] = appuser
    
    this_id = id
    if not Request.objects.filter(id=this_id).exists():
        raise Http404
        
    req = Request.objects.get(id=this_id)
    
    if not req.votes.filter(user=req.user).exists():
        new_like = Vote(like=False, user=req.user)
        new_like.save()
        req.votes.add(new_like)
        req.vote_count -= 1;
        req.save()
    context['request'] = req
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    #return render(request, "request_page.html", context)    
    
@login_required
def like_request(request, id):
    context = {}
    appuser = get_user_from_request(request)
    context['appuser'] = appuser
    
    this_id = id
    if not Request.objects.filter(id=this_id).exists():
        raise Http404
        
    req = Request.objects.get(id=this_id)
    
    if not req.votes:
        req.votes = []
    if not req.votes.filter(user=req.user).exists():
        new_like = Vote(like=True, user=req.user)
        new_like.save()
        req.votes.add(new_like)
        req.vote_count += 1;
        req.save()
    context['request'] = req
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    #return render(request, "request_page.html", context)

@login_required    
def get_followed_user_requests(request):
    context = {}
    context['appuser'] = get_user_from_request(request)
    return render(request, "follows.html", context)

@login_required
def view_my_requests(request):
    context = {}
    context['appuser'] = get_user_from_request(request)
    context['request_list'] = Request.get_my_requests(context['appuser'])
    return render(request, "my_requests.html", context)

@login_required
def new_request(request):
    context = {}
    asker = get_user_from_request(request)
    context['appuser'] = asker
    context['form'] = RequestForm
    if request.method == 'GET' or context['appuser'] == None:
        return render(request, "new_request.html", context)
        
    # else it's a post request, so get the request form
    form = RequestForm(request.POST, request.FILES)
    context['errors'] = []
    if not form.is_valid():
        for error in form.errors:
                context['errors'].append(error)
                print error
        for error in form.non_field_errors():
                context['errors'].append(error)
                print error
        return render(request, 'new_request.html', context)
    
    actualreq = form.save(commit=False)
    # check that the user has enough points
    if actualreq.reward > context['appuser'].points:
        context['errors'].append("Not enough points!")
        return render(request, 'new_request.html', context)
    
    actualreq.user = context['appuser']
#    actualreq.name = context['appuser'].user.username

    actualreq.selected_id = -1
    actualreq.vote_count = 0
    actualreq.save()
    if actualreq.tags_string:
        tags_list = actualreq.tags_string.split()
        for t in tags_list:
            tag = Tag(text=t)
            tag.save()
            actualreq.tags.add(tag)
    actualreq.save()
    actualreq.votes = []
    actualreq.save()
    #take points from the one who asked the question
    asker.points -= actualreq.reward
    asker.save()
    context['request'] = actualreq
    return HttpResponseRedirect('/view_request?id=' + str(actualreq.id))
    
@login_required
def new_response(request):
    context = {}
    context['appuser'] = get_user_from_request(request)
    context['form'] = ResponseForm
    if request.method == 'GET':
        get_id = request.GET['id']
        req = Request.objects.get(id=get_id)
        context['request'] = req
        return render(request, 'new_response.html', context)
        
    get_id = request.POST['id']
    req = Request.objects.get(id=get_id)
    context['request'] = req
    # else it's a post request, so get the request form
    form = ResponseForm(request.POST, request.FILES)
    context['errors'] = []
    if not form.is_valid():
        for error in form.errors:
                context['errors'].append(error)
                print error
        for error in form.non_field_errors():
                context['errors'].append(error)
                print error
        return render(request, 'new_response.html', context)
    
    actualres = form.save(commit=False)
    actualres.user = context['appuser']
    actualres.request = req
    actualres.vote_count = 0
    actualres.save()
    req.responses.add(actualres)
    req.save()
    return HttpResponseRedirect('/view_request?id=' + str(req.id))
    
def select_response(request):
    response = Response.objects.get(id=request.POST['response_id'])
    req = response.request
    req.selected_id = response.id
    req.answered = True
    req.save()
    
    #Give points to whomever answered correctly
    answerer = response.user
    answerer.points += req.reward
    answerer.save()
    
    context={}
    context['appuser'] = get_user_from_request(request)
    context['request'] = req
    
    return redirect(request.META.get('HTTP_REFERER'))
    
@login_required
def dislike_response(request, id):
    context = {}
    appuser = get_user_from_request(request)
    context['appuser'] = appuser
    
    this_id = id
    if not Response.objects.filter(id=this_id).exists():
        raise Http404
        
    res = Response.objects.get(id=this_id)
    
    if not res.votes.filter(user=appuser).exists():
        new_like = Vote(like=False, user=appuser)
        new_like.save()
        res.votes.add(new_like)
        res.vote_count -= 1;
        res.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    #return render(request, "request_page.html", context)    
    
@login_required
def like_response(request, id):
    context = {}
    appuser = get_user_from_request(request)
    context['appuser'] = appuser
    
    this_id = id
    if not Response.objects.filter(id=this_id).exists():
        raise Http404
        
    res = Response.objects.get(id=this_id)
    
    if not res.votes.filter(user=appuser).exists():
        new_like = Vote(like=True, user=appuser)
        new_like.save()
        res.votes.add(new_like)
        res.vote_count += 1;
        res.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
@login_required
def new_comment(request):
    context = {}
    appuser = get_user_from_request(request)
    context['appuser'] = appuser
    context['form'] = CommentForm
    
    if request.method == 'GET':
        get_id = request.GET['id']
        res = Response.objects.get(id=get_id)
        context['response'] = res
        context['req'] = res.request
        return render(request, 'new_comment.html', context)
        
    get_id = request.POST['res_id']
    res = Response.objects.get(id=get_id)
    # else it's a post request, so get the request form
    form = CommentForm(request.POST, request.FILES)
    context['errors'] = []
    if not form.is_valid():
        for error in form.errors:
                context['errors'].append(error)
                print error
        for error in form.non_field_errors():
                context['errors'].append(error)
                print error
        context['response'] = res
        return render(request, 'new_comment.html', context)
    
    actualcomment = form.save(commit=False)
    actualcomment.user = context['appuser']
    actualcomment.response = res
    actualcomment.vote_count = 0
    actualcomment.save()
    res.comments.add(actualcomment)
    res.save()

    return HttpResponseRedirect('/view_request?id=' + str(res.request.id))
    
    
        
# helper function to get the AppUser from the post/get request
def get_user_from_request(request):
    if request.user and request.user.is_authenticated():
        return AppUser.objects.get(user=request.user)
    else:
        return None
    
    
    
