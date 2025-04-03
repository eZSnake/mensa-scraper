import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QLabel, QPushButton, QLineEdit, QComboBox, QSizePolicy, QCheckBox,
                             QGroupBox, QFormLayout)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import sqlite3 as sql
import datetime as dt

mensen = ["stadtmitte", "lichtwiese"]#, "schoefferstrasse", "dieburg", "haardtring", "schoeffers"]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mensa dish price comparison")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Options Panel
        options_panel = QWidget()
        options_layout = QVBoxLayout()
        options_panel.setLayout(options_layout)

        options_layout.addWidget(QLabel("Options"))
        options_layout.addWidget(QLabel("Mensa:"))
        self.mensa_select = QComboBox()
        self.mensa_select.addItems({"Stadtmitte", "Lichtwiese"})
        options_layout.addWidget(self.mensa_select)
        options_layout.addWidget(QLabel("Dish:"))
        self.dish_select = QComboBox()
        options_layout.addWidget(self.dish_select)
        options_layout.addWidget(QLabel("Date range:"))

        self.custom_date = QGroupBox("Use custom date range")
        self.custom_date.setCheckable(True)
        self.custom_date.setChecked(False)
        self.custom_date_layout = QFormLayout(self.custom_date)
        self.custom_date_layout.addWidget(QLabel("Please input dates in the format 'DD/MM/YYYY'"))
        self.custom_date_layout.addWidget(QLabel("Start date"))
        self.start_date = QLineEdit()
        self.custom_date_layout.addWidget(self.start_date)
        self.custom_date_layout.addWidget(QLabel("End date"))
        self.end_date = QLineEdit()
        self.custom_date_layout.addWidget(self.end_date)
        options_layout.addWidget(self.custom_date)

        options_layout.addStretch(1)  # Add vertical stretch to push widgets to the top
        self.apply_button = QPushButton("Apply")
        options_layout.addWidget(self.apply_button)

        main_layout.addWidget(options_panel)

        self.liwi = []
        self.stami = []
        self.liwi_dishes = []
        self.stami_dishes = []
        self.read_in_db()
        # Plotting Area
        plotting_area = QWidget()
        plotting_layout = QVBoxLayout()
        plotting_area.setLayout(plotting_layout)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        plotting_layout.addWidget(self.toolbar)
        plotting_layout.addWidget(self.canvas)

        main_layout.addWidget(plotting_area)

        # Connect the Apply button to the update plot function
        self.apply_button.clicked.connect(self.update_plot)

        # Set some stretch factors to control the size of the panels
        main_layout.setStretchFactor(options_panel, 1)
        main_layout.setStretchFactor(plotting_area, 3)

        self.plot_example()

    def plot_example(self):
        # Example plotting code
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 1, 5, 3]
        self.axes.clear()
        self.axes.plot(x, y)
        self.axes.set_title('Example Plot')
        self.canvas.draw()

    def update_plot(self, nested_lists, dates):
        """Updates the plot based on the current values in the option widgets."""
        mensa = self.mensa_select.currentData()
        data = []
        if mensa == "Lichtwiese":
            data = self.liwi
        else:
            data = self.stami

        dish_data = {}  # Dictionary to store data for each dish

        for nested_list in nested_lists:
            dish_name = nested_list[0]
            price = float(nested_list[1])
            date = nested_list[3]

            if dish_name not in dish_data:
                dish_data[dish_name] = {'dates': [], 'prices': []}

            dish_data[dish_name]['dates'].append(dt.datetime.strptime(date, '%d.%m.%Y'))
            dish_data[dish_name]['prices'].append(price)

        # Plot the data for each dish in a separate plot
        for dish_name, data in dish_data.items():
            self.axes.clear()
            self.axes.plot(data['dates'], data['prices'], marker='o')
            self.axes.xlabel('Date')
            self.axes.xlim(dt.datetime.strptime(dates[0], '%d.%m.%Y'),
                    dt.datetime.strptime(dates[-1], '%d.%m.%Y'))
            self.axes.ylabel('Price (in €)')
            self.axes.title(f'{dish_name}')
            self.axes.grid(True)
            self.axes.xticks(rotation=45)
            self.axes.tight_layout()
            # self.axes.show()
            self.canvas.draw()

    def read_in_db(self):
        conn = sql.connect('mensa.db')
        cursor = conn.cursor()
        for mensa in mensen:
            cursor.execute(f'SELECT * FROM {mensa}')
            all_elems = cursor.fetchall()
            if mensa == "lichtwiese":
                self.liwi = [list(tupel) for tupel in all_elems]
                self.liwi_dishes = self.set_unique_dishes(all_elems)
            else:
                self.stami = [list(tupel) for tupel in all_elems]
                self.stami_dishes = self.set_unique_dishes(all_elems)
        conn.commit()
        conn.close()

    def set_unique_dishes(self, all_elems):
        unique_dishes = set()
        for dish_info in all_elems:
            dish_name = dish_info[0]
            unique_dishes.add(dish_name)

        return list(unique_dishes)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
