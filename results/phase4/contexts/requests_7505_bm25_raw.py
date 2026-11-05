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

def test_rewind_partially_read_body(self):
    data = io.BytesIO(b'the data')
    data.read(4)
    prep = requests.Request('GET', 'http://example.com', data=data).prepare()
    assert prep._body_position == 4
    assert prep.body.read() == b'data'
    assert prep.body.read() == b''
    requests.utils.rewind_body(prep)
    assert prep.body.read() == b'data'

class ReadTimeout(Timeout):
    """The server did not send any data in the allotted amount of time."""

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

def test_response_is_iterable(self):
    r = requests.Response()
    io = StringIO.StringIO('abc')
    read_ = io.read

    def read_mock(amt, decode_content=None):
        return read_(amt)
    setattr(io, 'read', read_mock)
    r.raw = io
    assert next(iter(r))
    io.close()

def add_header(self, key: str, val: str) -> None:
    """cookiejar has no legitimate use for this method; add it back if you find one."""
    raise NotImplementedError('Cookie headers should be added with add_unredirected_header()')

def parse_dict_header(value: str) -> dict[str, str | None]:
    """Parse lists of key, value pairs as described by RFC 2068 Section 2 and
    convert them into a python dict:

    >>> d = parse_dict_header('foo="is a fish", bar="as well"')
    >>> type(d) is dict
    True
    >>> sorted(d.items())
    [('bar', 'as well'), ('foo', 'is a fish')]

    If there is no value for a key it will be `None`:

    >>> parse_dict_header('key_without_value')
    {'key_without_value': None}

    To create a header from the :class:`dict` again, use the
    :func:`dump_header` function.

    :param value: a string with a dict header.
    :return: :class:`dict`
    :rtype: dict
    """
    result: dict[str, str | None] = {}
    for item in _parse_list_header(value):
        if '=' not in item:
            result[item] = None
            continue
        name, value = item.split('=', 1)
        if value[:1] == value[-1:] == '"':
            value = unquote_header_value(value[1:-1])
        result[name] = value
    return result

def super_len(o: Any) -> int:
    total_length = None
    current_position = 0
    if not is_urllib3_1 and isinstance(o, str):
        o = o.encode('utf-8')
    if hasattr(o, '__len__'):
        total_length = len(o)
    elif hasattr(o, 'len'):
        total_length = o.len
    elif hasattr(o, 'fileno'):
        try:
            fileno = o.fileno()
        except (io.UnsupportedOperation, AttributeError):
            pass
        else:
            total_length = os.fstat(fileno).st_size
            if 'b' not in o.mode:
                warnings.warn("Requests has determined the content-length for this request using the binary size of the file: however, the file has been opened in text mode (i.e. without the 'b' flag in the mode). This may lead to an incorrect content-length. In Requests 3.0, support will be removed for files in text mode.", FileModeWarning)
    if hasattr(o, 'tell'):
        try:
            current_position = o.tell()
        except OSError:
            if total_length is not None:
                current_position = total_length
        else:
            if hasattr(o, 'seek') and total_length is None:
                try:
                    o.seek(0, 2)
                    total_length = o.tell()
                    o.seek(current_position or 0)
                except OSError:
                    total_length = 0
    if total_length is None:
        total_length = 0
    return max(0, total_length - current_position)