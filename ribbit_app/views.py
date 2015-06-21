from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from ribbit_app.forms import AuthenticateForm, UserCreateForm, RibbitForm
from ribbit_app.models import Ribbit
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

def index(request, auth_form=None, user_form=None):
    # If user is logged in, render the relevent templates
    if request.user.is_authenticated():
        ribbit_form = RibbitForm()
        user = request.user
        ribbits_self = Ribbit.objects.filter(user=user.id) #only contains own ribbits
        ribbits_buddies = Ribbit.objects.filter(user__userprofile__in=user.profile.follows.all) #only contains buddy ribbits
        ribbits = ribbits_self | ribbits_buddies #. The querysets ribbits_self and ribbits_buddies are merged with the | operator
 
        return render(request,
                      'buddies.html',
                      {'ribbit_form': ribbit_form, 'user': user,
                       'ribbits': ribbits,
                       'next_url': '/', })
    else:
        # if user is not logged in, render the relevent templates
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()
 
        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, })

def login_view(request): #logs the user in
    if request.method == 'POST': # expects a HTTP POST request for the login (since the form's method is POST)
        form = AuthenticateForm(data=request.POST)
        if form.is_valid(): #If form validation is successful, login the user using the login() method which starts the session and then redirects to the root url.
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return index(request, auth_form=form) #pass the instance of the auth_form received from the user to the index function and list the errors
    return redirect('/') #if the request isn't POST then the user is redirected to the root url
 
 
def logout_view(request): #logs the user out
    logout(request)
    return redirect('/')

def signup(request):#the view to sign up and register a user
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST': #the signup view expects a POST request
        if user_form.is_valid(): #If the Sign Up form is valid, the user is saved to the database, authenticated, logged in and redirected to the home page.
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else: #Otherwise, call the index function and pass in the instance of user_form submitted by the user to list out the errors
            return index(request, user_form=user_form)
    return redirect('/')#if the request isn't POST then the user is redirected to the root url

@login_required #this decorator executes the function only if the user is authenticated; else the user is redirected to the path specified in LOGIN_URL constant in the settings
def submit(request):
    if request.method == "POST":
        ribbit_form = RibbitForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if ribbit_form.is_valid(): #If form validation is successful, we manually set the user to the one contained in the session and then save the records.
            ribbit = ribbit_form.save(commit=False)
            ribbit.user = request.user
            ribbit.save()
            return redirect(next_url) #the user is redirected to the path specified in next_url field which is a hidden form field we manually entered in the template for this purpose. The value of next_url is passed along in the views that render the Ribbit Form.
        else:
            return public(request, ribbit_form)
    return redirect('/')

@login_required #this decorator executes the function only if the user is authenticated; else the user is redirected to the path specified in LOGIN_URL constant in the settings
def public(request, ribbit_form=None):
    ribbit_form = ribbit_form or RibbitForm()
    ribbits = Ribbit.objects.reverse()[:10] #we query the database for the last 10 ribbits by slicing the queryset to the last 10 elements
    return render(request, #The form along with the ribbits are then rendered to the template
                  'public.html',
                  {'ribbit_form': ribbit_form, 'next_url': '/ribbits',
                   'ribbits': ribbits, 'username': request.user.username})

def get_latest(user): #This makes use of a backward relation on the User<-->Ribbit relation.
    try: #user.ribbit_set.all() returns all the ribbits by the user. We order the ribbits by id in descending order and slice the first element
        return user.ribbit_set.order_by('-id')[0]
    except IndexError:
        return ""
 
 
@login_required
def users(request, username="", ribbit_form=None):
    if username:#if a username is passed and is not empty.
        # Show a profile
        try: #ensuring that only logged in users are able to view profiles
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404 #raise a Http404 exception provided by Django to redirect to the default 404 template
        ribbits = Ribbit.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username): 
            # check if the profile requested is of the logged in user or one of his buddies.
            return render(request, 'user.html', {'user': user, 'ribbits': ribbits, }) #If so we don't need to render a follow link in the profile since the 'follow' relationship is already established
        return render(request, 'user.html', {'user': user, 'ribbits': ribbits, 'follow': True, }) #Otherwise, we pass along the follow parameter in the view to print the Follow link
    users = User.objects.all().annotate(ribbit_count=Count('ribbit')) #if username was empty, fetch a list of all the users and use the annotate() function to add a ribbit_count attribute to all objects, which stores the number of Ribbits made by each user in the queryset.
    ribbits = map(get_latest, users) #getting latest ribbit by each user, use Python's built in map() function for this and call get_latest() to all the elements of users queryset
    obj = zip(users, ribbits) #using Python's zip() function to link up each element of both iterators (users and ribbits) so that we have a tuple with User Object and Latest Ribbit pair
    ribbit_form = ribbit_form or RibbitForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/', #pass along the zipped object along with the forms to the template
                   'ribbit_form': ribbit_form,
                   'username': request.user.username, })

@login_required 
def follow(request): #view that will accept the request to follow a user
    if request.method == "POST":
        follow_id = request.POST.get('follow', False) # we get the value of the follow parameter, passed by POST
        if follow_id: #check if a user exists and add the relation
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile) #adding the relation
            except ObjectDoesNotExist:
                return redirect('/users/') #else catch an ObjectDoesNotExist exception and redirect the user to the page that lists all User Profiles.
    return redirect('/users/')
                                                                        
