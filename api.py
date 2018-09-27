import json, io, requests
from categories import get_last_category_id


#scry_path='https://dev.scry.info:443/scry2/'
#publisher_path='https://dev.scry.info:443/meta/'
publisher_url = 'http://localhost:2222/'
scry_url = 'http://localhost:1234/'


class ScryApiException(Exception):
    def __init__(self, status_code, response):
        assert status_code >= 400
        super(ScryApiException, self).__init__('HTTP error %d' % status_code)
        self.response = response


class ScryApi(object):

    # TRICK: mapping endpoint to which backend is serving it.
    paths = dict(
        login=scry_url,
        protected=publisher_url,
        publisher=publisher_url,
        categories=publisher_url,
        listing_by_categories=publisher_url,
        listing=publisher_url,
        get_categories=publisher_url,
        get_categories_parents=publisher_url,
        delete_categories=publisher_url,
    )

    def _get_url(self, path):
        return self.paths[path] + path


    def _make_headers(self):
        if getattr(self, 'jwt_token', None) is not None:
            return {"Authorization": "JWT " + self.jwt_token}


    def _post(self, path, **payload):
        r = requests.post(self._get_url(path), headers=self._make_headers(), **payload)
        if r.status_code >= 400:
            try:
                response = json.loads(r.text)
            except:
                response = r.text
                print('failed to decode response as JSON: "%s"' % response)
            raise ScryApiException(r.status_code, response)
        return json.loads(r.text)


    def _get(self, path, **payload):
        r = requests.get(self._get_url(path), payload, headers=self._make_headers())
        if r.status_code >= 400:
            try:
                response = json.loads(r.text)
            except:
                response = r.text
                print('failed to decode response as JSON: "%s"' % response)
            raise ScryApiException(r.status_code, response)
        return json.loads(r.text)

    def login(self, username, password):
        response = self._post('login', json=dict(username=username, password=password))
        self.jwt_token = response['token']
        return self.jwt_token

    def protected(self):
        return self._post('protected')

    def publisher(self, data=None, listing_info=None):
        files = {}
        if data:
            files['data'] = open(self.data_path + data, 'rb')
        if listing_info:
            files['listing_info'] = open(self.listing_path + listing_info)
        try:
            res = self._post('publisher', files=files)
        finally:
            for f in files.values():
                f.close()
        return res

    def publisher2(self, data=None, listing_info=None):
        files = {}
        if data:
            files['data'] = open(self.data_path + data, 'rb')
        if listing_info:
            f1 = open(self.listing_path + listing_info)
            listing_info = json.loads(f1.read())
            f1.close()
            listing_info['category_id'] = get_last_category_id(listing_info['category_name'])
            listing_info = json.dumps(listing_info)

            files['listing_info'] = listing_info
        try:
            res = self._post('publisher', files=files)
        finally:
            for f in files.values():
                try:
                    f.close()
                except:
                    continue
        return res

    def search(self, payload):
        return self._get('search_keywords', params=payload)

    def categories(self, metadata):
        return self._post('categories', json=metadata)

    def get_categories(self, payload):
        return self._post('get_categories', json=payload)

    def get_categories_parents(self, payload):
        return self._post('get_categories_parents', json=payload)

    def delete_categories(self, payload):
        return self._post('delete_categories', json=payload)

    def listing_by_categories(self, payload):
        return self._get('listing_by_categories', params=payload)
