from django.contrib import admin
from .models import Budget, Expense

# Register your models here.
admin.site.register(Expense)
admin.site.register(Budget)
