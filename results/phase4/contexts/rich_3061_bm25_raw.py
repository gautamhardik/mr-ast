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
    """Converts tabs to spaces.

        Args:
            tab_size (int, optional): Size of tabs. Defaults to 8.

        """
    if '\t' not in self.plain:
        return
    pos = 0
    if tab_size is None:
        tab_size = self.tab_size
    assert tab_size is not None
    result = self.blank_copy()
    append = result.append
    _style = self.style
    for line in self.split('\n', include_separator=True):
        parts = line.split('\t', include_separator=True)
        for part in parts:
            if part.plain.endswith('\t'):
                part._text = [part.plain[:-1] + ' ']
                append(part)
                pos += len(part)
                spaces = tab_size - (pos - 1) % tab_size - 1
                if spaces:
                    append(' ' * spaces, _style)
                    pos += spaces
            else:
                append(part)
    self._text = [result.plain]
    self._length = len(self.plain)
    self._spans[:] = result._spans

def test_wrap_tabs():
    text = Text('foo\tbar', justify='left')
    lines = text.wrap(Console(), 4)
    assert len(lines) == 2
    assert str(lines[0]) == 'foo '
    assert str(lines[1]) == 'bar '

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
    """
    Ensure that themes supplied via Console init work on Tracebacks.
    Regression test for https://github.com/Textualize/rich/issues/1786
    """
    r, g, b = (123, 234, 123)
    console = Console(force_terminal=True, _environ={'COLORTERM': 'truecolor'}, theme=Theme({'traceback.title': f'rgb({r},{g},{b})'}))
    console.begin_capture()
    try:
        1 / 0
    except Exception:
        console.print_exception()
    result = console.end_capture()
    assert f'\\x1b[38;2;{r};{g};{b}mTraceback \\x1b[0m' in repr(result)

def make_sponsor_message() -> Panel:
    """Some example content."""
    sponsor_message = Table.grid(padding=1)
    sponsor_message.add_column(style='green', justify='right')
    sponsor_message.add_column(no_wrap=True)
    sponsor_message.add_row('Twitter', '[u blue link=https://twitter.com/textualize]https://twitter.com/textualize')
    sponsor_message.add_row('CEO', '[u blue link=https://twitter.com/willmcgugan]https://twitter.com/willmcgugan')
    sponsor_message.add_row('Textualize', '[u blue link=https://www.textualize.io]https://www.textualize.io')
    message = Table.grid(padding=1)
    message.add_column()
    message.add_column(no_wrap=True)
    message.add_row(sponsor_message)
    message_panel = Panel(Align.center(Group('\n', Align.center(sponsor_message)), vertical='middle'), box=box.ROUNDED, padding=(1, 2), title='[b red]Thanks for trying out Rich!', border_style='bright_blue')
    return message_panel

# Module: rich.filesize


class ISO8601Highlighter(RegexHighlighter):
    """Highlights the ISO8601 date time strings.
    Regex reference: https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s07.html
    """
    base_style = 'iso8601.'
    highlights = ['^(?P<year>[0-9]{4})-(?P<month>1[0-2]|0[1-9])$', '^(?P<date>(?P<year>[0-9]{4})(?P<month>1[0-2]|0[1-9])(?P<day>3[01]|0[1-9]|[12][0-9]))$', '^(?P<date>(?P<year>[0-9]{4})-?(?P<day>36[0-6]|3[0-5][0-9]|[12][0-9]{2}|0[1-9][0-9]|00[1-9]))$', '^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9]))$', '^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9])-?(?P<day>[1-7]))$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9]):?(?P<minute>[0-5][0-9]))$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))$', '^(?P<timezone>(Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?))$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?)$', '^(?P<date>(?P<year>[0-9]{4})(?P<hyphen>-)?(?P<month>1[0-2]|0[1-9])(?(hyphen)-)(?P<day>3[01]|0[1-9]|[12][0-9])) (?P<time>(?P<hour>2[0-3]|[01][0-9])(?(hyphen):)(?P<minute>[0-5][0-9])(?(hyphen):)(?P<second>[0-5][0-9]))$', '^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<frac>\\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$', '^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))T(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<ms>\\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$']

@property
def _title(self) -> Optional[Text]:
    if self.title:
        title_text = Text.from_markup(self.title) if isinstance(self.title, str) else self.title.copy()
        title_text.end = ''
        title_text.plain = title_text.plain.replace('\n', ' ')
        title_text.no_wrap = True
        title_text.expand_tabs()
        title_text.pad(1)
        return title_text
    return None

@property
def _subtitle(self) -> Optional[Text]:
    if self.subtitle:
        subtitle_text = Text.from_markup(self.subtitle) if isinstance(self.subtitle, str) else self.subtitle.copy()
        subtitle_text.end = ''
        subtitle_text.plain = subtitle_text.plain.replace('\n', ' ')
        subtitle_text.no_wrap = True
        subtitle_text.expand_tabs()
        subtitle_text.pad(1)
        return subtitle_text
    return None

@classmethod
def from_path(cls, path: str, encoding: str='utf-8', lexer: Optional[Union[Lexer, str]]=None, theme: Union[str, SyntaxTheme]=DEFAULT_THEME, dedent: bool=False, line_numbers: bool=False, line_range: Optional[Tuple[int, int]]=None, start_line: int=1, highlight_lines: Optional[Set[int]]=None, code_width: Optional[int]=None, tab_size: int=4, word_wrap: bool=False, background_color: Optional[str]=None, indent_guides: bool=False, padding: PaddingDimensions=0) -> 'Syntax':
    """Construct a Syntax object from a file.

        Args:
            path (str): Path to file to highlight.
            encoding (str): Encoding of file.
            lexer (str | Lexer, optional): Lexer to use. If None, lexer will be auto-detected from path/file content.
            theme (str, optional): Color theme, aka Pygments style (see https://pygments.org/docs/styles/#getting-a-list-of-available-styles). Defaults to "emacs".
            dedent (bool, optional): Enable stripping of initial whitespace. Defaults to True.
            line_numbers (bool, optional): Enable rendering of line numbers. Defaults to False.
            start_line (int, optional): Starting number for line numbers. Defaults to 1.
            line_range (Tuple[int, int], optional): If given should be a tuple of the start and end line to render.
            highlight_lines (Set[int]): A set of line numbers to highlight.
            code_width: Width of code to render (not including line numbers), or ``None`` to use all available width.
            tab_size (int, optional): Size of tabs. Defaults to 4.
            word_wrap (bool, optional): Enable word wrapping of code.
            background_color (str, optional): Optional background color, or None to use theme color. Defaults to None.
            indent_guides (bool, optional): Show indent guides. Defaults to False.
            padding (PaddingDimensions): Padding to apply around the syntax. Defaults to 0 (no padding).

        Returns:
            [Syntax]: A Syntax object that may be printed to the console
        """
    code = Path(path).read_text(encoding=encoding)
    if not lexer:
        lexer = cls.guess_lexer(path, code=code)
    return cls(code, lexer, theme=theme, dedent=dedent, line_numbers=line_numbers, line_range=line_range, start_line=start_line, highlight_lines=highlight_lines, code_width=code_width, tab_size=tab_size, word_wrap=word_wrap, background_color=background_color, indent_guides=indent_guides, padding=padding)

@classmethod
def assemble(cls, *parts: Union[str, 'Text', Tuple[str, StyleType]], style: Union[str, Style]='', justify: Optional['JustifyMethod']=None, overflow: Optional['OverflowMethod']=None, no_wrap: Optional[bool]=None, end: str='\n', tab_size: int=8, meta: Optional[Dict[str, Any]]=None) -> 'Text':
    """Construct a text instance by combining a sequence of strings with optional styles.
        The positional arguments should be either strings, or a tuple of string + style.

        Args:
            style (Union[str, Style], optional): Base style for text. Defaults to "".
            justify (str, optional): Justify method: "left", "center", "full", "right". Defaults to None.
            overflow (str, optional): Overflow method: "crop", "fold", "ellipsis". Defaults to None.
            end (str, optional): Character to end text with. Defaults to "\\\\n".
            tab_size (int): Number of spaces per tab, or ``None`` to use ``console.tab_size``. Defaults to 8.
            meta (Dict[str, Any], optional). Meta data to apply to text, or None for no meta data. Default to None

        Returns:
            Text: A new text instance.
        """
    text = cls(style=style, justify=justify, overflow=overflow, no_wrap=no_wrap, end=end, tab_size=tab_size)
    append = text.append
    _Text = Text
    for part in parts:
        if isinstance(part, (_Text, str)):
            append(part)
        else:
            append(*part)
    if meta:
        text.apply_meta(meta)
    return text

def append_text(self, text: 'Text') -> 'Text':
    """Append another Text instance. This method is more performant that Text.append, but
        only works for Text.

        Returns:
            Text: Returns self for chaining.
        """
    _Span = Span
    text_length = self._length
    if text.style is not None:
        self._spans.append(_Span(text_length, text_length + len(text), text.style))
    self._text.append(text.plain)
    self._spans.extend((_Span(start + text_length, end + text_length, style) for start, end, style in text._spans))
    self._length += len(text)
    return self

class StyleSuite:

    def setup(self):
        self.console = Console(file=StringIO(), color_system='truecolor', legacy_windows=False, width=100)
        self.style1 = Style.parse('blue on red')
        self.style2 = Style.parse('green italic bold')

    def time_parse_ansi(self):
        Style.parse('red on blue')

    def time_parse_hex(self):
        Style.parse('#f0f0f0 on #e2e28a')

    def time_parse_mixed_complex_style(self):
        Style.parse('dim bold reverse #00ee00 on rgb(123,12,50)')

    def time_style_add(self):
        self.style1 + self.style2

def test_highlight_json_no_indent():
    json_string = json.dumps({'name': 'apple', 'count': 1}, indent=None)
    text = Text(json_string)
    highlighter = JSONHighlighter()
    highlighter.highlight(text)
    assert text.spans == [Span(0, 1, 'json.brace'), Span(1, 7, 'json.str'), Span(9, 16, 'json.str'), Span(18, 25, 'json.str'), Span(27, 28, 'json.number'), Span(28, 29, 'json.brace'), Span(1, 7, 'json.key'), Span(18, 25, 'json.key')]

def time_parse_hex(self):
    Style.parse('#f0f0f0 on #e2e28a')

def blank_copy(self, plain: str='') -> 'Text':
    """Return a new Text instance with copied meta data (but not the string or spans)."""
    copy_self = Text(plain, style=self.style, justify=self.justify, overflow=self.overflow, no_wrap=self.no_wrap, end=self.end, tab_size=self.tab_size)
    return copy_self

from rich import print

print("If your terminal supports links, the following text should be clickable:")
print("[link=https://www.willmcgugan.com][i]Visit [red]my[/red][/i] [yellow]Blog[/]")


# Module: rich._win32_console


# Module: rich._emoji_replace
