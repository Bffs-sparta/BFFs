from django.contrib import admin
from .models import User

# Register your models here.
from user.models import User, Profile

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
