"""Login Viewset."""
from django.conf import settings
from django.contrib.auth import logout
from rest_framework import viewsets
from rest_framework.response import Response
from accounts.helpers import perform_login
from accounts.serializer import UserProfileFullSerializer
from django.utils import timezone
from accounts.models import UserProfile


class LoginViewSet(viewsets.ViewSet):
    """Login"""

    @staticmethod
    def login(request):
        """Log in.
        Uses the `code` and `redir` query parameters."""

        # Check if we have the auth code
        auth_code = request.GET.get('code')
        if auth_code is None:
            return Response({"message": "{?code} is required"}, status=400)

        # Check we have redir param
        redir = request.GET.get('redir')
        if redir is None:
            return Response({"message": "{?redir} is required"}, status=400)

        return perform_login(auth_code, redir, request)



    @staticmethod
    def get_user(request):
        """Get session and profile."""

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({"message": "not logged in"}, status=401)

        # Check if the user has a profile
        try:
            queryset = UserProfileFullSerializer.setup_eager_loading(UserProfile.objects)
            user_profile = queryset.get(user=request.user)
            profile_serialized = UserProfileFullSerializer(
                user_profile, context={'request': request})
        except UserProfile.DoesNotExist:
            return Response({'message': "UserProfile doesn't exist"}, status=500)

        # Count this as a ping
        user_profile.last_ping = timezone.now()
        user_profile.save(update_fields=['last_ping'])

        # Return the details and nested profile
        return Response({
            'sessionid': request.session.session_key,
            'user': request.user.username,
            'profile_id': user_profile.id,
            'profile': profile_serialized.data
        })



    @staticmethod
    def logout(request):
        """Log out."""

        logout(request)
        return Response({'message': 'logged out'})