from django.urls import path, include
from django.views.generic import TemplateView

from rest_auth.views import (
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)
from rest_auth.registration.views import RegisterView, VerifyEmailView
from allauth.account.views import ConfirmEmailView

from cblock.accounts.views import (
    MetamaskUserDetailsView,
    GenerateMetamaskMessageView
)



urlpatterns = [
    path('get_metamask_message/', GenerateMetamaskMessageView.as_view()),

    path('registration/', RegisterView.as_view(), name='account_signup'),
    path('registration/account-confirm-email/<str:key>/', ConfirmEmailView.as_view(), name='account_confirm_email'),
    path('registration/account-email-verification-sent/', TemplateView.as_view(),
        name='account_email_verification_sent'),

    path('login/', LoginView.as_view(), name='account_login'),
    path('logout/', LogoutView.as_view(), name='account_logout'),
    path('user/', MetamaskUserDetailsView.as_view(), name='account_user_details'),

    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    path('password/change/', PasswordChangeView.as_view(), name='account_password_change'),

]
