from django.urls import path
from .views import *

from django.contrib.auth import views as auth_views

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

    path('settings/', user_settings, name='user_settings'),



    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
         name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),

]





