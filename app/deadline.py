from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import QDateTime
from PyQt6.QtWidgets import QDateTimeEdit


class DeadlineDialog(QDialog):
    """
    Диалоговое окно для задания параметров задачи и ее дедлайна.

    Предоставляет пользователю возможность выбрать категорию задачи и дедлайн (дату и время выполнения)

    """
    def __init__(self, parent=None):
        """
        Инициализирует диалоговое окно параметров задачи.

        Создаёт элементы интерфейса
        - выпадающий список категорий
        - поле выбора даты и времени
        - кнопки подтверждения и отмены

        :param parent: Родительский виджет.
        :type parent: QWidget | None
        """
        QDialog.__init__(self, parent)
        self.setWindowTitle("Параметры задачи")
        self.resize(250, 180)

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())


        self.category_box = QComboBox()
        self.category_box.addItems([
            "Учебная",
            "Рабочая",
            "Домашняя",
            "Хобби"
        ])

        self.ok_button = QPushButton("ОК")
        self.cancel_button = QPushButton("Отмена")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Категория:"))
        layout.addWidget(self.category_box)
        layout.addWidget(QLabel("Дедлайн (дата и время):"))
        layout.addWidget(self.datetime_edit)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def get_deadline(self):
        """
        Возвращает выбранный пользователем дедлайн.

        :return: Дата и время дедлайна.
        :rtype: datetime.datetime
        """
        return self.datetime_edit.dateTime().toPyDateTime()

    def get_category(self):
        """
        Возвращает выбранную категорию задачи.

        :return: Название категории.
        :rtype: str
        """
        return self.category_box.currentText()
