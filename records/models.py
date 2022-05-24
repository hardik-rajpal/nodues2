from turtle import ondrag
from django.utils import timezone
from django.db import models
class Department(models.Model):
    name=models.CharField(max_length=100,blank=False,null=False)
    email=models.CharField(max_length=200,blank=False,null=False)
    def __str__(self):
        return self.name
class Requirement(models.Model):
    department = models.ForeignKey(Department,max_length=50,on_delete=models.CASCADE)
    comment = models.TextField(max_length=500,default='None')
    time_posted = models.DateTimeField(default=timezone.now)
    roll_number = models.CharField(max_length=11,blank=False,null=False)
    def __str__(self):
        return self.department.name+':'+self.roll_number
class Queries(models.Model):
    title = models.CharField(max_length=50,blank=True)
    comment = models.TextField(max_length=500)
    document_id = models.CharField(max_length=50,blank=True)
    status_check = models.BooleanField(default=None,null=True)
    time_posted = models.DateTimeField()
    response = models.TextField(max_length=500,default='')
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.requirement)+'->'+self.comment[:min(len(self.comment),20)]
class Balance(models.Model):
    requirement = models.ForeignKey(Requirement,on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    isMonetary = models.BooleanField(default=True)
    comment = models.TextField(max_length=500,default='None')
    def __str__(self):
        return str(self.requirement)+self.comment[:20]