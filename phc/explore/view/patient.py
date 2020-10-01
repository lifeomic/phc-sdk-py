import pandas as pd
from phc.explore.imports import w
import threading
import pprint
from typing import Dict, Callable, List

from phc.easy.auth import Auth

from phc.explore.column import Column, ColumnConfig
from phc.explore.custom_frame import CustomFrame

from phc.explore.view.widget import WidgetView
from phc.explore.view.widget_module import WidgetModuleView
from phc.explore.view.panel.patient import PatientPanelView

from phc.explore.view.navigation.button import NavigationButton
from phc.explore.view.navigation import NavigationView
from phc.explore.view.column.custom import CustomColumnView

from collections import namedtuple as Struct


class PatientView(WidgetModuleView):
    hbox: w.HBox
    preview: pd.DataFrame
    table_output: w.Output
    navigation: NavigationView

    column_configs: Dict[str, ColumnConfig]

    def will_load(self):
        super().will_load()
        self.navigation = NavigationView(title="Patient")

        self.navigation.add_left_button(
            w.Button(description="Columns", layout=dict(width="80px")),
            self.show_columns,
        )

        self.preview = pd.DataFrame()
        self.column_configs = {}
        self.table_output = w.Output(layout=dict(overflow_x="auto"))

        self.add_widget(self.navigation.widget())
        self.add_message("<b>Loading preview...</b>")
        self.main_widget.layout = w.Layout(flex_flow="column", height="100%")

        def load_preview(self):
            self.preview = self.module.get_data_frame(
                page_size=100, auth_args=self.auth
            )
            self.update_preview()
            self.add_widget(self.table_output)
            if self.count:
                self.add_widget(
                    w.HTML(f"<p>Displaying preview of {self.count} rows</p>")
                )

        thread = threading.Thread(target=load_preview, args=(self,))
        thread.start()

    def modal_did_finish(self, attrs: dict):
        super().modal_did_finish(attrs)

        column, config = attrs["column"], attrs["config"]
        self.column_configs[column.name] = config.dict()
        self.update_preview()

    def update_preview(self):
        columns = [("id", {"raw": True}), *self.column_configs.items()]

        preview_df = CustomFrame.transform(self.module, self.preview, columns)

        # Export code to the current Jupyter Notebook cell :-)
        # LiveCode.export(self.state.auth, self.module, columns)

        self.table_output.outputs = []

        self.table_output.append_display_data(preview_df.head(20))

    def show_columns(self, _w=None):
        self.present_modal(
            PatientPanelView(preview=self.preview, auth=self.auth)
        )
