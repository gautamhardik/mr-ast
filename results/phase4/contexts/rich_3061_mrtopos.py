def test_tabs_to_spaces():
    text = Text('\tHello\tWorld', tab_size=8)
    text.expand_tabs()
    assert text.plain == '        Hello   World'
    text = Text('\tHello\tWorld', tab_size=4)
    text.expand_tabs()
    assert text.plain == '    Hello   World'
    text = Text('.\t..\t...\t....\t', tab_size=4)
    text.expand_tabs()
    assert text.plain == '.   ..  ... ....    '
    text = Text('No Tabs')
    text.expand_tabs()
    assert text.plain == 'No Tabs'

def expand_tabs(self, tab_size: Optional[int]=None) -> None:
    """Converts tabs to spaces."""
    ...

def test_wrap_tabs():
    text = Text('foo\tbar', justify='left')
    lines = text.wrap(Console(), 4)
    assert len(lines) == 2
    assert str(lines[0]) == 'foo '
    assert str(lines[1]) == 'bar '

class Text(JupyterMixin):
    __slots__ = ['_text', 'style', 'justify', 'overflow', 'no_wrap', 'end', 'tab_size', '_spans', '_length']

    def __init__(self, text='', style='', *, justify=None, overflow=None, no_wrap=None, end='\n', tab_size=8, spans=None):
        ...

    def __len__(self):
        ...

    def __bool__(self):
        ...

    def __str__(self):
        ...

    def __repr__(self):
        ...

    def __add__(self, other):
        ...

    def __eq__(self, other):
        ...

    def __contains__(self, other):
        ...

    def __getitem__(self, slice):
        ...

    @property
    def cell_len(self):
        ...

    @property
    def markup(self):
        ...

    @classmethod
    def from_markup(cls, text, *, style='', emoji=True, emoji_variant=None, justify=None, overflow=None, end='\n'):
        ...

    @classmethod
    def from_ansi(cls, text, *, style='', justify=None, overflow=None, no_wrap=None, end='\n', tab_size=8):
        ...

    @classmethod
    def styled(cls, text, style='', *, justify=None, overflow=None):
        ...

    @classmethod
    def assemble(cls, *parts, style='', justify=None, overflow=None, no_wrap=None, end='\n', tab_size=8, meta=None):
        ...

    @property
    def plain(self):
        ...

    def plain(self, new_text):
        ...

    @property
    def spans(self):
        ...

    def spans(self, spans):
        ...

    def blank_copy(self, plain=''):
        ...

    def copy(self):
        ...

    def stylize(self, style, start=0, end=None):
        ...

    def stylize_before(self, style, start=0, end=None):
        ...

    def apply_meta(self, meta, start=0, end=None):
        ...

    def on(self, meta=None, **handlers):
        ...

    def remove_suffix(self, suffix):
        ...

    def get_style_at_offset(self, console, offset):
        ...

    def highlight_regex(self, re_highlight, style=None, *, style_prefix=''):
        ...

    def highlight_words(self, words, style, *, case_sensitive=True):
        ...

    def rstrip(self):
        ...

    def rstrip_end(self, size):
        ...

    def set_length(self, new_length):
        ...

    def __rich_console__(self, console, options):
        ...

    def __rich_measure__(self, console, options):
        ...

    def render(self, console, end=''):
        ...

    def join(self, lines):
        ...

    def expand_tabs(self, tab_size=None):
        ...

    def truncate(self, max_width, *, overflow=None, pad=False):
        ...

    def _trim_spans(self):
        ...

    def pad(self, count, character=' '):
        ...

    def pad_left(self, count, character=' '):
        ...

    def pad_right(self, count, character=' '):
        ...

    def align(self, align, width, character=' '):
        ...

    def append(self, text, style=None):
        ...

    def append_text(self, text):
        ...

    def append_tokens(self, tokens):
        ...

    def copy_styles(self, text):
        ...

    def split(self, separator='\n', *, include_separator=False, allow_blank=False):
        ...

    def divide(self, offsets):
        ...

    def right_crop(self, amount=1):
        ...

    def wrap(self, console, width, *, justify=None, overflow=None, tab_size=8, no_wrap=None):
        ...

    def fit(self, width):
        ...

    def detect_indentation(self):
        ...

    def with_indent_guides(self, indent_size=None, *, character='│', style='dim green'):
        ...

def extend(self, lines: Iterable['Text']) -> None:
    self._lines.extend(lines)

def copy_styles(self, text: 'Text') -> None:
    """Copy styles from another Text instance.

        Args:
            text (Text): A Text instance to copy styles from, must be the same length.
        """
    self._spans.extend(text._spans)

@pytest.mark.skipif(sys.platform == 'win32', reason='renders different on windows')
def test_traceback_console_theme_applies():
    """Ensure that themes supplied via Console init work on Tracebacks."""
    ...

def make_sponsor_message() -> Panel:
    """Some example content."""
    ...

# Module: rich.filesize


class ISO8601Highlighter(RegexHighlighter):
    """Highlights the ISO8601 date time strings.
    Regex reference: https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s07.html
    """
    base_style = 'iso8601.'
    highlights = ['^(?P<year>[0-9]{4})-(?P<month>1[0-2]|0[1-9])$', '^(?P<date>(?P<year>[0-9]{4})(?P<month>1[0-2]|0[1-9])(?P<day>3[01]|0[1-9]|[12][0-9]))$', '^(?P<date>(?P<year>[0-9]{4})-?(?P<day>36[0-6]|3[0-5][0-9]|[12][0-9]{2}|0[1-9][0-9]|00[1-9]))$', '^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9]))$', '^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9])-?(?P<day>[1-7]))$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9]):?(?P<minute>[0-5][0-9]))$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))$', '^(?P<timezone>(Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?))$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?)$', '^(?P<date>(?P<year>[0-9]{4})(?P<hyphen>-)?(?P<month>1[0-2]|0[1-9])(?(hyphen)-)(?P<day>3[01]|0[1-9]|[12][0-9])) (?P<time>(?P<hour>2[0-3]|[01][0-9])(?(hyphen):)(?P<minute>[0-5][0-9])(?(hyphen):)(?P<second>[0-5][0-9]))$', '^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<frac>\\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$', '^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))T(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<ms>\\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$']

@property
def _title(self) -> Optional[Text]:
    ...

@property
def _subtitle(self) -> Optional[Text]:
    ...

@classmethod
def assemble(cls, *parts, style='', justify=None, overflow=None, no_wrap=None, end='\n', tab_size=8, meta=None):
    ...

def append_text(self, text: 'Text') -> 'Text':
    """Append another Text instance. This method is more performant that Text.append, but"""
    ...

class StyleSuite:

    def setup(self):
        ...

    def time_parse_ansi(self):
        ...

    def time_parse_hex(self):
        ...

    def time_parse_mixed_complex_style(self):
        ...

    def time_style_add(self):
        ...

def test_highlight_json_no_indent():
    ...

def time_parse_hex(self):
    Style.parse('#f0f0f0 on #e2e28a')

def blank_copy(self, plain: str='') -> 'Text':
    """Return a new Text instance with copied meta data (but not the string or spans)."""
    copy_self = Text(plain, style=self.style, justify=self.justify, overflow=self.overflow, no_wrap=self.no_wrap, end=self.end, tab_size=self.tab_size)
    return copy_self

def truncate(self, max_width: int, *, overflow: Optional['OverflowMethod']=None, pad: bool=False) -> None:
    """Truncate text if it is longer that a given width."""
    ...

@classmethod
def from_ansi(cls, text: str, *, style: Union[str, Style]='', justify: Optional['JustifyMethod']=None, overflow: Optional['OverflowMethod']=None, no_wrap: Optional[bool]=None, end: str='\n', tab_size: Optional[int]=8) -> 'Text':
    """Create a Text object from a string containing ANSI escape codes."""
    ...

def __init__(self, text: str='', style: Union[str, Style]='', *, justify: Optional['JustifyMethod']=None, overflow: Optional['OverflowMethod']=None, no_wrap: Optional[bool]=None, end: str='\n', tab_size: Optional[int]=8, spans: Optional[List[Span]]=None) -> None:
    ...

class RichRenderable(ABC):
    """An abstract base class for Rich renderables."""

    @classmethod
    def __subclasshook__(cls, other: type) -> bool:
        """Check if this class supports the rich render protocol."""
        ...

def wrap(self, console: 'Console', width: int, *, justify: Optional['JustifyMethod']=None, overflow: Optional['OverflowMethod']=None, tab_size: int=8, no_wrap: Optional[bool]=None) -> Lines:
    """Word wrap the text."""
    ...

def align(self, align: AlignMethod, width: int, character: str=' ') -> None:
    """Align text to a given width."""
    ...

from rich import print

print("If your terminal supports links, the following text should be clickable:")
print("[link=https://www.willmcgugan.com][i]Visit [red]my[/red][/i] [yellow]Blog[/]")


@classmethod
def strip_styles(cls, segments: Iterable['Segment']) -> Iterable['Segment']:
    """Remove all styles from an iterable of segments."""
    ...

def __rich_console__(self, console: 'Console', options: 'ConsoleOptions') -> 'RenderResult':
    ...

def copy(self) -> 'Text':
    """Return a copy of this instance."""
    copy_self = Text(self.plain, style=self.style, justify=self.justify, overflow=self.overflow, no_wrap=self.no_wrap, end=self.end, tab_size=self.tab_size)
    copy_self._spans[:] = self._spans
    return copy_self

expected = ...

def test_highlight_regex_callable():
    ...

@classmethod
def replace(cls, text: str) -> str:
    """Replace emoji markup with corresponding unicode characters."""
    ...

@classmethod
def combine(cls, styles: Iterable['Style']) -> 'Style':
    """Combine styles and get result.

        Args:
            styles (Iterable[Style]): Styles to combine.

        Returns:
            Style: A new style instance.
        """
    iter_styles = iter(styles)
    return sum(iter_styles, next(iter_styles))

@classmethod
def chain(cls, *styles: 'Style') -> 'Style':
    """Combine styles from positional argument in to a single style."""
    ...

def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
    ...

def group(fit: bool=True) -> Callable[..., Callable[..., Group]]:
    """A decorator that turns an iterable of renderables in to a group."""
    ...

def __init__(self, title: Union[str, Text]='', *, characters: str='─', style: Union[str, Style]='rule.line', end: str='\n', align: AlignMethod='center') -> None:
    ...

def justify(self, console: 'Console', width: int, justify: 'JustifyMethod'='left', overflow: 'OverflowMethod'='fold') -> None:
    """Justify and overflow text to a given width."""
    ...

def __rich_console__(self, console: 'Console', options: 'ConsoleOptions') -> Iterable[Segment]:
    ...

def push_theme(self, theme, *, inherit=True):
    ...

def test_export_html():
    ...

def test_decode_issue_2688(ansi_bytes, expected_text):
    ...

def add_split(self, *layouts: Union['Layout', RenderableType]) -> None:
    """Add a new layout(s) to existing split."""
    ...

def pad(self, count: int, character: str=' ') -> None:
    """Pad left and right with a given number of characters."""
    ...

def _emoji_replace(text: str, default_variant: Optional[str]=None, _emoji_sub: _EmojiSubMethod=re.compile('(:(\\S*?)(?:(?:\\-)(emoji|text))?:)').sub) -> str:
    """Replace emoji code in text."""
    ...

def test_highlight_words():
    ...

def test_rich() -> None:
    ...

@classmethod
def adjust_line_length(cls, line, length, style=None, pad=True):
    ...

@pytest.mark.parametrize('align,outcome', [('center', '───\n'), ('left', '… ─\n'), ('right', '─ …\n')])
def test_rule_not_enough_space_for_title_text(align, outcome):
    console = Console(width=3, file=io.StringIO(), record=True)
    console.rule('Hello!', align=align)
    assert console.file.getvalue() == outcome

def move(self, offset: int) -> 'Span':
    """Move start and end by a given offset."""
    ...

def __rich_console__(self, console: 'Console', options: 'ConsoleOptions') -> 'RenderResult':
    ...

def right_crop(self, amount: int=1) -> None:
    """Remove a number of characters from the end of the text."""
    ...

# Module: rich._win32_console


def test_export_html_inline():
    ...

# Module: rich._emoji_replace
