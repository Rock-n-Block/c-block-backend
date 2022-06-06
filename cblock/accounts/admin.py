from django.contrib import admin

from read_only_admin.admin import ReadonlyAdmin
from cblock.accounts.models import Profile

class ProfileAdmin(ReadonlyAdmin):
    pass


admin.site.register(Profile, ProfileAdmin)