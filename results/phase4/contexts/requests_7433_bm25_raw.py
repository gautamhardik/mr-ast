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

    class BadFileObj:

        def __init__(self, data):
            self.data = data

        def tell(self):
            return 0

        def __iter__(self):
            return
    data = BadFileObj('the data')
    prep = requests.Request('GET', 'http://example.com', data=data).prepare()
    assert prep._body_position == 0
    with pytest.raises(UnrewindableBodyError) as e:
        requests.utils.rewind_body(prep)
    assert 'Unable to rewind request body' in str(e)

def patch(url: _t.UriType, data: _t.DataType=None, **kwargs: Unpack[_t.DataKwargs]) -> Response:
    """Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param \\*\\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('patch', url, data=data, **kwargs)

def put(url: _t.UriType, data: _t.DataType=None, **kwargs: Unpack[_t.DataKwargs]) -> Response:
    """Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param \\*\\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('put', url, data=data, **kwargs)

def register_hook(self, event: str, hook: Iterable[_t.HookType] | _t.HookType) -> None:
    """Properly register a hook."""
    if event not in self.hooks:
        raise ValueError(f'Unsupported event specified, with event name "{event}"')
    if isinstance(hook, Callable):
        self.hooks[event].append(hook)
    elif hasattr(hook, '__iter__'):
        self.hooks[event].extend((h for h in hook if isinstance(h, Callable)))

def iter_content(self, chunk_size: int | None=1, decode_unicode: bool=False) -> Iterator[str | bytes]:
    """Iterates over the response data.  When stream=True is set on the
        request, this avoids reading the content at once into memory for
        large responses.  The chunk size is the number of bytes it should
        read into memory.  This is not necessarily the length of each item
        returned as decoding can take place.

        chunk_size must be of type int or None. A value of None will
        function differently depending on the value of `stream`.
        stream=True will read data as it arrives in whatever size the
        chunks are received. If stream=False, data is returned as
        a single chunk.

        If decode_unicode is True, content will be decoded using encoding
        information from the response. If no encoding information is available,
        bytes will be returned. This can be bypassed by manually setting
        `encoding` on the response.
        """

    def generate() -> Generator[bytes, None, None]:
        if hasattr(self.raw, 'stream'):
            try:
                yield from self.raw.stream(chunk_size, decode_content=True)
            except ProtocolError as e:
                raise ChunkedEncodingError(e)
            except DecodeError as e:
                raise ContentDecodingError(e)
            except ReadTimeoutError as e:
                raise ConnectionError(e)
            except SSLError as e:
                raise RequestsSSLError(e)
        else:
            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        self._content_consumed = True
    if self._content_consumed and isinstance(self._content, bool):
        raise StreamConsumedError()
    elif chunk_size is not None and (not isinstance(chunk_size, int)):
        raise TypeError(f'chunk_size must be an int, it is instead a {type(chunk_size)}.')
    if self._content_consumed:
        content = cast(bytes, self._content)
        chunks = iter_slices(content, chunk_size)
    else:
        chunks = generate()
    if decode_unicode:
        chunks = stream_decode_response_unicode(chunks, self)
    return chunks

def test_rewind_body_failed_seek(self):

    class BadFileObj:

        def __init__(self, data):
            self.data = data

        def tell(self):
            return 0

        def seek(self, pos, whence=0):
            raise OSError()

        def __iter__(self):
            return
    data = BadFileObj('the data')
    prep = requests.Request('GET', 'http://example.com', data=data).prepare()
    assert prep._body_position == 0
    with pytest.raises(UnrewindableBodyError) as e:
        requests.utils.rewind_body(prep)
    assert 'error occurred when rewinding request body' in str(e)

def test_rewind_body_failed_tell(self):

    class BadFileObj:

        def __init__(self, data):
            self.data = data

        def tell(self):
            raise OSError()

        def __iter__(self):
            return
    data = BadFileObj('the data')
    prep = requests.Request('GET', 'http://example.com', data=data).prepare()
    assert prep._body_position is not None
    with pytest.raises(UnrewindableBodyError) as e:
        requests.utils.rewind_body(prep)
    assert 'Unable to rewind request body' in str(e)

def request(method: str, url: _t.UriType, **kwargs: Unpack[_t.RequestKwargs]) -> Response:
    """Constructs and sends a :class:`Request <Request>`.

    :param method: method for the new :class:`Request` object: ``GET``, ``OPTIONS``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content_type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
        to add for the file.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response

    Usage::

      >>> import requests
      >>> req = requests.request('GET', 'https://httpbin.org/get')
      >>> req
      <Response [200]>
    """
    with sessions.Session() as session:
        return session.request(method=method, url=url, **kwargs)

def test_binary_put(self):
    request = requests.Request('PUT', 'http://example.com', data='ööö'.encode()).prepare()
    assert isinstance(request.body, bytes)