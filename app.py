import csv
import math
from datetime import date
import sqlite3

from textual.app import App
from textual.containers import (
    Horizontal,
    Vertical,
    HorizontalScroll,
    VerticalScroll,
    Container
)
from textual.widgets import Label, Static, DataTable
from textual.widgets import Tabs, Tab, Header, Footer
from textual.binding import Binding

from meals_table import MealsTableContainer

DB_PATH = "calories.db"

def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS calories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food TEXT NOT NULL,
            meal TEXT NOT NULL,
            quantity REAL NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            sugar REAL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

class CalorieTrackerApp(App):
    CSS_PATH = "calorie_tracker.tcss"
    VERSION = "0.1.1"

    BINDINGS = [
        Binding("1", "focus_today_food", "Meals", show=False),
        Binding("3", "focus_food_db", "Food DB", show=False),
        Binding("2", "focus_macros_history", "Dates", show=False)
    ]

    food_db_dict = {}
    
    def compose(self):
        
        self.calories_today = 0
        self.protein_today = 0

        yield Horizontal(
            Label("Calorie Tracker", id="app-label-title"),
            Label(f"Version: {CalorieTrackerApp.VERSION}", id="app-label-version"),
            Tabs(
                Tab("Tracker", id="app-tab-tracker"),
                Tab("Insights", id="app-tab-insights")
            ),
            id="app-container-header"
        )

        with Horizontal(id="content-container-outer"):
            with Vertical(classes="outer-pane outer-pane-left"):
                daily_macros_box = Container(classes="pane pane-top-left")
                daily_macros_box.border_title = "Today's Macros"
                with daily_macros_box:
                    yield Horizontal(
                        Label("Calories: ", classes="daily-calorie-marker daily-macro-marker"),
                        Label(str(self.calories_today), classes="daily-calorie-value daily-macro-value", id="calorie-today"),
                        classes = "daily-calorie-container"
                    )

                    yield Horizontal(
                        Label("Protein: ", classes="daily-protein-marker daily-macro-marker"),
                        Label(str(self.protein_today), classes="daily-protein-value daily-macro-value", id="protein-today"),
                        classes = "daily-calorie-container"
                    )

                macros_history_box = Container(classes="pane pane-bottom-left")
                macros_history_box.border_title = "Dates"
                macros_history_box.border_subtitle = "2"
                with macros_history_box:
                    yield DataTable(id="macros-history-table")

            with Vertical(classes="outer-pane outer-pane-right"):
                meals_table_container = MealsTableContainer(classes="pane pane-top-right", id="meals_table_container")
                meals_table_container.border_title = "Meals"
                meals_table_container.border_subtitle = "1"
                with meals_table_container:
                    yield DataTable(id="today-food-table")

                food_db_box = Container(classes="pane pane-bottom-right")
                food_db_box.border_title = "Food Database"
                food_db_box.border_subtitle = "3"
                with food_db_box:
                    yield DataTable(id="food-database-table")

        yield Footer()

    def on_mount(self) -> None:
        init_db()
        macros_history_table = self.query_one("#macros-history-table", DataTable)
        macros_history_table.add_column("Date", key="date", width=10)
        macros_history_table.add_column("Calories", key="calories", width=10)
        macros_history_table.add_column("Protein", key="protein", width=10)
        macros_history_table.zebra_stripes = True
        macros_history_table.cursor_type = "row"
        macros_history_table.expand = True

        today_food_table = self.query_one("#today-food-table", DataTable)
        today_food_table.add_column("Food", key="food", width=22)
        today_food_table.add_column("Meal", key="meal", width=9)
        today_food_table.add_column("Quantity", key="quantity", width=8)
        today_food_table.add_column("Calories", key="calories", width=8)
        today_food_table.add_column("Protein", key="protein", width=7)
        today_food_table.add_column("Date", key="date", width=0)
        today_food_table.zebra_stripes = True
        today_food_table.cursor_type = "row"
        today_food_table.expand = True
        today_food_table.add_row("// comment row")
        self.load_table()

        food_database_table = self.query_one("#food-database-table", DataTable)
        food_database_table.add_column("Ingredient", key="ingredient", width=26)
        food_database_table.add_column("Calories", key="calories", width=10)
        food_database_table.add_column("Protein", key="protein", width=10)
        food_database_table.add_column("Sugar", key="sugar", width=9)
        food_database_table.zebra_stripes = True
        food_database_table.cursor_type = "row"
        food_database_table.expand = True

        i = 0
        with open("data/food_db.csv", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if i == 0:
                    i = i + 1
                    continue
                
                # ingredients - calories - protein - sugar
                food_database_table.add_row(row[0], row[1], row[3], row[4])
                self.food_db_dict[row[0]] = [row[1], row[3], row[4]]

    def load_table(self) -> None:
        # clear table and load from sqlite
        today_food_table = self.query_one("#today-food-table", DataTable)
        today_food_table.clear(columns=False)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, food, meal, quantity, calories, protein, sugar, date FROM calories ORDER BY id")
        rows = cur.fetchall()

        order = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
        for i, meal_type in enumerate(order):
            counter = 0
            for calories_id, food, meal, quantity, calories, protein, sugar, dates in rows:
                if meal == meal_type:
                    counter += 1
                    if counter == 1:
                        if i != 0:
                            today_food_table.add_row(" ")
                        today_food_table.add_row(f"// {meal_type}")
                    today_food_table.add_row(str(food), str(meal), str(quantity), str(calories), str(protein), str(dates), key=str(calories_id))

        # update today's macros
        date_today = str(date.today())
        cur.execute("SELECT * FROM calories where date = ?", (date_today,))
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.app.calories_today = float(self.calories_today) + float(row[4])
            self.app.protein_today = float(self.protein_today) + float(row[5])

        calorie_label = self.query_one("#calorie-today", Label).update(str(math.trunc(self.calories_today)))
        protein_label = self.query_one("#protein-today", Label).update(str(math.trunc(self.protein_today)))

    def action_focus_today_food(self) -> None:
        self.set_focus(self.query_one("#today-food-table", DataTable))

    def action_focus_macros_history(self) -> None:
        self.set_focus(self.query_one("#macros-history-table", DataTable))

    def action_focus_food_db(self) -> None:
        self.set_focus(self.query_one("#food-database-table", DataTable))

if __name__ == "__main__":
    app = CalorieTrackerApp()
    app.run()