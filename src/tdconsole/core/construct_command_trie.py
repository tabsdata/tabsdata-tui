import shlex

import click
import typer
from tabsdata.api.tabsdata_server import TabsdataServer
from textual.app import App, ComposeResult
from textual.widgets import Input
from textual_autocomplete import AutoComplete
from textual_autocomplete._autocomplete import DropdownItem, TargetState


class CliAutoComplete(AutoComplete):
    def get_search_string(self, state: TargetState) -> str:
        return state.text.split(" ")[-1]

    def should_show_dropdown(self, search_string: str) -> bool:
        return True

    def apply_completion(self, completion, state: TargetState) -> None:
        val = str(getattr(completion, "main", completion))

        t = state.text
        if t.endswith(" "):
            new = t + val + " "
        else:
            parts = t.split(" ")
            parts[-1] = val
            new = " ".join(parts) + " "

        self.target.value = new
        self.target.cursor_position = len(new)

    def post_completion(self) -> None:
        self._handle_target_update()


def build_typer_tree() -> click.Command:
    server = TabsdataServer("127.0.0.1:2457", "admin", "tabsdata", "sys_admin")
    colls = [c.name for c in server.list_collections()]

    app = typer.Typer(name="td")
    table = typer.Typer()
    app.add_typer(table, name="table")

    CollChoice = click.Choice(colls, case_sensitive=False)

    @table.command()
    def sample(
        coll: str = typer.Option(..., "--coll", click_type=CollChoice),
        name: str = typer.Option(..., "--name"),
    ):
        pass

    @table.command()
    def schema(
        coll: str = typer.Option(..., "--coll", click_type=CollChoice),
        name: str = typer.Option(..., "--name"),
    ):
        pass

    return typer.main.get_command(app)


Multi = getattr(click, "MultiCommand", click.Group)


def walk_click(cmd: click.Command, tokens: list[str]):
    cur = cmd
    i = 1
    while i < len(tokens) and isinstance(cur, Multi):
        nxt = tokens[i]
        print(i)
        print(len(tokens))
        print(nxt)
        if nxt in cur.commands:
            cur = cur.commands[nxt]
            i += 1
            print(type(cur))
        else:
            print("finish")
            break
    return cur, tokens[i:]


def click_suggestions(root: click.Command, text: str) -> list[str]:
    tokens = shlex.split(text) if text.strip() else []
    cur, rest = walk_click(root, tokens)

    if rest:
        last = rest[-1]
        for p in getattr(cur, "params", []):
            if isinstance(p, click.Option) and last in (p.opts + p.secondary_opts):
                ch = getattr(p.type, "choices", None)
                return list(ch) if ch else []

    # Otherwise suggest subcommands (if still at a MultiCommand) + unseen options
    seen = {t for t in rest if t.startswith("-")}

    subs = list(cur.commands.keys()) if isinstance(cur, Multi) and not rest else []

    opts: list[str] = []
    for p in getattr(cur, "params", []):
        if isinstance(p, click.Option):
            for o in p.opts + p.secondary_opts:
                if o not in seen:
                    opts.append(o)

    return subs + opts


class DynamicDataApp(App[None]):
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+b", "go_back", "Go Back"),
    ]

    def __init__(self):
        self.root = build_typer_tree()  # click.Command tree
        super().__init__()

    def compose(self) -> ComposeResult:
        input_widget = Input()
        yield input_widget
        yield CliAutoComplete(input_widget, candidates=self.candidates_callback)

    def candidates_callback(self, state: TargetState) -> list[DropdownItem]:
        items = click_suggestions(self.root, state.text)
        return [DropdownItem(i) for i in items]


if __name__ == "__main__":
    if True:
        DynamicDataApp().run()
    items = click_suggestions(build_typer_tree(), "td table sample")
    print(items)


# from dataclasses import dataclass, field
# from typing import Awaitable, Callable, Optional

# from tabsdata.api.tabsdata_server import TabsdataServer
# from textual.app import App, ComposeResult
# from textual.widgets import Input
# from textual_autocomplete import AutoComplete
# from textual_autocomplete._autocomplete import DropdownItem, TargetState

# ValueProvider = Callable[[], Awaitable[list[str]]]
# import typer
# from tabsdata.api.tabsdata_server import TabsdataServer


# @dataclass
# class Node:
#     children: dict[str, "Node"] = field(default_factory=dict)
#     value_provider: Optional[ValueProvider] = None  # if next token is an enum value
#     arg: bool = False

#     def search(self, key: str) -> Optional["Node"]:
#         return self.children.get(key)

#     def construct_collections(self):
#         server = TabsdataServer("127.0.0.1:2457", "admin", "tabsdata", "sys_admin")
#         collections = server.list_collections()
#         collections = [i.name for i in collections]

#         node = Node(arg=True)
#         for i in collections:
#             node.children[i] = Node()
#         return node


# class CliAutoComplete(AutoComplete):
#     def get_search_string(self, state: TargetState) -> str:
#         # Only the token currently being typed.
#         t = state.text
#         if t.endswith(" "):
#             return t.split(" ")[-1]
#         return t.split(" ")[-1]

#     def should_show_dropdown(self, search_string: str) -> bool:
#         """
#         Determine whether to show or hide the dropdown based on the current state.

#         This method can be overridden to customize the visibility behavior.

#         Args:
#             search_string: The current search string.

#         Returns:
#             bool: True if the dropdown should be shown, False otherwise.
#         """
#         return True

#     def apply_completion(self, completion, state: TargetState) -> None:
#         # completion is usually a DropdownItemHit/DropdownItem; grab its main text
#         val = getattr(completion, "main", completion)
#         val = str(val)

#         t = state.text
#         if t.endswith(" "):
#             new = t + val + " "
#         else:
#             parts = t.split(" ")
#             parts[-1] = val
#             new = " ".join(parts) + " "

#         self.target.value = new
#         self.target.cursor_position = len(new)

#     def post_completion(self) -> None:
#         # Don't hide after completion; instead rebuild+show based on new state
#         self._handle_target_update()


# async def list_collections() -> list[str]:
#     return ["default", "analytics", "prod"]


# class DynamicDataApp(App[None]):
#     BINDINGS = [
#         ("ctrl+c", "quit", "Quit"),
#         ("ctrl+b", "go_back", "Go Back"),
#     ]

#     def __init__(self):
#         self.root = self.build_cli_trie()
#         super().__init__()

#     def compose(self) -> ComposeResult:
#         input_widget = Input()
#         yield input_widget
#         yield CliAutoComplete(input_widget, candidates=self.candidates_callback)

#     def candidates_callback(self, state: TargetState) -> list[DropdownItem]:
#         text = state.text
#         text_args = text.split(" ")
#         cursor = self.root
#         arg_cursor = cursor
#         freeze_flag = False
#         frozen_cursor = cursor
#         while len(text_args) > 0:
#             child_query = cursor.search(text_args[0])
#             self.app.notify(f"cursor: {str(cursor)}")
#             self.app.notify(f"child_query: {str(child_query)}")
#             if not child_query:
#                 break
#             if child_query.arg == True:
#                 freeze_flag = True
#                 frozen_cursor = cursor

#             cursor = child_query
#             text_args.pop(0)

#         items = list(cursor.children.keys())
#         arg_items = list(arg_cursor.children.keys())
#         # self.app.notify(f"cursor: {str(items)}")
#         # self.app.notify(f"arg cursor: {str(arg_items)}")
#         return [DropdownItem(item) for item in items]

#     def build_cli_trie(self):
#         server = TabsdataServer("127.0.0.1:2457", "admin", "tabsdata", "sys_admin")
# COLLS = [c.name for c in server.list_collections()]

# app = typer.Typer(name="td")
# table = typer.Typer()
# app.add_typer(table, name="table")

# @table.command()
# def sample(
#     coll: str = typer.Option(..., "--coll", case_sensitive=False, show_choices=True, rich_help_panel="Options"),
#     name: str = typer.Option(..., "--name"),
# ):
#     ...

# @table.command()
# def schema(
#     coll: str = typer.Option(..., "--coll", case_sensitive=False, show_choices=True, rich_help_panel="Options"),
#     name: str = typer.Option(..., "--name"),
# ):
#     ...


# if __name__ == "__main__":
#     app = DynamicDataApp()
#     app.run()
