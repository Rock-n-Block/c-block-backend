from django.urls import path
from .views import history, lastwill_dead_list, lostkey_dead_list, new_lastwill, new_lostkey, \
    new_token, new_wedding, new_crowdsale


urlpatterns = [
    path('history/<str:address>/', history, name='history_read'),
    path('lastwill_dead_list/', lastwill_dead_list, name='lastwill_dead_list'),
    path('lostkey_dead_list/', lostkey_dead_list, name='lostkey_dead_list'),
    path('new_lastwill/', new_lastwill, name='new_lastwill'),
    path('new_lostkey/', new_lostkey, name='new_lostkey'),
    path('new_wedding/', new_wedding, name='new_wedding'),
    path('new_crowdsale/', new_crowdsale, name='new_crowdsale'),
    path('new_token/', new_token, name='new_token'),
]
