import logging

from urllib.parse import urlsplit

from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import build_absolute_uri

from cblock.accounts.utils import get_domain_for_emails
from cblock.settings import  config, ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL

class CustomDomainAdapter(DefaultAccountAdapter):

    def get_email_confirmation_redirect_url(self, request):
        if not config.frontend_host_domain:
            return super().get_email_confirmation_redirect_url(request)

        location = ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL
        redirect_url =f"{request.scheme}://{config.frontend_host_domain}{location}"
        logging.info(redirect_url)
        return redirect_url


    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": get_domain_for_emails(request),
            "key": emailconfirmation.key,
        }
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.owner_address = form.cleaned_data.get('owner_address')
        user.save()
        return user