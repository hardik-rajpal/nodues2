from django.contrib import admin
from records.models import Balance
from records.models import Department

from records.models import Requirement, Queries

# Register your models here.
admin.site.register(Requirement)
admin.site.register(Queries)
admin.site.register(Department)
admin.site.register(Balance)