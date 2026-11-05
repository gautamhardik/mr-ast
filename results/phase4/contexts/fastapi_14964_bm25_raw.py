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

def get_swagger_ui_html(*, openapi_url: Annotated[str, Doc('\n            The OpenAPI URL that Swagger UI should load and use.\n\n            This is normally done automatically by FastAPI using the default URL\n            `/openapi.json`.\n\n            Read more about it in the\n            [FastAPI docs for Conditional OpenAPI](https://fastapi.tiangolo.com/how-to/conditional-openapi/#conditional-openapi-from-settings-and-env-vars)\n            ')], title: Annotated[str, Doc('\n            The HTML `<title>` content, normally shown in the browser tab.\n\n            Read more about it in the\n            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)\n            ')], swagger_js_url: Annotated[str, Doc('\n            The URL to use to load the Swagger UI JavaScript.\n\n            It is normally set to a CDN URL.\n\n            Read more about it in the\n            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)\n            ')]='https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js', swagger_css_url: Annotated[str, Doc('\n            The URL to use to load the Swagger UI CSS.\n\n            It is normally set to a CDN URL.\n\n            Read more about it in the\n            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)\n            ')]='https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css', swagger_favicon_url: Annotated[str, Doc('\n            The URL of the favicon to use. It is normally shown in the browser tab.\n            ')]='https://fastapi.tiangolo.com/img/favicon.png', oauth2_redirect_url: Annotated[str | None, Doc('\n            The OAuth2 redirect URL, it is normally automatically handled by FastAPI.\n\n            Read more about it in the\n            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)\n            ')]=None, init_oauth: Annotated[dict[str, Any] | None, Doc('\n            A dictionary with Swagger UI OAuth2 initialization configurations.\n\n            Read more about the available configuration options in the\n            [Swagger UI docs](https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/).\n            ')]=None, swagger_ui_parameters: Annotated[dict[str, Any] | None, Doc('\n            Configuration parameters for Swagger UI.\n\n            It defaults to [swagger_ui_default_parameters][fastapi.openapi.docs.swagger_ui_default_parameters].\n\n            Read more about it in the\n            [FastAPI docs about how to Configure Swagger UI](https://fastapi.tiangolo.com/how-to/configure-swagger-ui/).\n            ')]=None) -> HTMLResponse:
    """
    Generate and return the HTML  that loads Swagger UI for the interactive
    API docs (normally served at `/docs`).

    You would only call this function yourself if you needed to override some parts,
    for example the URLs to use to load Swagger UI's JavaScript and CSS.

    Read more about it in the
    [FastAPI docs for Configure Swagger UI](https://fastapi.tiangolo.com/how-to/configure-swagger-ui/)
    and the [FastAPI docs for Custom Docs UI Static Assets (Self-Hosting)](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/).
    """
    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)
    html = f"""\n    <!DOCTYPE html>\n    <html>\n    <head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">\n    <link rel="shortcut icon" href="{swagger_favicon_url}">\n    <title>{title}</title>\n    </head>\n    <body>\n    <div id="swagger-ui">\n    </div>\n    <script src="{swagger_js_url}"></script>\n    <!-- `SwaggerUIBundle` is now available on the page -->\n    <script>\n    const ui = SwaggerUIBundle({{\n        url: '{openapi_url}',\n    """
    for key, value in current_swagger_ui_parameters.items():
        html += f'{json.dumps(key)}: {json.dumps(jsonable_encoder(value))},\n'
    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"
    html += '\n    presets: [\n        SwaggerUIBundle.presets.apis,\n        SwaggerUIBundle.SwaggerUIStandalonePreset\n        ],\n    })'
    if init_oauth:
        html += f'\n        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})\n        '
    html += '\n    </script>\n    </body>\n    </html>\n    '
    return HTMLResponse(html)

@deprecated('\n        on_event is deprecated, use lifespan event handlers instead.\n\n        Read more about it in the\n        [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).\n        ')
def on_event(self, event_type: Annotated[str, Doc('\n                The type of event. `startup` or `shutdown`.\n                ')]) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """
        Add an event handler for the application.

        `on_event` is deprecated, use `lifespan` event handlers instead.

        Read more about it in the
        [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/#alternative-events-deprecated).
        """
    return self.router.on_event(event_type)

@deprecated('\n        on_event is deprecated, use lifespan event handlers instead.\n\n        Read more about it in the\n        [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).\n        ')
def on_event(self, event_type: Annotated[str, Doc('\n                The type of event. `startup` or `shutdown`.\n                ')]) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """
        Add an event handler for the router.

        `on_event` is deprecated, use `lifespan` event handlers instead.

        Read more about it in the
        [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/#alternative-events-deprecated).
        """

    def decorator(func: DecoratedCallable) -> DecoratedCallable:
        self.add_event_handler(event_type, func)
        return func
    return decorator

def add_task(self, func: Annotated[Callable[P, Any], Doc('\n                The function to call after the response is sent.\n\n                It can be a regular `def` function or an `async def` function.\n                ')], *args: P.args, **kwargs: P.kwargs) -> None:
    """
        Add a function to be called in the background after the response is sent.

        Read more about it in the
        [FastAPI docs for Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/).
        """
    return super().add_task(func, *args, **kwargs)

# Module: fastapi.responses


# Module: fastapi.__init__


# Module: tests.test_fastapi_cli


# Module: tests.test_file_and_form_order_issue_9116


# Module: fastapi._compat.v2
