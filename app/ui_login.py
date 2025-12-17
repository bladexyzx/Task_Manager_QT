from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from .ui_main import MainWindow
from .ui_register import RegisterWindow
from .storage import Storage, UserNotFoundError,EmptyUsernameError, WrongPasswordError



class LoginWindow(QWidget):
    """
    Представляет меню входа в аккаунт
    Это окно предоставляет пользователю поля для ввода логина и пароля,
    а также кнопки для входа и перехода к регистрации. При успешной
    авторизации открывается основное окно приложения.

    :ivar storage: Хранилище данных, используемое для проверки логина и пароля.
    :type storage: Storage
    :ivar label: Текстовая инструкция для пользователя.
    :type label: QLabel
    :ivar username_input: Поле ввода логина.
    :type username_input: QLineEdit
    :ivar password_input: Поле ввода пароля.
    :type password_input: QLineEdit
    :ivar login_button: Кнопка входа в аккаунт.
    :type login_button: QPushButton
    :ivar register_button: Кнопка открытия окна регистрации.
    :type register_button: QPushButton
    :ivar main_window: Главное окно приложения, создаётся при успешном входе.
    :type main_window: MainWindow | None
    :ivar reg_window: Окно регистрации.
    :type reg_window: RegisterWindow | None
    """
    def __init__(self):
        """
        Создаёт окно входа и инициализирует интерфейс.
        """
        QWidget.__init__(self)
        self.setWindowTitle("Вход")
        self.resize(300, 200)
        self.storage = Storage()

        self.init_ui()

    def init_ui(self):
        """
        Создаёт и размещает элементы интерфейса окна.
        """
        self.label = QLabel("Введите логин и пароль")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Регистрация")
        self.register_button.clicked.connect(self.open_register)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button) 
        self.setLayout(layout)

    def open_register(self):
        """
        Открывает окно регистрации.
        """
        self.reg_window = RegisterWindow()
        self.reg_window.show()

    def login(self):
        """ 
        Выполняет авторизацию пользователя по логину и паролю.
        При успешной авторизации открывает главное окно приложения.
        
        :raises EmptyUsernameError: если логин или пароль не введены.
        :raises UserNotFoundError: если пользователь с таким логином не найден.
        :raises WrongPasswordError: если введён неверный пароль.
        """
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()


        try:
            if not username or not password:
                raise EmptyUsernameError("Введите логин и пароль")

            self.storage.check_login(username, password)

        except EmptyUsernameError as err:
            QMessageBox.warning(self, "Ошибка", str(err))
            return

        except UserNotFoundError as err:
            QMessageBox.warning(self, "Ошибка входа", str(err))
            return

        except WrongPasswordError as err:
            QMessageBox.warning(self, "Ошибка входа", str(err))
            return

        self.storage.current_user = username
        self.main_window = MainWindow(self.storage)
        self.main_window.show()
        self.close()