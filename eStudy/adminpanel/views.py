# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.apps import apps
from courses.models import *
from django.forms import modelform_factory
from django.contrib.auth.models import User  # Default User model

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



def home(request):
    # Get the default User model
    user_model_info = {
        'name': User.__name__,
        'app_label': User._meta.app_label,
        'verbose_name': User._meta.verbose_name_plural,
    }

    # Get all models from your custom apps
    custom_models_info = []
    for app_config in apps.get_app_configs():
        # Exclude Django's built-in apps (e.g., admin, auth, sessions)
        if not app_config.name.startswith('django.') and app_config.name != 'adminpanel':
            for model in app_config.get_models():
                custom_models_info.append({
                    'name': model.__name__,
                    'app_label': model._meta.app_label,
                    'verbose_name': model._meta.verbose_name_plural,
                })

    # Combine the User model and custom app models
    models = [user_model_info] + custom_models_info

    return render(request, 'adminpanel/home.html', {'models': models})