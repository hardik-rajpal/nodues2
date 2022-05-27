import json
from turtle import up
from django.core.paginator import Paginator
from django.http import FileResponse, HttpRequest
from django.contrib.sessions.models import Session
from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from accounts.serializer import UserProfileFullSerializer
from django.utils import timezone
from accounts.models import UserProfile
from accounts.models import AdminProfile
from accounts.helpers import userFromRequestByCookies
from records.models import Balance
from records.models import Queries
from records.serializer import QuerySerializer
from records.models import Department
from records.models import Requirement
from records.serializer import RequirementSerializer
import hashlib


class RequirementViewSet(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = ()

    def clearBalance(viewset, request: HttpRequest):
        #should be called with balance id now.
        userobj = userFromRequestByCookies(request)
        try:
            upro = UserProfile.objects.get(user=userobj)
        except:
            return Response({'message': 'User profile does not exist.'},
                            status=403)
        upro: UserProfile
        adminpros = AdminProfile.objects.filter(user=upro)
        if (adminpros.__len__() == 0):
            return Response({'message': 'Admin Profile does not exist.'},
                            status=403)
        balanceID = request.GET.get('reqID')
        balance = None
        try:
            balance = Balance.objects.get(id=balanceID)
        except:
            return Response({'detail': 'Requirement with given id not found.'})
        balance: Balance
        balance.amount = 0
        t_temp = timezone.now()
        balance.comment += f"; Cleared at {' '.join(t_temp.isoformat().split('.')[0].split('T'))} by {upro.roll_no}"
        balance.save()
        return Response({}, status=200)

    def get_requirements(viewset, request: HttpRequest):
        """Get requirements."""
        userobj = userFromRequestByCookies(request)
        try:
            queryset = UserProfileFullSerializer.setup_eager_loading(
                UserProfile.objects)
            user_profile = queryset.get(user=userobj)
        except UserProfile.DoesNotExist:
            return Response({'message': "UserProfile doesn't exist"},
                            status=500)
        # print('hi')
        roll_no = user_profile.roll_no
        adminAccountList = AdminProfile.objects.filter(user=user_profile)

        user_profile.last_ping = timezone.now()
        user_profile.save(update_fields=['last_ping'])

        reqs = None
        if (len(adminAccountList) > 0):
            reqs = Requirement.objects.filter(
                department=adminAccountList[0].department)
        else:
            reqs = Requirement.objects.filter(roll_number=roll_no)
        print('hi1')
        if (reqs == None):
            return {'data': [], 'error': 'Neither admin nor recorded student'}

        data = RequirementSerializer(reqs, many=True).data
        resp = Response({'data': data},
                        headers={'Access-Control-Allow-Origin': True})
        print(resp.headers)
        return resp

    def parse_data(datastr: str):
        datastr = datastr.replace('\r', '')
        lines = datastr.split('\n')
        lines = list(filter(lambda x: len(x) != 0, lines))
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
                'index': int(line[1]),
                'amount': int(line[2]),
                'isMonetary': line[3],
                'comment': line[4]
            }
        return data

    def updateRecords(data: dict, department: Department):
        # print(data)
        # return
        # balance = Requirement.objects.get_or_create(roll_)
        for key in data.keys():
            balance, _ = Requirement.objects.get_or_create(
                roll_number=key, department=department)
            balance: Requirement
            balance.time_posted = timezone.now()
            balance = Balance.objects.get_or_create(requirement=balance,
                                                    index=data[key]['index'])
            balance: Balance
            balance.amount = data[key]['amount']
            balance.isMonetary = data[key]['isMonetary'] == '1'
            balance.comment = data[key]['comment']
            balance.save()
            balance.save()

    def post_requirements(viewset, request):
        # UploadFileForm(request.POST)
        # print()
        # print()
        # userid = request.POST['userID']
        userobj = userFromRequestByCookies(request)
        userid = UserProfile.objects.get(user=userobj).roll_no
        department = None
        try:
            user = User.objects.get(username=userid)
            userpro = UserProfile.objects.get(user=user)
            admin = AdminProfile.objects.get(user=userpro)
            department = admin.department
        except Exception as e:
            return Response({'error': str(e) + f' UserID: {userid}'},
                            status=403)
        data = request.FILES['file'].read().decode('utf-8')
        parsedData = RequirementViewSet.parse_data(data)
        RequirementViewSet.updateRecords(parsedData, department)
        return Response({'status': 200})


class QueriesViewSet(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = ()

    def getQueries(viewset, request: HttpRequest):
        logs = ''
        userobj = userFromRequestByCookies(request)
        user_profile = UserProfile.objects.get(user=userobj)
        roll_no = user_profile.roll_no
        responded = request.GET.get('responded') == '1'
        pagenum = request.GET.get('page')
        adminAccountList = AdminProfile.objects.filter(user=user_profile)
        queries = None
        reqs = None
        if (len(adminAccountList) == 0):
            reqs = Requirement.objects.filter(roll_number=roll_no)
        else:
            reqs = Requirement.objects.filter(
                department=adminAccountList[0].department)
            # queries = Queries.objects.filter(requirement__in=reqs)
        if not responded:
            queries = Queries.objects.filter(requirement__in=reqs,
                                             status_check=None)
        else:
            queries = Queries.objects.filter(requirement__in=reqs,
                                             status_check__in=[True, False])

        queries = QuerySerializer(queries, many=True).data
        paginator = Paginator(queries, 2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(pagenum)
        return Response({
            'rn':
            roll_no,
            'rir':
            responded,
            'rawqs':
            queries,
            'reqs':
            RequirementSerializer(reqs, many=True).data,
            'data':
            page_obj.object_list,
            'count':
            paginator.num_pages,
            'next':
            page_obj.next_page_number() if page_obj.has_next() else None,
            'prev':
            page_obj.previous_page_number()
            if page_obj.has_previous() else None
        })

    def upload_file_queries(viewset, request):
        try:
            file_received = request.FILES['file']
            ext = file_received.name.split('.')[-1]

            def handle_uploaded_file(f, ext):
                md5_hash = hashlib.md5()
                # Read and update hash in chunks of 4K
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
                # print(md5_hash.hexdigest())
                hash_val = md5_hash.hexdigest()
                import os
                print(os.getcwd())
                destination = open('./records/storage/' + hash_val + '.' + ext,
                                   'bw+')
                for chunk in f.chunks():
                    destination.write(chunk)
                return hash_val

            MD5_hash = handle_uploaded_file(file_received, ext)
            return Response({'docID': MD5_hash + '.' + ext})
        except:
            return Response({'error': 'failed to upload file'})

    def get_uploaded_file(viewset, request: HttpRequest, pk):
        import os
        if os.path.exists('./records/storage/' + pk):
            file = open('./records/storage/' + pk, 'rb')
            return FileResponse(file)
        else:
            return Response({'message': 'file not found'})

    def postQueryByStudent(viewset, request):
        data = json.loads(request.body.decode())
        #TODO:Check auth permissions
        balance = None
        print(data)
        try:
            balance = Requirement.objects.get(id=data['reqID'])
        except:
            return Response({'error': 'Requirement not found'}, 500)
        Queries.objects.create(requirement=balance,
                               comment=data['comment'],
                               document_id=data['docID'],
                               time_posted=timezone.now())
        return Response({}, 200)

    def respondToQuery(viewset, request):
        data = json.loads(request.body.decode())
        data['response']
        data['queryID']
        print(data)
        userobj = userFromRequestByCookies(request)
        roll_no = UserProfile.objects.get(user=userobj).roll_no
        try:
            queryset = UserProfileFullSerializer.setup_eager_loading(
                UserProfile.objects)
            user_profile = queryset.get(roll_no=roll_no)
        except UserProfile.DoesNotExist:
            return Response({'message': "UserProfile doesn't exist"},
                            status=500)
        roll_no = user_profile.roll_no
        adminAccountList = AdminProfile.objects.filter(user=user_profile)
        if (len(adminAccountList) == 0):
            return Response({'error': 'No admin account found'}, status=401)
        q = Queries.objects.get(id=data['queryID'])
        q.response = data['response']
        q.status_check = data['accepted']
        q.save()
        return Response({}, status=200)
