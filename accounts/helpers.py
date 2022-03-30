"""Helpers for login functions."""
import json
import requests
from django.conf import settings
from rest_framework.response import Response
from accounts.models import UserProfile
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import login
from accounts.serializer import UserProfileFullSerializer
from accounts.models import AdminProfile

def user_serializer(data):
    user = User()
    user.first_name = data['first_name']
    user.last_name = data['first_name']
    user.username = data['username']
    user.roll_no = data['roll_number']
    return user



def perform_login(auth_code, redir, request):
    """Perform login with code and redir."""

    post_data = 'code=' + auth_code + '&redirect_uri=' + redir + '&grant_type=authorization_code'
    print(post_data)
    # Get our access token
    response = requests.post(
        settings.SSO_TOKEN_URL,
        data=post_data,
        headers={
            "Authorization": "Basic " + settings.SSO_CLIENT_ID_SECRET_BASE64,
            "Content-Type": "application/x-www-form-urlencoded"
        }, verify=not settings.SSO_BAD_CERT)
    response_json = response.json()

    # Check that we have the access token
    if 'access_token' not in response_json:
        return Response(response_json, status=400)

    # Get the user's profile
    profile_response = requests.get(
        settings.SSO_PROFILE_URL,
        headers={
            "Authorization": "Bearer " + response_json['access_token'],
        }, verify=not settings.SSO_BAD_CERT)
    profile_json = profile_response.json()

    # Check if we got at least the user's SSO id
    if 'id' not in profile_json:
        return Response(profile_response, status=400)

    # Check that we have basic details like name and roll no.
    required_fields = ['first_name', 'roll_number', 'username']
    if not all([((field in profile_json) and profile_json[field]) for field in required_fields]):
        return Response({'message': 'All required fields not present'}, status=403)
    # print(profile_json)
    """
    {
        'id': 22681,
        'program': {
            'id': 20071,
            'department_name': 'Computer Science & Engineering',
            'degree_name': 'Bachelor of Technology',
            'department': 'CSE',
            'join_year': 2020,
            'graduation_year': 2024,
            'degree': 'BTECH'
            },
        'secondary_emails': [{'id': 9358, 'email': 'hardikraj08@gmail.com'}],
        'contacts': [{'id': 19536, 'number': '7893915484'}, {'id': 19537, 'number': '7671961129'}, {'id': 19538, 'number': '7893915640'}],
        'insti_address': {'id': 16172, 'hostel_name': 'Hostel 5', 'room': '00', 'hostel': '5'},
        'mobile': None,
        'roll_number': '200050048',
        'profile_picture':'/profiles/media/profile_picture/2e3afe0d75e642f3b932f31838ede52a.png',
        'sex': 'male',
        'type': 'ug',
        'username': '200050048',
        'first_name': 'Hardik',
        'last_name': 'Rajpal',
        'email': '200050048@iitb.ac.in'
    }"""
    username = profile_json['username']
    #TODO:ASKDEV: are usernames always RNs?
    roll_no = profile_json['roll_number']

    # Check if a user exists with same username or roll number
    query = Q(username=username)
    if roll_no:
        query = query | Q(profile__roll_no=roll_no)
    user = User.objects.filter(query).first()

    # Create a new user if not found
    if not user:
        user = User.objects.create_user(username)

    # Set username again in case LDAP ID changed
    user.username = username

    # Check if User has a profile and create if not
    try:
        queryset = UserProfileFullSerializer.setup_eager_loading(UserProfile.objects)
        user_profile = queryset.get(user=user)

    except UserProfile.DoesNotExist:
        #TODO:pass correct params from sso data.
        user_profile = UserProfile.objects.create(
            user=user,
            name=username,
            roll_no=roll_no,
            profile_pic = profile_json['profile_picture'],
            email=profile_json['email'],
            contact_no=json.dumps(profile_json['contacts'])
        )

    # Fill models with new data
    # fill_models_from_sso(user_profile, user, profile_json)
    # Log in the user
    login(request, user)
    request.session.save()
    # print(user_profile)
    adminAccountList = (AdminProfile.objects.filter(user=user_profile))
    # Return the session id
    return Response({
        'sessionid': request.session.session_key,
        'user': user.username,
        'username':str(user_profile),
        'profile_id': user_profile.id,
        'is_admin':(len(adminAccountList)>0)
    #     'profile': UserProfileFullSerializer(
    #         user_profile,
    #         # context={'request': request}
    #         ).data
    }
    )



def fill_models_from_sso(user_profile, user, profile_json):
    """Fill models from SSO data."""
    SSOFiller(user_profile, user, profile_json).fill().save()

class SSOFiller():
    """Helper class to fill user model from SSO."""

    def __init__(self, user_profile, user, profile_json):
        self.user_profile = user_profile
        self.user = user
        self.profile_json = profile_json

    def fill(self):
        self.fill_common()
        self.fill_name()
        self.oset('email')
        self.fill_contact()
        self.fill_profile_pic()
        self.fill_program()
        self.fill_insti_address()
        return self

    def save(self):
        self.user.save()
        self.user_profile.save()
        return self

    def fill_common(self):
        """Fill in common data into the profile from SSO. """
        for response_key, data_key in {
                'first_name': 'name',
                'email': 'email',
                'mobile': 'contact_no',
                'roll_number': 'roll_no',
                'username': 'ldap_id'
        }.items():
            self.oset(response_key, data_key)

    def fill_name(self):
        if self.jhas('first_name') and self.jhas('last_name'):
            self.user_profile.name = ('%s %s' % (self.jget('first_name'), self.jget('last_name'))).title()
            self.user.first_name = str(self.jget('first_name')).title()
            self.user.last_name = str(self.jget('last_name')).title()

    def fill_contact(self):
        if self.jhas('contacts') and self.jget('contacts'):
            self.user_profile.contact_no = self.jget('contacts')[0]['number']

    def fill_profile_pic(self):
        if self.jhas('profile_picture'):
            self.user_profile.profile_pic = 'https://gymkhana.iitb.ac.in' + self.jget('profile_picture')

    def fill_program(self):
        if self.jhas('program'):
            target = self.jget('program')
            self.oset('join_year', target=target)
            self.oset('department', target=target)
            self.oset('department_name', target=target)
            self.oset('degree', target=target)
            self.oset('degree_name', target=target)
            self.oset('graduation_year', target=target)

    def fill_insti_address(self):
        if self.jhas('insti_address'):
            target = self.jget('insti_address')
            self.oset('hostel', target=target)
            self.oset('room', target=target)

    def jhas(self, response_key, target=None):
        if not target:
            target = self.profile_json
        return response_key in target and target[response_key] is not None

    def jget(self, response_key):
        return self.profile_json[response_key]

    def oset(self, response_key, data_key=None, target=None):
        if data_key is None:
            data_key = response_key
        if not target:
            target = self.profile_json
        if self.jhas(response_key, target):
            print(data_key,type(data_key),target[response_key],type(target[response_key]))
            setattr(self.user_profile, data_key, target[response_key])