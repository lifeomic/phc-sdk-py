import os
import re
import pandas as pd


class CSVWriter:
    """Class for progressively writing batches of pandas data frames to a CSV
    file where additional columns may be added in subsequent writes
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.bak_filename = filename + ".bak"
        self.batch_filename = filename + ".batch.bak"

    def write(self, frame: pd.DataFrame):
        """Write a data frame to an existing CSV file without loading the entire
        file into memory
        """

        # Remove newlines from column names
        frame.columns = [
            re.sub(r"[\t\n]", "", c) for c in frame.columns.tolist()
        ]

        if not os.path.exists(self.filename):
            frame.to_csv(
                self.filename, date_format="%Y-%m-%dT%H:%M:%S%z", index=False
            )
            return

        self._copy_to_backup_file_without_header()

        original_columns = self._columns()
        new_columns = [c for c in frame.columns if c not in original_columns]
        columns_not_in_this_batch = [
            c for c in original_columns if c not in frame.columns
        ]

        # Create frame with all columns (order doesn't matter here)
        superset_frame = pd.concat(
            [frame, pd.DataFrame(None, columns=columns_not_in_this_batch)]
        )

        # Create ordered list to select order of values when writing to the file
        ordered_columns = [*original_columns, *new_columns]

        superset_frame[ordered_columns].to_csv(self.batch_filename, index=False)

        self._finalize()

    def _columns(self):
        return pd.read_csv(self.filename, nrows=0).columns.tolist()

    def _copy_to_backup_file_without_header(self):
        os.system(f"sed 1,1d {self.filename} > {self.bak_filename}")

    def _finalize(self):
        os.system(
            f"""
          head -n 1 {self.batch_filename} > {self.filename} && \
            cat {self.bak_filename} >> {self.filename} && \
            sed 1,1d {self.batch_filename} >> {self.filename} && \
            rm {self.batch_filename} {self.bak_filename}
        """
        )
