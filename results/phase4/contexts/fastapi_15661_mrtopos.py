class PartialGitHubEvent(BaseModel):
    pull_request: PartialGitHubEventIssue | None = None

@app.command()
def make_pr(*, language: Annotated[str | None, typer.Option(envvar='LANGUAGE')]=None, command: Annotated[str | None, typer.Option(envvar='COMMAND')]=None, github_token: Annotated[str, typer.Option(envvar='GITHUB_TOKEN')], github_repository: Annotated[str, typer.Option(envvar='GITHUB_REPOSITORY')], commit_in_place: Annotated[bool, typer.Option(envvar='COMMIT_IN_PLACE', show_default=True)]=False) -> None:
    ...

def get_pr_nodes(settings: Settings) -> list[PullRequestNode]:
    pr_nodes: list[PullRequestNode] = []
    pr_edges = get_graphql_pr_edges(settings=settings)
    while pr_edges:
        for edge in pr_edges:
            pr_nodes.append(edge.node)
        last_edge = pr_edges[-1]
        pr_edges = get_graphql_pr_edges(settings=settings, after=last_edge.cursor)
    return pr_nodes

class PartialGitHubEventIssue(BaseModel):
    number: int | None = None

def main() -> None:
    ...

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

def main() -> None:
    ...

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

def main() -> None:
    ...

def get_graphql_pr_edges(*, settings: Settings, after: str | None=None) -> list[PullRequestEdge]:
    data = get_graphql_response(settings=settings, query=prs_query, after=after)
    graphql_response = PRsResponse.model_validate(data)
    return graphql_response.data.repository.pullRequests.edges

class UpdateDiscussionComment(BaseModel):
    comment: Comment

class AddDiscussionComment(BaseModel):
    comment: Comment

class AllDiscussionsDiscussionNode(BaseModel):
    title: str
    id: str
    number: int
    labels: AllDiscussionsDiscussionLabels

class AllDiscussionsDiscussionLabels(BaseModel):
    edges: list[AllDiscussionsLabelsEdge]

def get_graphql_translation_discussion_comments_edges(*, settings: Settings, discussion_number: int, after: str | None=None) -> list[CommentsEdge]:
    data = get_graphql_response(settings=settings, query=translation_discussion_query, discussion_number=discussion_number, after=after)
    graphql_response = CommentsResponse.model_validate(data)
    return graphql_response.data.repository.discussion.comments.edges

def create_comment(*, settings: Settings, discussion_id: str, body: str) -> Comment:
    data = get_graphql_response(settings=settings, query=add_comment_mutation, discussion_id=discussion_id, body=body)
    response = AddCommentResponse.model_validate(data)
    return response.data.addDiscussionComment.comment

# Module: tests.test_list_bytes_file_order_preserved_issue_14811


def get_graphql_response(*, settings: Settings, query: str, after: str | None=None, category_id: str | None=None, discussion_number: int | None=None, discussion_id: str | None=None, comment_id: str | None=None, body: str | None=None) -> dict[str, Any]:
    headers = {'Authorization': f'token {settings.github_token.get_secret_value()}'}
    variables = {'after': after, 'category_id': category_id, 'discussion_number': discussion_number, 'discussion_id': discussion_id, 'comment_id': comment_id, 'body': body}
    response = httpx.post(github_graphql_url, headers=headers, timeout=settings.httpx_timeout, json={'query': query, 'variables': variables, 'operationName': 'Q'})
    if response.status_code != 200:
        logging.error(f'Response was not 200, after: {after}, category_id: {category_id}')
        logging.error(response.text)
        raise RuntimeError(response.text)
    data = response.json()
    if 'errors' in data:
        logging.error(f'Errors in response, after: {after}, category_id: {category_id}')
        logging.error(data['errors'])
        logging.error(response.text)
        raise RuntimeError(response.text)
    return cast(dict[str, Any], data)

class CommentsRepository(BaseModel):
    discussion: CommentsDiscussion

class DiscussionExpertsResults(BaseModel):
    commenters: Counter[str]
    last_month_commenters: Counter[str]
    three_months_commenters: Counter[str]
    six_months_commenters: Counter[str]
    one_year_commenters: Counter[str]
    authors: dict[str, Author]

class UpdateCommentData(BaseModel):
    updateDiscussionComment: UpdateDiscussionComment

class AddCommentData(BaseModel):
    addDiscussionComment: AddDiscussionComment

def get_graphql_question_discussion_edges(*, settings: Settings, after: str | None=None) -> list[DiscussionsEdge]:
    with rate_limiter:
        data = get_graphql_response(settings=settings, query=discussions_query, after=after, category_id=questions_category_id)
    rate_limiter.update_request_info(cost=data['data']['rateLimit']['cost'], remaining=data['data']['rateLimit']['remaining'], reset_at=data['data']['rateLimit']['resetAt'])
    graphql_response = DiscussionsResponse.model_validate(data)
    return graphql_response.data.repository.discussions.edges

# Module: tests.test_response_change_status_code


class AllDiscussionsDiscussions(BaseModel):
    nodes: list[AllDiscussionsDiscussionNode]

def extract_markdown_links(lines: list[str]) -> list[MarkdownLinkInfo]:
    """
    Extract all markdown links from the given lines.

    Return list of MarkdownLinkInfo, where each dict contains:
    - `line_no` - line number (1-based)
    - `url` - link URL
    - `text` - link text
    - `title` - link title (if any)
    """
    links: list[MarkdownLinkInfo] = []
    for line_no, line in enumerate(lines, start=1):
        for m in MARKDOWN_LINK_RE.finditer(line):
            links.append(MarkdownLinkInfo(line_no=line_no, url=m.group('url'), text=m.group('text'), title=m.group('title'), attributes=m.group('attrs'), full_match=m.group(0)))
    return links

class Settings(BaseSettings):
    sponsors_token: SecretStr
    pr_token: SecretStr
    github_repository: str
    httpx_timeout: int = 30

def extract_html_links(lines: list[str]) -> list[HtmlLinkInfo]:
    """Extract all HTML links from the given lines."""
    ...

def main() -> None:
    ...

def get_discussions_experts(discussion_nodes: list[DiscussionsNode]) -> DiscussionExpertsResults:
    ...

# Module: tests.test_tutorial.test_response_change_status_code.__init__


def replace_markdown_links(text: list[str], links: list[MarkdownLinkInfo], original_links: list[MarkdownLinkInfo], lang_code: str) -> list[str]:
    """Replace markdown links in the given text with the original links."""
    ...

def main() -> None:
    ...

def _construct_markdown_link(url: str, text: str, title: str | None, attributes: str | None, lang_code: str) -> str:
    """
    Construct a markdown link, adjusting the URL for the given language code if needed.
    """
    url = _add_lang_code_to_url(url, lang_code)
    if title:
        link = f'[{text}]({url} "{title}")'
    else:
        link = f'[{text}]({url})'
    if attributes:
        link += f'{{{attributes}}}'
    return link

def replace_html_links(text: list[str], links: list[HtmlLinkInfo], original_links: list[HtmlLinkInfo], lang_code: str) -> list[str]:
    """Replace HTML links in the given text with the links from the original document."""
    ...

class PullRequestNode(BaseModel):
    number: int
    labels: Labels
    author: Author | None = None
    title: str
    createdAt: datetime
    lastEditedAt: datetime | None = None
    updatedAt: datetime | None = None
    state: str
    reviews: Reviews

def _construct_html_link(link_text: str, attributes: list[HTMLLinkAttribute], lang_code: str) -> str:
    """
    Reconstruct HTML link, adjusting the URL for the given language code if needed.
    """
    attributes_upd: list[HTMLLinkAttribute] = []
    for attribute in attributes:
        if attribute['name'] == 'href':
            original_url = attribute['value']
            url = _add_lang_code_to_url(original_url, lang_code)
            attributes_upd.append(HTMLLinkAttribute(name='href', quote=attribute['quote'], value=url))
        else:
            attributes_upd.append(attribute)
    attrs_str = ' '.join((f"{attribute['name']}={attribute['quote']}{attribute['value']}{attribute['quote']}" for attribute in attributes_upd))
    return f'<a {attrs_str}>{link_text}</a>'

# Module: scripts.add_latest_release_date


class PullRequestEdge(BaseModel):
    cursor: str
    node: PullRequestNode

# Module: tests.test_tutorial.test_response_change_status_code.test_tutorial001


# Module: tests.test_stream_cancellation


def update_comment(*, settings: Settings, comment_id: str, body: str) -> Comment:
    data = get_graphql_response(settings=settings, query=update_comment_mutation, comment_id=comment_id, body=body)
    response = UpdateCommentResponse.model_validate(data)
    return response.data.updateDiscussionComment.comment

# Module: docs_src.response_change_status_code.__init__


class PullRequests(BaseModel):
    edges: list[PullRequestEdge]

def __enter__(self) -> 'RateLimiter':
    ...

class Link(BaseModelWithConfig):
    operationRef: str | None = None
    operationId: str | None = None
    parameters: dict[str, Any | str] | None = None
    requestBody: Any | str | None = None
    description: str | None = None
    server: Server | None = None

# Module: tests.test_additional_responses_union_duplicate_anyof


@dataclass
class ParamDetails:
    type_annotation: Any
    depends: params.Depends | None
    field: ModelField | None

async def _startup(self) -> None:
    """
        Run any `.on_startup` event handlers.

        This method is kept for backward compatibility after Starlette removed
        support for on_startup/on_shutdown handlers.

        Ref: https://github.com/Kludex/starlette/pull/3117
        """
    for handler in self.on_startup:
        if is_async_callable(handler):
            await handler()
        else:
            handler()

async def _shutdown(self) -> None:
    """
        Run any `.on_shutdown` event handlers.

        This method is kept for backward compatibility after Starlette removed
        support for on_startup/on_shutdown handlers.

        Ref: https://github.com/Kludex/starlette/pull/3117
        """
    for handler in self.on_shutdown:
        if is_async_callable(handler):
            await handler()
        else:
            handler()

def get_graphql_translation_discussions(*, settings: Settings) -> list[AllDiscussionsDiscussionNode]:
    data = get_graphql_response(settings=settings, query=all_discussions_query, category_id=questions_translations_category_id)
    graphql_response = AllDiscussionsResponse.model_validate(data)
    return graphql_response.data.repository.discussions.nodes

class LinkData(BaseModel):
    previous_link: str
    preview_link: str
    en_link: str | None = None

def main() -> None:
    ...

class Response(BaseModelWithConfig):
    description: str
    headers: dict[str, Header | Reference] | None = None
    content: dict[str, MediaType] | None = None
    links: dict[str, Link | Reference] | None = None

@app.command()
def new_lang(lang: str=typer.Argument(..., callback=lang_callback)):
    """Generate a new docs translation directory for the language LANG."""
    ...

def add_event_handler(self, event_type: str, func: Callable[[], Any]) -> None:
    """Add an event handler function for startup or shutdown."""
    ...

# Module: docs_src.response_change_status_code.tutorial001_py310
