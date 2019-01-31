import StringIO
import abc
import base64
import os
import re
import urlparse

import basic_models
from datetime import datetime, timedelta
from hashlib import sha1, md5
import hmac
import uuid

import requests
from basic_models.managers import ActiveObjectsManager
from basic_models.models import CreatedUpdatedBy, CreatedUpdatedAt, IsActive
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.files.storage import DefaultStorage
from django.core.urlresolvers import reverse
from django.db import models

from autoslug import AutoSlugField
import cachemodel
from django.db.models import Manager
from django.utils.deconstruct import deconstructible
from jsonfield import JSONField
from oauth2_provider.models import AccessToken
from rest_framework.authtoken.models import Token

from mainsite.utils import OriginSetting, fetch_remote_file_to_storage
from .mixins import ResizeUploadedImage


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class BadgrAppManager(Manager):
    def get_current(self, request=None, raise_exception=True):
        origin = None
        existing_session_app_id = None

        if request:
            if request.META.get('HTTP_ORIGIN'):
                origin = request.META.get('HTTP_ORIGIN')
            elif request.META.get('HTTP_REFERER'):
                origin = request.META.get('HTTP_REFERER')
            existing_session_app_id = request.session.get('badgr_app_pk', None)

        if origin:
            url = urlparse.urlparse(origin)
            try:
                return self.get(cors=url.netloc)
            except self.model.DoesNotExist:
                pass

        if existing_session_app_id:
            try:
                return self.get(id=existing_session_app_id)
            except self.model.DoesNotExist:
                pass
        badgr_app_id = getattr(settings, 'BADGR_APP_ID', None)
        if raise_exception and not badgr_app_id:
            raise ImproperlyConfigured("Must specify a BADGR_APP_ID")
        return self.get(id=badgr_app_id)


class BadgrApp(CreatedUpdatedBy, CreatedUpdatedAt, IsActive, cachemodel.CacheModel):
    name = models.CharField(max_length=254)
    cors = models.CharField(max_length=254, unique=True)
    email_confirmation_redirect = models.URLField()
    signup_redirect = models.URLField()
    forgot_password_redirect = models.URLField()
    ui_login_redirect = models.URLField(null=True)
    ui_signup_success_redirect = models.URLField(null=True)
    ui_connect_success_redirect = models.URLField(null=True)
    public_pages_redirect = models.URLField(null=True)
    oauth_authorization_redirect = models.URLField(null=True)
    use_auth_code_exchange = models.BooleanField(default=False)
    oauth_application = models.ForeignKey("oauth2_provider.Application", null=True, blank=True)

    objects = BadgrAppManager()

    def __unicode__(self):
        return self.cors


@deconstructible
class DefinedScopesValidator(object):
    message = "Does not match defined scopes"
    code = 'invalid'

    def __call__(self, value):
        defined_scopes = set(getattr(settings, 'OAUTH2_PROVIDER', {}).get('SCOPES', {}).keys())
        provided_scopes = set(s.strip() for s in re.split(r'[\s\n]+', value))
        if provided_scopes - defined_scopes:
            raise ValidationError(self.message, code=self.code)
        pass

    def __eq__(self, other):
        return isinstance(other, self.__class__)


class ApplicationInfo(cachemodel.CacheModel):
    application = models.OneToOneField('oauth2_provider.Application')
    icon = models.FileField(blank=True, null=True)
    name = models.CharField(max_length=254, blank=True, null=True, default=None)
    website_url = models.URLField(blank=True, null=True, default=None)
    allowed_scopes = models.TextField(blank=False, validators=[DefinedScopesValidator()])
    trust_email_verification = models.BooleanField(default=False)

    def get_visible_name(self):
        if self.name:
            return self.name
        return self.application.name

    def get_icon_url(self):
        if self.icon:
            return self.icon.url

    @property
    def scope_list(self):
        return [s for s in re.split(r'[\s\n]+', self.allowed_scopes) if s]


class AccessTokenProxy(AccessToken):
    class Meta:
        proxy = True
        verbose_name = 'access token'
        verbose_name_plural = 'access tokens'

    def __str__(self):
        return self.obscured_token

    def __unicode__(self):
        return self.obscured_token

    @property
    def obscured_token(self):
        if self.token:
            return "{}***".format(self.token[:4])


class LegacyTokenProxy(Token):
    class Meta:
        proxy = True
        verbose_name = 'Legacy token'
        verbose_name_plural = 'Legacy tokens'

    def __str__(self):
        return self.obscured_token

    def __unicode__(self):
        return self.obscured_token

    @property
    def obscured_token(self):
        if self.key:
            return "{}***".format(self.key[:4])
