import threading
from collections import namedtuple as Struct
from typing import Callable, List, Union, Any

from phc.explore.util.jupyter_lab import JupyterLab

from phc.explore.imports import w
from phc.explore.imports import display

ModalDelegate = Struct("ModalDelegate", ["modal_did_finish"])

_WidgetView = Any


class WidgetView:
    widgets: List[w.DOMWidget]
    will_move_to_window: bool

    modal_delegate: Union[ModalDelegate, None]
    modal: Union[w.DOMWidget, None]
    modal_view: Union[_WidgetView, None]

    def __init__(self):
        self.main_widget = w.Box(children=[])
        self.main_widget.layout = dict(flex_flow="column")
        self.will_move_to_window = False
        self.widgets = []

    def add_widget(
        self, widget: w.DOMWidget, handler: Callable[[w.DOMWidget], None] = None
    ):
        if self.has_widget(widget):
            return

        def callback(change):
            if handler:
                handler(change.owner)
            else:
                self.did_change_value(change.owner)

        widget.observe(callback, "value")
        self.widgets.append(widget)
        self.main_widget.children = self.widgets

    def add_message(self, html: str):
        output = w.Output()

        with output:
            display(w.HTML(html))

        self.main_widget.children = [*self.widgets, output]

    def remove_widget(self, widget: w.DOMWidget):
        if widget in self.widgets:
            self.widgets.remove(widget)

        self.main_widget.children = self.widgets

    def remove_all_widgets(self):
        self.widgets = []
        self.main_widget.children = self.widgets

    def has_widget(self, widget: w.DOMWidget):
        return widget in self.widgets

    def will_load(self):
        """Lifecycle method for loading sub-widgets"""
        pass

    def did_load(self):
        """Lifecycle method for doing async heavy lifting after load"""
        pass

    def did_change_value(self, widget: w.DOMWidget):
        """Lifecycle method for changes in widgets that don't have handlers"""
        pass

    def widget(self):
        if self.will_move_to_window:
            return self.main_widget

        self.will_move_to_window = True
        self.will_load()

        thread = threading.Thread(target=self.did_load, args=[])
        thread.start()

        return self.main_widget

    ## Modals

    def modal_did_finish(self, options: dict):
        self._exit_modal()
        pass

    def _exit_modal(self, _w=None):
        self.remove_widget(self.modal)
        self.modal = None
        self.modal_view = None

    def _background_color(self):
        if JupyterLab.is_dark_theme():
            return "rgba(0, 0, 0, 0.9)"
        else:
            return "rgba(255, 255, 255, 0.9)"

    def present_modal(self, view: _WidgetView):
        self.modal_view = view

        close_button = w.Button(icon="close", layout=dict(width="30px"))
        close_button.on_click(self._exit_modal)
        right_align_box = w.HBox(
            children=[close_button], layout=dict(justify_content="flex-end")
        )

        self.add_widget(
            w.HTML(
                f"""
        <style>
          .Modal-container {{
             position: absolute;
             top: 0;
             left: 0;
             right: 0;
             bottom: 0;
             background: rgba(0, 0, 0, 0.2);
          }}
          .Modal-content {{
             border: 1px solid black;
             background: {self._background_color()};
             margin: 10px auto;
             height: min-content;
          }}
        </style>
        """
            )
        )

        self.modal_view.modal_delegate = ModalDelegate(self.modal_did_finish)

        modal_content = w.VBox(
            children=[right_align_box, self.modal_view.widget()]
        )
        modal_content.add_class("Modal-content")

        self.modal = w.Box(children=[modal_content])
        self.modal.add_class("Modal-container")

        self.add_widget(self.modal)
