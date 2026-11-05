class UJSONResponse(JSONResponse):
    """
    JSON response using the high-performance ujson library to serialize data to JSON.

    Read more about it in the
    [FastAPI docs for Custom Response - HTML, Stream, File, others](https://fastapi.tiangolo.com/advanced/custom-response/).
    """

    def render(self, content: Any) -> bytes:
        assert ujson is not None, 'ujson must be installed to use UJSONResponse'
        return ujson.dumps(content, ensure_ascii=False).encode('utf-8')

class ORJSONResponse(JSONResponse):
    """
    JSON response using the high-performance orjson library to serialize data to JSON.

    Read more about it in the
    [FastAPI docs for Custom Response - HTML, Stream, File, others](https://fastapi.tiangolo.com/advanced/custom-response/).
    """

    def render(self, content: Any) -> bytes:
        assert orjson is not None, 'orjson must be installed to use ORJSONResponse'
        return orjson.dumps(content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY)

def render(self, content: Any) -> bytes:
    assert ujson is not None, 'ujson must be installed to use UJSONResponse'
    return ujson.dumps(content, ensure_ascii=False).encode('utf-8')

def render(self, content: Any) -> bytes:
    assert orjson is not None, 'orjson must be installed to use ORJSONResponse'
    return orjson.dumps(content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY)

class CustomORJSONResponse(Response):
    media_type = 'application/json'

    def render(self, content: Any) -> bytes:
        assert orjson is not None, 'orjson must be installed'
        return orjson.dumps(content, option=orjson.OPT_INDENT_2)

class ORJSONResponse(JSONResponse):
    media_type = 'application/x-orjson'

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content)

def render(self, content: Any) -> bytes:
    assert orjson is not None, 'orjson must be installed'
    return orjson.dumps(content, option=orjson.OPT_INDENT_2)

# Module: tests.test_orjson_response_class


def test_orjson_non_str_keys():
    with client:
        response = client.get('/orjson_non_str_keys')
    assert response.json() == {'msg': 'Hello World', '1': 1}

@app.get('/orjson_non_str_keys')
def get_orjson_non_str_keys():
    key = quoted_name(value='msg', quote=False)
    return {key: 'Hello World', 1: 1}

@app.get('/items/', response_class=ORJSONResponse)
async def read_items():
    return ORJSONResponse([{'item_id': 'Foo'}])

@app.get('/items/', response_class=UJSONResponse)
async def read_items():
    return [{'item_id': 'Foo'}]

# Module: tests.test_additional_responses_union_duplicate_anyof


# Module: tests.test_list_bytes_file_order_preserved_issue_14811


@app.get('/fastapi', response_class=RedirectResponse)
async def redirect_fastapi():
    return 'https://fastapi.tiangolo.com'

def test_fastapi_cli_not_installed():
    with patch.object(fastapi.cli, 'cli_main', None):
        with pytest.raises(RuntimeError) as exc_info:
            fastapi.cli.main()
        assert 'To use the fastapi command, please install' in str(exc_info.value)

@app.get('/', response_class=CustomORJSONResponse)
async def main():
    return {'message': 'Hello World'}

def render(self, content: Any) -> bytes:
    return orjson.dumps(content)

def test_router_a():
    with client:
        response = client.get('/a')
    assert response.json() == {'msg': 'Hello A'}
    assert response.headers['content-type'] == orjson_type

def test_router_a_a():
    with client:
        response = client.get('/a/a')
    assert response.json() == {'msg': 'Hello A A'}
    assert response.headers['content-type'] == orjson_type

def test_app():
    with client:
        response = client.get('/')
    assert response.json() == {'msg': 'Hello World'}
    assert response.headers['content-type'] == orjson_type

def test_redirect_response_class():
    response = client.get('/fastapi', follow_redirects=False)
    assert response.status_code == 307
    assert response.headers['location'] == 'https://fastapi.tiangolo.com'

@pytest.mark.xfail(reason='Code example is not valid. See https://github.com/fastapi/fastapi/issues/12419')
def test_query_params_str_validations_no_query(client: TestClient):
    response = client.get('/items/')
    assert response.status_code == 200
    assert response.json() == {'items': [{'item_id': 'Foo'}, {'item_id': 'Bar'}]}

# Module: fastapi.dependencies.models


# Module: fastapi.openapi.models


@pytest.mark.xfail(reason='Code example is not valid. See https://github.com/fastapi/fastapi/issues/12419')
def test_query_params_str_validations_empty_str(client: TestClient):
    response = client.get('/items/?q=')
    assert response.status_code == 200
    assert response.json() == {'items': [{'item_id': 'Foo'}, {'item_id': 'Bar'}]}

def test_openapi_schema():
    response = client.get('/openapi.json')
    assert response.status_code == 200, response.text
    assert response.json() == snapshot({'openapi': '3.1.0', 'info': {'title': 'FastAPI', 'version': '0.1.0'}, 'paths': {'/fastapi': {'get': {'summary': 'Redirect Fastapi', 'operationId': 'redirect_fastapi_fastapi_get', 'responses': {'307': {'description': 'Successful Response'}}}}}})

def get_swagger_ui_html(*, openapi_url: str, title: str, swagger_js_url: str='https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js', swagger_css_url: str='https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css', swagger_favicon_url: str='https://fastapi.tiangolo.com/img/favicon.png', oauth2_redirect_url: str | None=None, init_oauth: dict[str, Any] | None=None, swagger_ui_parameters: dict[str, Any] | None=None) -> HTMLResponse:
    """Generate and return the HTML  that loads Swagger UI for the interactive"""
    ...

def add_task(self, func: Annotated[Callable[P, Any], Doc('\n                The function to call after the response is sent.\n\n                It can be a regular `def` function or an `async def` function.\n                ')], *args: P.args, **kwargs: P.kwargs) -> None:
    """
        Add a function to be called in the background after the response is sent.

        Read more about it in the
        [FastAPI docs for Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/).
        """
    return super().add_task(func, *args, **kwargs)

class _DefaultLifespan:
    """
    Default lifespan context manager that runs on_startup and on_shutdown handlers.

    This is a copy of the Starlette _DefaultLifespan class that was removed
    in Starlette. FastAPI keeps it to maintain backward compatibility with
    on_startup and on_shutdown event handlers.

    Ref: https://github.com/Kludex/starlette/pull/3117
    """

    def __init__(self, router: 'APIRouter') -> None:
        self._router = router

    async def __aenter__(self) -> None:
        await self._router._startup()

    async def __aexit__(self, *exc_info: object) -> None:
        await self._router._shutdown()

    def __call__(self: _T, app: object) -> _T:
        return self

def main() -> None:
    if not cli_main:
        message = 'To use the fastapi command, please install "fastapi[standard]":\n\n\tpip install "fastapi[standard]"\n'
        print(message)
        raise RuntimeError(message)
    cli_main()

def __init__(self, status_code: int, detail: Any=None, headers: Mapping[str, str] | None=None) -> None:
    ...

# Module: fastapi.responses


def get_redoc_html(*, openapi_url: str, title: str, redoc_js_url: str='https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js', redoc_favicon_url: str='https://fastapi.tiangolo.com/img/favicon.png', with_google_fonts: bool=True) -> HTMLResponse:
    """Generate and return the HTML response that loads ReDoc for the alternative"""
    ...

# Module: fastapi.__init__


class OAuth2(SecurityBase):
    """This is the base class for OAuth2 authentication, an instance of it would be used"""

    def __init__(self, *, flows: OAuthFlowsModel | dict[str, dict[str, Any]]=OAuthFlowsModel(), scheme_name: str | None=None, description: str | None=None, auto_error: bool=True):
        ...

    def make_not_authenticated_error(self) -> HTTPException:
        """The OAuth 2 specification doesn't define the challenge that should be used,"""
        ...

    async def __call__(self, request: Request) -> str | None:
        ...

# Module: tests.test_fastapi_cli


# Module: tests.test_file_and_form_order_issue_9116


def Query(default=Undefined, *, default_factory=_Unset, alias=None, alias_priority=_Unset, validation_alias=None, serialization_alias=None, title=None, description=None, gt=None, ge=None, lt=None, le=None, min_length=None, max_length=None, pattern=None, regex=None, discriminator=None, strict=_Unset, multiple_of=_Unset, allow_inf_nan=_Unset, max_digits=_Unset, decimal_places=_Unset, examples=None, example=_Unset, openapi_examples=None, deprecated=None, include_in_schema=True, json_schema_extra=None, **extra):
    ...

class HTTPBasic(HTTPBase):
    """HTTP Basic authentication."""

    def __init__(self, *, scheme_name: str | None=None, realm: str | None=None, description: str | None=None, auto_error: bool=True):
        ...

    def make_authenticate_headers(self) -> dict[str, str]:
        ...

    async def __call__(self, request: Request) -> HTTPBasicCredentials | None:
        ...

def test_openapi_schema():
    ...

def Security(dependency: Callable[..., Any] | None=None, *, scopes: Sequence[str] | None=None, use_cache: bool=True) -> Any:
    """Declare a FastAPI Security dependency."""
    ...

def test_fastapi_cli():
    result = subprocess.run([sys.executable, '-m', 'coverage', 'run', '-m', 'fastapi', 'dev', 'non_existent_file.py'], capture_output=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    assert result.returncode == 1, result.stdout
    assert 'Path does not exist non_existent_file.py' in result.stdout

class HTTPBasicCredentials(BaseModel):
    """
    The HTTP Basic credentials given as the result of using `HTTPBasic` in a
    dependency.

    Read more about it in the
    [FastAPI docs for HTTP Basic Auth](https://fastapi.tiangolo.com/advanced/security/http-basic-auth/).
    """
    username: Annotated[str, Doc('The HTTP Basic username.')]
    password: Annotated[str, Doc('The HTTP Basic password.')]

def test_fastapi_error(mod: ModuleType):
    client = TestClient(mod.app)
    with pytest.raises(FastAPIError) as exc_info:
        client.get('/items/portal-gun')
    assert 'raising an exception and a dependency with yield' in exc_info.value.args[0]

class OAuth2PasswordBearer(OAuth2):
    """OAuth2 flow for authentication using a bearer token obtained with a password."""

    def __init__(self, tokenUrl: str, scheme_name: str | None=None, scopes: dict[str, str] | None=None, description: str | None=None, auto_error: bool=True, refreshUrl: str | None=None):
        ...

    async def __call__(self, request: Request) -> str | None:
        ...

def Depends(dependency: Callable[..., Any] | None=None, *, use_cache: bool=True, scope: Literal['function', 'request'] | None=None) -> Any:
    """Declare a FastAPI dependency."""
    ...

# Module: fastapi._compat.v2


def test_post_body(client: TestClient):
    data = [{'url': 'http://example.com/', 'name': 'Example'}, {'url': 'http://fastapi.tiangolo.com/', 'name': 'FastAPI'}]
    response = client.post('/images/multiple', json=data)
    assert response.status_code == 200, response.text
    assert response.json() == data

class HTTPException(StarletteHTTPException):
    """An HTTP exception you can raise in your own code to show errors to the client."""

    def __init__(self, status_code: int, detail: Any=None, headers: Mapping[str, str] | None=None) -> None:
        ...