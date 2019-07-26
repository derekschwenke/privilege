# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class User(models.Model):
    acct_name = models.CharField(max_length=24)  #   primary_key=True  "id" field is default
    first_name = models.CharField(max_length=24)
    last_name = models.CharField(max_length=24)

    def __str__(self):
        return('%s: %s %s' % (self.acct_name, self.first_name, self.last_name))
    
class Permission(models.Model):
    permission_name = models.CharField(max_length=80)

    def __str__(self):
        return(self.permission_name)
    
class Role(models.Model):
    role_name = models.CharField(max_length=80)
    users = models.ManyToManyField(User)
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return(self.role_name)
  
  
