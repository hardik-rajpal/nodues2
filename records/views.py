from django.http import HttpRequest
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from setuptools import Require
from django.contrib.auth.models import User
from accounts.serializer import UserProfileFullSerializer
from django.utils import timezone
from accounts.models import UserProfile
from accounts.models import AdminProfile
from records.models import Department
from records.models import Requirement
from records.serializer import RequirementSerializer
# from django import forms

# class UploadFileForm(forms.Form):
#     title = forms.CharField(max_length=50)
#     file = forms.FileField()
class RequirementViewSet(viewsets.ViewSet):
    
    
    def get_requirements(viewset,request):
        """Get requirements."""
        print(request.user)
        roll_no = request.GET.get('userID')
        # print(roll_no,type(roll_no))
        # return Response({})
        # Check if the user is authenticated
        #TODO:USer Auth with angular & rest in between
        # if not request.user.is_authenticated:
        #     return Response({"message": "not logged in"}, status=401)

        # Check if the user has a profile
        try:
            queryset = UserProfileFullSerializer.setup_eager_loading(UserProfile.objects)
            user_profile = queryset.get(roll_no=roll_no)
        except UserProfile.DoesNotExist:
            return Response({'message': "UserProfile doesn't exist"}, status=500)
        print('hi')
        roll_no = user_profile.roll_no
        adminAccountList = AdminProfile.objects.filter(user=user_profile)
        
        user_profile.last_ping = timezone.now()
        user_profile.save(update_fields=['last_ping'])
        
        reqs = None
        if(len(adminAccountList)>0):
            reqs = Requirement.objects.filter(department=adminAccountList[0].department)    
        else:
            reqs = Requirement.objects.filter(roll_number=roll_no)
        print('hi1')
        if(reqs==None):
            return {'data':[],'error':'Neither admin nor recorded student'}
        
        data = RequirementSerializer(reqs,many=True).data
        return Response({'data':data})

    def parse_data(datastr:str):
        datastr = datastr.replace('\r','')
        lines = datastr.split('\n')
        lines = list(filter(lambda x:len(x)!=0,lines))
        lines = [line.split(',') for line in lines]
        data = {}
        try:
            int(lines[0][2])
            #throws error if title row is present
        except:
            #remove title row.
            lines.pop(0)
        for line in lines:
            data[line[0]] = {
                'balance':int(line[1]) ,
                'comment':line[2]
                }

        return data
    def updateRecords(data:dict,department:Department):
        print(data)
        # return
        for key in data.keys():
            req,_ = Requirement.objects.get_or_create(roll_number=key,department=department)
            req:Requirement
            req.balance = data[key]['balance']
            req.comment = data[key]['comment']
            req.time_posted = timezone.now()
            print(req.time_posted)
            print(req)
            req.save()
    def post_requirements(viewset,request):
        # UploadFileForm(request.POST)
        # print()
        # print()
        userid = request.POST['userID']
        department = None
        try:
            user = User.objects.get(username=userid)
            userpro = UserProfile.objects.get(user=user)
            admin = AdminProfile.objects.get(user=userpro)
            department = admin.department
        except:
            return {'error':'User does not exist'}
        data = request.FILES['file'].read().decode('utf-8')
        parsedData = RequirementViewSet.parse_data(data)
        RequirementViewSet.updateRecords(parsedData,department)
        return Response({'status':200})
