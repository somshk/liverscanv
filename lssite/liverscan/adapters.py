from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url  # Correct import
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        # Assign a default role if not set (modify logic as needed)
        if not user.role:
            if '@gmail.com' in user_email(user):  # Example: Assign role based on email domain
                user.role = 'doctor'
            else:
                user.role = 'patient'

        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)  # Call the parent method

        # Ensure role is set before saving
        if not user.role:
            if '@gmail.com' in user_email(user):
                user.role = 'doctor'
            else:
                user.role = 'patient'

        user.save()  # Save the updated user
        return user

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_safe_url(self, url):
        return is_safe_url(url, allowed_hosts=None)
