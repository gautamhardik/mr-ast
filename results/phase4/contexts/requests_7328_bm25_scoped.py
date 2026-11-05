class TestRequests:
    # [Enclosing Scope]


def test_history_is_always_a_list(self, httpbin):
    """Show that even with redirects, Response.history is always a list."""
    resp = requests.get(httpbin('get'))
    assert isinstance(resp.history, list)
    resp = requests.get(httpbin('redirect/1'))
    assert isinstance(resp.history, list)
    assert not isinstance(resp.history, tuple)

def test_requests_history_is_saved(self, httpbin):
    r = requests.get(httpbin('redirect/5'))
    total = r.history[-1].history
    i = 0
    for item in r.history:
        assert item.history == total[0:i]
        i += 1

def test_HTTP_302_TOO_MANY_REDIRECTS_WITH_PARAMS(self, httpbin):
    s = requests.session()
    s.max_redirects = 5
    try:
        s.get(httpbin('relative-redirect', '50'))
    except TooManyRedirects as e:
        url = httpbin('relative-redirect', '45')
        assert e.request.url == url
        assert e.response.url == url
        assert len(e.response.history) == 5
    else:
        pytest.fail('Expected custom max number of redirects to be respected but was not')

def test_requests_in_history_are_not_overridden(self, httpbin):
    resp = requests.get(httpbin('redirect/3'))
    urls = [r.url for r in resp.history]
    req_urls = [r.request.url for r in resp.history]
    assert urls == req_urls

def test_http_302_doesnt_change_head_to_get(self, httpbin):
    r = requests.head(httpbin('status', '302'), allow_redirects=True)
    assert r.status_code == 200
    assert r.request.method == 'HEAD'
    assert r.history[0].status_code == 302
    assert r.history[0].is_redirect

def test_http_303_doesnt_change_head_to_get(self, httpbin):
    r = requests.head(httpbin('status', '303'), allow_redirects=True)
    assert r.status_code == 200
    assert r.request.method == 'HEAD'
    assert r.history[0].status_code == 303
    assert r.history[0].is_redirect

def test_http_301_doesnt_change_head_to_get(self, httpbin):
    r = requests.head(httpbin('status', '301'), allow_redirects=True)
    print(r.content)
    assert r.status_code == 200
    assert r.request.method == 'HEAD'
    assert r.history[0].status_code == 301
    assert r.history[0].is_redirect

def test_HTTP_302_ALLOW_REDIRECT_GET(self, httpbin):
    r = requests.get(httpbin('redirect', '1'))
    assert r.status_code == 200
    assert r.history[0].status_code == 302
    assert r.history[0].is_redirect

def test_fragment_maintained_on_redirect(self, httpbin):
    fragment = '#view=edit&token=hunter2'
    r = requests.get(httpbin('redirect-to?url=get') + fragment)
    assert len(r.history) > 0
    assert r.history[0].request.url == httpbin('redirect-to?url=get') + fragment
    assert r.url == httpbin('get') + fragment