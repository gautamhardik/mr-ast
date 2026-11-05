class PartialGitHubEvent(BaseModel):
    pull_request: PartialGitHubEventIssue | None = None

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
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    logging.info(f'Using config: {settings.model_dump_json()}')
    g = Github(auth=Auth.Token(settings.github_token.get_secret_value()))
    repo = g.get_repo(settings.github_repository)
    use_pr = next((pr for pr in repo.get_pulls() if pr.head.sha == settings.commit_sha), None)
    if not use_pr:
        logging.error(f'No PR found for hash: {settings.commit_sha}')
        return
    commits = list(use_pr.get_commits())
    current_commit = [c for c in commits if c.sha == settings.commit_sha][0]
    run_url = f'https://github.com/{settings.github_repository}/actions/runs/{settings.run_id}'
    if settings.state == 'pending':
        current_commit.create_status(state='pending', description='Deploying Docs', context='deploy-docs', target_url=run_url)
        logging.info('No deploy URL available yet')
        return
    if settings.state == 'error':
        current_commit.create_status(state='error', description='Error Deploying Docs', context='deploy-docs', target_url=run_url)
        logging.info('Error deploying docs')
        return
    assert settings.state == 'success'
    if not settings.deploy_url:
        current_commit.create_status(state='success', description='No Docs Changes', context='deploy-docs', target_url=run_url)
        logging.info('No docs changes found')
        return
    assert settings.deploy_url
    current_commit.create_status(state='success', description='Docs Deployed', context='deploy-docs', target_url=run_url)
    files = list(use_pr.get_files())
    docs_files = [f for f in files if f.filename.startswith('docs/')]
    deploy_url = settings.deploy_url.rstrip('/')
    lang_links: dict[str, list[LinkData]] = {}
    for f in docs_files:
        match = re.match('docs/([^/]+)/docs/(.*)', f.filename)
        if not match:
            continue
        lang = match.group(1)
        path = match.group(2)
        if path.endswith('index.md'):
            path = path.replace('index.md', '')
        else:
            path = path.replace('.md', '/')
        en_path = path
        if lang == 'en':
            use_path = en_path
        else:
            use_path = f'{lang}/{path}'
        link = LinkData(previous_link=f'https://fastapi.tiangolo.com/{use_path}', preview_link=f'{deploy_url}/{use_path}')
        if lang != 'en':
            link.en_link = f'https://fastapi.tiangolo.com/{en_path}'
        lang_links.setdefault(lang, []).append(link)
    links: list[LinkData] = []
    en_links = lang_links.get('en', [])
    en_links.sort(key=lambda x: x.preview_link)
    links.extend(en_links)
    langs = list(lang_links.keys())
    langs.sort()
    for lang in langs:
        if lang == 'en':
            continue
        current_lang_links = lang_links[lang]
        current_lang_links.sort(key=lambda x: x.preview_link)
        links.extend(current_lang_links)
    header = '## 📝 Docs preview'
    message = header
    message += f'\n\nLast commit {settings.commit_sha} at: {deploy_url}'
    if links:
        message += '\n\n### Modified Pages\n\n'
        for link in links:
            message += f'* {link.preview_link}'
            message += f' - ([before]({link.previous_link}))'
            if link.en_link:
                message += f' - ([English]({link.en_link}))'
            message += '\n'
    print(message)
    issue = use_pr.as_issue()
    comments = list(issue.get_comments())
    for comment in comments:
        if comment.body.startswith(header) and comment.user.login == 'github-actions[bot]':
            comment.edit(message)
            break
    else:
        issue.create_comment(message)
    logging.info('Finished')

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

class Settings(BaseSettings):
    sponsors_token: SecretStr
    pr_token: SecretStr
    github_repository: str
    httpx_timeout: int = 30

# Module: tests.test_tutorial.test_response_change_status_code.__init__


# Module: scripts.add_latest_release_date


# Module: tests.test_tutorial.test_response_change_status_code.test_tutorial001
