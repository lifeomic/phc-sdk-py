import pandas as pd
from phc.explore.imports import w
from typing import List

import phc.easy as phc

from phc.explore.custom_frame import CustomFrame

from phc.explore.view.widget import WidgetView

from phc.explore.view.column.custom import CustomColumnView

from phc.explore.column import Column


class PatientPanelView(WidgetView):
    preview: pd.DataFrame
    auth: phc.Auth

    output: w.Output
    details: w.VBox
    submit: w.HBox

    current_column: CustomColumnView
    columns: List[Column]

    def __init__(self, preview: pd.DataFrame, auth: phc.Auth):
        super().__init__()
        self.preview = preview
        self.auth = auth
        self.columns = [
            c
            for c in CustomFrame.get_columns(phc.Patient)
            if c.is_available(self.preview)
        ]
        self.current_column = None
        self.output = w.Output()

    def finish(self, _w=None):
        self.modal_delegate.modal_did_finish(
            {
                "column": self.current_column.column,
                "config": self.current_column.config,
            }
        )

    def did_select_column(self, name: str):
        column = next(filter(lambda c: c.name == name, self.columns))
        self.current_column = CustomColumnView(self.preview, column)

        self.details.children = [self.current_column.widget(), self.submit]

    def will_load(self):
        super().will_load()
        self.main_widget.layout = w.Layout(flex_flow="column", padding="5px")

        # TODO: What happens if no columns available?

        column_selector = w.Select(
            options=[c.name for c in self.columns],
            value=self.columns[0].name,
            layout=dict(width="100px"),
        )

        column_selector.observe(
            lambda c: self.did_select_column(c.owner.value), "value"
        )

        save_button = w.Button(description="Save")
        save_button.on_click(self.finish)
        self.submit = w.HBox(
            children=[save_button], layout=dict(justify_content="flex-end")
        )

        self.details = w.VBox(
            children=[w.Label(value="Loading..."), self.submit]
        )

        split = w.HBox(children=[column_selector, self.details])

        self.add_widget(split)

        # Set the current column view
        self.did_select_column(column_selector.value)
