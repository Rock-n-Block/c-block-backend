from django.contrib import admin
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django_dramatiq.models import Task
from rest_framework.authtoken.models import TokenProxy

from cblock.accounts.models import Profile

class ProfileAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
admin.site.unregister(EmailAddress)
admin.site.unregister(Task)
admin.site.unregister(Site)