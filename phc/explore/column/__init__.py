import pandas as pd
from typing import Callable, List, Optional
from pydantic import BaseModel


class ColumnConfig(BaseModel):
    column: Optional[str]
    columns: Optional[List[str]]


class Column(BaseModel):
    name: str
    get_possible_columns: Callable[[pd.DataFrame], List[str]]
    transform: Callable[[pd.DataFrame, ColumnConfig], pd.Series]
    multi_column: bool = False

    def is_available(self, preview: pd.DataFrame):
        return len(self.get_possible_columns(preview)) > 0
