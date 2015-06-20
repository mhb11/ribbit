from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from ribbit_app.forms import AuthenticateForm, UserCreateForm, RibbitForm
from ribbit_app.models import Ribbit

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