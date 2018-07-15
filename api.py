import json
import requests


publisher_url = 'http://localhost:2222/'
scry_url = 'http://localhost:1234/'


class ScryApiException(Exception):
    def __init__(self, status_code, response):
        assert status_code > 400
        super(ScryApiException, self).__init__('HTTP error %d' % status_code)
        self.response = response


class ScryApi(object):

    paths = dict(
        login=scry_url,
        protected=publisher_url,
    )

    def login(self, username, password):
        response = self._request('login', dict(username=username, password=password))
        self.jwt_token = response['token']
        return self.jwt_token

    def get_url(self, path):
        return self.paths[path] + path

    def _request(self, path, payload):
        r = requests.post(self.get_url(path), json=payload, headers=self.get_headers())
        if r.status_code > 400:
            try:
                response = json.loads(r.text)
            except:
                response = r.text
                print('failed to decode response as JSON: "%s"' % response)
            raise ScryApiException(r.status_code, response)
        return json.loads(r.text)

    def get_headers(self):
        if getattr(self,'jwt_token', None) is not None:
            return {"Authorization": "JWT " + self.jwt_token}

    def protected(self):
        return self._request('protected', None)

    def publisher(self, files):
        r = requests.post(publisher_url + 'publisher', files=files, headers=self.get_headers())
        if r.status_code > 400:
            raise ScryApiException(r.status_code, json.loads(r.text))
        return json.loads(r.text)

    def search(self, payload):
        r = requests.get(publisher_url + 'search_keywords', params=payload, headers=self.get_headers())
        return json.loads(r.text)

    def getcategories(self):
        r = requests.post(publisher_url + 'getcategories', headers=self.get_headers())
        return json.loads(r.text)

    def test_json(self, payload):
        r = requests.post(publisher_url + 'test_json', json=payload, headers=self.get_headers())
        return json.loads(r.text)

    def categories(self, payload):
        r = requests.post(publisher_url + 'categories', json=payload, headers=self.get_headers())
        return json.loads(r.text)
