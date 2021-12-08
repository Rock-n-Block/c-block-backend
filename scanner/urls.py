from django.urls import path
from .views import history, probates, new_probate, new_token, new_wedding, new_crowdsale


urlpatterns = [
    path('history/<str:address>/', history),
    path('probates/', probates),
    path('new_probate/', new_probate, name='new_probate'),
    path('new_wedding/', new_wedding, name='new_wedding'),
    path('new_crowdsale/', new_crowdsale, name='new_crowdsale'),
    path('new_token/', new_token, name='new_token'),
]
