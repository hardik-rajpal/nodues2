from django.utils import timezone
from django.db import models
class Department(models.Model):
    name=models.CharField(max_length=100,blank=False,null=False)
    email=models.CharField(max_length=200,blank=False,null=False)
    def __str__(self):
        return self.name
class Requirement(models.Model):
    # title = models.CharField(max_length=50)
    balance = models.IntegerField(default=0)
    # status = models.CharField(max_length=50)
    department = models.ForeignKey(Department,max_length=50,on_delete=models.CASCADE)
    comment = models.TextField(max_length=500,default='None')
    time_posted = models.DateTimeField(default=timezone.now)
    # user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name = "requirements")
    roll_number = models.CharField(max_length=11,blank=False,null=False)
class Queries(models.Model):
    title = models.CharField(max_length=50)
    document_id = models.CharField(max_length=50)
    status_check = models.BooleanField(default=False)
    time_posted = models.DateTimeField()
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
