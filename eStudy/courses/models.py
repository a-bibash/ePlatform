from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Count

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings 

class User(AbstractUser):
    """Custom User model replacing Django's default User"""
    email = models.EmailField(unique=True, db_index=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",  # Avoids conflict with default User model
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",  # Avoids conflict
        blank=True
    )

    def __str__(self):
        return self.username


class Course(models.Model):
    """Course model representing different courses"""
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def video_count(self):
        """Returns the count of videos in this course"""
        return self.videos.count()

    def enrolled_users_count(self):
        """Returns the count of users enrolled in this course"""
        return self.enrollments.count()

    def __str__(self):
        return self.title


class Video(models.Model):
    """Video model linked to a Course"""
    course = models.ForeignKey(
        Course, related_name='videos', on_delete=models.CASCADE, db_index=True
    )
    title = models.CharField(max_length=255, db_index=True)
    s3_file_key = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    playtime = models.PositiveIntegerField(help_text="Duration in minutes")

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """Tracks which users are enrolled in which courses"""
    user = models.ForeignKey(
        User, related_name='enrollments', on_delete=models.CASCADE, db_index=True
    )
    course = models.ForeignKey(
        Course, related_name='enrollments', on_delete=models.CASCADE, db_index=True
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')  
        indexes = [
            models.Index(fields=['user', 'course']), 
        ]

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class UserVideoAccess(models.Model):
    """Tracks user access to videos"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, db_index=True
    )
    access_count = models.PositiveIntegerField(default=2)
    playtime_left = models.PositiveIntegerField(help_text="User-specific playtime")

    class Meta:
        unique_together = ('user', 'video')
        indexes = [
            models.Index(fields=['user', 'video']), 
        ]

    def save(self, *args, **kwargs):
        if not self.pk and self.video:
            self.playtime_left = int(self.video.playtime * 1.5)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.username} - {self.video.title} ({self.playtime_left} mins left)"

