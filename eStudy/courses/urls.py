from django.urls import path
from .views import *



urlpatterns = [
    # Course URLs
    # path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),

    
    path('courses/<int:course_id>/', course_videos, name='course_videos'),
    path('videos/<int:video_id>/stream/', stream_video, name='stream_video'),


    # Authentication URLs
    path('', login_view, name='login'),
    # path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),


    path('videos/<int:video_id>/track_watch/', track_video_watch, name='track_video_watch'),

    path('video/<int:video_id>/update_playtime/', update_playtime, name='update_playtime'),

]





