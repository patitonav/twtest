import json
import hashlib
import hmac
import time
import urllib

from restful_lib import Connection

from config import ADFLY_SECRET_API_KEY, ADFLY_PUBLIC_API_KEY, ADFLY_USER_ID

class AdflyManager():
    BASE_HOST = 'http://api.adf.ly'
    # TODO: Replace this with your secret key.
    SECRET_KEY = ADFLY_SECRET_API_KEY
    # TODO: Replace this with your public key.
    PUBLIC_KEY = ADFLY_PUBLIC_API_KEY
    # TODO: Replace this with your user id.
    USER_ID = ADFLY_USER_ID
    AUTH_TYPE = dict(basic=1, hmac=2)
    
    def __init__(self):
        # In this example we use rest client provided by
        # http://code.google.com/p/python-rest-client/
        # Of course you are free to use any other client.
        self._connection = Connection(self.BASE_HOST)
    
    def get_groups(self, page=1):
        response = self._connection.request_get(
            '/v1/urlGroups',
            args=self._get_params(dict(_page=page), self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])
    
    def expand(self, urls, hashes=[]):
        params = dict()
        
        if type(urls) == list:
            for i, url in enumerate(urls):
                params['url[%d]' % i] = url
        elif type(urls) == str:
            params['url'] = urls
        
        if type(hashes) == list:
            for i, hashval in enumerate(hashes):
                params['hash[%d]' % i] = hashval
        elif type(hashes) == str:
            params['hash'] = hashes
        
        response = self._connection.request_get(
            '/v1/expand',
            args=self._get_params(params, self.AUTH_TYPE['basic']))
        return json.loads(response['body'])
    
    def shorten(self, urls, domain=None, advert_type=None, group_id=None):
        params = dict()
        if domain:
            params['domain'] = domain
        if advert_type:
            params['advert_type'] = advert_type
        if group_id:
            params['group_id'] = group_id
        
        if type(urls) == list:
            for i, url in enumerate(urls):
                params['url[%d]' % i] = url
        elif type(urls) == str:
            params['url'] = urls
        
        response = self._connection.request_post(
            '/v1/shorten',
            args=self._get_params(params, self.AUTH_TYPE['basic']))
        return json.loads(response['body'])
    
    def get_urls(self, page=1, search_str=None):
        response = self._connection.request_get(
            '/v1/urls',
            args=self._get_params(dict(_page=page, q=search_str), self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])
    
    def update_url(self, url_id, **kwargs):
        params = dict()
        
        allowed_kwargs = ['url', 'advert_type', 'title',
                          'group_id', 'fb_description', 'fb_image']
        for k, v in kwargs.items():
            if k in allowed_kwargs:
                params[k] = v
        
        response = self._connection.request_put(
            '/v1/urls/%d' % url_id,
            args=self._get_params(params, self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])
    
    def delete_url(self, url_id):
        response = self._connection.request_delete(
            '/v1/urls/%d' % url_id,
            args=self._get_params(dict(), self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])
    
    def _get_params(self, params={}, auth_type=None):
        """Populates request parameters with required parameters,
        such as _user_id, _api_key, etc.
        """
        auth_type = auth_type or self.AUTH_TYPE['basic']
        
        params['_user_id'] = self.USER_ID
        params['_api_key'] = self.PUBLIC_KEY
        
        if self.AUTH_TYPE['basic'] == auth_type:
            pass
        elif self.AUTH_TYPE['hmac'] == auth_type:
            # Get current unix timestamp (UTC time).
            params['_timestamp'] = int(time.time())
            params['_hash'] = self._do_hmac(params)
        else:
            raise RuntimeError
        
        return params

    def _do_hmac(self, params):
        if type(params) != dict:
            raise RuntimeError
        
        # Get parameter names.
        keys = params.keys()
        # Sort them using byte ordering.
        # So 'param[10]' comes before 'param[2]'.
        keys.sort()
        queryParts = []
        
        # Url encode query string. The encoding should be performed
        # per RFC 1738 (http://www.faqs.org/rfcs/rfc1738)
        # which implies that spaces are encoded as plus (+) signs.
        for key in keys:
            quoted_key = urllib.quote_plus(str(key))
            if params[key] is None:
                params[key] = ''
            
            quoted_value = urllib.quote_plus(str(params[key]))
            queryParts.append('%s=%s' % (quoted_key, quoted_value))
        
        return hmac.new(
            self.SECRET_KEY,
            '&'.join(queryParts),
            hashlib.sha256).hexdigest()