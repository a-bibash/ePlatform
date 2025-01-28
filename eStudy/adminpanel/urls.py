from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='adminpanel_home'),  # Home page

    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/update/<int:pk>/', views.user_update, name='user_update'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),
    
    path('models/<str:app_label>/<str:model_name>/', views.model_list, name='model_list'),
    path('models/<str:app_label>/<str:model_name>/create/', views.model_create, name='model_create'),
    path('models/<str:app_label>/<str:model_name>/update/<int:pk>/', views.model_update, name='model_update'),
    path('models/<str:app_label>/<str:model_name>/delete/<int:pk>/', views.model_delete, name='model_delete'),
]