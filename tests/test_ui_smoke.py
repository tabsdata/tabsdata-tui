import unittest

from textual.app import App, ComposeResult
from textual.widgets import Button, Static

from tdconsole.textual_assets.textual_screens import CurrentInstanceWidget, ExitBar


class _SmokeApp(App):
    def compose(self) -> ComposeResult:
        yield ExitBar()
        yield Static("body")


class TestUiSmoke(unittest.IsolatedAsyncioTestCase):
    async def test_exit_button_mounts(self) -> None:
        app = _SmokeApp()
        async with app.run_test() as pilot:
            button = app.query_one("#exit-btn", Button)
            self.assertIsNotNone(button)
            await pilot.click("#exit-btn")
            await pilot.pause()
            self.assertTrue(app._exit)

    async def test_current_instance_widget_renders(self) -> None:
        app = _SmokeApp()
        async with app.run_test():
            widget = CurrentInstanceWidget()
            renderable = widget.render()
            self.assertIsNotNone(renderable)
