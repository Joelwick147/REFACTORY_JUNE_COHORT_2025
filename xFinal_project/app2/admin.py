from django.contrib.auth.forms import UserCreationForm
#import all models
from .models import *
from .models import UserProfile


from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Farmer, ChickStock, ChickRequest, Sale, FeedStock

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Farmer)
admin.site.register(ChickStock)
admin.site.register(ChickRequest)
admin.site.register(Sale)
admin.site.register(FeedStock)


#auto hashing password
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    def save_model(self,request,obj, form,change):
        if UserProfile.objects.filter(user=obj.user).exists():
            existing_profile =UserProfile.objects.get(user=obj.user)
            pass
        else:
            super().save_model(request,obj,form,change)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    

class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
