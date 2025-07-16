import calendar
import json
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window

DATA_FILE = "attendance_data.json"

Window.size = (800, 600)

departments = ["CS", "AIML", "EEE", "Mech"]

students_by_department = {
    "CS": ["Aditi", "Ravi", "Nisha"],
    "AIML": ["Maya", "Suresh", "Latha"],
    "EEE": ["Praveen", "Diya", "Arun"],
    "Mech": ["Rohan", "Karthik", "Pooja"]
}

class AttendanceApp(App):

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.attendance_data, f)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.attendance_data = json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                self.attendance_data = {}
        else:
            self.attendance_data = {}

    def build(self):
        self.attendance_data = {}
        self.total_labels = {}
        self.buttons = {}
        self.current_month = "July"
        self.current_department = "CS"
        self.current_week = None
        self.months = list(calendar.month_name)[1:]
        self.weeks = {}
        self.load_data()

        self.root = BoxLayout(orientation='vertical')

        top_bar = BoxLayout(size_hint_y=None, height=40)

        self.dept_spinner = Spinner(text=self.current_department, values=departments)
        self.dept_spinner.bind(text=self.on_department_change)
        top_bar.add_widget(self.dept_spinner)

        self.month_spinner = Spinner(text=self.current_month, values=self.months)
        self.month_spinner.bind(text=self.on_month_change)
        top_bar.add_widget(self.month_spinner)

        manage_btn = Button(text="Manage Students", size_hint_x=0.3)
        manage_btn.bind(on_press=self.open_student_editor)
        top_bar.add_widget(manage_btn)

        self.root.add_widget(top_bar)

        self.week_bar = BoxLayout(size_hint_y=None, height=40)
        self.root.add_widget(self.week_bar)

        self.title_label = Label(
            text=f"Attendance - {self.current_department} - {self.current_month}",
            size_hint_y=None, height=40, font_size=20
        )
        self.root.add_widget(self.title_label)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=7, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.root.add_widget(self.scroll)

        self.generate_weeks(self.current_month)
        self.update_week_bar()
        self.update_grid()
        return self.root

    def on_department_change(self, spinner, dept):
        self.current_department = dept
        self.title_label.text = f"Attendance - {dept} - {self.current_month}"
        self.generate_weeks(self.current_month)
        self.update_week_bar()
        self.update_grid()

    def on_month_change(self, spinner, month):
        self.current_month = month
        self.title_label.text = f"Attendance - {self.current_department} - {month}"
        self.generate_weeks(month)
        self.update_week_bar()
        self.update_grid()

    def generate_weeks(self, month):
        month_index = list(calendar.month_name).index(month)
        _, num_days = calendar.monthrange(2025, month_index)
        days = [day for day in range(1, num_days + 1) if calendar.weekday(2025, month_index, day) < 5]

        self.weeks = {}
        week_num = 1
        for i in range(0, len(days), 5):
            label = f"Week {week_num}"
            self.weeks[label] = days[i:i+5]
            week_num += 1

        self.current_week = list(self.weeks.keys())[0]

    def update_week_bar(self):
        self.week_bar.clear_widgets()
        for week in self.weeks:
            btn = Button(text=week)
            btn.bind(on_press=self.change_week)
            self.week_bar.add_widget(btn)

    def change_week(self, instance):
        self.current_week = instance.text
        self.update_grid()

    def update_grid(self):
        days = self.weeks[self.current_week]
        self.scroll.remove_widget(self.grid)
        self.grid = GridLayout(cols=len(days) + 2, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)

        self.grid.clear_widgets()
        dept = self.current_department
        month = self.current_month

        if dept not in self.attendance_data:
            self.attendance_data[dept] = {}
        if month not in self.attendance_data[dept]:
            self.attendance_data[dept][month] = {student: {} for student in students_by_department[dept]}

        self.buttons = {}
        self.total_labels = {}

        self.grid.add_widget(Label(text="Name", size_hint_y=None, height=30))
        for day in days:
            self.grid.add_widget(Label(text=str(day), size_hint_y=None, height=30))
        self.grid.add_widget(Label(text="Total", size_hint_y=None, height=30))

        for student in students_by_department[dept]:
            self.grid.add_widget(Label(text=student, size_hint_y=None, height=30))
            self.buttons[student] = {}

            for day in days:
                if day not in self.attendance_data[dept][month][student]:
                    self.attendance_data[dept][month][student][day] = False
                present = self.attendance_data[dept][month][student][day]
                btn = Button(text="P" if present else "A", size_hint_y=None, height=30)
                btn.student = student
                btn.day = day
                btn.bind(on_press=self.toggle_attendance)
                self.grid.add_widget(btn)
                self.buttons[student][day] = btn

            total_label = Label(text=str(self.get_total(student)), size_hint_y=None, height=30)
            self.grid.add_widget(total_label)
            self.total_labels[student] = total_label

    def toggle_attendance(self, instance):
        student = instance.student
        day = instance.day
        dept = self.current_department
        month = self.current_month

        current = self.attendance_data[dept][month][student][day]
        new_value = not current
        self.attendance_data[dept][month][student][day] = new_value
        instance.text = "P" if new_value else "A"
        self.total_labels[student].text = str(self.get_total(student))
        self.save_data()

    def get_total(self, student):
        dept = self.current_department
        month = self.current_month
        return sum(1 for val in self.attendance_data[dept][month][student].values() if val)

    def open_student_editor(self, instance):
        dept = self.current_department
        student_checkboxes = {}
        popup = Popup(title=f"Manage Students - {dept}", size_hint=(None, None), size=(400, 500))

        def rebuild_popup():
            layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
            student_checkboxes.clear()

            for student in students_by_department[dept]:
                row = BoxLayout(size_hint_y=None, height=30)
                cb = CheckBox()
                student_checkboxes[student] = cb
                row.add_widget(cb)
                row.add_widget(Label(text=student))
                layout.add_widget(row)

            add_box = BoxLayout(size_hint_y=None, height=40)
            new_name_input = TextInput(hint_text="New student name")
            add_button = Button(text="Add")

            def add_student(_):
                name = new_name_input.text.strip()
                if name and name not in students_by_department[dept]:
                    students_by_department[dept].append(name)
                    for month in self.months:
                        self.attendance_data.setdefault(dept, {}).setdefault(month, {})[name] = {}
                    self.save_data()
                    rebuild_popup()
                    self.update_grid()

            add_button.bind(on_press=add_student)
            add_box.add_widget(new_name_input)
            add_box.add_widget(add_button)
            layout.add_widget(add_box)

            button_bar = BoxLayout(size_hint_y=None, height=40)
            remove_button = Button(text="Remove Selected")
            close_button = Button(text="Close")

            def remove_selected(_):
                to_remove = [name for name, cb in student_checkboxes.items() if cb.active]
                for name in to_remove:
                    if name in students_by_department[dept]:
                        students_by_department[dept].remove(name)
                        for month in self.attendance_data.get(dept, {}):
                            self.attendance_data[dept][month].pop(name, None)
                self.save_data()
                rebuild_popup()
                self.update_grid()

            remove_button.bind(on_press=remove_selected)
            close_button.bind(on_press=popup.dismiss)
            button_bar.add_widget(remove_button)
            button_bar.add_widget(close_button)
            layout.add_widget(button_bar)

            popup.content = layout

        rebuild_popup()
        popup.open()

AttendanceApp().run()
