import sys
from PyQt6.QtWidgets import QApplication
from app.ui_login import LoginWindow

def main():
    """
    Главная функция запуска приложения.

    Создаёт экземпляр QApplication, инициализирует окно входа
    в систему и запускает основной цикл обработки событий Qt.
    """

    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
