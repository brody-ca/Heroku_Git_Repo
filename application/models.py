from django.db import models
# User class for built-in authentication module
from django.contrib.auth.models import User

class AppUser(models.Model):
    career = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    expertise = models.ManyToManyField('Tag')
    first_name = models.CharField(max_length=50, blank=True)
    followed_users = models.ManyToManyField('AppUser', related_name='f_users')
    last_name = models.CharField(max_length=50, blank=True)
    picture = models.ImageField(upload_to="pictures",blank=True)
    points = models.IntegerField(default=100)
    requests = models.ManyToManyField('Request')
    user = models.ForeignKey(User)
    votes_for = models.ManyToManyField('Vote',related_name="reversevote",blank=True)

    @property
    def get_reputation(self):
        rep = 0
        for vote in self.reversevote.all():
            if vote.like is True:
                rep += 1
            else:
                rep -= 1
        return rep
    
    def __unicode__(self):
        return self.first_name + " " + self.last_name
        
class Comment(models.Model):
    date = models.DateTimeField(auto_now=False, auto_now_add=True)
    response = models.ForeignKey('Response')
    text = models.CharField(max_length=500)
    user = models.ForeignKey(AppUser)
    votes = models.ManyToManyField('Vote')

    def __unicode__(self):
        return user.user.username + ": " + text    

class Request(models.Model):
    answered = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)
    details = models.CharField(max_length=10000)
    name = models.CharField(max_length=40)
    picture = models.ImageField(upload_to="pictures", blank=True)
    reward = models.IntegerField(default=0)
    responses = models.ManyToManyField('Response', related_name='Response')
    selected_id = models.IntegerField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    tags_string = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey('AppUser')
    vote_count = models.IntegerField(default=0, blank=True)
    votes = models.ManyToManyField('Vote')
    
    @staticmethod
    def get_my_requests(owner):
        return Request.objects.filter(user=owner).order_by('answered', '-date')
        
    @staticmethod
    def get_all_requests(owner):
        return Request.objects.all().order_by('answered', '-date')
        
    @staticmethod
    def get_valuable_requests(owner):
        return Request.objects.filter(answered=False).order_by('-reward', '-date')    
    
    @staticmethod
    def get_popular_requests(owner):
        return Request.objects.all().order_by('-vote_count', '-date')        
        
    @staticmethod
    def get_unanswered_requests(owner):
        return Request.objects.filter(answered=False).order_by('answered', '-date')        
            
    @staticmethod
    def get_top_user_requests(owner):
        return Request.objects.all().order_by('-user.get_reputation', '-date')
        
    @staticmethod
    def get_newest_requests(owner):  
        return Request.objects.all().order_by('-date')
        
    def __unicode__(self):
        return self.name 
    
class Response(models.Model):
    comments = models.ManyToManyField('Comment', related_name='rpns', blank=True)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)
    details = models.CharField(max_length=2000)
    name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to="pictures", blank=True)
    request = models.ForeignKey('Request')
    selected_answer = models.BooleanField(default=False)
    user = models.ForeignKey('AppUser')
    vote_count = models.IntegerField(default=0, blank=True)
    votes = models.ManyToManyField('Vote', blank=True)

    def __unicode__(self):
        return user.user.username + ": " + text 

class Tag(models.Model):
    text = models.CharField(max_length=20)

    def __unicode__(self):
        return self.text

class Vote(models.Model):
    # true for upvote, false for downvote
    user = models.ForeignKey('AppUser',related_name="reversevote")
    like = models.BooleanField()

    def __unicode__(self):
        if like:
            return user.user.username + " like"
        else:
            return user.user.username + " dislike"
    
