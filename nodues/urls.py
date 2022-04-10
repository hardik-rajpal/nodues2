from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/accounts/',include('accounts.urls')),
    path('api/records',include('records.urls'))
]
