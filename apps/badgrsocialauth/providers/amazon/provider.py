from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AmazonAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get('name',
                                           super(AmazonAccount, self).to_str())


class AmazonProvider(OAuth2Provider):
    id = 'amazon'
    name = 'Amazon'
    account_class = AmazonAccount

    def get_default_scope(self):
        return ['profile']

    def extract_uid(self, data):
        return str(data['user_id'])

    def extract_common_fields(self, data):
        return {
            'email': data['primary_email'],
            'first_name': data['first_name'],
            'last_name': data['last_name']
        }



provider_classes = [AmazonProvider]
