@runtime_checkable
class SupportsRead(Protocol[_T_co]):

    def read(self, length: int=..., /) -> _T_co:
        ...

class TestSuperLen:
    # [Enclosing Scope]


def test_super_len_correctly_calculates_len_of_partially_read_file(self):
    """Ensure that we handle partially consumed file like objects."""
    s = StringIO.StringIO()
    s.write('foobarbogus')
    assert super_len(s) == 0

class HTTPAdapter:
    # [Enclosing Scope]


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

class RequestEncodingMixin:
    # [Enclosing Scope]


@staticmethod
def _encode_params(data: _t.EncodableDataType) -> str | bytes | _t.SupportsRead[str | bytes]:
    """Encode parameters in a piece of data.

        Will successfully encode parameters when passed as a dict or a list of
        2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
        if parameters are supplied as a dict.
        """
    if isinstance(data, (str, bytes)):
        return data
    elif isinstance(data, _SupportsRead):
        return data
    elif hasattr(data, '__iter__'):
        result: list[tuple[bytes, bytes]] = []
        for k, vs in to_key_val_list(data):
            if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                vs = [vs]
            for v in vs:
                if v is not None:
                    result.append((k.encode('utf-8') if isinstance(k, str) else k, v.encode('utf-8') if isinstance(v, str) else v))
        return urlencode(result, doseq=True)
    else:
        return data

class Response:
    # [Enclosing Scope]


def __bool__(self) -> bool:
    """Returns True if :attr:`status_code` is less than 400.

        This attribute checks if the status code of the response is between
        400 and 600 to see if there was a client error or a server error. If
        the status code, is between 200 and 400, this will return True. This
        is **not** a check to see if the response code is ``200 OK``.
        """
    return self.ok

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
    """Returns True if :attr:`status_code` is less than 400, False if not.

        This attribute checks if the status code of the response is between
        400 and 600 to see if there was a client error or a server error. If
        the status code is between 200 and 400, this will return True. This
        is **not** a check to see if the response code is ``200 OK``.
        """
    try:
        self.raise_for_status()
    except HTTPError:
        return False
    return True

class ReadTimeout(Timeout):
    """The server did not send any data in the allotted amount of time."""

class SupportsRead:
    # [Enclosing Scope]


def read(self, length: int=..., /) -> _T_co:
    ...

class MockRequest:
    """Wraps a `requests.PreparedRequest` to mimic a `urllib2.Request`.

    The code in `http.cookiejar.CookieJar` expects this interface in order to correctly
    manage cookie policies, i.e., determine whether a cookie can be set, given the
    domains of the request and the cookie.

    The original request object is read-only. The client is responsible for collecting
    the new headers via `get_new_headers()` and interpreting them appropriately. You
    probably want `get_cookie_header`, defined below.
    """
    type: str

    def __init__(self, request: PreparedRequest) -> None:
        assert _is_prepared(request)
        self._r = request
        self._new_headers: dict[str, str] = {}
        self.type = urlparse(self._r.url).scheme

    def get_type(self) -> str:
        return self.type

    def get_host(self) -> str:
        return urlparse(self._r.url).netloc

    def get_origin_req_host(self) -> str:
        return self.get_host()

    def get_full_url(self) -> str:
        if not self._r.headers.get('Host'):
            return self._r.url
        host = to_native_string(self._r.headers['Host'], encoding='utf-8')
        parsed = urlparse(self._r.url)
        return urlunparse([parsed.scheme, host, parsed.path, parsed.params, parsed.query, parsed.fragment])

    def is_unverifiable(self) -> bool:
        return True

    def has_header(self, name: str) -> bool:
        return name in self._r.headers or name in self._new_headers

    def get_header(self, name: str, default: str | None=None) -> str | None:
        return self._r.headers.get(name, self._new_headers.get(name, default))

    def add_header(self, key: str, val: str) -> None:
        """cookiejar has no legitimate use for this method; add it back if you find one."""
        raise NotImplementedError('Cookie headers should be added with add_unredirected_header()')

    def add_unredirected_header(self, name: str, value: str) -> None:
        self._new_headers[name] = value

    def get_new_headers(self) -> dict[str, str]:
        return self._new_headers

    @property
    def unverifiable(self) -> bool:
        return self.is_unverifiable()

    @property
    def origin_req_host(self) -> str:
        return self.get_origin_req_host()

    @property
    def host(self) -> str:
        return self.get_host()

def test_rewind_body(self):
    data = io.BytesIO(b'the data')
    prep = requests.Request('GET', 'http://example.com', data=data).prepare()
    assert prep._body_position == 0
    assert prep.body.read() == b'the data'
    assert prep.body.read() == b''
    requests.utils.rewind_body(prep)
    assert prep.body.read() == b'the data'

@runtime_checkable
class SupportsItems(Protocol[_KT_co, _VT_co]):

    def items(self) -> Iterable[tuple[_KT_co, _VT_co]]:
        ...