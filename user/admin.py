from django.contrib import admin

# Register your models here.
from .models import User, Profile, GuestBook

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(GuestBook)
