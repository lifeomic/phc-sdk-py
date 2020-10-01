from phc.explore.imports import w
from typing import Callable

from phc.explore.view.widget import WidgetView


class NavigationView(WidgetView):
    width: int
    _left_buttons: w.HBox
    _right_buttons: w.HBox
    _title: w.Label

    def __init__(self, title: str = "", width: int = 800):
        super().__init__()
        self._left_buttons = w.HBox(
            children=[], layout=w.Layout(width="{int(width / 4)}px")
        )
        self._right_buttons = w.HBox(
            children=[], layout=w.Layout(width="{int(width / 4)}px")
        )
        self._title = w.Label(value=title)

    def will_load(self):
        super().will_load()
        style = w.HTML(
            """
        <style>
            .NavigationView-nav-header {
                background-color: #F5F5F5;
            }
            .NavigationView-nav-title {
                color: #111;
            }
            .NavigationView-nav-buttons {
                position: absolute;
                top: 0px;
                left: 0px;
            }
        </style>
        """
        )

        self._title.add_class("NavigationView-nav-title")
        hbox = w.HBox(
            children=[self._title, style],
            layout=w.Layout(flex="0 0 100%", justify_content="center"),
        )
        hbox.add_class("NavigationView-nav-header")
        self.add_widget(hbox)

        nav_buttons = w.HBox(
            children=[self._left_buttons, self._right_buttons],
            layout=w.Layout(flex="0 0 100%", justify_content="space-between"),
        )
        nav_buttons.add_class("NavigationView-nav-buttons")
        self.add_widget(nav_buttons)

    def did_load(self):
        super().did_load()
        self.main_widget.layout = w.Layout(
            margin="10px 0 0 0",
            flex_flow="column",
            height="33px",
            display="table",
        )

    @property
    def title(self):
        return self._title.value

    @title.setter
    def title(self, title: str):
        self._title.value = title

    def add_left_button(
        self, button: w.Button, handler: Callable[[w.Button], None]
    ):
        button.on_click(handler)
        self._left_buttons.children = [*self._left_buttons.children, button]

    def left_button(self):
        return self._left_buttons.children[0]
