def test_inline_styles_with_justification():
    """Regression test for https://github.com/Textualize/rich/issues/3115

    In particular, this tests the interaction between the change that was made to fix
    #3115 and column text justification.
    """
    markdown = Markdown('| left | center | right |\n| :- | :-: | -: |\n| This is a long row | because it contains | a fairly long sentence. |\n| a*b* _c_ ~~d~~ e | a*b* _c_ ~~d~~ e | a*b* _c_ ~~d~~ e |')
    result = render(markdown)
    expected = '\n                                                                      \n \x1b[1m \x1b[0m\x1b[1mleft              \x1b[0m\x1b[1m \x1b[0m \x1b[1m \x1b[0m\x1b[1m      center       \x1b[0m\x1b[1m \x1b[0m \x1b[1m \x1b[0m\x1b[1m                  right\x1b[0m\x1b[1m \x1b[0m \n ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ \n  This is a long row   because it contains   a fairly long sentence.  \n  a\x1b[3mb\x1b[0m \x1b[3mc\x1b[0m \x1b[9md\x1b[0m e                  a\x1b[3mb\x1b[0m \x1b[3mc\x1b[0m \x1b[9md\x1b[0m e                        a\x1b[3mb\x1b[0m \x1b[3mc\x1b[0m \x1b[9md\x1b[0m e  \n                                                                      \n'
    assert result == expected

class Console:
    # [Enclosing Scope]


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

def set_window_title(self, title: str) -> bool:
    """Set the title of the console terminal window.

        Warning: There is no means within Rich of "resetting" the window title to its
        previous value, meaning the title you set will persist even after your application
        exits.

        ``fish`` shell resets the window title before and after each command by default,
        negating this issue. Windows Terminal and command prompt will also reset the title for you.
        Most other shells and terminals, however, do not do this.

        Some terminals may require configuration changes before you can set the title.
        Some terminals may not support setting the title at all.

        Other software (including the terminal itself, the shell, custom prompts, plugins, etc.)
        may also set the terminal window title. This could result in whatever value you write
        using this method being overwritten.

        Args:
            title (str): The new title of the terminal window.

        Returns:
            bool: True if the control code to change the terminal title was
                written, otherwise False. Note that a return value of True
                does not guarantee that the window title has actually changed,
                since the feature may be unsupported/disabled in some terminals.
        """
    if self.is_terminal:
        self.control(Control.title(title))
        return True
    return False

def test_table_with_empty_cells() -> None:
    """Test a table with empty cells is rendered without extra newlines above.
    Regression test for #3027 https://github.com/Textualize/rich/issues/3027
    """
    complete_table = Markdown('| First Header  | Second Header |\n| ------------- | ------------- |\n| Content Cell  | Content Cell  |\n| Content Cell  | Content Cell  |\n')
    table_with_empty_cells = Markdown('| First Header  |               |\n| ------------- | ------------- |\n| Content Cell  | Content Cell  |\n|               | Content Cell  |\n')
    result = len(render(table_with_empty_cells).splitlines())
    expected = len(render(complete_table).splitlines())
    assert result == expected

def test_append_loop_regression() -> None:
    """Regression text for https://github.com/Textualize/rich/issues/3479"""
    a = Text('one', 'blue')
    a.append(a)
    assert a.plain == 'oneone'
    b = Text('two', 'blue')
    b.append_text(b)
    assert b.plain == 'twotwo'