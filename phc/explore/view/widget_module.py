from phc.explore.imports import w

from phc.easy.auth import Auth
from phc.easy.item import Item

from phc.explore.state import State
from phc.explore.view.widget import WidgetView


class WidgetModuleView(WidgetView):
    state: State
    auth: Auth
    module: Item
    count: int

    def __init__(self, state: State, module: type, count: int):
        super().__init__()
        self.state = state
        self.auth = state.auth  # TODO: Remove this
        self.module = module
        self.count = count

    def will_load(self):
        self.main_widget.layout = w.Layout(flex="0 0 100%")
