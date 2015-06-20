from django.db import models
from django.contrib.auth.models import User
import hashlib
 
 
class Ribbit(models.Model): #like tweets
    content = models.CharField(max_length=140)
    user = models.ForeignKey(User) #a ForeignKey to the User model, so that we have a relation between the two models
    creation_date = models.DateTimeField(auto_now=True, blank=True)
 
 
class UserProfile(models.Model): #a subclass of User, just includes the extra attribute of "follows"
    user = models.OneToOneField(User) #defines a One to One relation with the User Model
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)#implements follows and followed_by both
 
    def gravatar_url(self): #defines a function to get the link to the gravatar image based upon the user's url
        return "http://www.gravatar.com/avatar/%s?s=50" % hashlib.md5(self.user.email).hexdigest()
 
 
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0]) #a property to get (if the UserProfile exists for the user) or create one when we use the syntax <user_object>.profile

''' Here's an example of how to use above to get the users that a given User follows and is followed by:
superUser = User.object.get(id=1)
superUser.profile.follows.all() # Will return an iterator of UserProfile instances of all users that superUser follows
superUse.profile.followed_by.all() # Will return an iterator of UserProfile instances of all users that follow superUser''' 