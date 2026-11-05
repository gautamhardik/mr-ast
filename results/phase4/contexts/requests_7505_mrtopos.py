@runtime_checkable
class SupportsRead(Protocol[_T_co]):

    def read(self, length: int=..., /) -> _T_co:
        ...

def test_super_len_correctly_calculates_len_of_partially_read_file(self):
    """Ensure that we handle partially consumed file like objects."""
    s = StringIO.StringIO()
    s.write('foobarbogus')
    assert super_len(s) == 0

def proxy_headers(self, proxy: str) -> dict[str, str]:
    """Returns a dictionary of the headers to add to any request sent
        through a proxy. This works with urllib3 magic to ensure that they are
        correctly sent to the proxy, rather than in a tunnelled request if
        CONNECT is being used.

        This should not be called from user code, and is only exposed for use
        when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param proxy: The url of the proxy being used for this request.
        :rtype: dict
        """
    headers: dict[str, str] = {}
    username, password = get_auth_from_url(proxy)
    if username:
        headers['Proxy-Authorization'] = _basic_auth_str(username, password)
    return headers

@staticmethod
def _encode_params(data: _t.EncodableDataType) -> str | bytes | _t.SupportsRead[str | bytes]:
    """Encode parameters in a piece of data."""
    ...

def __bool__(self) -> bool:
    """Returns True if :attr:`status_code` is less than 400."""
    ...

def __nonzero__(self) -> bool:
    """Returns True if :attr:`status_code` is less than 400.

        This attribute checks if the status code of the response is between
        400 and 600 to see if there was a client error or a server error. If
        the status code, is between 200 and 400, this will return True. This
        is **not** a check to see if the response code is ``200 OK``.
        """
    return self.ok

@property
def ok(self) -> bool:
    """Returns True if :attr:`status_code` is less than 400, False if not."""
    ...

class ReadTimeout(Timeout):
    """The server did not send any data in the allotted amount of time."""

def read(self, length: int=..., /) -> _T_co:
    ...

class MockRequest:
    type: str

    def __init__(self, request):
        ...

    def get_type(self):
        ...

    def get_host(self):
        ...

    def get_origin_req_host(self):
        ...

    def get_full_url(self):
        ...

    def is_unverifiable(self):
        ...

    def has_header(self, name):
        ...

    def get_header(self, name, default=None):
        ...

    def add_header(self, key, val):
        ...

    def add_unredirected_header(self, name, value):
        ...

    def get_new_headers(self):
        ...

    @property
    def unverifiable(self):
        ...

    @property
    def origin_req_host(self):
        ...

    @property
    def host(self):
        ...

def test_hasattr(self):
    assert hasattr(self.lookup_dict, 'bad_gateway') is True
    assert hasattr(self.lookup_dict, 'not_a_key') is False

@pytest.mark.parametrize('timeout', ((None, 0.1), Urllib3Timeout(connect=None, read=0.1)))
def test_read_timeout(self, httpbin, timeout):
    try:
        requests.get(httpbin('delay/10'), timeout=timeout)
        pytest.fail('The recv() request should time out.')
    except ReadTimeout:
        pass

def add_header(self, key: str, val: str) -> None:
    """cookiejar has no legitimate use for this method; add it back if you find one."""
    raise NotImplementedError('Cookie headers should be added with add_unredirected_header()')

def parse_dict_header(value: str) -> dict[str, str | None]:
    """Parse lists of key, value pairs as described by RFC 2068 Section 2 and"""
    ...

def super_len(o: Any) -> int:
    ...

class CookieConflictError(RuntimeError):
    """There are two cookies that meet the criteria specified in the cookie jar.
    Use .get and .set and include domain and path args in order to be more specific.
    """

@pytest.mark.parametrize('timeout', (None, Urllib3Timeout(connect=None, read=None)))
def test_none_timeout(self, httpbin, timeout):
    """Check that you can set None as a valid timeout value."""
    ...

def iter_content(self, chunk_size: int | None=1, decode_unicode: bool=False) -> Iterator[str | bytes]:
    """Iterates over the response data.  When stream=True is set on the"""
    ...

@pytest.mark.parametrize('var,scheme', _proxy_combos)
def test_use_proxy_from_environment(httpbin, var, scheme):
    url = f'{scheme}://httpbin.org'
    fake_proxy = Server()
    with fake_proxy as (host, port):
        proxy_url = f'socks5://{host}:{port}'
        kwargs = {var: proxy_url}
        with override_environ(**kwargs):
            with pytest.raises(requests.exceptions.ConnectionError):
                requests.get(url)
        assert len(fake_proxy.handler_results) == 1
        assert len(fake_proxy.handler_results[0]) > 0

def rebuild_auth(self, prepared_request: PreparedRequest, response: Response) -> None:
    """When being redirected we may want to strip authentication from the"""
    ...

@property
def is_redirect(self) -> bool:
    """True if this Response is a well-formed HTTP redirect that could have
        been processed automatically (by :meth:`Session.resolve_redirects`).
        """
    return 'location' in self.headers and self.status_code in REDIRECT_STATI

@runtime_checkable
class SupportsItems(Protocol[_KT_co, _VT_co]):

    def items(self) -> Iterable[tuple[_KT_co, _VT_co]]:
        ...

@pytest.mark.parametrize('value, expected', (('foo="is a fish", bar="as well"', {'foo': 'is a fish', 'bar': 'as well'}), ('key_without_value', {'key_without_value': None})))
def test_parse_dict_header(value, expected):
    assert parse_dict_header(value) == expected

def session() -> Session:
    """Returns a :class:`Session` for context-management."""
    ...

def add_headers(self, request: PreparedRequest, **kwargs: Any) -> None:
    """Add any headers needed by the connection. As of v2.0 this does"""
    ...

def __init__(self, *args: Any, **kwargs: Any) -> None:
    """Initialize RequestException with `request` and `response` objects."""
    ...

def test_super_len_with_fileno(self):
    with open(__file__, 'rb') as f:
        length = super_len(f)
        file_data = f.read()
    assert length == len(file_data)

def __init__(self, headers: Any) -> None:
    """Make a MockResponse for `cookiejar` to read.

        :param headers: a httplib.HTTPMessage or analogous carrying the headers
        """
    self._headers = headers

def request_url(self, request: PreparedRequest, proxies: dict[str, str] | None) -> str:
    """Obtain the url to use when making the final request."""
    ...

def rewind_body(prepared_request: PreparedRequest) -> None:
    """Move file pointer back to its recorded starting position"""
    ...

def consume_socket_content(sock, timeout=0.5):
    ...

class Timeout(RequestException):
    """The request timed out.

    Catching this error will catch both
    :exc:`~requests.exceptions.ConnectTimeout` and
    :exc:`~requests.exceptions.ReadTimeout` errors.
    """

@pytest.mark.parametrize('timeout', ((0.1, None), Urllib3Timeout(connect=0.1, read=None)))
def test_connect_timeout(self, timeout):
    try:
        requests.get(TARPIT, timeout=timeout)
        pytest.fail('The connect() request should time out.')
    except ConnectTimeout as e:
        assert isinstance(e, ConnectionError)
        assert isinstance(e, Timeout)

def _basic_auth_str(username: bytes | str, password: bytes | str) -> str:
    """Returns a Basic Auth string."""
    ...

def send(self, request: PreparedRequest, stream: bool=False, timeout: _t.TimeoutType=None, verify: _t.VerifyType=True, cert: _t.CertType=None, proxies: dict[str, str] | None=None) -> Response:
    """Sends PreparedRequest object. Returns Response object."""
    ...

def rebuild_proxies(self, prepared_request: PreparedRequest, proxies: dict[str, str] | None) -> dict[str, str]:
    """This method re-evaluates the proxy configuration by considering the"""
    ...

def send(self, request: PreparedRequest, stream: bool=False, timeout: _t.TimeoutType=None, verify: _t.VerifyType=True, cert: _t.CertType=None, proxies: dict[str, str] | None=None) -> Response:
    """Sends PreparedRequest object. Returns Response object."""
    ...

def merge_environment_settings(self, url: str, proxies: dict[str, str] | None, stream: bool | None, verify: _t.VerifyType | None, cert: _t.CertType) -> dict[str, Any]:
    """Check the environment and merge it with some settings."""
    ...

def proxy_manager_for(self, proxy: str, **proxy_kwargs: Any) -> Any:
    """Return urllib3 ProxyManager for the given proxy."""
    ...

class TestTimeout:

    def test_stream_timeout(self, httpbin):
        ...

    def test_invalid_timeout(self, httpbin, timeout, error_text):
        ...

    def test_none_timeout(self, httpbin, timeout):
        ...

    def test_read_timeout(self, httpbin, timeout):
        ...

    def test_connect_timeout(self, timeout):
        ...

    def test_total_timeout_connect(self, timeout):
        ...

    def test_encoded_methods(self, httpbin):
        ...

def register_hook(self, event: str, hook: Iterable[_t.HookType] | _t.HookType) -> None:
    """Properly register a hook."""
    ...

def __getitem__(self, name: str) -> str | None:
    """Dict-like __getitem__() for compatibility with client code. Throws"""
    ...

def __setitem__(self, name: str, value: str | Morsel[dict[str, str]] | None) -> None:
    """Dict-like __setitem__ for compatibility with client code. Throws
        exception if there is already a cookie of that name in the jar. In that
        case, use the more explicit set() method instead.
        """
    self.set(name, value)

class TestSuperLen:

    def test_io_streams(self, stream, value):
        ...

    def test_super_len_correctly_calculates_len_of_partially_read_file(self):
        ...

    def test_super_len_handles_files_raising_weird_errors_in_tell(self, error):
        ...

    def test_super_len_tell_ioerror(self, error):
        ...

    def test_string(self):
        ...

    def test_file(self, tmpdir, mode, warnings_num, recwarn):
        ...

    def test_tarfile_member(self, tmpdir):
        ...

    def test_super_len_with__len__(self):
        ...

    def test_super_len_with_no__len__(self):
        ...

    def test_super_len_with_tell(self):
        ...

    def test_super_len_with_fileno(self):
        ...

    def test_super_len_with_no_matches(self):
        ...

def cert_verify(self, conn: Any, url: str, verify: _t.VerifyType, cert: _t.CertType) -> None:
    """Verify a SSL certificate. This method should not be called from user"""
    ...

def test_stream_timeout(self, httpbin):
    try:
        requests.get(httpbin('delay/10'), timeout=2.0)
    except requests.exceptions.Timeout as e:
        assert 'Read timed out' in e.args[0].args[0]

def __iter__(self) -> Iterator[bytes]:
    """Allows you to use a response as an iterator."""
    return self.iter_content(128)