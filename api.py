import json
import requests


publisher_url = 'http://localhost:2222/'
scry_url = 'http://localhost:1234/'


def api_categories(payload, headers):
    r = requests.post(publisher_url + 'categories', json=payload, headers=headers)
    return r.text


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

    def login(self, **payload):
        response = self._request('login', payload)
        return response['token']

    def get_url(self, path):
        return  self.paths[path] + path

    def _request(self, path, payload):
        r = requests.post(self.get_url(path), json=payload)
        if r.status_code > 400:
            try:
                response = json.loads(r.text)
            except:
                response = r.text
                print('failed to decode response as JSON: "%s"' % response)
            raise ScryApiException(r.status_code, response)
        return json.loads(r.text)


def api_protected(headers):
    return ScryApi()._request('protected', headers)


def api_publisher(files, headers):
    r = requests.post(publisher_url + 'publisher', files=files, headers=headers)
    if r.status_code > 400:
        raise ScryApiException(r.status_code, json.loads(r.text))
    return r.text


def api_search(payload, headers):
    r = requests.get(publisher_url + 'search_keywords', params=payload, headers=headers)
    response = r.text
    return response


def api_getcategories(headers):
    r = requests.post(publisher_url + 'getcategories', headers=headers)
    response = r.text
    return response


def api_test_json(payload):
    r = requests.post(publisher_url + 'test_json', json=payload)
    response = r.text
    return response