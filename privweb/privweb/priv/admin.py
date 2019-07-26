# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import User, Permission, Role

admin.site.site_header = "Genhub Privileges"
admin.site.site_title = "Genhub Privileges"

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    fields=[
        'acct_name',
        'first_name',
        'last_name'
    ]

admin.site.register(User, UserAdmin)

class RoleAdmin(admin.ModelAdmin):
    fieldsets=[
        (None,          {'fields': ['role_name']}),
        ('Users',       {'fields': ['users'],  'classes':['collapse']}),
        ('Permissions', {'fields': ['permissions'], 'classes':['collapse']})
    ]

admin.site.register(Role,RoleAdmin)

class PermissionAdmin(admin.ModelAdmin):
    fields=[
        'permission_name'
    ]
admin.site.register(Permission,PermissionAdmin)

