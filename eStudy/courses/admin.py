from django.contrib import admin
from .models import Course, Video, UserVideoAccess
# Register your models here.



admin.site.register(Course)
admin.site.register(Video)
admin.site.register(UserVideoAccess)