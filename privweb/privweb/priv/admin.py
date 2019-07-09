# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import User, Permission, Role

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    fields=[
        'acctname',
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

