from datetime import date, timedelta
import math
import sqlite3

from textual.binding import Binding
from textual.widgets import DataTable, Label
from textual.containers import Container

from modal_entry import GetModalScreen

DB_PATH = "calories.db"

class MealsTableContainer(Container):
    can_focus = True
    BINDINGS = [
        Binding("a", "add_food", "Add food"),
        Binding("d", "delete_selected", "Delete row"),
        Binding("ctrl+n", "add_today", "Add today")
    ]

    def handle_input(self, values:list):
        if values is None:
            return

        table = self.app.query_one("#today-food-table", DataTable)
        food = values[0]
        meal = values[1]
        quantity = values[2]
        date_given = values[3]

        if food not in self.app.food_db_dict:
            print("Ingredient not in list")
            return

        macros = self.app.food_db_dict[food]
        calories = float(macros[0])*float(quantity)
        if macros[1] != "":
            protein = float(macros[1])*float(quantity)
        else:
            protein = 0

        sugar = 0
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO calories (food, meal, quantity, calories, protein, sugar, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (food, meal, quantity, calories, protein, sugar, date_given),
        )
        conn.commit()
        conn.close()
        calories_id = cur.lastrowid

        self.app.load_today_food_table()
        self.app.load_macros_history_table()

    def action_add_food(self) -> None:
        self.app.push_screen(GetModalScreen("1"), self.handle_input)

    def action_add_today(self) -> None:
        self.app.push_screen(GetModalScreen("1", "today"), self.handle_input)

    def action_delete_selected(self) -> None:
        table = self.app.query_one("#today-food-table", DataTable)
        coord = table.cursor_coordinate
        row_key, _column_key = table.coordinate_to_cell_key(coord)
        
        # Don't delete code generated rows for spacing
        row_values = table.get_row(row_key)
        if row_values[1] == None:
            return

        if row_key is None:
            return
        
        calories_id = row_key.value
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM calories WHERE id = ?", (calories_id,))
        conn.commit()
        conn.close()

        self.app.load_today_food_table()
        self.app.load_macros_history_table()