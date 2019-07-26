# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q 
from priv.models import User, Role, Permission

# See search write up:  https://wsvincent.com/django-search/
# logging.basicConfig()        self.logger = logging.getLogger('logger')
# = list(obj.translations.all().values_list('pk', flat=True))

class QueryParser():
    def __init__(self,view):
        self.query = view.request.GET.get('q')
        logging.basicConfig()
        self.logger = logging.getLogger('logger')
    
    def isActive(self):
        return len(self.query)

    def userFilter(self):
        return self.parseQuery()
    
    def roleFilter(self):
        return self.parseQuery(role=True)
        
    def userRoleFilter(self):
        return self.parseQuery(roleu=True)
    
    def permissionFilter(self):
        return self.parseQuery(permission=True)
    
    def permission2role(self):
        f = Q()
        if not self.query: return
        for term in self.query.split():
            term = term.strip()
            if term.startswith("permission:"): 
                f = f | Q(permissions__permission_name=term[11:])#  VS permission_name__icontains ?
                self.query = self.query.replace(term,"")
        if not len(f): return 
        for r in Role.objects.filter(f):  # roles for this permission
            self.query = self.query + " role:" + r.role_name

        #self.logger.warning("QueryParser permission2role " + str(q) + " --> " + str(self.query) + " filter " + str(f) )
        return
    
    def parseQuery(self, role=False, roleu=False, permission=False):
        f = Q()
        if not self.query: return f

        for term in self.query.split():
            term = term.strip()
            if not term: pass
            if role and term.startswith("role:"): 
                f = f | Q(role_name__icontains=term[5:])
            elif roleu and term.startswith("role:"): 
                f = f | Q(role__role_name=term[5:])
            elif permission and term.startswith("permission:"): 
                f = f | Q(permission_name__icontains=term[11:])
            elif role: pass
            elif roleu: pass
            elif permission: pass
            elif term.startswith("role:"): pass
            elif term.startswith("permission:"): pass
            elif term.startswith("first:"): f = f | Q(first_name__icontains=term[6:])
            elif term.startswith("last:"): f = f | Q(last_name__icontains=term[5:])
            elif term.startswith("acct:"): f = f | Q(acct_name__icontains=term[5:])
            else: 
                f = f | Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(acct_name__icontains=term)
        self.logger.warning("QueryParser " + str(role) + str(roleu) + " " + str(permission) + " " + str(self.query) + " is " + str(f) )
        return f

#def index(request):
#    return HttpResponse("Placeholder index for app <tt>priv</tt>")

class IndexView(TemplateView):
    template_name = 'index.html'

class SearchView(TemplateView):
    template_name = 'search.html'

class CheckView(TemplateView):
    template_name = 'search.html'

class ResultsView(ListView):
    model = User
    template_name = 'results.html'
    
    def get_queryset(self):
        parser = QueryParser(self)
        parser.permission2role()
        object_list = User.objects.filter( parser.userFilter() ).filter( parser.userRoleFilter() ).order_by('acct_name').distinct()
        return object_list

class DetailView(DetailView):  # or --> TemplateView 
    model = User
    template_name = 'detail.html'   
    
    def get_context_data(self, **kwargs):
        context = super(DetailView,self).get_context_data(**kwargs)
        user_object = User.objects.filter(id=int(self.kwargs['pk']))[:1].get()
        u = user_object
        u.perms = set()
        u.roles = Role.objects.filter(users__acct_name=u.acct_name) 
        for r in u.roles:  
            u.perms.update( r.permissions.all() )
        for p in u.perms: 
            p.roles = u.roles.filter(permissions__permission_name=p.permission_name) 
        context['permission_list'] = u.perms
        context['user_object'] = u
        return context

class RoleUserView(ListView):
    model = User
    template_name = 'role_user.html'
    def get_queryset(self):
        parser = RoleUserView.query = QueryParser(self)
        object_list = User.objects.filter(parser.userFilter()).order_by('acct_name').distinct()
        return object_list

    def get_context_data(self, **kwargs):
        parser = RoleUserView.query
        context = super(RoleUserView,self).get_context_data(**kwargs)
        roles = Role.objects.filter(parser.roleFilter())
        rm = Q()
        if parser.isActive(): 
            for r in roles: 
                if not r.users.filter(parser.userFilter()).order_by('acct_name').distinct(): 
                    rm = rm | Q(id=r.id)

        roles = Role.objects.exclude(rm).filter(parser.roleFilter())
        for r in roles: 
            r.users_list = r.users.filter(parser.userFilter()).order_by('acct_name').distinct()

        context['role_list'] = roles
        return context
        
class UserRoleView(ListView):
    model = User
    template_name = 'user_role.html'

    def get_queryset(self):
        parser = UserRoleView.query = QueryParser(self)
        object_list = User.objects.filter(parser.userFilter()).order_by('acct_name').distinct()
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super(UserRoleView,self).get_context_data(**kwargs)
        parser = UserRoleView.query
        parser.permission2role()
        users = User.objects.filter(parser.userFilter()).filter(parser.userRoleFilter())
        for u in users: 
            u.roles = Role.objects.filter(users__acct_name=u.acct_name).filter(parser.roleFilter()) 
        context['user_list'] = users
        return context
    

class UserPermissionView(ListView):
    model = User
    template_name = 'user_permission.html'

    def get_queryset(self):
        parser = UserPermissionView.query = QueryParser(self)
        object_list = User.objects.filter(parser.userFilter()).order_by('acct_name').distinct()
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super(UserPermissionView,self).get_context_data(**kwargs)
        parser = UserPermissionView.query
        parser.permission2role()
        users = User.objects.filter( parser.userFilter() ).filter(parser.userRoleFilter() )
        for u in users: 
            u.perms = set()
            for r in Role.objects.filter(users__acct_name=u.acct_name): 
                u.perms.update( r.permissions.filter(parser.permissionFilter()))
        context['user_list'] = users
        return context
        

class PermissionUserView(ListView):
    model = User
    template_name = 'permission_user.html'

    def get_queryset(self):
        parser = PermissionUserView.query = QueryParser(self)
        object_list = User.objects.filter(parser.userFilter()).order_by('acct_name').distinct()
        return object_list
    
    def get_context_data(self, **kwargs):
        parser = PermissionUserView.query
        context = super(PermissionUserView,self).get_context_data(**kwargs)
        perms = Permission.objects.filter(parser.permissionFilter())
        rm = Q()
        for p in perms: 
            p.users = set()
            for r in Role.objects.filter(parser.roleFilter()).filter(permissions__permission_name=p.permission_name):
                p.users.update(r.users.filter(parser.userFilter()))
            if parser.isActive and not len(p.users): 
                rm = rm | Q(id=p.id)
        perms = Permission.objects.exclude(rm).filter(parser.permissionFilter())
        for p in perms: 
            p.users = set()
            for r in Role.objects.filter(parser.roleFilter()).filter(permissions__permission_name=p.permission_name):
                p.users.update(r.users.filter(parser.userFilter()))
        
        context['permission_list'] = perms
        return context

class PermissionRoleView(ListView):
    model = User
    template_name = 'permission_role.html'
    
    def get_queryset(self):
        parser = PermissionRoleView.query = QueryParser(self)
        object_list = User.objects.filter(parser.userFilter()).order_by('acct_name').distinct()
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super(PermissionRoleView,self).get_context_data(**kwargs)
        parser = PermissionRoleView.query
        perms = Permission.objects.filter(parser.permissionFilter())
        rm = Q()
        for p in perms: 
            p.roles = Role.objects.filter(parser.roleFilter()).filter(permissions__permission_name=p.permission_name)
            if parser.isActive and not p.roles: 
                rm = rm | Q(id=p.id) 
        perms = Permission.objects.exclude(rm).filter(parser.permissionFilter())
        for p in perms: 
            p.roles = Role.objects.filter(parser.roleFilter()).filter(permissions__permission_name=p.permission_name)
        context['permission_list'] = perms
        return context
        
class RolePermissionView(ListView):
    model = User
    template_name = 'role_permission.html'

    def get_queryset(self):
        parser = RolePermissionView.query = QueryParser(self)
        object_list = User.objects.filter(parser.userFilter()).order_by('acct_name').distinct()
        return object_list
    

    def get_context_data(self, **kwargs):
        context = super(RolePermissionView,self).get_context_data(**kwargs)
        parser = RolePermissionView.query
        roles = Role.objects.filter(parser.roleFilter())
        rm = Q()
        for r in roles: 
            r.permissions_list = [ p.permission_name for p in r.permissions.filter(parser.permissionFilter()) ]
            if parser.isActive and not len(r.permissions_list): 
                rm = rm | Q(id=r.id) 

        roles = Role.objects.exclude(rm).filter(parser.roleFilter())
        for r in roles: 
            r.permissions_list = [ p.permission_name for p in r.permissions.filter(parser.permissionFilter()) ]
        context['role_list'] = roles
        return context
        

