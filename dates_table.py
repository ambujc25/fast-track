from datetime import date
import math
import sqlite3

from textual.binding import Binding
from textual.widgets import DataTable, Label
from textual.containers import Container

from modal_entry import GetModalScreen

DB_PATH = "calories.db"

class DatesTable(DataTable):
    BINDINGS = [
        ("enter", "show_meals", "Show Meals"),
    ]

    def action_show_meals(self):
        food_table = self.app.query_one("#today-food-table", DataTable)
        food_table.clear(columns=False)
        table = self.app.query_one("#macros-history-table", DataTable)
        coord = table.cursor_coordinate
        row_key, _column_key = table.coordinate_to_cell_key(coord)

        row_values = table.get_row(row_key)
        date_selected = row_values[0]

        self.app.load_today_food_table(date_selected)