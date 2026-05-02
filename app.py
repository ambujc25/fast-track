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
from textual.widgets import Label, Static, DataTable, Input
from textual.widgets import Tabs, Tab, Header, Footer
from textual.binding import Binding

from meals_table import MealsTableContainer
from dates_table import DatesTable
from food_db_table import FoodDatabaseTable

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS food_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            sugar REAL
        )
    """)

    conn.commit()
    conn.close()

class CalorieTrackerApp(App):
    CSS_PATH = "calorie_tracker.tcss"
    VERSION = "1.0.0"

    BINDINGS = [
        Binding("1", "focus_today_food", "Meals", show=False),
        Binding("3", "focus_food_db", "Food DB", show=False),
        Binding("2", "focus_macros_history", "Dates", show=False)
    ]

    food_db_dict = {}
    view_id_list = ["content-container-outer-tracker-view", "content-container-outer-recipes-view"]

    def compose(self):
        
        self.calories_today = 0
        self.protein_today = 0
        self.offline_mode = False
        self.logged_in = True

        yield Horizontal(
            Label("Calorie Tracker", id="app-label-title"),
            Label(f"Version: {CalorieTrackerApp.VERSION}", id="app-label-version"),
            Tabs(
                Tab("Tracker", id="content-container-outer-tracker"),
                Tab("Recipes", id="content-container-outer-recipes")
            ),
            id="app-container-header"
        )

        if self.offline_mode or self.logged_in:
            with Horizontal(id="content-container-outer-tracker-view"):
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
                        yield DatesTable(id="macros-history-table")

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
                        yield FoodDatabaseTable(id="food-database-table")

            with Horizontal(id="content-container-outer-recipes-view"):
                with Vertical(classes="outer-pane outer-pane-left"):
                    recipe_list_box = Container(classes="pane pane-left")
                    recipe_list_box.border_title = "Recipe List"
                    with recipe_list_box:
                        yield DataTable(id="recipe-list-table")

                with Vertical(classes="outer-pane outer-pane-right"):
                    recipe_full_box = Container(classes="pane pane-top-right")
                    recipe_full_box.border_title = "Recipe"
                    with recipe_full_box:
                        yield Label("Recipe")

                    ingredient_list_box = Container(classes="pane pane-bottom-right")
                    ingredient_list_box.border_title = "Ingredient List"
                    with ingredient_list_box:
                        yield Label("Recipe")

        else:
            with Vertical(id="login-container-outer"):
                yield Input(placeholder="Login", id="username", classes="input-login")
                yield Input(placeholder="Password", id="password", classes="input-login")
        yield Footer()

    def on_mount(self) -> None:
        if self.logged_in:
            init_db()

            # hide all
            for container_id in self.view_id_list:
                self.query_one(f"#{container_id}").display = False

            # show default tab
            self.query_one(f"#content-container-outer-tracker-view").display = True

            macros_history_table = self.query_one("#macros-history-table", DataTable)
            macros_history_table.add_column("Date", key="date", width=10)
            macros_history_table.add_column("Calories", key="calories", width=10)
            macros_history_table.add_column("Protein", key="protein", width=10)
            macros_history_table.zebra_stripes = True
            macros_history_table.cursor_type = "row"
            macros_history_table.expand = True
            self.load_macros_history_table()

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
            self.load_today_food_table()

            food_database_table = self.query_one("#food-database-table", DataTable)
            food_database_table.add_column("Ingredient", key="ingredient", width=26)
            food_database_table.add_column("Calories", key="calories", width=10)
            food_database_table.add_column("Protein", key="protein", width=10)
            food_database_table.add_column("Sugar", key="sugar", width=9)
            food_database_table.zebra_stripes = True
            food_database_table.cursor_type = "row"
            food_database_table.expand = True
            self.load_food_db_table()

            recipe_list_table = self.query_one("#recipe-list-table", DataTable)
            recipe_list_table.add_column("Name", key="name")
            recipe_list_table.add_column("Calories", key="calories")
            recipe_list_table.add_column("Protein", key="protein")

    def on_tabs_tab_activated(self, event: Tabs.TabActivated):
        # hide all
        for container_id in self.view_id_list:
            self.query_one(f"#{container_id}").display = False

        # show selected
        selected_tab = event.tab.id
        self.query_one(f"#{selected_tab}-view").display = True


    def load_food_db_table(self) -> None:
        food_database_table = self.query_one("#food-database-table", DataTable)
        food_database_table.clear(columns=False)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("SELECT id, ingredient, calories, protein, sugar FROM food_db ORDER BY id")
        rows = cur.fetchall()

        for food_id, ingredient, calories, protein, sugar in rows:
            food_database_table.add_row(str(ingredient), str(calories), str(protein), str(sugar), key=str(food_id))
            self.food_db_dict[ingredient] = [calories, protein, sugar]


    def load_today_food_table(self, date_given=None) -> None:
        # clear table and load from sqlite
        today_food_table = self.query_one("#today-food-table", DataTable)
        today_food_table.clear(columns=False)

        macros_history_table = self.query_one("#macros-history-table", DataTable)

        date_selected = str(date.today())
        if len(macros_history_table.rows) != 0:
            coord = macros_history_table.cursor_coordinate
            row_key, _column_key = macros_history_table.coordinate_to_cell_key(coord)
            row_values = macros_history_table.get_row(row_key)
            date_selected = row_values[0]

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        if date_given is None:
            cur.execute("SELECT id, food, meal, quantity, calories, protein, sugar, date FROM calories where date = ? ORDER BY id", (date_selected,))
        else:
            cur.execute("SELECT id, food, meal, quantity, calories, protein, sugar, date FROM calories where date = ? ORDER BY ID", (date_given,))
        rows = cur.fetchall()
        print(rows)
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
        cur.execute("SELECT * FROM calories where date = ?", (date_selected,))
        rows = cur.fetchall()

        self.calories_today = 0
        self.protein_today = 0

        for row in rows:
            self.app.calories_today = float(self.calories_today) + float(row[4])
            self.app.protein_today = float(self.protein_today) + float(row[5])

        calorie_label = self.query_one("#calorie-today", Label).update(str(math.trunc(self.calories_today)))
        protein_label = self.query_one("#protein-today", Label).update(str(math.trunc(self.protein_today)))

    def load_macros_history_table(self) -> None:
        macros_history_table = self.query_one("#macros-history-table", DataTable)
        coord = macros_history_table.cursor_coordinate

        date_selected = None
        if coord is not None:
            try:
                row_key, _column_key = macros_history_table.coordinate_to_cell_key(coord)
                date_selected = macros_history_table.get_row(row_key)[0]
            except Exception:
                coord = None
        
        macros_history_table.clear(columns=False)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT date, SUM(calories) as total_calories, SUM(protein) as total_protein
            FROM calories
            GROUP BY date
            ORDER BY date DESC
        """)
        rows = cur.fetchall()
        for date, calories, protein in rows:
            macros_history_table.add_row(str(date), str(math.trunc(float(calories))), str(math.trunc(float(protein))), key=str(date))
            if date_selected is not None and str(date) == date_selected:
                macros_history_table.move_cursor(row=(len(macros_history_table.rows)-1), column=0)

    def action_focus_today_food(self) -> None:
        self.set_focus(self.query_one("#today-food-table", DataTable))

    def action_focus_macros_history(self) -> None:
        self.set_focus(self.query_one("#macros-history-table", DataTable))

    def action_focus_food_db(self) -> None:
        self.set_focus(self.query_one("#food-database-table", DataTable))

if __name__ == "__main__":
    app = CalorieTrackerApp()
    app.run()