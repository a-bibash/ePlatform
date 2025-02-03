from django.contrib import admin
from .models import Course, Video, UserVideoAccess,User,Enrollment
# Register your models here.



admin.site.register(Course)
admin.site.register(Video)
admin.site.register(UserVideoAccess)
admin.site.register(User)

admin.site.register(Enrollment)