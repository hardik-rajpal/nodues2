from asyncio import QueueEmpty
import json
from django.core.paginator import Paginator
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
from records.models import Queries
from records.serializer import QuerySerializer
from records.models import Department
from records.models import Requirement
from records.serializer import RequirementSerializer

# from django import forms

# class UploadFileForm(forms.Form):
#     title = forms.CharField(max_length=50)
#     file = forms.FileField()
class RequirementViewSet(viewsets.ViewSet):
    def clearBalance(viewset, request):
        reqID = request.GET.get('reqID')
        req=None
        try:
            req = Requirement.objects.get(id=reqID)
        except:
            return Response({'detail':'Requirement with given id not found.'})
        req:Requirement
        req.balance=0;
        req.comment+="; Cleared "+str(timezone.now())+"by (userID)"
        req.save()
        return Response({},status=200)
    def get_requirements(viewset,request:HttpRequest):
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
        resp = Response({'data':data},headers={'Access-Control-Allow-Origin':True})
        print(resp.headers)
        return resp

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
class QueriesViewSet(viewsets.ViewSet):
    def getQueries(viewset,request:HttpRequest):
        print(request.user)
        roll_no = request.GET.get('userID')
        responded = request.GET.get('responded')=='0'
        print(responded)
        pagenum=request.GET.get('page')
        try:
            queryset = UserProfileFullSerializer.setup_eager_loading(UserProfile.objects)
            user_profile = queryset.get(roll_no=roll_no)
        except UserProfile.DoesNotExist:
            return Response({'message': "UserProfile doesn't exist"}, status=500)
        roll_no = user_profile.roll_no
        adminAccountList = AdminProfile.objects.filter(user=user_profile)
        queries = None
        if(len(adminAccountList)==0):
            reqs = Requirement.objects.filter(roll_number=roll_no)
        else:
            reqs = Requirement.objects.filter(department=adminAccountList[0].department)
            # queries = Queries.objects.filter(requirement__in=reqs)
        status = [True,False]
        # print(.__len__())
        queries = Queries.objects.filter(requirement__in=reqs,status_check__in=status)
        if not responded:
            queries=Queries.objects.filter(status_check=None)

        queries = QuerySerializer(queries,many=True).data
        # contact_list = Contact.objects.all()
        paginator = Paginator(queries, 1) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        
        page_obj = paginator.get_page(pagenum)
        return Response({
            'data':page_obj.object_list,
            'count':paginator.num_pages,
            'next':page_obj.next_page_number() if page_obj.has_next() else None,
            'prev':page_obj.previous_page_number() if page_obj.has_previous() else None})
    def postQueryByStudent(viewset,request):
        data = json.loads(request.body.decode())
        #TODO:Check auth permissions
        req = None
        print(data)
        try:
            req = Requirement.objects.get(id=data['reqID'])
        except:
            return Response({'error':'Requirement not found'},500)
        Queries.objects.create(requirement=req,comment=data['comment'],document_id=data['docID'],time_posted=timezone.now())
        return Response({},200)
    def respondToQuery(viewset,request):
        data = json.loads(request.body.decode())
        data['response']
        data['queryID']
        print(data)
        roll_no = data['userID']
        try:
            queryset = UserProfileFullSerializer.setup_eager_loading(UserProfile.objects)
            user_profile = queryset.get(roll_no=roll_no)
        except UserProfile.DoesNotExist:
            return Response({'message': "UserProfile doesn't exist"}, status=500)
        roll_no = user_profile.roll_no
        adminAccountList = AdminProfile.objects.filter(user=user_profile)
        if(len(adminAccountList)==0):
            return Response({'error':'No admin account found'},status=401)
        q = Queries.objects.get(id=data['queryID'])
        q.response = data['response']
        q.status_check = data['accepted']
        q.save()
        return Response({},status=200)