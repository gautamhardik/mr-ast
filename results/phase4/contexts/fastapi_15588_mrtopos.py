class PartialGitHubEvent(BaseModel):
    pull_request: PartialGitHubEventIssue | None = None

class PartialGitHubEventIssue(BaseModel):
    number: int | None = None

@app.command()
def make_pr(*, language: Annotated[str | None, typer.Option(envvar='LANGUAGE')]=None, command: Annotated[str | None, typer.Option(envvar='COMMAND')]=None, github_token: Annotated[str, typer.Option(envvar='GITHUB_TOKEN')], github_repository: Annotated[str, typer.Option(envvar='GITHUB_REPOSITORY')], commit_in_place: Annotated[bool, typer.Option(envvar='COMMIT_IN_PLACE', show_default=True)]=False) -> None:
    ...

@app.get('/items/stream-sse-event', response_class=EventSourceResponse)
async def sse_items_event():
    yield ServerSentEvent(data='hello', event='greeting', id='1')
    yield ServerSentEvent(data={'key': 'value'}, event='json-data', id='2')
    yield ServerSentEvent(comment='just a comment')
    yield ServerSentEvent(data='retry-test', retry=5000)

def get_graphql_pr_edges(*, settings: Settings, after: str | None=None) -> list[PullRequestEdge]:
    data = get_graphql_response(settings=settings, query=prs_query, after=after)
    graphql_response = PRsResponse.model_validate(data)
    return graphql_response.data.repository.pullRequests.edges

@app.get('/items/stream-raw', response_class=EventSourceResponse)
async def sse_items_raw():
    yield ServerSentEvent(raw_data='plain text without quotes')
    yield ServerSentEvent(raw_data='<div>html fragment</div>', event='html')
    yield ServerSentEvent(raw_data='cpu,87.3,1709145600', event='csv')

def get_pr_nodes(settings: Settings) -> list[PullRequestNode]:
    pr_nodes: list[PullRequestNode] = []
    pr_edges = get_graphql_pr_edges(settings=settings)
    while pr_edges:
        for edge in pr_edges:
            pr_nodes.append(edge.node)
        last_edge = pr_edges[-1]
        pr_edges = get_graphql_pr_edges(settings=settings, after=last_edge.cursor)
    return pr_nodes

@app.post('/chat/stream', response_class=EventSourceResponse)
async def stream_chat(prompt: Prompt) -> AsyncIterable[ServerSentEvent]:
    words = prompt.text.split()
    for word in words:
        yield ServerSentEvent(data=word, event='token')
    yield ServerSentEvent(raw_data='[DONE]', event='done')

def create_comment(*, settings: Settings, discussion_id: str, body: str) -> Comment:
    data = get_graphql_response(settings=settings, query=add_comment_mutation, discussion_id=discussion_id, body=body)
    response = AddCommentResponse.model_validate(data)
    return response.data.addDiscussionComment.comment

class ServerSentEvent(BaseModel):
    """Represents a single Server-Sent Event."""
    data: Any = None
    raw_data: str | None = None
    event: str | None = None
    id: Annotated[str | None, AfterValidator(_check_id_no_null)] = None
    retry: Annotated[int | None, Field(ge=0)] = None
    comment: str | None = None

    @model_validator(mode='after')
    def _check_data_exclusive(self) -> 'ServerSentEvent':
        ...

def get_contributors(pr_nodes: list[PullRequestNode]) -> ContributorsResults:
    ...

def get_graphql_translation_discussion_comments_edges(*, settings: Settings, discussion_number: int, after: str | None=None) -> list[CommentsEdge]:
    data = get_graphql_response(settings=settings, query=translation_discussion_query, discussion_number=discussion_number, after=after)
    graphql_response = CommentsResponse.model_validate(data)
    return graphql_response.data.repository.discussion.comments.edges

def test_server_sent_event_null_id_rejected():
    with pytest.raises(ValueError, match='null'):
        ServerSentEvent(data='test', id='has\x00null')

def test_server_sent_event_negative_retry_rejected():
    with pytest.raises(ValueError):
        ServerSentEvent(data='test', retry=-1)

def test_server_sent_event_float_retry_rejected():
    with pytest.raises(ValueError):
        ServerSentEvent(data='test', retry=1.5)

def main() -> None:
    ...

def main() -> None:
    ...

def get_graphql_question_discussion_edges(*, settings: Settings, after: str | None=None) -> list[DiscussionsEdge]:
    with rate_limiter:
        data = get_graphql_response(settings=settings, query=discussions_query, after=after, category_id=questions_category_id)
    rate_limiter.update_request_info(cost=data['data']['rateLimit']['cost'], remaining=data['data']['rateLimit']['remaining'], reset_at=data['data']['rateLimit']['resetAt'])
    graphql_response = DiscussionsResponse.model_validate(data)
    return graphql_response.data.repository.discussions.edges

@app.get('/items/stream', response_class=EventSourceResponse)
async def stream_items(last_event_id: Annotated[int | None, Header()]=None) -> AsyncIterable[ServerSentEvent]:
    start = last_event_id + 1 if last_event_id is not None else 0
    for i, item in enumerate(items):
        if i < start:
            continue
        yield ServerSentEvent(data=item, id=str(i))

@app.get('/items/stream', response_class=EventSourceResponse)
async def stream_items() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(comment='stream of item updates')
    for i, item in enumerate(items):
        yield ServerSentEvent(data=item, event='item_update', id=str(i + 1), retry=5000)

@app.get('/items/stream-string', response_class=EventSourceResponse)
async def sse_items_string():
    yield ServerSentEvent(data='plain text data')

class EventSourceResponse(StreamingResponse):
    """Streaming response with `text/event-stream` media type.

    Use as `response_class=EventSourceResponse` on a *path operation* that uses `yield`
    to enable Server Sent Events (SSE) responses.

    Works with **any HTTP method** (`GET`, `POST`, etc.), which makes it compatible
    with protocols like MCP that stream SSE over `POST`.

    The actual encoding logic lives in the FastAPI routing layer. This class
    serves mainly as a marker and sets the correct `Content-Type`.
    """
    media_type = 'text/event-stream'

class UpdateCommentData(BaseModel):
    updateDiscussionComment: UpdateDiscussionComment

class AddCommentData(BaseModel):
    addDiscussionComment: AddDiscussionComment

# Module: tests.test_response_change_status_code


@model_validator(mode='after')
def _check_data_exclusive(self) -> 'ServerSentEvent':
    if self.data is not None and self.raw_data is not None:
        raise ValueError("Cannot set both 'data' and 'raw_data' on the same ServerSentEvent. Use 'data' for JSON-serialized payloads or 'raw_data' for pre-formatted strings.")
    return self

def test_broken_session_data_no_raise():
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get('/broken-session-data')
    assert response.status_code == 500
    assert response.text == 'Internal Server Error'

@app.get('/logs/stream', response_class=EventSourceResponse)
async def stream_logs() -> AsyncIterable[ServerSentEvent]:
    logs = ['2025-01-01 INFO  Application started', '2025-01-01 DEBUG Connected to database', '2025-01-01 WARN  High memory usage detected']
    for log_line in logs:
        yield ServerSentEvent(raw_data=log_line)

@app.get('/items/stream-mixed', response_class=EventSourceResponse)
async def sse_items_mixed() -> AsyncIterable[Item]:
    yield items[0]
    yield ServerSentEvent(data='custom-event', event='special')
    yield items[1]

def get_discussion_nodes(settings: Settings) -> list[DiscussionsNode]:
    discussion_nodes: list[DiscussionsNode] = []
    discussion_edges = get_graphql_question_discussion_edges(settings=settings)
    while discussion_edges:
        for discussion_edge in discussion_edges:
            discussion_nodes.append(discussion_edge.node)
        last_edge = discussion_edges[-1]
        discussion_edges = get_graphql_question_discussion_edges(settings=settings, after=last_edge.cursor)
    return discussion_nodes

def get_graphql_translation_discussion_comments(*, settings: Settings, discussion_number: int) -> list[Comment]:
    comment_nodes: list[Comment] = []
    discussion_edges = get_graphql_translation_discussion_comments_edges(settings=settings, discussion_number=discussion_number)
    while discussion_edges:
        for discussion_edge in discussion_edges:
            comment_nodes.append(discussion_edge.node)
        last_edge = discussion_edges[-1]
        discussion_edges = get_graphql_translation_discussion_comments_edges(settings=settings, discussion_number=discussion_number, after=last_edge.cursor)
    return comment_nodes

class CommentsDiscussion(BaseModel):
    comments: Comments

class AllDiscussionsDiscussionNode(BaseModel):
    title: str
    id: str
    number: int
    labels: AllDiscussionsDiscussionLabels

class UpdateDiscussionComment(BaseModel):
    comment: Comment

class AddDiscussionComment(BaseModel):
    comment: Comment

class AllDiscussionsDiscussionLabels(BaseModel):
    edges: list[AllDiscussionsLabelsEdge]

def main() -> None:
    ...

def test_sse_events_with_fields(client: TestClient):
    ...

def test_broken_no_raise():
    """When a dependency with yield raises after the yield (not in an except), the"""
    ...

def test_broken_session_stream_no_raise():
    """When a dependency with yield raises after the streaming response already started"""
    ...

def test_resume_from_last_event_id(client: TestClient):
    response = client.get('/items/stream', headers={'last-event-id': '0'})
    assert response.status_code == 200, response.text
    data_lines = [line for line in response.text.strip().split('\n') if line.startswith('data: ')]
    assert len(data_lines) == 2
    id_lines = [line for line in response.text.strip().split('\n') if line.startswith('id: ')]
    assert id_lines == ['id: 1', 'id: 2']

def test_sse_on_router_included_in_app(client: TestClient):
    response = client.get('/api/events')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/event-stream; charset=utf-8'
    data_lines = [line for line in response.text.strip().split('\n') if line.startswith('data: ')]
    assert len(data_lines) == 2

def get_graphql_response(*, settings: Settings, query: str, after: str | None=None, category_id: str | None=None, discussion_number: int | None=None, discussion_id: str | None=None, comment_id: str | None=None, body: str | None=None) -> dict[str, Any]:
    ...

class CommentsRepository(BaseModel):
    discussion: CommentsDiscussion

def test_raw_data_sent_without_json_encoding(client: TestClient):
    """raw_data is sent as-is, not JSON-encoded."""
    ...

class DiscussionExpertsResults(BaseModel):
    commenters: Counter[str]
    last_month_commenters: Counter[str]
    three_months_commenters: Counter[str]
    six_months_commenters: Counter[str]
    one_year_commenters: Counter[str]
    authors: dict[str, Author]

def test_post_method_sse(client: TestClient):
    """SSE should work with POST (needed for MCP compatibility)."""
    response = client.post('/items/stream-post')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/event-stream; charset=utf-8'
    data_lines = [line for line in response.text.strip().split('\n') if line.startswith('data: ')]
    assert len(data_lines) == 3

def test_data_and_raw_data_mutually_exclusive():
    """Cannot set both data and raw_data."""
    with pytest.raises(ValueError, match='Cannot set both'):
        ServerSentEvent(data='json', raw_data='raw')

def format_sse_event(*, data_str: str | None=None, event: str | None=None, id: str | None=None, retry: int | None=None, comment: str | None=None) -> bytes:
    """Build SSE wire-format bytes from **pre-serialized** data."""
    ...

@app.get('/broken-session-data')
def get_broken_session_data(session: BrokenSessionDep) -> Any:
    return list(session)

def update_comment(*, settings: Settings, comment_id: str, body: str) -> Comment:
    data = get_graphql_response(settings=settings, query=update_comment_mutation, comment_id=comment_id, body=body)
    response = UpdateCommentResponse.model_validate(data)
    return response.data.updateDiscussionComment.comment

def test_stream_chat(client: TestClient):
    ...

def test_broken_session_data():
    with pytest.raises(ValueError, match='Session closed'):
        client.get('/broken-session-data')

def test_broken_scope() -> None:
    with pytest.raises(FastAPIError, match='The dependency "get_named_func_session" has a scope of "request", it cannot depend on dependencies with scope "function"'):

        @app.get('/broken-scope')
        def get_broken(sessions: BrokenSessionsDep) -> Any:
            pass

# Module: tests.test_tutorial.test_response_change_status_code.__init__


@app.on_event('shutdown')
def shutdown_event():
    with open('log.txt', mode='a') as log:
        log.write('Application shutdown')

@app.webhooks.post('new-subscription')
def new_subscription(body: Subscription):
    """
    When a new user subscribes to your service we'll send you a POST request with this
    data to the URL that you register for the event `new-subscription` in the dashboard.
    """

def test_broken_scope() -> None:
    ...

def get_graphql_translation_discussions(*, settings: Settings) -> list[AllDiscussionsDiscussionNode]:
    data = get_graphql_response(settings=settings, query=all_discussions_query, category_id=questions_translations_category_id)
    graphql_response = AllDiscussionsResponse.model_validate(data)
    return graphql_response.data.repository.discussions.nodes

def extract_markdown_links(lines: list[str]) -> list[MarkdownLinkInfo]:
    """Extract all markdown links from the given lines."""
    ...