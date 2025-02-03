# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')

    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else None
    get_role.short_description = 'Role'

# Unregister the original User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Optionally, also register the Profile model separately
admin.site.register(Profile)
