from django.contrib import admin
from django.urls import include, path

from records.views import RequirementViewSet

urlpatterns = [
    path('/',RequirementViewSet.as_view({'get': 'get_requirements','post':'post_requirements'}))
]
