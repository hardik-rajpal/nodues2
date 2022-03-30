from django.conf import settings
from rest_framework import serializers
from records.models import Department
from records.models import Requirement

class RequirementSerializer(serializers.ModelSerializer):
    # @staticmethod
    # def setup_eager_loading(queryset)
    #     """Perform necessary eager loading of data."""
    #     queryset = queryset.prefetch_related()
    #     return queryset
    class Meta:
        model = Requirement
        fields = '__all__'
    def to_representation(self, instance):
        repre = super().to_representation(instance)
        repre['department'] = Department.objects.get(id=repre['department']).name
        return repre