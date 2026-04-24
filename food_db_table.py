from datetime import date
import math
import sqlite3

from textual.binding import Binding
from textual.widgets import DataTable, Label
from textual.containers import Container

from modal_entry import GetModalScreen

DB_PATH = "calories.db"

class FoodDatabaseTable(DataTable):
    BINDINGS = [
        Binding("a", "add_food", "Add food"),
        Binding("d", "delete_selected", "Delete row"),
    ]

    def action_add_food(self) -> None:
        self.app.push_screen(GetModalScreen("3"), self.handle_input)

    def handle_input(self, values:list):
        if values is None:
            return

        food_db_table  = self.app.query_one("#food-database-table", DataTable)
        ingredient = values[0]
        calories = values[1]
        protein = values[2]
        sugar = values[3]

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO food_db (ingredient, calories, protein, sugar) VALUES (?, ?, ?, ?)",
            (ingredient, calories, protein, sugar),
        )
        conn.commit()
        conn.close()
        self.app.load_food_db_table()


    def action_delete_selected(self) -> None:
        table = self.app.query_one("#food-database-table", DataTable)
        coord = table.cursor_coordinate
        row_key, _column_key = table.coordinate_to_cell_key(coord)

        food_id = row_key.value

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM food_db WHERE id = ?", (food_id,))
        conn.commit()
        conn.close()

        table.remove_row(row_key)