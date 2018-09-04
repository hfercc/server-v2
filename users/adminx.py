import xadmin
from .models import UserProfile

class UserProfileAdmin(object):
    pass

xadmin.site.unregister(UserProfile)
xadmin.site.register(UserProfile, UserProfileAdmin)