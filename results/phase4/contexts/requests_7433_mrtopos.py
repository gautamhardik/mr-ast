@staticmethod
def _encode_params(data: _t.EncodableDataType) -> str | bytes | _t.SupportsRead[str | bytes]:
    """Encode parameters in a piece of data."""
    ...

def __init__(self, data: Mapping[str, _VT] | Iterable[tuple[str, _VT]] | None=None, **kwargs: _VT) -> None:
    self._store = OrderedDict()
    if data is None:
        data = {}
    self.update(data, **kwargs)

def test_prepare_body_position_non_stream(self):
    data = b'the data'
    prep = requests.Request('GET', 'http://example.com', data=data).prepare()
    assert prep._body_position is None

def dispatch_hook(key: str, hooks: _t.HooksInputType | None, hook_data: Response, **kwargs: Any) -> Response:
    """Dispatches a hook dictionary on a given piece of data."""
    hooks_dict = hooks or {}
    hook_list: Iterable[_t.HookType] | _t.HookType | None = hooks_dict.get(key)
    if hook_list:
        if isinstance(hook_list, Callable):
            hook_list = [hook_list]
        for hook in hook_list:
            _hook_data = hook(hook_data, **kwargs)
            if _hook_data is not None:
                hook_data = _hook_data
    return hook_data

def test_rewind_body_no_seek(self):
    ...

def patch(url: _t.UriType, data: _t.DataType=None, **kwargs: Unpack[_t.DataKwargs]) -> Response:
    """Sends a PATCH request."""
    ...

def put(url: _t.UriType, data: _t.DataType=None, **kwargs: Unpack[_t.DataKwargs]) -> Response:
    """Sends a PUT request."""
    ...

def register_hook(self, event: str, hook: Iterable[_t.HookType] | _t.HookType) -> None:
    """Properly register a hook."""
    if event not in self.hooks:
        raise ValueError(f'Unsupported event specified, with event name "{event}"')
    if isinstance(hook, Callable):
        self.hooks[event].append(hook)
    elif hasattr(hook, '__iter__'):
        self.hooks[event].extend((h for h in hook if isinstance(h, Callable)))

def iter_content(self, chunk_size: int | None=1, decode_unicode: bool=False) -> Iterator[str | bytes]:
    """Iterates over the response data.  When stream=True is set on the"""
    ...

def test_rewind_body_failed_seek(self):
    ...

def test_rewind_body_failed_tell(self):
    ...

def request(method: str, url: _t.UriType, **kwargs: Unpack[_t.RequestKwargs]) -> Response:
    """Constructs and sends a :class:`Request <Request>`."""
    ...

def prepare_body(self, data: _t.DataType, files: _t.FilesType, json: _t.JsonType=None) -> None:
    """Prepares the given HTTP body data."""
    ...

def post(url: _t.UriType, data: _t.DataType=None, json: _t.JsonType=None, **kwargs: Unpack[_t.PostKwargs]) -> Response:
    """Sends a POST request."""
    ...

def iter_lines(self, chunk_size: int=ITER_CHUNK_SIZE, decode_unicode: bool=False, delimiter: str | bytes | None=None) -> Iterator[str | bytes]:
    """Iterates over the response data, one line at a time.  When"""
    ...

def patch(self, url: _t.UriType, data: _t.DataType=None, **kwargs: Unpack[_t.DataKwargs]) -> Response:
    """Sends a PATCH request. Returns :class:`Response` object."""
    ...

def put(self, url: _t.UriType, data: _t.DataType=None, **kwargs: Unpack[_t.DataKwargs]) -> Response:
    """Sends a PUT request. Returns :class:`Response` object."""
    ...

class RequestHooksMixin:
    hooks: dict[str, list[_t.HookType]]

    def register_hook(self, event: str, hook: Iterable[_t.HookType] | _t.HookType) -> None:
        """Properly register a hook."""
        ...

    def deregister_hook(self, event: str, hook: _t.HookType) -> bool:
        """Deregister a previously registered hook."""
        ...

def test_POSTBIN_SEEKED_OBJECT_WITH_NO_ITER(self, httpbin):
    ...

def post(self, url: _t.UriType, data: _t.DataType=None, json: _t.JsonType=None, **kwargs: Unpack[_t.PostKwargs]) -> Response:
    """Sends a POST request. Returns :class:`Response` object."""
    ...

def test_post_with_custom_mapping(self, httpbin):
    ...

def test_stream_with_auth_does_not_set_transfer_encoding_header(self, httpbin):
    """Ensure that a byte stream with size > 0 will not set both a Content-Length"""
    ...

def test_binary_put(self):
    request = requests.Request('PUT', 'http://example.com', data='ööö'.encode()).prepare()
    assert isinstance(request.body, bytes)

def dict_to_sequence(d: _t.SupportsItems[Any, Any] | Iterable[tuple[Any, Any]]) -> Iterable[tuple[Any, Any]]:
    """Returns an internal sequence dictionary update."""
    if isinstance(d, _SupportsItems):
        return d.items()
    return d

def test_rewind_body(self):
    data = io.BytesIO(b'the data')
    prep = requests.Request('GET', 'http://example.com', data=data).prepare()
    assert prep._body_position == 0
    assert prep.body.read() == b'the data'
    assert prep.body.read() == b''
    requests.utils.rewind_body(prep)
    assert prep.body.read() == b'the data'

def rewind_body(prepared_request: PreparedRequest) -> None:
    """Move file pointer back to its recorded starting position"""
    ...

def test_rewind_partially_read_body(self):
    data = io.BytesIO(b'the data')
    data.read(4)
    prep = requests.Request('GET', 'http://example.com', data=data).prepare()
    assert prep._body_position == 4
    assert prep.body.read() == b'data'
    assert prep.body.read() == b''
    requests.utils.rewind_body(prep)
    assert prep.body.read() == b'data'

def test_empty_stream_with_auth_does_not_set_content_length_header(self, httpbin):
    """Ensure that a byte stream with size 0 will not set both a Content-Length
        and Transfer-Encoding header.
        """
    auth = ('user', 'pass')
    url = httpbin('post')
    file_obj = io.BytesIO(b'')
    r = requests.Request('POST', url, auth=auth, data=file_obj)
    prepared_request = r.prepare()
    assert 'Transfer-Encoding' in prepared_request.headers
    assert 'Content-Length' not in prepared_request.headers

@staticmethod
def _encode_files(files: _t.FilesType, data: _t.RawDataType | None) -> tuple[bytes, str]:
    """Build the body for a multipart/form-data request."""
    ...

def test_content_length_for_bytes_data(httpbin):
    data = 'This is a string containing multi-byte UTF-8 ☃️'
    encoded_data = data.encode('utf-8')
    length = str(len(encoded_data))
    req = requests.Request('POST', httpbin('post'), data=encoded_data)
    p = req.prepare()
    assert p.headers['Content-Length'] == length

def prepare_auth(self, auth: _t.AuthType, url: _t.UriType='') -> None:
    """Prepares the given HTTP auth data."""
    ...

def test_custom_content_type(self, httpbin):
    ...

@pytest.mark.parametrize('files', ('foo', b'foo', bytearray(b'foo')))
def test_can_send_objects_with_files(self, httpbin, files):
    data = {'a': 'this is a string'}
    files = {'b': files}
    r = requests.Request('POST', httpbin('post'), data=data, files=files)
    p = r.prepare()
    assert 'multipart/form-data' in p.headers['Content-Type']

def test_response_iter_lines(self, httpbin):
    r = requests.get(httpbin('stream/4'), stream=True)
    assert r.status_code == 200
    it = r.iter_lines()
    next(it)
    assert len(list(it)) == 3

def test_chunked_upload_does_not_set_content_length_header(self, httpbin):
    """Ensure that requests with a generator body stream using"""
    ...

def super_len(o: Any) -> int:
    ...

def test_chunked_upload():
    """can safely send generators"""
    ...

@pytest.mark.skipif(is_urllib3_1, reason='urllib3 2.x encodes all strings to utf-8, urllib3 1.x uses latin-1')
def test_content_length_for_string_data_counts_bytes(httpbin):
    data = 'This is a string containing multi-byte UTF-8 ☃️'
    length = str(len(data.encode('utf-8')))
    req = requests.Request('POST', httpbin('post'), data=data)
    p = req.prepare()
    assert p.headers['Content-Length'] == length

def stream_decode_response_unicode(iterator: Iterable[bytes], r: Response) -> Generator[str | bytes, None, None]:
    """Stream decodes an iterator."""
    ...

def test_super_len_with_fileno(self):
    with open(__file__, 'rb') as f:
        length = super_len(f)
        file_data = f.read()
    assert length == len(file_data)

def get_netrc_auth(url: _t.UriType, raise_errors: bool=False) -> tuple[str, str] | None:
    """Returns the Requests tuple auth for a given url from netrc."""
    ...

@pytest.mark.xfail
def test_response_iter_lines_reentrant(self, httpbin):
    """Response.iter_lines() is not reentrant safe"""
    r = requests.get(httpbin('stream/4'), stream=True)
    assert r.status_code == 200
    next(r.iter_lines())
    assert len(list(r.iter_lines())) == 3

@pytest.mark.parametrize('data', ({'stuff': 'ëlïxr'}, {'stuff': 'ëlïxr'.encode()}, {'stuff': 'elixr'}, {'stuff': b'elixr'}))
def test_unicode_multipart_post(self, httpbin, data):
    with open(__file__, 'rb') as f:
        r = requests.post(httpbin('post'), data=data, files={'file': ('test_requests.py', f)})
    assert r.status_code == 200

def test_can_send_file_object_with_non_string_filename(self, httpbin):
    f = io.BytesIO()
    f.name = 2
    r = requests.Request('POST', httpbin('post'), files={'f': f})
    p = r.prepare()
    assert 'multipart/form-data' in p.headers['Content-Type']

def guess_filename(obj: Any) -> str | None:
    """Tries to guess the filename of the given object."""
    name = getattr(obj, 'name', None)
    if name and isinstance(name, (str, bytes)) and (name[0] != '<') and (name[-1] != '>'):
        return os.path.basename(name)

@pytest.mark.parametrize('data', ((('a', 'b'), ('c', 'd')), (('c', 'd'), ('a', 'b')), (('a', 'b'), ('c', 'd'), ('e', 'f'))))
def test_data_argument_accepts_tuples(data):
    """Ensure that the data argument will accept tuples of strings
    and properly encode them.
    """
    p = PreparedRequest()
    p.prepare(method='GET', url='http://www.example.com', data=data, hooks=default_hooks())
    assert p.body == urlencode(data)

def test_json_encodes_as_bytes():
    body = {'key': 'value'}
    p = PreparedRequest()
    p.prepare(method='GET', url='https://www.example.com/', json=body)
    assert isinstance(p.body, bytes)

def test_history_is_always_a_list(self, httpbin):
    """Show that even with redirects, Response.history is always a list."""
    resp = requests.get(httpbin('get'))
    assert isinstance(resp.history, list)
    resp = requests.get(httpbin('redirect/1'))
    assert isinstance(resp.history, list)
    assert not isinstance(resp.history, tuple)

def __init__(self, method=None, url=None, headers=None, files=None, data=None, params=None, auth=None, cookies=None, hooks=None, json=None):
    ...

def test_chunked_upload_doesnt_skip_host_header():
    """Ensure we don't omit all Host headers with chunked requests."""
    ...

def test_manual_redirect_with_partial_body_read(self, httpbin):
    ...

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

def test_chunked_upload_uses_only_specified_host_header():
    """Ensure we use only the specified Host header for chunked requests."""
    ...

def test_json_param_post_should_not_override_data_param(self, httpbin):
    r = requests.Request(method='POST', url=httpbin('post'), data={'stuff': 'elixr'}, json={'music': 'flute'})
    prep = r.prepare()
    assert 'stuff=elixr' == prep.body

def test_unicode_multipart_post_fieldnames(self, httpbin):
    ...

def test_response_decode_unicode(self):
    """When called with decode_unicode, Response.iter_content should always"""
    ...

def _validate_header_part(header: tuple[str | bytes, str | bytes], header_part: str | bytes, header_validator_index: int) -> None:
    ...

def from_key_val_list(value):
    ...