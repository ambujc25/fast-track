from datetime import date, timedelta

from textual.app import App
from textual.containers import (
    Horizontal,
    Vertical,
    HorizontalScroll,
    VerticalScroll,
    Center,
    Middle,
    VerticalGroup,
    HorizontalGroup,
    Container
)
from textual.widgets import Label, Static, Input, Footer, Button, OptionList
from textual.widgets import Tabs, Tab, ListView, ListItem, Header, DataTable
from textual.binding import Binding
from textual.screen import ModalScreen

class GetModalScreen(ModalScreen):
    CSS_PATH = "modal_screen.tcss"

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    contents = {
        "1": ["Food", "Meal", "Quantity"],
        "3": ["Ingredient", "Calories", "Protein", "Sugar"]
    }


    def __init__(self, form_type, today=False):
        super().__init__()
        self.setting_input_by_code = False
        self.food_suggestions = self.app.food_db_dict.keys()
        self.meal_suggestions = ["Breakfast", "Lunch", "Snacks", "Dinner"]
        self.form_type = form_type
        self.today = today
        self.suggestion_dict = {
            "food": self.food_suggestions,
            "meal": self.meal_suggestions
        }

        self.date_today = str(date.today())
        self.date_selected = str(date.today())
        macros_history_table = self.app.query_one("#macros-history-table", DataTable)
        if len(macros_history_table.rows) != 0:
            coord = macros_history_table.cursor_coordinate
            row_key, _column_key = macros_history_table.coordinate_to_cell_key(coord)
            row_values = macros_history_table.get_row(row_key)
            self.date_selected = row_values[0]

    def compose(self):
        with VerticalGroup(id="dialog"):

            yield Header(
                id="modal-header",
                show_clock = True,
                icon = "x"
            )

            with Container(id="dialog-body"):
                for question in self.contents[self.form_type]:
                    with Container(classes = f"form form-{question}"):
                        yield Label(f"{question}:")
                        yield Input(placeholder=f"Add {question}...", classes="entry-input", id=f"input-{question}")
                        if question == "Food":
                            option_list = OptionList(*self.food_suggestions, id="food_suggestions")
                            option_list.styles.display = "none"
                            yield option_list
                        if question == "Meal":
                            option_list = OptionList(*self.meal_suggestions, id="meal_suggestions")
                            option_list.styles.display = "none"
                            yield option_list
 

            yield Footer(id="modal-footer")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        self.setting_input_by_code = True
        question = event.option_list.id.split("_")[0]
        self.query_one(f"#input-{question.capitalize()}", Input).value = str(event.option.prompt)
        self.query_one(f"#{event.option_list.id}", OptionList).clear_options()     
        self.query_one(f"#{event.option_list.id}", OptionList).styles.display = "none" 
        self.query_one(f"#input-{question.capitalize()}").focus()

    def on_input_changed(self, event: Input.Changed):
        input_id = event.input.id
        if input_id != "input-Food" and input_id != "input-Meal":
            return

        if self.setting_input_by_code:
            self.setting_input_by_code = False
            return

        question = input_id[6:].lower()
        self.query_one(f"#{question}_suggestions", OptionList).styles.display = "block" 
        value = event.value.lower().strip()
        matches = [food for food in self.suggestion_dict[question] if value in food.lower()]
        self.query_one(f"#{question}_suggestions", OptionList).clear_options()
        self.query_one(f"#{question}_suggestions", OptionList).add_options(matches)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        current_question = event.input.id[6:]
        content_list = self.contents[self.form_type]
        current_index = content_list.index(current_question)

        if current_index != (len(content_list) - 1):
            self.query_one(f"#input-{content_list[current_index+1]}").focus()
            return

        if self.form_type == "1":
            food = self.query_one("#input-Food", Input).value
            meal = self.query_one("#input-Meal", Input).value.strip()
            quantity = self.query_one("#input-Quantity", Input).value.strip()
            if self.today:
                date = self.date_today
            else:
                date = self.date_selected

            if not food or not meal or not quantity:
                self.dismiss(None)
                return

            self.dismiss([food, meal, quantity, date])
        elif self.form_type == "3":
            ingredient = self.query_one("#input-Ingredient", Input).value.strip()
            calories = self.query_one("#input-Calories", Input).value.strip()
            protein = self.query_one("#input-Protein", Input).value.strip()
            sugar = self.query_one("#input-Sugar", Input).value.strip()
            print(ingredient, calories, protein, sugar)
            if not ingredient or not calories or not protein:
                print("here??")
                self.dismiss(None)
                return
        
            self.dismiss([ingredient, calories, protein, sugar])


    def action_cancel(self):
        self.dismiss(None)
