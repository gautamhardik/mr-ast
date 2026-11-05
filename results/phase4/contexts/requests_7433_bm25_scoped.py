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

class CaseInsensitiveDict:
    # [Enclosing Scope]


def __init__(self, data: Mapping[str, _VT] | Iterable[tuple[str, _VT]] | None=None, **kwargs: _VT) -> None:
    self._store = OrderedDict()
    if data is None:
        data = {}
    self.update(data, **kwargs)

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

class RequestHooksMixin:
    # [Enclosing Scope]


def register_hook(self, event: str, hook: Iterable[_t.HookType] | _t.HookType) -> None:
    """Properly register a hook."""
    if event not in self.hooks:
        raise ValueError(f'Unsupported event specified, with event name "{event}"')
    if isinstance(hook, Callable):
        self.hooks[event].append(hook)
    elif hasattr(hook, '__iter__'):
        self.hooks[event].extend((h for h in hook if isinstance(h, Callable)))

class Response:
    # [Enclosing Scope]


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

def post(url: _t.UriType, data: _t.DataType=None, json: _t.JsonType=None, **kwargs: Unpack[_t.PostKwargs]) -> Response:
    """Sends a POST request.

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param \\*\\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    return request('post', url, data=data, json=json, **kwargs)