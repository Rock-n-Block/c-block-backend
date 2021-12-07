from django.urls import path
from .views import history, probate, mail_list


urlpatterns = [
    path('history/<str:address>/', history),
    path('probate/', probate),
    path('probate/mail_list/', mail_list),
]
