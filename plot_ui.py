import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QLabel, QPushButton, QLineEdit, QComboBox, QGroupBox, QFormLayout)
from PyQt6 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import sqlite3 as sql
import datetime as dt
import mplcursors

mensen = ["Stadtmitte", "Lichtwiese"]#, "Schoefferstrasse", "Dieburg", "Haardtring", "Schoeffers"]

class MainWindow(QMainWindow):
    def __init__(self):
        '''Creates UI to visualize data'''
        super().__init__()

        self.setWindowTitle("Mensa dish price visualizer")
        self.setWindowIcon(QtGui.QIcon('mensa_logo.png'))
        self.setGeometry(100, 100, 1500, 800)

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
        self.mensa_select.addItems(mensen)
        options_layout.addWidget(self.mensa_select)
        options_layout.addWidget(QLabel("Dish:"))
        self.dish_select = QComboBox()
        options_layout.addWidget(self.dish_select)
        options_layout.addWidget(QLabel("Date range:"))

        self.custom_date = QGroupBox("Use custom date range")
        self.custom_date.setCheckable(True)
        self.custom_date.setChecked(False)
        self.custom_date_layout = QFormLayout(self.custom_date)
        self.custom_date_layout.addWidget(QLabel("Please input dates in the format 'DD.MM.YYYY'"))
        self.custom_date_layout.addWidget(QLabel("Start date"))
        self.start_date = QLineEdit()
        self.custom_date_layout.addWidget(self.start_date)
        self.custom_date_layout.addWidget(QLabel("End date"))
        self.end_date = QLineEdit()
        self.custom_date_layout.addWidget(self.end_date)
        options_layout.addWidget(self.custom_date)

        options_layout.addStretch(1)
        self.apply_button = QPushButton("Apply")
        options_layout.addWidget(self.apply_button)

        main_layout.addWidget(options_panel)

        self.mensa = []
        self.mensa_dishes = []
        self.dates = []
        self.read_in_db()
        self.update_dish_select()

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

        self.mensa_select.currentIndexChanged.connect(self.update_dish_select)
        self.apply_button.clicked.connect(self.update_plot)

        main_layout.setStretchFactor(options_panel, 1)
        main_layout.setStretchFactor(plotting_area, 3)

    def update_plot(self):
        '''Updates the plot based on the current values in the option widgets'''
        data = self.mensa[self.mensa_select.currentIndex()]
        dish_to_disp = self.dish_select.currentText()

        if self.custom_date.isChecked():
            dates = [self.start_date.text(), self.end_date.text()]
        else:
            dates = [self.dates[0], self.dates[-1]]

        dish_data = {}

        for nested_list in data:
            dish_name = nested_list[0]
            if dish_name == dish_to_disp:
                price = float(nested_list[1])
                date = nested_list[3]

                if dish_name not in dish_data:
                    dish_data[dish_name] = {'dates': [], 'prices': []}

                dish_data[dish_name]['dates'].append(dt.datetime.strptime(date, '%d.%m.%Y'))
                dish_data[dish_name]['prices'].append(price)

        self.axes.clear()

        if not dish_data:
            self.axes.set_title('No data to display')
            self.canvas.draw()
            return

        for dish_name, data in dish_data.items():
            self.axes.plot(data['dates'], data['prices'], marker='o')

        self.axes.set_xlabel('Date')
        self.axes.set_xlim(dt.datetime.strptime(dates[0], '%d.%m.%Y'),
                           dt.datetime.strptime(dates[-1], '%d.%m.%Y'))
        self.axes.set_ylabel('Price (in €)')
        self.axes.set_title(f'{dish_name}')
        self.axes.grid(True)
        self.axes.tick_params(axis='x', labelrotation=45)

        # Use tight_layout on the figure, not axes
        self.axes.figure.tight_layout()

        # attempting to show data for each data point when hovering over it
        cursor = mplcursors.cursor(self.axes, multiple=True)
        cursor.connect("add", lambda sel: sel.annotation.set_backgroundcolor('pink'))

        self.canvas.draw()

    def read_in_db(self):
        '''Reads in data from database'''
        conn = sql.connect('mensa.db')
        cursor = conn.cursor()

        for _, mensa in enumerate(mensen):
            cursor.execute(f'SELECT * FROM {mensa.lower()}')
            all_elems = cursor.fetchall()

            self.mensa.append([list(tupel) for tupel in all_elems])
            self.mensa_dishes.append(self.set_unique_dishes(all_elems))

        self.dates = sorted([item[3] for item in all_elems],
                            key=lambda x: dt.datetime.strptime(x, '%d.%m.%Y').date())

        conn.commit()
        conn.close()

    def set_unique_dishes(self, all_elems):
        '''Gathers list of unique dishes'''
        unique_dishes = set()
        for dish_info in all_elems:
            dish_name = dish_info[0]
            unique_dishes.add(dish_name)

        return sorted(list(unique_dishes))

    def update_dish_select(self):
        '''Updates the dishes displayed in dropdown to correspond to the selected Mensa location'''
        self.dish_select.clear()
        self.dish_select.addItems(self.mensa_dishes[self.mensa_select.currentIndex()])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
