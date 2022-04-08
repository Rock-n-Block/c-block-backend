from django.urls import path
from cblock.rates.views import RateRequest

urlpatterns = [
    path('rates/', RateRequest.as_view(), name='rates')
]
