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

class RedirectSession(SessionRedirectMixin):

    def __init__(self, order_of_redirects):
        ...

    def send(self, *args, **kwargs):
        ...

    def build_response(self):
        ...

    def _build_raw(self):
        ...

def test_fragment_maintained_on_redirect(self, httpbin):
    fragment = '#view=edit&token=hunter2'
    r = requests.get(httpbin('redirect-to?url=get') + fragment)
    assert len(r.history) > 0
    assert r.history[0].request.url == httpbin('redirect-to?url=get') + fragment
    assert r.url == httpbin('get') + fragment

def test_HTTP_307_ALLOW_REDIRECT_POST(self, httpbin):
    r = requests.post(httpbin('redirect-to'), data='test', params={'url': 'post', 'status_code': 307})
    assert r.status_code == 200
    assert r.history[0].status_code == 307
    assert r.history[0].is_redirect
    assert r.json()['data'] == 'test'

def test_HTTP_302_TOO_MANY_REDIRECTS(self, httpbin):
    try:
        requests.get(httpbin('relative-redirect', '50'))
    except TooManyRedirects as e:
        url = httpbin('relative-redirect', '20')
        assert e.request.url == url
        assert e.response.url == url
        assert len(e.response.history) == 30
    else:
        pytest.fail('Expected redirect to raise TooManyRedirects but it did not')

def merge_hooks(request_hooks, session_hooks, dict_class=OrderedDict):
    """Properly merges both requests and session hooks."""
    ...

def test_HTTP_307_ALLOW_REDIRECT_POST_WITH_SEEKABLE(self, httpbin):
    byte_str = b'test'
    r = requests.post(httpbin('redirect-to'), data=io.BytesIO(byte_str), params={'url': 'post', 'status_code': 307})
    assert r.status_code == 200
    assert r.history[0].status_code == 307
    assert r.history[0].is_redirect
    assert r.json()['data'] == byte_str.decode('utf-8')

@property
def is_redirect(self):
    """True if this Response is a well-formed HTTP redirect that could have
        been processed automatically (by :meth:`Session.resolve_redirects`).
        """
    return 'location' in self.headers and self.status_code in REDIRECT_STATI

def _patch_adapter_gzipped_redirect(self, session, url):
    ...

def test_auth_is_retained_for_redirect_on_host(self, httpbin):
    r = requests.get(httpbin('redirect/1'), auth=('user', 'pass'))
    h1 = r.history[0].request.headers['Authorization']
    h2 = r.request.headers['Authorization']
    assert h1 == h2

class Response:
    __attrs__ = ['_content', 'status_code', 'headers', 'url', 'history', 'encoding', 'reason', 'cookies', 'elapsed', 'request']

    def __init__(self):
        ...

    def __enter__(self):
        ...

    def __exit__(self, *args):
        ...

    def __getstate__(self):
        ...

    def __setstate__(self, state):
        ...

    def __repr__(self):
        ...

    def __bool__(self):
        ...

    def __nonzero__(self):
        ...

    def __iter__(self):
        ...

    @property
    def ok(self):
        ...

    @property
    def is_redirect(self):
        ...

    @property
    def is_permanent_redirect(self):
        ...

    @property
    def next(self):
        ...

    @property
    def apparent_encoding(self):
        ...

    def iter_content(self, chunk_size=1, decode_unicode=False):
        ...

    def iter_lines(self, chunk_size=ITER_CHUNK_SIZE, decode_unicode=False, delimiter=None):
        ...

    @property
    def content(self):
        ...

    @property
    def text(self):
        ...

    def json(self, **kwargs):
        ...

    @property
    def links(self):
        ...

    def raise_for_status(self):
        ...

    def close(self):
        ...

def test_custom_redirect_mixin(self, httpbin):
    """Tests a custom mixin to overwrite ``get_redirect_target``."""
    ...

def rebuild_method(self, prepared_request, response):
    """When being redirected we may want to change the method of the request"""
    ...

def test_http_301_changes_post_to_get(self, httpbin):
    r = requests.post(httpbin('status', '301'))
    assert r.status_code == 200
    assert r.request.method == 'GET'
    assert r.history[0].status_code == 301
    assert r.history[0].is_redirect

def test_http_302_changes_post_to_get(self, httpbin):
    r = requests.post(httpbin('status', '302'))
    assert r.status_code == 200
    assert r.request.method == 'GET'
    assert r.history[0].status_code == 302
    assert r.history[0].is_redirect

def test_http_303_changes_post_to_get(self, httpbin):
    r = requests.post(httpbin('status', '303'))
    assert r.status_code == 200
    assert r.request.method == 'GET'
    assert r.history[0].status_code == 303
    assert r.history[0].is_redirect

def resolve_redirects(self, resp, req, stream=False, timeout=None, verify=True, cert=None, proxies=None, yield_requests=False, **adapter_kwargs):
    """Receives a Response. Returns a generator of Responses or Requests."""
    ...

@property
def is_permanent_redirect(self):
    """True if this Response one of the permanent versions of redirect."""
    return 'location' in self.headers and self.status_code in (codes.moved_permanently, codes.permanent_redirect)

def test_cookie_persists_via_api(self, httpbin):
    s = requests.session()
    r = s.get(httpbin('redirect/1'), cookies={'foo': 'bar'})
    assert 'foo' in r.request.headers['Cookie']
    assert 'foo' in r.history[0].request.headers['Cookie']

class SessionRedirectMixin:

    def get_redirect_target(self, resp):
        ...

    def should_strip_auth(self, old_url, new_url):
        ...

    def resolve_redirects(self, resp, req, stream=False, timeout=None, verify=True, cert=None, proxies=None, yield_requests=False, **adapter_kwargs):
        ...

    def rebuild_auth(self, prepared_request, response):
        ...

    def rebuild_proxies(self, prepared_request, proxies):
        ...

    def rebuild_method(self, prepared_request, response):
        ...

def get_redirect_target(self, resp):
    """Receives a Response. Returns a redirect URI or ``None``"""
    if resp.is_redirect:
        location = resp.headers['location']
        location = location.encode('latin1')
        return to_native_string(location, 'utf8')
    return None

def __init__(self, *args, **kwargs):
    """Initialize RequestException with `request` and `response` objects."""
    ...

def test_request_and_response_are_pickleable(self, httpbin):
    r = requests.get(httpbin('get'))
    assert pickle.loads(pickle.dumps(r.request))
    pr = pickle.loads(pickle.dumps(r))
    assert r.request.url == pr.request.url
    assert r.request.headers == pr.request.headers

def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
    """Sends PreparedRequest object. Returns Response object."""
    ...

def test_requests_are_updated_each_time(httpbin):
    ...

def __iter__(self):
    """Allows you to use a response as an iterator."""
    return self.iter_content(128)

def test_auth_is_stripped_on_http_downgrade(self, httpbin, httpbin_secure, httpbin_ca_bundle):
    r = requests.get(httpbin_secure('redirect-to'), params={'url': httpbin('get')}, auth=('user', 'pass'), verify=httpbin_ca_bundle)
    assert r.history[0].request.headers['Authorization']
    assert 'Authorization' not in r.request.headers

class RequestException(IOError):
    """There was an ambiguous exception that occurred while handling your"""

    def __init__(self, *args, **kwargs):
        """Initialize RequestException with `request` and `response` objects."""
        ...

def test_response_without_release_conn(self):
    """Test `close` call for non-urllib3-like raw objects.
        Should work when `release_conn` attr doesn't exist on `response.raw`.
        """
    resp = requests.Response()
    resp.raw = StringIO.StringIO('test')
    assert not resp.raw.closed
    resp.close()
    assert resp.raw.closed

def test_fragment_update_on_redirect():
    """Verify we only append previous fragment if one doesn't exist on new"""
    ...

def test_unconsumed_session_response_closes_connection(self, httpbin):
    s = requests.session()
    with contextlib.closing(s.get(httpbin('stream/4'), stream=True)) as response:
        pass
    assert response._content_consumed is False
    assert response.raw.closed

def test_transfer_enc_removal_on_redirect(self, httpbin):
    ...

def test_redirect_with_wrong_gzipped_header(self, httpbin):
    s = requests.Session()
    url = httpbin('redirect/1')
    self._patch_adapter_gzipped_redirect(s, url)
    s.get(url)

def build_response(self, req, resp):
    """Builds a :class:`Response <requests.Response>` object from a urllib3"""
    ...

def send(self, *args, **kwargs):
    self.calls.append(SendCall(args, kwargs))
    return self.build_response()

def head(url, **kwargs):
    """Sends a HEAD request."""
    ...

def test_requests_after_timeout_are_not_received(self):
    """the basic response handler times out when receiving requests"""
    server = Server.basic_response_server(request_timeout=1)
    with server as address:
        sock = socket.socket()
        sock.connect(address)
        time.sleep(1.5)
        sock.sendall(b'hehehe, not received')
        sock.close()
    assert server.handler_results[0] == b''

def test_cookie_sent_on_redirect(self, httpbin):
    s = requests.session()
    s.get(httpbin('cookies/set?foo=bar'))
    r = s.get(httpbin('redirect/1'))
    assert 'Cookie' in r.json()['headers']

def stream_decode_response_unicode(iterator, r):
    """Stream decodes an iterator."""
    ...

def __call__(self, r):
    ...

def test_respect_proxy_env_on_send_with_redirects(self, httpbin):
    with override_environ(http_proxy=INVALID_PROXY):
        with pytest.raises(ProxyError):
            session = requests.Session()
            url = httpbin('redirect/1')
            print(url)
            request = requests.Request('GET', url)
            session.send(request.prepare())

def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
    """Sends PreparedRequest object. Returns Response object."""
    ...

def test_digestauth_401_count_reset_on_redirect():
    """Ensure we correctly reset num_401_calls after a successful digest auth,"""
    ...

def test_cookielib_cookiejar_on_redirect(self, httpbin):
    """Tests resolve_redirect doesn't fail when merging cookies"""
    ...

def test_manual_redirect_with_partial_body_read(self, httpbin):
    ...

def get_unicode_from_response(r):
    """Returns the requested content back in unicode."""
    ...

def __init__(self):
    ...

@pytest.mark.parametrize('files', ('foo', b'foo', bytearray(b'foo')))
def test_can_send_objects_with_files(self, httpbin, files):
    ...

def test_redirect_rfc1808_to_non_ascii_location():
    ...

def test_header_and_body_removal_on_redirect(self, httpbin):
    ...