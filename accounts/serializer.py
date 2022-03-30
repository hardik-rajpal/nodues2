from django.conf import settings
from rest_framework import serializers
from accounts.models import UserProfile

class UserProfileFullSerializer(serializers.ModelSerializer):
    """Full serializer for UserProfile with detailed information and events."""

    email = serializers.SerializerMethodField()
    contact_no = serializers.SerializerMethodField()

    @staticmethod
    def setup_eager_loading(queryset):
        """Perform necessary eager loading of data."""
        queryset = queryset.prefetch_related()
        return queryset
    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'profile_pic', 'email', 'roll_no',
                    'contact_no',
                    # 'show_contact_no',
                    'ldap_id', 'hostel')
    