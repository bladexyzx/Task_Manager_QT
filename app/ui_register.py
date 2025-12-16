from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from .storage import Storage, EmptyPasswordError, UserAlreadyExistsError


class RegisterWindow(QWidget):
    """
    Окно регистрации нового пользователя.
    Предоставляет интерфейс для создания аккаунта с логином и паролем.

    :ivar storage: Хранилище данных, используемое для регистрации пользователей.
    :type storage: Storage
    :ivar label: Текстовая инструкция для пользователя.
    :type label: QLabel
    :ivar username_input: Поле ввода логина.
    :type username_input: QLineEdit
    :ivar password_input: Поле ввода пароля.
    :type password_input: QLineEdit
    :ivar button: Кнопка для отправки данных регистрации.
    :type button: QPushButton
    """
    def __init__(self):
        """
        Инициализирует окно регистрации и настраивает интерфейс.
        Устанавливает заголовок, размеры окна и создаёт элементы управления.
        """
        QWidget.__init__(self)
        self.setWindowTitle("Регистрация")
        self.resize(250, 200)
        self.storage = Storage()

        self.init_ui()

    def init_ui(self):
        """
        Создаёт и размещает элементы интерфейса окна регистрации.
        Настраивает поля для ввода логина и пароля, а также кнопку регистрации.
        """
        self.label = QLabel("Создайте аккаунт")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.button = QPushButton("Зарегистрироваться")
        self.button.clicked.connect(self.register)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def register(self):
        """
        Выполняет регистрацию нового пользователя.
        Проверяет корректность введённых данных, обрабатывает ошибки и уведомляет пользователя о результате.

        :raises EmptyPasswordError: если введён пустой пароль.
        :raises UserAlreadyExistsError: если пользователь с таким логином уже существует.
        """
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()



        try:
            self.storage.register_user(username, password)

        except EmptyUsernameError as err:
            QMessageBox.warning(self, "Пустой логин", str(err))
            return

        except EmptyPasswordError as err:
            QMessageBox.warning(self, "Пустой пароль", str(err))
            return

        except UserAlreadyExistsError as err:
            QMessageBox.warning(self, "Ошибка регистрации", str(err))
            return
        else:
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            self.close()

    