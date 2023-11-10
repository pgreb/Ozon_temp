import os
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, \
    QFileDialog, QTableWidget, QTableWidgetItem, QCheckBox, QPlainTextEdit, QWidget

class OceanApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ocean App")
        self.setGeometry(100, 100, 800, 600)

        # Создаем основной виджет
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Создаем компоновщик для основного виджета
        main_layout = QHBoxLayout(main_widget)

        # Объединяем элементы в группы
        left_group = QGroupBox("Data Actions", self)
        right_group = QGroupBox("Log", self)

        # Устанавливаем минимальные размеры для групп
        left_group.setMinimumWidth(200)
        right_group.setMinimumWidth(200)

        # Создаем компоновщики для каждой группы
        left_layout = QVBoxLayout(left_group)
        right_layout = QVBoxLayout(right_group)

        self.chk_remove_db = QCheckBox("Remove Old Database", self)
        left_layout.addWidget(self.chk_remove_db)

        self.btn_load_data = QPushButton("Load Data", self)
        self.btn_load_data.clicked.connect(self.load_excel)
        left_layout.addWidget(self.btn_load_data)

        self.btn_show_data = QPushButton("Show Data", self)
        self.btn_show_data.clicked.connect(self.show_data)
        left_layout.addWidget(self.btn_show_data)

        self.table_widget = QTableWidget(self)
        left_layout.addWidget(self.table_widget)

        self.log_field = QPlainTextEdit(self)
        right_layout.addWidget(self.log_field)

        # Добавляем группы к основному компоновщику
        main_layout.addWidget(left_group)
        main_layout.addWidget(right_group)

        self.db_connection = None

    def log_message(self, message):
        self.log_field.appendPlainText(message)

    def load_excel(self):
        remove_old_db = self.chk_remove_db.isChecked()

        if remove_old_db and os.path.exists('ocean_data.db'):
            os.remove('ocean_data.db')
            self.table_widget.clearContents()
            self.table_widget.setRowCount(0)
            self.log_message("Old database removed.")

        self.db_connection = sqlite3.connect('ocean_data.db')
        self.log_message(f"Database connection established. Database created in ocean_data.db.")
        
        excel_file, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")

        if excel_file:
            df = pd.read_excel(excel_file, header=None)
            df.to_sql('ocean_data', self.db_connection, if_exists='replace', index=False)
            self.log_message("Data loaded into the database.")

    def show_data(self):
        if not self.db_connection:
            self.log_message("Database connection not established.")
            return

        query = "SELECT * FROM ocean_data"
        df = pd.read_sql(query, self.db_connection)

        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

        if df.empty:
            self.log_message("No data in the database.")
            return

        self.table_widget.setRowCount(len(df.index))
        self.table_widget.setColumnCount(len(df.columns))
        self.table_widget.setHorizontalHeaderLabels(df.iloc[0].astype(str))

        for i, row in enumerate(df.iloc[1:].itertuples(index=False), 0):
            for j, value in enumerate(row, 0):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(i, j, item)
        
        self.log_message("Data displayed from the database.")

if __name__ == "__main__":
    app = QApplication([])
    window = OceanApp()
    window.show()
    app.exec_()
