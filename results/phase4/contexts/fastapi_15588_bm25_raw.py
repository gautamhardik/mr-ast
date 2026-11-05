class PartialGitHubEvent(BaseModel):
    pull_request: PartialGitHubEventIssue | None = None

class PartialGitHubEventIssue(BaseModel):
    number: int | None = None

@app.command()
def make_pr(*, language: Annotated[str | None, typer.Option(envvar='LANGUAGE')]=None, command: Annotated[str | None, typer.Option(envvar='COMMAND')]=None, github_token: Annotated[str, typer.Option(envvar='GITHUB_TOKEN')], github_repository: Annotated[str, typer.Option(envvar='GITHUB_REPOSITORY')], commit_in_place: Annotated[bool, typer.Option(envvar='COMMIT_IN_PLACE', show_default=True)]=False) -> None:
    print('Setting up GitHub Actions git user')
    repo = git.Repo(Path(__file__).absolute().parent.parent)
    if not repo.is_dirty(untracked_files=True):
        print('Repository is clean, no changes to commit')
        return
    subprocess.run(['git', 'config', 'user.name', 'github-actions[bot]'], check=True)
    subprocess.run(['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)
    current_branch = repo.active_branch.name
    if current_branch == 'master' and commit_in_place:
        print("Can't commit directly to master")
        raise typer.Exit(code=1)
    if not commit_in_place:
        branch_name = 'translate'
        if language:
            branch_name += f'-{language}'
        if command:
            branch_name += f'-{command}'
        branch_name += f'-{secrets.token_hex(4)}'
        print(f'Creating a new branch {branch_name}')
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
    else:
        branch_name = current_branch
        print(f'Committing in place on branch {branch_name}')
    print('Adding updated files')
    git_path = Path('docs')
    subprocess.run(['git', 'add', str(git_path)], check=True)
    print('Committing updated file')
    message = '🌐 Update translations'
    if language:
        message += f' for {language}'
    if command:
        message += f' ({command})'
    subprocess.run(['git', 'commit', '-m', message], check=True)
    print('Pushing branch')
    subprocess.run(['git', 'push', 'origin', branch_name], check=True)
    if not commit_in_place:
        print('Creating PR')
        g = Github(github_token)
        gh_repo = g.get_repo(github_repository)
        body = message + '\n\nThis PR was created automatically using LLMs.' + f'\n\nIt uses the prompt file https://github.com/fastapi/fastapi/blob/master/docs/{language}/llm-prompt.md.' + "\n\nIn most cases, it's better to make PRs updating that file so that the LLM can do a better job generating the translations than suggesting changes in this PR."
        pr = gh_repo.create_pull(title=message, body=body, base='master', head=branch_name)
        print(f'Created PR: {pr.number}')
    print('Finished')

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
    """Represents a single Server-Sent Event.

    When `yield`ed from a *path operation function* that uses
    `response_class=EventSourceResponse`, each `ServerSentEvent` is encoded
    into the [SSE wire format](https://html.spec.whatwg.org/multipage/server-sent-events.html#parsing-an-event-stream)
    (`text/event-stream`).

    If you yield a plain object (dict, Pydantic model, etc.) instead, it is
    automatically JSON-encoded and sent as the `data:` field.

    All `data` values **including plain strings** are JSON-serialized.

    For example, `data="hello"` produces `data: "hello"` on the wire (with
    quotes).
    """
    data: Annotated[Any, Doc('\n            The event payload.\n\n            Can be any JSON-serializable value: a Pydantic model, dict, list,\n            string, number, etc. It is **always** serialized to JSON: strings\n            are quoted (`"hello"` becomes `data: "hello"` on the wire).\n\n            Mutually exclusive with `raw_data`.\n            ')] = None
    raw_data: Annotated[str | None, Doc('\n            Raw string to send as the `data:` field **without** JSON encoding.\n\n            Use this when you need to send pre-formatted text, HTML fragments,\n            CSV lines, or any non-JSON payload. The string is placed directly\n            into the `data:` field as-is.\n\n            Mutually exclusive with `data`.\n            ')] = None
    event: Annotated[str | None, Doc('\n            Optional event type name.\n\n            Maps to `addEventListener(event, ...)` on the browser. When omitted,\n            the browser dispatches on the generic `message` event.\n            ')] = None
    id: Annotated[str | None, AfterValidator(_check_id_no_null), Doc('\n            Optional event ID.\n\n            The browser sends this value back as the `Last-Event-ID` header on\n            automatic reconnection. **Must not contain null (`\\0`) characters.**\n            ')] = None
    retry: Annotated[int | None, Field(ge=0), Doc('\n            Optional reconnection time in **milliseconds**.\n\n            Tells the browser how long to wait before reconnecting after the\n            connection is lost. Must be a non-negative integer.\n            ')] = None
    comment: Annotated[str | None, Doc('\n            Optional comment line(s).\n\n            Comment lines start with `:` in the SSE wire format and are ignored by\n            `EventSource` clients. Useful for keep-alive pings to prevent\n            proxy/load-balancer timeouts.\n            ')] = None

    @model_validator(mode='after')
    def _check_data_exclusive(self) -> 'ServerSentEvent':
        if self.data is not None and self.raw_data is not None:
            raise ValueError("Cannot set both 'data' and 'raw_data' on the same ServerSentEvent. Use 'data' for JSON-serialized payloads or 'raw_data' for pre-formatted strings.")
        return self

def get_contributors(pr_nodes: list[PullRequestNode]) -> ContributorsResults:
    contributors = Counter[str]()
    translation_reviewers = Counter[str]()
    translators = Counter[str]()
    authors: dict[str, Author] = {}
    for pr in pr_nodes:
        if pr.author:
            authors[pr.author.login] = pr.author
        is_lang = False
        for label in pr.labels.nodes:
            if label.name == 'lang-all':
                is_lang = True
                break
        for review in pr.reviews.nodes:
            if review.author:
                authors[review.author.login] = review.author
                if is_lang:
                    translation_reviewers[review.author.login] += 1
        if pr.state == 'MERGED' and pr.author:
            if is_lang:
                translators[pr.author.login] += 1
            else:
                contributors[pr.author.login] += 1
    return ContributorsResults(contributors=contributors, translation_reviewers=translation_reviewers, translators=translators, authors=authors)

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
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    logging.info(f'Using config: {settings.model_dump_json()}')
    g = Github(settings.github_token.get_secret_value())
    repo = g.get_repo(settings.github_repository)
    pr_nodes = get_pr_nodes(settings=settings)
    contributors_results = get_contributors(pr_nodes=pr_nodes)
    authors = contributors_results.authors
    top_contributors = get_users_to_write(counter=contributors_results.contributors, authors=authors)
    top_translators = get_users_to_write(counter=contributors_results.translators, authors=authors)
    top_translations_reviewers = get_users_to_write(counter=contributors_results.translation_reviewers, authors=authors)
    contributors_path = Path('./docs/en/data/contributors.yml')
    translators_path = Path('./docs/en/data/translators.yml')
    translation_reviewers_path = Path('./docs/en/data/translation_reviewers.yml')
    updated = [update_content(content_path=contributors_path, new_content=top_contributors), update_content(content_path=translators_path, new_content=top_translators), update_content(content_path=translation_reviewers_path, new_content=top_translations_reviewers)]
    if not any(updated):
        logging.info("The data hasn't changed, finishing.")
        return
    logging.info('Setting up GitHub Actions git user')
    subprocess.run(['git', 'config', 'user.name', 'github-actions[bot]'], check=True)
    subprocess.run(['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)
    branch_name = f'fastapi-people-contributors-{secrets.token_hex(4)}'
    logging.info(f'Creating a new branch {branch_name}')
    subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
    logging.info('Adding updated file')
    subprocess.run(['git', 'add', str(contributors_path), str(translators_path), str(translation_reviewers_path)], check=True)
    logging.info('Committing updated file')
    message = '👥 Update FastAPI People - Contributors and Translators'
    subprocess.run(['git', 'commit', '-m', message], check=True)
    logging.info('Pushing branch')
    subprocess.run(['git', 'push', 'origin', branch_name], check=True)
    logging.info('Creating PR')
    pr = repo.create_pull(title=message, body=message, base='master', head=branch_name)
    logging.info(f'Created PR: {pr.number}')
    logging.info('Finished')

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

class UpdateCommentData(BaseModel):
    updateDiscussionComment: UpdateDiscussionComment