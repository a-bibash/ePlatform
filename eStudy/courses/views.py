from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.http import FileResponse
from .models import *

from django.contrib.auth import get_user_model

from django.shortcuts import render, redirect

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from .utils import generate_presigned_url
import boto3
import os
from dotenv import load_dotenv
from .forms import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


load_dotenv()
User = get_user_model() 

BUCKET_NAME = os.getenv('BUCKET_NAME')


def home(request):
    courses = Course.objects.all()
    return render(request, 'home/home.html', {'courses': courses})


@login_required
def course_videos(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    is_enrolled = Enrollment.objects.filter(user=user, course=course).exists()
    
    videos = Video.objects.filter(course=course)
    
    return render(request, 'courses/course_details.html', {
        'course': course,
        'videos': videos,
        'is_enrolled': is_enrolled,
    })



@login_required
def stream_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    course = video.course  

    access, _ = UserVideoAccess.objects.get_or_create(
        user=request.user, 
        video=video,
        defaults={'playtime_left': int(video.playtime * 1.5)} 
    )

    if access.playtime_left <= 0 or access.access_count <= 0:
        messages.error(request, 'You have no remaining views or playback time for this video. Please contact admin.')
        return redirect('course_videos', course_id=course.id)

    presigned_url = generate_presigned_url(BUCKET_NAME, video.s3_file_key)
    if not presigned_url:
        messages.error(request, "Unable to generate a pre-signed URL for the video.")
        return redirect('course_videos', course_id=course.id)

    return render(request, 'courses/stream_video.html', {
        'video': video,
        'access': access,
        'presigned_url': presigned_url,
        'course': course,
    })



@login_required
@csrf_exempt
def track_video_watch(request, video_id):
    """Decrements the access count when the user starts watching."""
    video = get_object_or_404(Video, id=video_id)
    access = UserVideoAccess.objects.filter(user=request.user, video=video).first()

    if not access:
        return JsonResponse({'error': 'Access not found'}, status=404)

    if access.access_count > 0:
        access.access_count -= 1
        access.save()
        return JsonResponse({'message': 'View count updated', 'remaining_views': access.access_count})
    
    return JsonResponse({'error': 'No remaining views'}, status=403)




@csrf_exempt
@login_required
def update_playtime(request, video_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            watched_seconds = int(data.get("watched_seconds", 0))  

            video = get_object_or_404(Video, id=video_id)
            access, created = UserVideoAccess.objects.get_or_create(
                user=request.user, 
                video=video,
                defaults={'playtime_left': video.playtime}
            )

            watched_minutes = -(-watched_seconds // 60)  
            access.playtime_left = max(0, access.playtime_left - watched_minutes)
            access.save()

            return JsonResponse({"success": True, "playtime_left": access.playtime_left})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)



def get_video_size_from_s3(file_key):

    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    CUSTOM_ENDPOINT_URL = os.getenv('CUSTOM_ENDPOINT_URL')
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=CUSTOM_ENDPOINT_URL
        )
        response = s3_client.head_object(Bucket=BUCKET_NAME, Key=file_key)
        return response['ContentLength'] 
    except Exception as e:
        print(f"Error fetching video size: {e}")
        return None



# def register_view(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get("email")

#             if User.objects.filter(email=email).exists():
#                 messages.warning(request, "This email is already in use. Please use a different email.")
#                 return render(request, 'accounts/register.html', {'form': form})

#             try:
#                 user = form.save(commit=False)
#                 user.set_password(form.cleaned_data["password1"])  # Hash the password
#                 user.save()

#                 messages.success(request, 'Registration successful! Please login.')
#                 return redirect('login')

#             except Exception as e:
#                 messages.error(request, f"An unexpected error occurred: {str(e)}")
#                 return render(request, 'accounts/register.html', {'form': form})

#         else:
#             # Show specific field errors
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"{field.capitalize()}: {error}")

#     else:
#         form = RegistrationForm()

#     return render(request, 'accounts/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username_or_email, password=password)
            if user is None and '@' in username_or_email:
                try:
                    user = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('adminpanel_home')
                return redirect('dashboard')

        messages.error(request, "Invalid details. Please check your credentials.")

    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required  
def dashboard(request):
    enrolled_courses = Course.objects.filter(enrollments__user=request.user)
    return render(request, 'home/dashboard.html', {'courses': enrolled_courses})





@login_required
def user_settings(request):
    user = request.user  
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }
    return render(request, 'courses/settings.html', context)
