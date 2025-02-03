# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.apps import apps
from courses.models import *
from django.forms import modelform_factory
# from django.contrib.auth.models import User  # Default User model
from django.contrib.auth import get_user_model
User = get_user_model()  # Defined once at the top

def user_list(request):
    users = User.objects.all()
    return render(request, 'adminpanel/user_list.html', {'users': users})

def user_create(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'User created successfully.')
        return redirect('user_list')
    return render(request, 'adminpanel/user_form.html')

def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        if request.POST['password']:
            user.set_password(request.POST['password'])
        user.save()
        messages.success(request, 'User updated successfully.')
        return redirect('user_list')
    return render(request, 'adminpanel/user_form.html', {'user': user})

def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('user_list')



def model_list(request, app_label, model_name):
    # Get the model dynamically
    if app_label == 'auth' and model_name == 'user':
        model = User  # Default User model
    else:
        model = apps.get_model(app_label=app_label, model_name=model_name)

    objects = model.objects.all()
    return render(request, 'adminpanel/model_list.html', {
        'objects': objects,
        'model_name': model_name,
        'app_label': app_label,
    })




def model_create(request, app_label, model_name):
    # Get the model using the provided app_label and model_name
    model = apps.get_model(app_label=app_label, model_name=model_name)
    
    # Dynamically create a ModelForm for the model
    ModelForm = modelform_factory(model, fields='__all__')
    
    if request.method == 'POST':
        # Create a new object with the submitted data
        form = ModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model_name} created successfully.')
            return redirect('model_list', app_label=app_label, model_name=model_name)
    else:
        # Display an empty form for creating a new object
        form = ModelForm()
    
    return render(request, 'adminpanel/model_form.html', {'form': form, 'model_name': model_name})






def model_update(request, app_label, model_name, pk):
    # Get the model using the provided app_label and model_name
    model = apps.get_model(app_label=app_label, model_name=model_name)
    
    # Retrieve the object to be updated
    obj = get_object_or_404(model, pk=pk)
    
    # Dynamically create a ModelForm for the model
    ModelForm = modelform_factory(model, fields='__all__')
    
    if request.method == 'POST':
        # Update the object with the submitted data
        form = ModelForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model_name} updated successfully.')
            return redirect('model_list', app_label=app_label, model_name=model_name)
    else:
        # Display the form with the current object data
        form = ModelForm(instance=obj)
    
    return render(request, 'adminpanel/model_form.html', {'form': form, 'model_name': model_name})





def model_delete(request, app_label, model_name, pk):
    # Get the model using the provided app_label and model_name
    model = apps.get_model(app_label=app_label, model_name=model_name)
    
    # Retrieve the object to be deleted
    obj = get_object_or_404(model, pk=pk)
    
    # Delete the object
    obj.delete()
    messages.success(request, f'{model_name} deleted successfully.')
    
    # Redirect to the model list view
    return redirect('model_list', app_label=app_label, model_name=model_name)



from django.apps import apps
from django.contrib.auth import get_user_model
from django.shortcuts import render

def home(request):
    User = get_user_model()  # Get the currently used User model

    # Store User model info separately to ensure it appears only once
    user_model_info = {
        'name': User.__name__,
        'app_label': User._meta.app_label,
        'verbose_name': User._meta.verbose_name_plural,
    }

    # Get all models from your custom apps, excluding duplicates of User
    custom_models_info = []
    for app_config in apps.get_app_configs():
        if not app_config.name.startswith('django.') and app_config.name != 'adminpanel':
            for model in app_config.get_models():
                if model.__name__.lower() != "user":  # Ensure we don't add 'User' twice
                    custom_models_info.append({
                        'name': model.__name__,
                        'app_label': model._meta.app_label,
                        'verbose_name': model._meta.verbose_name_plural,
                    })

    # Combine User model and other models
    models = [user_model_info] + custom_models_info

    return render(request, 'adminpanel/home.html', {'models': models})














from django.shortcuts import render
from django.utils.timezone import now, timedelta
from django.contrib.auth import get_user_model
from courses.models import Enrollment, Course

User = get_user_model()

def stats_dashboard_view(request):
    # User Statistics
    total_users = User.objects.count()
    new_users = User.objects.filter(date_joined__gte=now() - timedelta(days=30)).count()
    users_enrolled = Enrollment.objects.values("user").distinct().count()
    users_not_enrolled = total_users - users_enrolled
    active_users = User.objects.filter(is_active=True).count()

    # Course Statistics
    total_courses = Course.objects.count()
    most_enrolled_course = (
        Course.objects.annotate(enrollment_count=models.Count("enrollments"))
        .order_by("-enrollment_count")
        .first()
    )
    avg_enrollments = (
        Enrollment.objects.count() / total_courses if total_courses > 0 else 0
    )

    context = {
        "total_users": total_users,
        "new_users": new_users,
        "users_enrolled": users_enrolled,
        "users_not_enrolled": users_not_enrolled,
        "active_users": active_users,
        "total_courses": total_courses,
        "most_enrolled_course": most_enrolled_course.title if most_enrolled_course else "N/A",
        "avg_enrollments": round(avg_enrollments, 2),
    }
    return render(request, "stats/stats_dashboard.html", context)




from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()

# User Stats Detailed View
def user_stats_detail(request):
    users = User.objects.values("first_name", "last_name", "email", "date_joined",'username')
    context = {
        "users": users
    }
    return render(request, "stats/user_stats_details.html", context)








import pandas as pd
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils.timezone import make_naive

User = get_user_model()

def export_users_excel(request):
    # Exclude sensitive fields if needed
    excluded_fields = ['password', 'last_login','is_superuser','is_staff']
    model_fields = [field.name for field in User._meta.fields if field.name not in excluded_fields]

    # Fetch user data dynamically
    users = list(User.objects.values(*model_fields))

    # Convert timezone-aware datetime fields
    for user in users:
        for field, value in user.items():
            if isinstance(value, (pd.Timestamp,)):
                user[field] = value.tz_localize(None)  # Remove timezone
            elif hasattr(value, 'tzinfo'):  # Django datetime fields
                user[field] = make_naive(value)  # Convert to naive datetime

    # Convert data to DataFrame
    df = pd.DataFrame(users)

    # Format datetime fields properly
    for field in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[field]):  # Auto-detect datetime fields
            df[field] = df[field].dt.strftime('%Y-%m-%d %H:%M')

    # Generate Excel response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="All_users_details.xlsx"'

    df.to_excel(response, index=False, engine='openpyxl')

    return response






from django.shortcuts import render
from courses.models import Course, Enrollment, Video

def course_stats_detail(request):
    course_data = []
    
    # Fetch all courses and calculate required details
    courses = Course.objects.all()
    for course in courses:
        total_enrollments = Enrollment.objects.filter(course=course).count()
        total_videos = Video.objects.filter(course=course).count()
        
        course_data.append({
            "title": course.title,
            "total_enrollments": total_enrollments,
            "total_videos": total_videos,
        })

    return render(request, 'stats/course_stats_details.html', {'courses': course_data})




from django.shortcuts import render, get_object_or_404
from courses.models import Course, Enrollment
from django.contrib.auth import get_user_model

User = get_user_model()

def course_enrollment_details(request, course_title):
    # Get the course object
    course = get_object_or_404(Course, title=course_title)

    # Fetch enrolled users using the Enrollment model
    enrollments = Enrollment.objects.filter(course=course).select_related("user")

    # Extract user details dynamically
    enrolled_users = [
        {
            "username": enrollment.user.username,
            "first_name": enrollment.user.first_name,
            "last_name": enrollment.user.last_name,
            "email": enrollment.user.email,
            "date_joined": enrollment.user.date_joined,
        }
        for enrollment in enrollments
    ]

    context = {
        "course": course,
        "enrolled_users": enrolled_users,
    }
    return render(request, "stats/course_enrollment_details.html", context)






import pandas as pd
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_naive
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment

User = get_user_model()

def export_course_users_excel(request, course_title):
    # Get the course object
    course = get_object_or_404(Course, title=course_title)

    # Fetch enrolled users dynamically
    excluded_fields = ['password', 'last_login', 'is_superuser', 'is_staff']
    user_fields = [field.name for field in User._meta.fields if field.name not in excluded_fields]

    enrollments = Enrollment.objects.select_related("user").filter(course=course)
    users = [ {field: getattr(enrollment.user, field, None) for field in user_fields} for enrollment in enrollments]

    # Convert timezone-aware datetime fields
    for user in users:
        for field, value in user.items():
            if hasattr(value, 'tzinfo'):  # Check if it's a timezone-aware datetime
                user[field] = make_naive(value)  # Convert to naive datetime

    # Convert data to DataFrame
    df = pd.DataFrame(users)

    # Format datetime fields properly
    for field in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[field]):
            df[field] = df[field].dt.strftime('%Y-%m-%d %H:%M')

    # Generate Excel response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Users_enrolled_on_{course.title}.xlsx"'

    df.to_excel(response, index=False, engine='openpyxl')

    return response
