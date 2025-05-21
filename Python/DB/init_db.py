from __future__ import annotations
import requests, time, pathlib, sqlite3
from datetime import datetime, date
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from os.path import exists

DB_FILE    = pathlib.Path("feedback.db")
def init_db() -> None:
    """Ensure SQLite file & table exist."""
    with sqlite3.connect(DB_FILE) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
              id               INTEGER PRIMARY KEY AUTOINCREMENT,
              camunda_task_id  TEXT    NOT NULL,
              created_at       TEXT    NOT NULL,
              feedback_date    TEXT    NOT NULL,
              feedback_type    TEXT,
              query            TEXT,
              email            TEXT,
              phone            TEXT,
              first_name       TEXT,
              last_name        TEXT,
              feedback_text    TEXT,
              needs_clarification TEXT,
              urgency          TEXT,
              impact_scope     TEXT,
              forward_to_dept  TEXT,
              link_to_add_form TEXT,
              reminder_sent    TEXT,
              status           TEXT
            )
            """
        )
    print("SQLite ready →", DB_FILE)



init_db()