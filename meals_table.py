from datetime import date
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
    ]

    def handle_input(self, values:list):
        if values is None:
            return

        table = self.app.query_one("#today-food-table", DataTable)
        food = values[0]
        meal = values[1]
        quantity = values[2]

        macros = self.app.food_db_dict[food]
        print(macros)
        calories = float(macros[0])*float(quantity)
        protein = float(macros[1])*float(quantity)
        sugar = 0
        date_today = str(date.today())
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO calories (food, meal, quantity, calories, protein, sugar, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (food, meal, quantity, calories, protein, sugar, date_today),
        )
        conn.commit()
        conn.close()
        calories_id = cur.lastrowid

        table.add_row(food, meal, quantity, str(calories), str(protein), str(date.today()), key=str(calories_id))
        self.app.load_table()
        # when the first of the day is added, create entry in dates table
        # if table.row_count == 1:
            

    def action_add_food(self) -> None:
        self.app.push_screen(GetModalScreen("1"), self.handle_input)

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

        table.remove_row(row_key)
        self.app.load_table()