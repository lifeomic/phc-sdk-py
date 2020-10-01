import pandas as pd
from phc.explore.imports import w
from phc.explore.view.widget import WidgetView
from phc.explore.column import Column, ColumnConfig
from typing import Callable


class CustomColumnView(WidgetView):
    preview: pd.DataFrame
    column_preview: w.Output
    button_w: w.Button

    column: Column
    config: ColumnConfig

    def __init__(self, preview: pd.DataFrame, column: Column):
        super().__init__()
        self.preview = preview
        self.column_preview = w.Output()
        self.column = column
        self.config = ColumnConfig()

        # TODO: Support multi-column in the future
        assert self.column.multi_column is False

    def did_select_column(self, widget: w.Dropdown):
        self.config.column = widget.value

        count = 10

        self.column_preview.outputs = []
        self.column_preview.append_display_data(
            pd.concat(
                [
                    self.column.transform(
                        self.preview.head(count), self.config
                    ),
                    pd.Series(["  :  " for _ in range(count)], name=""),
                    self.preview.head(10)[self.config.column],
                ],
                axis=1,
            )
        )

    def will_load(self):
        self.column_selector = w.Dropdown(
            options=self.column.get_possible_columns(self.preview)
        )
        self.add_widget(self.column_selector, self.did_select_column)
        self.add_widget(self.column_preview)

        self.did_select_column(self.column_selector)
