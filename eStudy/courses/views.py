from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import FileResponse
from django.contrib.auth.decorators import login_required  # Import the decorator
from .models import Course, Video, UserVideoAccess, User
from .forms import UserRegistrationForm, UserLoginForm

# Course Views

def home(request):
    courses = Course.objects.all()
    return render(request, 'home/home.html', {'courses': courses})

@login_required  # Add this decorator
def course_videos(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    videos = Video.objects.filter(course=course)
    return render(request, 'courses/course_details.html', {
        'course': course,
        'videos': videos
    })






from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Video, UserVideoAccess

@login_required
def stream_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    # Track video views
    access, created = UserVideoAccess.objects.get_or_create(
        user=request.user, 
        video=video
    )
    
    # Check if the user has access to the video
    if access.access_count <= 0:
        messages.error(request, 'You have no remaining views for this video')
        return redirect('course_videos', course_id=video.course.id)
    
    # Decrement the access count only after the video is successfully loaded
    access.access_count -= 1
    access.save()
    
    # Render the template with the video and access context
    context = {
        'video': video,
        'access': access,
    }
    
    return render(request, 'courses/stream_video.html', context)

# Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")

            if User.objects.filter(email=email).exists():
                messages.warning(request, "This email is already in use. Please use a different email.")
                return render(request, 'accounts/register.html', {'form': form})

            try:
                user = form.save()
                messages.success(request, 'Registration successful! Please login.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
                return render(request, 'accounts/register.html', {'form': form})

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            return render(request, 'accounts/register.html', {'form': form})

    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            
            user = authenticate(
                request,
                username=username_or_email,
                password=password
            )
            
            if user is None and '@' in username_or_email:
                try:
                    user = User.objects.get(email=username_or_email)
                    user = authenticate(
                        request,
                        username=user.username,
                        password=password
                    )
                except User.DoesNotExist:
                    pass

            if user is not None:
                login(request, user)
                if user.is_superuser:
                        return redirect('adminpanel_home')
                return redirect('dashboard')
                
        
        messages.error(request, 'Invalid credentials')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})





def logout_view(request):
    logout(request)
    return redirect('home')

@login_required  # Add this decorator
def dashboard(request):
    courses = Course.objects.all()
    return render(request, 'home/dashboard.html', {'courses': courses})



from django.shortcuts import render
from .models import Course

@login_required
def courses_page(request):
    courses = Course.objects.all()  # Fetch all courses from the database
    return render(request, 'courses/courses.html', {'courses': courses})