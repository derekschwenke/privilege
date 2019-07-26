from django.conf.urls import url

from . import views
from .views import IndexView, SearchView, CheckView, ResultsView, DetailView, RoleUserView, UserRoleView, UserPermissionView, PermissionUserView, PermissionRoleView, RolePermissionView

urlpatterns = [
	url(r'results/', ResultsView.as_view(), name='results'),
	url(r'search/', SearchView.as_view(), name='search'),
	url(r'check/', CheckView.as_view(), name='check'),
    #url(r'detail/(?P<pk>[a-zA-Z0-9]*)/$', DetailView.as_view(), name='detail'),
    url(r'detail/(?P<pk>[0-9]*)/$', DetailView.as_view(), name='detail'),
	url(r'^$', IndexView.as_view(), name='index'),
	
	url(r'role_user/', RoleUserView.as_view(), name='role_user'),
	url(r'user_role/', UserRoleView.as_view(), name='user_role'),
	url(r'role_permission/', RolePermissionView.as_view(), name='role_permission'),
	url(r'permission_role/', PermissionRoleView.as_view(), name='permission_role'),
	url(r'user_permission/', UserPermissionView.as_view(), name='user_permission'),
	url(r'permission_user/', PermissionUserView.as_view(), name='permission_user'),	
]
