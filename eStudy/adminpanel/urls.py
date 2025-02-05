from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='adminpanel_home'),  # Home page

    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_create'),
    path('users/update/<int:pk>/', user_update, name='user_update'),
    path('users/delete/<int:pk>/', user_delete, name='user_delete'),
    
    path('models/<str:app_label>/<str:model_name>/', model_list, name='model_list'),
    path('models/<str:app_label>/<str:model_name>/create/', model_create, name='model_create'),
    path('models/<str:app_label>/<str:model_name>/update/<int:pk>/', model_update, name='model_update'),
    path('models/<str:app_label>/<str:model_name>/delete/<int:pk>/', model_delete, name='model_delete'),

    path('stats_dashboard/', stats_dashboard_view, name='stats_dashboard'),

    path('stats/users/', user_stats_detail, name='user_stats_detail'),
    path('stats/users/export/', export_users_excel, name='export_users_excel'),

    path('stats/courses/', course_stats_detail, name='course_stats_detail'),
    path('stats/courses/<str:course_title>/enrollments/', course_enrollment_details, name='course_enrollment_details'),
    path('stats/courses/<str:course_title>/export/', export_course_users_excel, name='export_course_users_excel'),
    
    path('upload-video/', upload_video_view, name='upload_video'),
]




    
