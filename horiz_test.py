from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static


class HorizontalLayoutExample(App):
    CSS = """

"""
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+b", "go_back", "Go Back"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static("One", classes="box")
            yield Static("Two", classes="box")
            yield Static("Three", classes="box")


if __name__ == "__main__":
    app = HorizontalLayoutExample()
    app.run()
