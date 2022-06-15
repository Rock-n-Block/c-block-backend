from django.urls import path
from cblock.rates.views import RateRequest

urlpatterns = [
    path('', RateRequest.as_view(), name='rates')
]
