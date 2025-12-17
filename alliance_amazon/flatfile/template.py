from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..spreadsheets.xlsx import XlsxWorkbook


@dataclass(frozen=True)
class AmazonTemplateSheet:
    xlsm_path: Path
    sheet_name: str = "Template"
    local_label_row: int = 4
    attribute_key_row: int = 5

    def read_headers(self) -> tuple[list[str], list[str]]:
        """
        Returns (local_labels, attribute_keys), aligned by column index.

        Index 0 corresponds to column 1.
        """
        with XlsxWorkbook(self.xlsm_path) as wb:
            sheet = wb.sheet_by_name(self.sheet_name)
            labels = wb.read_row(sheet=sheet, row_number=self.local_label_row)
            keys = wb.read_row(sheet=sheet, row_number=self.attribute_key_row)
        max_col = max([0, *labels.keys(), *keys.keys()])
        local_labels = [labels.get(i, "") for i in range(1, max_col + 1)]
        attribute_keys = [keys.get(i, "") for i in range(1, max_col + 1)]
        return local_labels, attribute_keys

