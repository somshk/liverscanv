from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_field
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import uuid

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Custom logic to avoid requiring a username when using Google login.
        """
        user = super().populate_user(request, sociallogin, data)

        if sociallogin.account.provider == "google":
            # Generate a unique username from email or a random UUID
            email = data.get("email", "")
            base_username = slugify(email.split("@")[0]) if email else f"user-{uuid.uuid4().hex[:10]}"
            
            # Ensure username uniqueness
            user_field(user, "username", self.generate_unique_username(base_username))

        return user

    def generate_unique_username(self, base_username):
        """
        Ensure that the generated username is unique.
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}-{counter}"
            counter += 1

        return username

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Bypass the intermediary signup page and allow automatic signup.
        """
        return True
