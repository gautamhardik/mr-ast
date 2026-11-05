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
        self.redirects = order_of_redirects
        self.calls = []
        self.max_redirects = 30
        self.cookies = {}
        self.trust_env = False

    def send(self, *args, **kwargs):
        self.calls.append(SendCall(args, kwargs))
        return self.build_response()

    def build_response(self):
        request = self.calls[-1].args[0]
        r = requests.Response()
        try:
            r.status_code = int(self.redirects.pop(0))
        except IndexError:
            r.status_code = 200
        r.headers = CaseInsensitiveDict({'Location': '/'})
        r.raw = self._build_raw()
        r.request = request
        return r

    def _build_raw(self):
        string = StringIO.StringIO('')
        setattr(string, 'release_conn', lambda *args: args)
        return string

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
    """Properly merges both requests and session hooks.

    This is necessary because when request_hooks == {'response': []}, the
    merge breaks Session hooks entirely.
    """
    if session_hooks is None or session_hooks.get('response') == []:
        return request_hooks
    if request_hooks is None or request_hooks.get('response') == []:
        return session_hooks
    return merge_setting(request_hooks, session_hooks, dict_class)

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
    adapter = session.get_adapter(url=url)
    org_build_response = adapter.build_response
    self._patched_response = False

    def build_response(*args, **kwargs):
        resp = org_build_response(*args, **kwargs)
        if not self._patched_response:
            resp.raw.headers['content-encoding'] = 'gzip'
            self._patched_response = True
        return resp
    adapter.build_response = build_response

def test_auth_is_retained_for_redirect_on_host(self, httpbin):
    r = requests.get(httpbin('redirect/1'), auth=('user', 'pass'))
    h1 = r.history[0].request.headers['Authorization']
    h2 = r.request.headers['Authorization']
    assert h1 == h2

def test_custom_redirect_mixin(self, httpbin):
    """Tests a custom mixin to overwrite ``get_redirect_target``.

        Ensures a subclassed ``requests.Session`` can handle a certain type of
        malformed redirect responses.

        1. original request receives a proper response: 302 redirect
        2. following the redirect, a malformed response is given:
            status code = HTTP 200
            location = alternate url
        3. the custom session catches the edge case and follows the redirect
        """
    url_final = httpbin('html')
    querystring_malformed = urlencode({'location': url_final})
    url_redirect_malformed = httpbin('response-headers?%s' % querystring_malformed)
    querystring_redirect = urlencode({'url': url_redirect_malformed})
    url_redirect = httpbin('redirect-to?%s' % querystring_redirect)
    urls_test = [url_redirect, url_redirect_malformed, url_final]

    class CustomRedirectSession(requests.Session):

        def get_redirect_target(self, resp):
            if resp.is_redirect:
                return resp.headers['location']
            location = resp.headers.get('location')
            if location and location != resp.url:
                return location
            return None
    session = CustomRedirectSession()
    r = session.get(urls_test[0])
    assert len(r.history) == 2
    assert r.status_code == 200
    assert r.history[0].status_code == 302
    assert r.history[0].is_redirect
    assert r.history[1].status_code == 200
    assert not r.history[1].is_redirect
    assert r.url == urls_test[2]

def rebuild_method(self, prepared_request, response):
    """When being redirected we may want to change the method of the request
        based on certain specs or browser behavior.
        """
    method = prepared_request.method
    if response.status_code == codes.see_other and method != 'HEAD':
        method = 'GET'
    if response.status_code == codes.found and method != 'HEAD':
        method = 'GET'
    if response.status_code == codes.moved and method == 'POST':
        method = 'GET'
    prepared_request.method = method

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
    hist = []
    url = self.get_redirect_target(resp)
    previous_fragment = urlparse(req.url).fragment
    while url:
        prepared_request = req.copy()
        hist.append(resp)
        resp.history = hist[1:]
        try:
            resp.content
        except (ChunkedEncodingError, ContentDecodingError, RuntimeError):
            resp.raw.read(decode_content=False)
        if len(resp.history) >= self.max_redirects:
            raise TooManyRedirects(f'Exceeded {self.max_redirects} redirects.', response=resp)
        resp.close()
        if url.startswith('//'):
            parsed_rurl = urlparse(resp.url)
            url = ':'.join([to_native_string(parsed_rurl.scheme), url])
        parsed = urlparse(url)
        if parsed.fragment == '' and previous_fragment:
            parsed = parsed._replace(fragment=previous_fragment)
        elif parsed.fragment:
            previous_fragment = parsed.fragment
        url = parsed.geturl()
        if not parsed.netloc:
            url = urljoin(resp.url, requote_uri(url))
        else:
            url = requote_uri(url)
        prepared_request.url = to_native_string(url)
        self.rebuild_method(prepared_request, resp)
        if resp.status_code not in (codes.temporary_redirect, codes.permanent_redirect):
            purged_headers = ('Content-Length', 'Content-Type', 'Transfer-Encoding')
            for header in purged_headers:
                prepared_request.headers.pop(header, None)
            prepared_request.body = None
        headers = prepared_request.headers
        headers.pop('Cookie', None)
        extract_cookies_to_jar(prepared_request._cookies, req, resp.raw)
        merge_cookies(prepared_request._cookies, self.cookies)
        prepared_request.prepare_cookies(prepared_request._cookies)
        proxies = self.rebuild_proxies(prepared_request, proxies)
        self.rebuild_auth(prepared_request, resp)
        rewindable = prepared_request._body_position is not None and ('Content-Length' in headers or 'Transfer-Encoding' in headers)
        if rewindable:
            rewind_body(prepared_request)
        req = prepared_request
        if yield_requests:
            yield req
        else:
            resp = self.send(req, stream=stream, timeout=timeout, verify=verify, cert=cert, proxies=proxies, allow_redirects=False, **adapter_kwargs)
            extract_cookies_to_jar(self.cookies, prepared_request, resp.raw)
            url = self.get_redirect_target(resp)
            yield resp

@property
def is_permanent_redirect(self):
    """True if this Response one of the permanent versions of redirect."""
    return 'location' in self.headers and self.status_code in (codes.moved_permanently, codes.permanent_redirect)

def test_cookie_persists_via_api(self, httpbin):
    s = requests.session()
    r = s.get(httpbin('redirect/1'), cookies={'foo': 'bar'})
    assert 'foo' in r.request.headers['Cookie']
    assert 'foo' in r.history[0].request.headers['Cookie']

def get_redirect_target(self, resp):
    """Receives a Response. Returns a redirect URI or ``None``"""
    if resp.is_redirect:
        location = resp.headers['location']
        location = location.encode('latin1')
        return to_native_string(location, 'utf8')
    return None

def test_request_and_response_are_pickleable(self, httpbin):
    r = requests.get(httpbin('get'))
    assert pickle.loads(pickle.dumps(r.request))
    pr = pickle.loads(pickle.dumps(r))
    assert r.request.url == pr.request.url
    assert r.request.headers == pr.request.headers

def send(self, *args, **kwargs):
    self.calls.append(SendCall(args, kwargs))
    return self.build_response()