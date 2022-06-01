from django.urls import path, include
from cblock.accounts.views import MetamaskLoginView, generate_metamask_message


urlpatterns = [
    # path('metamask_login/', MetamaskLoginView.as_view(), name='metamask_login'),
    path('get_metamask_message/', generate_metamask_message),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls'))

]
