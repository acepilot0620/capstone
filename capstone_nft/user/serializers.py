from rest_framework import serializers, exceptions
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists

from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate
from django.urls import exceptions as url_exceptions
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .models import User


class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    nick_name = serializers.CharField(write_only=True)

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _('A user is already registered with this e-mail address.'),
                )
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        user.name = self.cleaned_data['name']
        user.phone = self.cleaned_data['phone']
        user.nick_name = self.cleaned_data['nick_name']
        return user

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'phone': self.validated_data.get('phone', ''),
            'name': self.validated_data.get('name', ''),
            'nick_name': self.validated_data.get('nick_name', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password1'], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user = self.custom_signup(request, user)
        user.save()
        setup_user_email(request, user, [])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    nick_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_phone(self, phone, password):
        if phone and password:
            user = self.authenticate(phone=phone, password=password)
        else:
            msg = _('Must include "phone" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_nick_name(self, nick_name, password):
        if nick_name and password:
            user = self.authenticate(nick_name=nick_name, password=password)
        else:
            msg = _('Must include "nick_name" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def get_auth_user_using_allauth(self, email, password):
        from allauth.account import app_settings

        # Authentication through email
        if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
            return self._validate_email(email, password)

    def get_auth_user_using_orm(self, email, phone, nick_name, password):
        if email:
            try:
                username = User.objects.get(email__iexact=email).get_username()
            except User.DoesNotExist:
                pass

        elif phone:
            try:
                username = User.objects.get(phone=phone).get_username()
            except User.DoesNotExist:
                pass

        elif nick_name:
            try:
                username = User.objects.get(nick_name=nick_name).get_username()
            except User.DoesNotExist:
                pass

        if username:
            return self._validate_username_email(username, '', password)

        return None

    def get_auth_user(self, email, phone, nick_name, password):
        """
        Retrieve the auth user from given POST payload by using
        either `allauth` auth scheme or bare Django auth scheme.

        Returns the authenticated user instance if credentials are correct,
        else `None` will be returned
        """
        if 'allauth' in settings.INSTALLED_APPS:

            # When `is_active` of a user is set to False, allauth tries to return template html
            # which does not exist. This is the solution for it. See issue #264.
            try:
                if not email:
                    pass
                else:
                    return self.get_auth_user_using_allauth(email, password)
            except url_exceptions.NoReverseMatch:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        return self.get_auth_user_using_orm(email, phone, nick_name, password)

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.ValidationError(msg)

    @staticmethod
    def validate_email_verification_status(user):
        from allauth.account import app_settings
        if (
            app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY
            and not user.emailaddress_set.filter(email=user.email, verified=True).exists()
        ):
            raise serializers.ValidationError(_('E-mail is not verified.'))

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        nick_name = attrs.get('nick_name')
        password = attrs.get('password')
        user = self.get_auth_user(email, phone, nick_name, password)

        if not user:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # Did we get back an active user?
        self.validate_auth_user_status(user)

        # If required, is the email verified?
        if 'dj_rest_auth.registration' in settings.INSTALLED_APPS:
            self.validate_email_verification_status(user)

        attrs['user'] = user
        return attrs


class UserField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return User.objects.all()

    def to_representation(self, value):
        return UserBreifSerializer(self.get_queryset().get(pk=value.pk)).data


class UserBreifSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'name', 'nick_name', 'following_num', 'follower_num'
        ]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'created', 'email', 'phone', 'name', 'nick_name', 'following_num', 'follower_num'
        ]

class FollowingSerializer(serializers.ModelSerializer):
    followings = UserBreifSerializer(read_only=True, many=True)
    class Meta:
        model = User
        fields = [
            'followings'
        ]
        read_only_fields = fields

class FollowerSerializer(serializers.ModelSerializer):
    followers = UserBreifSerializer(read_only=True, many=True)
    class Meta:
        model = User
        fields = [
            'followers'
        ]
        read_only_fields = fields

