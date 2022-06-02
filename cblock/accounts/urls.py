from django.urls import path, include
from django.views.generic import TemplateView

from rest_auth.views import (
    LoginView, LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)
from rest_auth.registration.views import RegisterView, VerifyEmailView
from allauth.account.views import ConfirmEmailView, confirm_email

from cblock.accounts.views import MetamaskLoginView, MetamaskUserDetailsView, generate_metamask_message



urlpatterns = [
    # path('metamask_login/', MetamaskLoginView.as_view(), name='metamask_login'),
    path('get_metamask_message/', generate_metamask_message),
    # path('rest-auth/', include('rest_auth.urls')),
    # path('rest-auth/registration/', include('rest_auth.registration.urls'))

    path('password/reset/', PasswordResetView.as_view(),
        name='rest_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'),
    path('login/', LoginView.as_view(), name='account_login'),
    # URLs that require a user to be logged in with a valid session / token.
    path('logout/', LogoutView.as_view(), name='account_logout'),
    path('user/', MetamaskUserDetailsView.as_view(), name='account_user_details'),
    path('password/change/', PasswordChangeView.as_view(), name='account_password_change'),
    path('registration/', RegisterView.as_view(), name='account_signup'),
    # path('registration/verify-email/', VerifyEmailView.as_view(), name='account_confirm_email'),
    path('registration/account-confirm-email/<str:key>/', ConfirmEmailView.as_view(), name='account_confirm_email'),
    path('registration/account-email-verification-sent/', TemplateView.as_view(),
        name='account_email_verification_sent'),

    # This url is used by django-allauth and empty TemplateView is
    # defined just to allow reverse() call inside app, for example when email
    # with verification link is being sent, then it's required to render email
    # content.

    # account_confirm_email - You should override this view to handle it in
    # your API client somehow and then, send post to /verify-email/ endpoint
    # with proper key.
    # If you don't want to use API on that step, then just use ConfirmEmailView
    # view from:
    # django-allauth https://github.com/pennersr/django-allauth/blob/master/allauth/account/views.py
]
