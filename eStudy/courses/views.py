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


# Course Views

def home(request):
    courses = Course.objects.all()
    return render(request, 'home/home.html', {'courses': courses})


@login_required
def course_videos(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    # Check if the user is enrolled
    is_enrolled = Enrollment.objects.filter(user=user, course=course).exists()
    
    videos = Video.objects.filter(course=course)
    
    return render(request, 'courses/course_details.html', {
        'course': course,
        'videos': videos,
        'is_enrolled': is_enrolled,
    })



@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user

    # Check if the user is already enrolled
    if Enrollment.objects.filter(user=user, course=course).exists():
        messages.info(request, "You are already enrolled in this course.")
    else:
        Enrollment.objects.create(user=user, course=course)
        messages.success(request, f"You have successfully enrolled in {course.title}!")

    return redirect('course_videos', course_id=course.id)



@login_required
def stream_video(request, video_id):
    # Fetch the video object, or raise a 404 if it doesn't exist
    video = get_object_or_404(Video, id=video_id)
    
    # Track video views (but don't decrement yet)
    access, created = UserVideoAccess.objects.get_or_create(
        user=request.user, 
        video=video,
        defaults={'playtime_left': int(video.playtime * 1.5)} 
    )

    # Check if the user has access to the video
    if access.playtime_left <= 0 or access.access_count <= 0:
        messages.error(request, 'You have no remaining views or playback time for this video.')
        return redirect('course_videos', course_id=video.course.id)


    # Get the video size and calculate the chunk range
    video_size = get_video_size_from_s3(video.s3_file_key)

    if not video_size:
        messages.error(request, "Error: Unable to fetch video size.")
        return redirect('course_videos', course_id=video.course.id)

    # Default to entire video URL if no specific byte range is requested
    range_start = request.GET.get('start', 0)
    range_end = request.GET.get('end', video_size)

    # Get the pre-signed URL for the chunk range
    presigned_url = generate_presigned_url('study-material', video.s3_file_key, range_start, range_end)

    if not presigned_url:
        messages.error(request, "Error: Unable to generate a pre-signed URL for the video.")
        return redirect('course_videos', course_id=video.course.id)

    # Render the template with the video and access context
    context = {
        'video': video,
        'access': access,
        'presigned_url': presigned_url,
        'video_size': video_size,
    }
    
    return render(request, 'courses/stream_video.html', context)





@login_required
@csrf_exempt  # Only use if you’re not sending CSRF tokens from JavaScript
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




@csrf_exempt  # Allow AJAX requests
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

            # Convert watched seconds to minutes (rounding up)
            watched_minutes = -(-watched_seconds // 60)  # Equivalent to math.ceil()

            # Decrease playtime_left but never below zero
            access.playtime_left = max(0, access.playtime_left - watched_minutes)
            access.save()

            return JsonResponse({"success": True, "playtime_left": access.playtime_left})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
















def get_video_size_from_s3(file_key):
    """
    Helper function to get the size of the video from S3
    """
    # Fetch AWS credentials from environment variables
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    CUSTOM_ENDPOINT_URL = os.getenv('CUSTOM_ENDPOINT_URL')
    try:
        # Get the file size from S3 using the head_object API
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=CUSTOM_ENDPOINT_URL
        )
        response = s3_client.head_object(Bucket='study-material', Key=file_key)
        return response['ContentLength']  # Returns size in bytes
    except Exception as e:
        print(f"Error fetching video size: {e}")
        return None



def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.warning(request, "This email is already in use. Please use a different email.")
                return render(request, 'accounts/register.html', {'form': form})

            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data["password1"])  # Hash the password
                user.save()

                messages.success(request, 'Registration successful! Please login.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
                return render(request, 'accounts/register.html', {'form': form})

        else:
            # Show specific field errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})







def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username_or_email, password=password)

            # If authentication fails, check if it's an email
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
    return redirect('home')

@login_required  # Add this decorator
def dashboard(request):
    courses = Course.objects.all()
    return render(request, 'home/dashboard.html', {'courses': courses})





@login_required
def courses_page(request):
    courses = Course.objects.all()  # Fetch all courses from the database
    return render(request, 'courses/courses.html', {'courses': courses})