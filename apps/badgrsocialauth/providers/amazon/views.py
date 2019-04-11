import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import AmazonProvider


class AmazonOAuth2Adapter(OAuth2Adapter):
    provider_id = AmazonProvider.id

    # "token_endpoint": "https://idp-integ.federate.amazon.com/api/oauth2/v2/token",
    # access_token_url = 'https://api.amazon.com/auth/o2/token'
    access_token_url = 'https://idp-integ.federate.amazon.com/api/oauth2/v2/token'

    # "authorization_endpoint": "https://idp-integ.federate.amazon.com/api/oauth2/v1/authorize",
    # authorize_url = 'http://www.amazon.com/ap/oa'
    authorize_url = 'https://idp-integ.federate.amazon.com/api/oauth2/v1/authorize'

    # "userinfo_endpoint": "https://idp-integ.federate.amazon.com/api/oauth2/v1/userinfo",
    # profile_url = 'https://www.amazon.com/ap/user/profile'
    profile_url = 'https://idp-integ.federate.amazon.com/api/oauth2/v1/userinfo'

    supports_state = False
    redirect_uri_protocol = 'https'

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(
            self.profile_url,
            params={'access_token': token})
        extra_data = response.json()

        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(AmazonOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AmazonOAuth2Adapter)
