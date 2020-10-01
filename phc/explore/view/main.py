import phc.easy as phc
import pandas as pd
from typing import Callable, Union, List, Dict

from phc.explore.view.widget import WidgetView
from phc.explore.view.widget_module import WidgetModuleView
from phc.explore.view.patient import PatientView
from phc.explore.state import State, NOT_SELECTED

from phc.explore.imports import display
from phc.explore.imports import w


class MainView(WidgetView):
    state: State

    account_w: w.Dropdown
    projects_w: w.Dropdown
    entities_w: w.Dropdown

    module_view: Union[WidgetModuleView, None]

    custom_views: Dict[type, WidgetView]

    container: w.DOMWidget

    def __init__(
        self, shared_auth: bool = True, height: int = 800, **state_kwargs
    ):
        super().__init__()
        auth = phc.Auth.shared() if shared_auth else phc.Auth()
        self.state = State(auth=auth, **state_kwargs)
        self.height = height
        self.module_view = None
        self.custom_views = {phc.Patient: PatientView}
        self.container = None

    def will_load(self):
        self.add_message("<b>Loading...</b>")

    def widget(self):
        main = super().widget()

        if not self.container:
            spacer = w.Box(children=[])
            spacer.add_class("Main-spacer")

            self.container = w.Box(
                children=[
                    w.HTML(
                        f"""
                <style>
                .Main-spacer {{
                   height: {self.height}px;
                }}
                .Main-main {{
                   position: absolute;
                   left: 0;
                   right: 0;
                   height: {self.height}px;
                }}
                </style>
                """
                    ),
                    spacer,
                    main,
                ]
            )
            main.add_class("Main-main")

        return self.container

    def did_load(self):
        self.main_widget.layout = w.Layout(flex="0 0 100%", flex_flow="column")
        self.state.load_projects()

        self.accounts_w = w.Dropdown(
            options=[NOT_SELECTED, *self.state.accounts], description="Account"
        )
        self.projects_w = w.Dropdown(
            options=[NOT_SELECTED], description="Project"
        )
        self.entities_w = w.Dropdown(options=[], description="Entity")

        self.add_widget(self.accounts_w, self.did_change_account)

    def did_change_account(self, widget: w.Dropdown):
        self.state.account = widget.value

        if self.state.account == NOT_SELECTED:
            self.remove_all_widgets()
            self.add_widget(widget)
            return

        self.projects_w.options = [
            (NOT_SELECTED, NOT_SELECTED),
            *[(p["name"], p["id"]) for _, p in self.state.projects.iterrows()],
        ]

        self.add_widget(self.projects_w, self.did_change_project_index)

    def did_change_project_index(self, widget: w.Dropdown):
        self.remove_widget(self.entities_w)

        if widget.value is NOT_SELECTED:
            # Close below views
            print("TODO: Close below views")
            return

        self.state.select_project(widget.value)

        self.add_message(
            f"<b>Loading entity counts for {self.state.project['name']}</b>"
        )

        self.entities_w.options = [
            (
                (
                    f"{r.module.__name__} ({r['count']})"
                    if r["count"]
                    else r.module.__name__
                ),
                i,
            )
            for i, r in self.state.entity_counts.iterrows()
        ]

        print(self.state.entity_counts)

        rows = self.state.entity_counts[
            self.state.entity_counts.module == phc.Patient
        ]
        if len(rows) == 1:
            self.entities_w.index = int(rows.iloc[0].name)

        self.add_widget(self.entities_w, self.did_change_entity)
        self.did_change_entity(self.entities_w)

    def did_change_entity(self, widget: w.Dropdown):
        selected = self.state.entity_counts.iloc[widget.value]
        module, count = selected["module"], selected["count"]

        if self.module_view:
            self.remove_widget(self.module_view.widget())

        self.module_view = self.custom_views.get(module, WidgetModuleView)(
            self.state, module, count
        )

        self.add_widget(self.module_view.widget())
