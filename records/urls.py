from django.contrib import admin
from django.urls import include, path
from records.views import QueriesViewSet
from records.views import RequirementViewSet

urlpatterns = [
    path('/',RequirementViewSet.as_view({'get': 'get_requirements','post':'post_requirements'})),
    path('/query',QueriesViewSet.as_view({'get':'getQueries','post':'postQueryByStudent','put':'respondToQuery'})),
    path('/upload',QueriesViewSet.as_view({'post':'upload_file_queries'})),
    path('/get_file/<pk>', QueriesViewSet.as_view({'get': 'get_uploaded_file'})),
    path('/clear',RequirementViewSet.as_view({'get':'clearBalance'}))
]
