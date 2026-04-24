from datetime import date
import math
import sqlite3

from textual.binding import Binding
from textual.widgets import DataTable, Label
from textual.containers import Container

from modal_entry import GetModalScreen

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

        food_db_table.add_row(ingredient, calories, protein, sugar)

        # conn = sqlite3.connect(DB_PATH)
        # cur = conn.cursor()
        # cur.execute(
        #     "INSERT INTO calories (food, meal, quantity, calories, protein, sugar, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        #     (food, meal, quantity, calories, protein, sugar, date_today),
        # )
        # conn.commit()
        # conn.close()
        # calories_id = cur.lastrowid

        # self.app.load_today_food_table()
        # self.app.load_macros_history_table()
        # when the first of the day is added, create entry in dates table
        # if table.row_count == 1:1

    def action_delete_selected(self) -> None:
        table = self.app.query_one("#food-database-table", DataTable)
        coord = table.cursor_coordinate
        row_key, _column_key = table.coordinate_to_cell_key(coord)

        table.remove_row(row_key)