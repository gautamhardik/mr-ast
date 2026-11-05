def test_inline_styles_with_justification():
    """Regression test for https://github.com/Textualize/rich/issues/3115"""
    ...

def on_broken_pipe(self) -> None:
    """This function is called when a `BrokenPipeError` is raised.

        This can occur when piping Textual output in Linux and macOS.
        The default implementation is to exit the app, but you could implement
        this method in a subclass to change the behavior.

        See https://docs.python.org/3/library/signal.html#note-on-sigpipe for details.
        """
    self.quiet = True
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())
    raise SystemExit(1)

def test_clear_meta_and_links_clears_hash():
    """Regression test for https://github.com/Textualize/rich/issues/2942."""
    style = Style.parse('bold red on black link https://example.org') + Style.on(click='CLICK')
    hash(style)
    assert style._hash is not None
    clear_style = style.clear_meta_and_links()
    assert clear_style._hash is None

def test_append_tokens() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/3014"""
    console = Console()
    t = Text().append_tokens([('long text that will be wrapped with a control code \r\n', 'red')])
    with console.capture() as capture:
        console.print(t, width=40)
    output = capture.get()
    print(repr(output))
    assert output == 'long text that will be wrapped with a \ncontrol code \n\n'

def make_sponsor_message() -> Panel:
    """Some example content."""
    ...

def test_columns_highlight_added_by_add_row() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/3517"""
    table = Table(show_header=False, highlight=True)
    table.add_row('1', repr('FOO'))
    assert table.columns[0].highlight == table.highlight
    assert table.columns[1].highlight == table.highlight
    console = Console(record=True)
    console.print(table)
    output = console.export_text(styles=True)
    print(repr(output))
    expected = "┌───┬───────┐\n│ \x1b[1;36m1\x1b[0m │ \x1b[32m'FOO'\x1b[0m │\n└───┴───────┘\n"
    assert output == expected

@classmethod
def get_default_columns(cls) -> Tuple[ProgressColumn, ...]:
    """Get the default columns used for a new Progress instance:"""
    ...

def set_window_title(self, title: str) -> bool:
    """Set the title of the console terminal window."""
    ...

def test_table_with_empty_cells() -> None:
    """Test a table with empty cells is rendered without extra newlines above."""
    ...

def test_append_loop_regression() -> None:
    """Regression text for https://github.com/Textualize/rich/issues/3479"""
    a = Text('one', 'blue')
    a.append(a)
    assert a.plain == 'oneone'
    b = Text('two', 'blue')
    b.append_text(b)
    assert b.plain == 'twotwo'

@classmethod
def _guess_lexer(cls, filename: str, code: str) -> str:
    ...

def test_wrap_cjk_mixed():
    """Regression test covering https://github.com/Textualize/rich/issues/3176 and
    https://github.com/Textualize/textual/issues/3567 - double width characters could
    result in text going missing when wrapping."""
    text = Text('123ありがとうございました')
    console = Console(width=20)
    wrapped_lines = text.wrap(console, width=8)
    with console.capture() as capture:
        console.print(wrapped_lines)
    assert capture.get() == '123あり\nがとうご\nざいまし\nた\n'

# Module: rich.filesize


def test_inline_styles_in_table():
    """Regression test for https://github.com/Textualize/rich/issues/3115"""
    ...

def test_no_output_if_progress_is_disabled() -> None:
    ...

# Data module: constants


def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
    """Render markdown to the console."""
    ...

def test_padding_plus_wrap() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/3727"""
    ...

def test_live_is_not_started_if_progress_is_disabled() -> None:
    progress = Progress(auto_refresh=False, disable=True)
    with progress:
        assert not progress.live._started

class NewLine:
    """A renderable to generate new line(s)"""

    def __init__(self, count: int=1) -> None:
        self.count = count

    def __rich_console__(self, console: 'Console', options: 'ConsoleOptions') -> Iterable[Segment]:
        yield Segment('\n' * self.count)

from rich import print

print("If your terminal supports links, the following text should be clickable:")
print("[link=https://www.willmcgugan.com][i]Visit [red]my[/red][/i] [yellow]Blog[/]")


def add_task(self, description: str, start: bool=True, total: Optional[float]=100.0, completed: int=0, visible: bool=True, **fields: Any) -> TaskID:
    """Add a new 'task' to the Progress display."""
    ...

def test_capture_and_record() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/2563"""
    ...

def test_live_empty() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/3796"""
    ...

def track(self, sequence: Iterable[ProgressType], total: Optional[float]=None, completed: int=0, task_id: Optional[TaskID]=None, description: str='Working...', update_period: float=0.1) -> Iterable[ProgressType]:
    """Track progress by iterating over a sequence."""
    ...

def test_recursive_exception() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/3708"""
    ...

def __init__(self, lines: Iterable[List[Segment]], new_lines: bool=False) -> None:
    """A simple renderable containing a number of lines of segments. May be used as an intermediate"""
    ...

def line(self, count: int=1) -> None:
    """Write new line(s).

        Args:
            count (int, optional): Number of new lines. Defaults to 1.
        """
    assert count >= 0, 'count must be >= 0'
    self.print(NewLine(count))

def test_dataclass_no_attribute() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/3417"""
    ...

def test_background_color_override_includes_padding() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/3295"""
    ...

def export_svg(self, *, title: str='Rich', theme: Optional[TerminalTheme]=None, clear: bool=True, code_format: str=CONSOLE_SVG_FORMAT, font_aspect_ratio: float=0.61, unique_id: Optional[str]=None) -> str:
    """Generate an SVG from the console contents (requires record=True in Console constructor)."""
    ...

def set_alt_screen(self, enable: bool=True) -> bool:
    """Enables alternative screen mode."""
    ...

class Progress(JupyterMixin):

    def __init__(self, *columns, console=None, auto_refresh=True, refresh_per_second=10, speed_estimate_period=30.0, transient=False, redirect_stdout=True, redirect_stderr=True, get_time=None, disable=False, expand=False):
        ...

    @classmethod
    def get_default_columns(cls):
        ...

    @property
    def console(self):
        ...

    @property
    def tasks(self):
        ...

    @property
    def task_ids(self):
        ...

    @property
    def finished(self):
        ...

    def start(self):
        ...

    def stop(self):
        ...

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    def track(self, sequence, total=None, completed=0, task_id=None, description='Working...', update_period=0.1):
        ...

    def wrap_file(self, file, total=None, *, task_id=None, description='Reading...'):
        ...

    def open(self, file, mode, buffering=-1, encoding=None, errors=None, newline=None, *, total=None, task_id=None, description='Reading...'):
        ...

    def open(self, file, mode, buffering=-1, encoding=None, errors=None, newline=None, *, total=None, task_id=None, description='Reading...'):
        ...

    def open(self, file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, *, total=None, task_id=None, description='Reading...'):
        ...

    def start_task(self, task_id):
        ...

    def stop_task(self, task_id):
        ...

    def update(self, task_id, *, total=None, completed=None, advance=None, description=None, visible=None, refresh=False, **fields):
        ...

    def reset(self, task_id, *, start=True, total=None, completed=0, visible=None, description=None, **fields):
        ...

    def advance(self, task_id, advance=1):
        ...

    def refresh(self):
        ...

    def get_renderable(self):
        ...

    def get_renderables(self):
        ...

    def make_tasks_table(self, tasks):
        ...

    def __rich__(self):
        ...

    def add_task(self, description, start=True, total=100.0, completed=0, visible=True, **fields):
        ...

    def remove_task(self, task_id):
        ...

@pytest.mark.skipif(sys.platform == 'win32', reason='renders different on windows')
def test_traceback_console_theme_applies():
    """Ensure that themes supplied via Console init work on Tracebacks."""
    ...

def test_title_text_with_panel_background() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/3569"""
    ...

def test_title_text_with_border_color() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/2745"""
    ...

@classmethod
def line(cls) -> 'Segment':
    """Make a new line segment."""
    return cls('\n')

def save_svg(self, path: str, *, title: str='Rich', theme: Optional[TerminalTheme]=None, clear: bool=True, code_format: str=CONSOLE_SVG_FORMAT, font_aspect_ratio: float=0.61, unique_id: Optional[str]=None) -> None:
    """Generate an SVG file from the console contents (requires record=True in Console constructor)."""
    ...

def stop(self) -> None:
    """Stop the progress display."""
    self.live.stop()
    if not self.console.is_interactive and (not self.console.is_jupyter):
        self.console.print()

def __rich_console__(self, console: 'Console', options: 'ConsoleOptions') -> 'RenderResult':
    if self.new_lines:
        new_line = Segment.line()
        for line in self.lines:
            yield from line
            yield new_line
    else:
        for line in self.lines:
            yield from line

def write(self, text: str) -> int:
    ...

def test_blank_lines() -> None:
    ...

def open(self, file: Union[str, 'PathLike[str]', bytes], mode: Union[Literal['rb'], Literal['rt'], Literal['r']]='r', buffering: int=-1, encoding: Optional[str]=None, errors: Optional[str]=None, newline: Optional[str]=None, *, total: Optional[int]=None, task_id: Optional[TaskID]=None, description: str='Reading...') -> Union[BinaryIO, TextIO]:
    """Track progress while reading from a binary file."""
    ...

def start(self) -> None:
    """Start the progress display."""
    if not self.disable:
        self.live.start(refresh=True)

class SegmentLines:

    def __init__(self, lines: Iterable[List[Segment]], new_lines: bool=False) -> None:
        """A simple renderable containing a number of lines of segments. May be used as an intermediate"""
        ...

    def __rich_console__(self, console: 'Console', options: 'ConsoleOptions') -> 'RenderResult':
        ...

def set_spinner(self, spinner_name: str, spinner_style: Optional[StyleType]='progress.spinner', speed: float=1.0) -> None:
    """Set a new spinner."""
    ...

response = ...
size = ...

def blank_copy(self, plain: str='') -> 'Text':
    """Return a new Text instance with copied metadata (but not the string or spans)."""
    copy_self = Text(plain, style=self.style, justify=self.justify, overflow=self.overflow, no_wrap=self.no_wrap, end=self.end, tab_size=self.tab_size)
    return copy_self

class Segments:

    def __init__(self, segments, new_lines=False):
        ...

    def __rich_console__(self, console, options):
        ...

def update_link(self, link: Optional[str]=None) -> 'Style':
    """Get a copy with a different value for link."""
    ...

def test_clear_meta_and_links():
    ...

def join(self, lines: Iterable['Text']) -> 'Text':
    """Join text together with this instance as the separator."""
    ...

cell_table = ...

cell_table = ...

cell_table = ...