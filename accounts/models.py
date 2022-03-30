from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from uuid import uuid4

from records.models import Department
class UserProfile(models.Model):
    """Profile of a unique user."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    last_ping = models.DateTimeField(default=now)

    # Linked Django User object
    user = models.OneToOneField(
        User, related_name='profile', on_delete=models.CASCADE, null=True, blank=True)

    # Basic info from SSO
    name = models.CharField(max_length=50, blank=True)
    roll_no = models.CharField(max_length=30, null=True, blank=True)
    ldap_id = models.CharField(max_length=50, null=True, blank=True)
    profile_pic = models.URLField(null=True, blank=True)

    # Advanced info from SSO
    contact_no = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    # department = models.ForeignKey(Department, on_delete=models.CASCADE,)
    degree = models.CharField(max_length=200, null=True, blank=True)
    degree_name = models.CharField(max_length=200, null=True, blank=True)
    join_year = models.CharField(max_length=5, null=True, blank=True)
    graduation_year = models.CharField(max_length=5, null=True, blank=True)
    hostel = models.CharField(max_length=100, null=True, blank=True)
    room = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_requirement_list(self):
        return self.requirements.all()
class AdminProfile(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    department=models.OneToOneField(Department,on_delete=models.DO_NOTHING) 
    def __str__(self):
        return self.department.name   
