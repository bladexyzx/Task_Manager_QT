from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QLabel, QMessageBox, QHBoxLayout, QComboBox,QDateEdit, QDialog
from PyQt6.QtCore import QDate
from app.deadline import DeadlineDialog
 
class MainWindow(QWidget):
    """
    Главное окно управления задачами.

    Отображает задачи текущего пользователя и предоставляет
    инструменты для работы с ними.
    """
    def __init__(self, storage):
        """
        Инициализирует интерфейс, загружает задачи пользователя
        и историю выполненных задач.

        :param storage: Объект хранилища данных приложения.
        :type storage: Storage
        """
        QWidget.__init__(self)
        self.storage = storage
        self.setWindowTitle(f"Task Manager - {storage.current_user}")
        self.resize(500, 500)
        self.init_ui()
        self.load_tasks()
        self.load_completed_tasks()

    def init_ui(self):
        """
        Инициализирует списки задач, поля ввода, кнопки управления
        и элементы поиска.
        """
        self.task_list = QListWidget()
        self.completed_list = QListWidget()  

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Описание задачи")

        self.add_button = QPushButton("Добавить задачу")
        self.add_button.clicked.connect(self.add_task)

        self.delete_button = QPushButton("Задача выполнена")
        self.delete_button.clicked.connect(self.delete_task)
        

        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск")

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)

        self.search_button = QPushButton("Найти")
        self.search_button.clicked.connect(self.search_tasks)


        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Пользователь: {self.storage.current_user}"))
        layout.addWidget(self.task_input)
        layout.addWidget(self.add_button)
        layout.addWidget(QLabel("Текущие задачи:"))
        layout.addWidget(self.task_list)
        layout.addWidget(self.delete_button)
        layout.addWidget(QLabel("История выполненных задач:"))
        layout.addWidget(self.completed_list)

        
        layout.addWidget(self.search_input)
        layout.addWidget(QLabel("С:"))
        layout.addWidget(self.date_from)
        layout.addWidget(QLabel("По:"))
        layout.addWidget(self.date_to)
        layout.addWidget(self.search_button)


        self.setLayout(layout)

    def add_task(self):
        """
        Добавляет новую задачу пользователю.

        Проверяет корректность введённых данных, открывает диалог
        выбора дедлайна и категории, после чего сохраняет задачу
        в хранилище.
        """
        text = self.task_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите описание задачи")
            return

        dialog = DeadlineDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return  # нажали "Отмена"

        deadline = dialog.get_deadline()
        category = dialog.get_category()

        self.storage.add_task(
            self.storage.current_user,
            text,
            deadline,
            category
        )

        self.task_input.clear()
        self.load_tasks()


    def delete_task(self):
        """
        Отмечает выбранную задачу как выполненную.

        Перемещает задачу из списка текущих задач
        в историю выполненных.
        """
        current = self.task_list.currentItem()
        if not current:
            QMessageBox.information(self, "Инфо", "Выберите задачу для выполнения")
            return

        text = current.text()
        

        #Заимствованный код.
        if " (до " in text:
            text = text.split(" (до ")[0]

        
        if text.startswith("[") and "] " in text:
            text = text.split("] ", 1)[1]

        #Заимствованный код.
        self.storage.delete_task(self.storage.current_user, text)
        self.load_tasks()
        self.load_completed_tasks()
    def load_tasks(self):
        """
        Загружает и отображает список текущих задач пользователя.
        """
        self.task_list.clear()
        tasks = self.storage.get_tasks(self.storage.current_user)
        for t in tasks:
            self.task_list.addItem(t)

    def load_completed_tasks(self):
        """
        Загружает и отображает систорию выполненных задач пользователя.
        """
        self.completed_list.clear()
        completed = self.storage.get_completed_tasks(self.storage.current_user)
        for t in completed:
            self.completed_list.addItem(t)
    def search_tasks(self):
        """
        Выполняет поиск задач по тексту и диапазону дат.

        Отображает только те задачи, которые соответствуют
        введённым критериям поиска.
        """
        text = self.search_input.text().strip()

        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()

        tasks = self.storage.search_tasks(
            self.storage.current_user,
            text if text else None,
            date_from,
            date_to
        )

        self.task_list.clear()
        for t in tasks:
            self.task_list.addItem(t)
