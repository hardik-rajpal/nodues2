from django.contrib import admin
from django.urls import include, path

from accounts.views import LoginViewSet

urlpatterns = [
    path('login', LoginViewSet.as_view({'get': 'login'})),
    path('logout', LoginViewSet.as_view({'get': 'logout'})),
]
