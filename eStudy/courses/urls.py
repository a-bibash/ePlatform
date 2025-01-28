from django.urls import path
from .views import *



urlpatterns = [
    # Course URLs
    path('', home, name='home'),
    
    path('dashboard/', dashboard, name='dashboard'),
    path('courses/', courses_page, name='courses_page'),
    
    path('courses/<int:course_id>/', course_videos, name='course_videos'),
    path('videos/<int:video_id>/stream/', stream_video, name='stream_video'),

    # Authentication URLs
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
]