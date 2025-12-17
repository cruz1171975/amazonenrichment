from __future__ import annotations

import zipfile
xml_ns_main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
xml_ns_rel = "http://schemas.openxmlformats.org/package/2006/relationships"

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _col_letters_to_index(col: str) -> int:
    n = 0
    for ch in col:
        if not ch.isalpha():
            break
        n = n * 26 + (ord(ch.upper()) - 64)
    return n


def _split_cell_ref(cell_ref: str) -> tuple[str, int]:
    col = "".join([c for c in cell_ref if c.isalpha()])
    row = "".join([c for c in cell_ref if c.isdigit()])
    return col, int(row) if row else 0


@dataclass(frozen=True)
class XlsxSheet:
    name: str
    path: str  # zip internal path like xl/worksheets/sheet1.xml


class XlsxWorkbook:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._zip = zipfile.ZipFile(path)
        self._shared_strings = self._load_shared_strings()
        self._sheets = self._load_sheets()

    def close(self) -> None:
        self._zip.close()

    def __enter__(self) -> "XlsxWorkbook":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def sheets(self) -> list[XlsxSheet]:
        return list(self._sheets)

    def sheet_by_name(self, name: str) -> XlsxSheet:
        for s in self._sheets:
            if s.name == name:
                return s
        raise KeyError(f"Sheet not found: {name}")

    def read_row(self, *, sheet: XlsxSheet, row_number: int) -> dict[int, str]:
        """
        Read a worksheet row as {1-based column index -> string value}.
        """
        root = ET.fromstring(self._zip.read(sheet.path))
        ns = {"m": xml_ns_main}
        target = None
        for r in root.findall(".//m:sheetData/m:row", ns):
            if r.get("r") == str(row_number):
                target = r
                break
        if target is None:
            return {}

        out: dict[int, str] = {}
        for c in target.findall("m:c", ns):
            ref = c.get("r")
            if not ref:
                continue
            col_letters, _ = _split_cell_ref(ref)
            col_idx = _col_letters_to_index(col_letters)
            if col_idx <= 0:
                continue
            t = c.get("t")
            v = c.find("m:v", ns)
            if v is None or v.text is None:
                continue
            raw = v.text
            if t == "s":
                try:
                    out[col_idx] = self._shared_strings[int(raw)]
                except Exception:
                    out[col_idx] = ""
            else:
                out[col_idx] = raw
        return out

    def _load_shared_strings(self) -> list[str]:
        if "xl/sharedStrings.xml" not in self._zip.namelist():
            return []
        root = ET.fromstring(self._zip.read("xl/sharedStrings.xml"))
        ns = {"m": xml_ns_main}
        strings: list[str] = []
        for si in root.findall("m:si", ns):
            texts = []
            for t in si.findall(".//m:t", ns):
                texts.append(t.text or "")
            strings.append("".join(texts))
        return strings

    def _load_sheets(self) -> list[XlsxSheet]:
        wb = ET.fromstring(self._zip.read("xl/workbook.xml"))
        ns = {
            "m": xml_ns_main,
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        }
        sheets_el = wb.find("m:sheets", ns)
        if sheets_el is None:
            return []

        rel = ET.fromstring(self._zip.read("xl/_rels/workbook.xml.rels"))
        rel_ns = {"r": xml_ns_rel}
        rel_map = {r.get("Id"): r.get("Target") for r in rel.findall("r:Relationship", rel_ns)}

        sheets: list[XlsxSheet] = []
        for sh in sheets_el.findall("m:sheet", ns):
            name = sh.get("name") or ""
            rel_id = sh.get(f"{{{ns['r']}}}id") or ""
            target = rel_map.get(rel_id, "")
            if not target:
                continue
            path = "xl/" + target.lstrip("/")
            sheets.append(XlsxSheet(name=name, path=path))
        return sheets

