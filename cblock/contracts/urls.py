from django.urls import path
from cblock.contracts.views import (
    history,
    lastwill_dead_list,
    lostkey_dead_list,
    new_lastwill,
    new_lostkey,
    new_token,
    new_wedding,
    new_crowdsale,
    platform_statistics,
    show_current_network_mode,
    update_network_mode
)

urlpatterns = [
    path('history/<str:address>/', history, name='history_read'),
    path('lastwill_finished/', lastwill_dead_list, name='lastwill_finished'),
    path('lostkey_finished/', lostkey_dead_list, name='lostkey_finished'),
    path('new_lastwill/', new_lastwill, name='new_lastwill'),
    path('new_lostkey/', new_lostkey, name='new_lostkey'),
    path('new_wedding/', new_wedding, name='new_wedding'),
    path('new_crowdsale/', new_crowdsale, name='new_crowdsale'),
    path('new_token/', new_token, name='new_token'),
    path('platform_statistics', platform_statistics, name='platform_statistics'),
    path('network_mode/', show_current_network_mode, name='get_network_mode'),
    path('network_mode/update', update_network_mode, name='get_network_mode'),
]
