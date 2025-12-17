import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, func, or_
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import bcrypt
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://taskuser:taskpassword@localhost:5432/taskdb"
)


Base = declarative_base()



class EmptyUsernameError(Exception):
    pass


class EmptyPasswordError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class WrongPasswordError(Exception):
    pass


class User(Base):
    """
    Инициализирует базу данных для хранения информации о пользователях

    :ivar id: Уникальный идентификатор пользователя.
    :type id: int
    :ivar username: Логин пользователя.
    :type username: str
    :ivar password_hash: Хэш пароля пользователя.
    :type password_hash: str
    :ivar tasks: Список задач пользователя.
    :type tasks: list[Task]
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    """
    Инициализирует базу данных для хранения информации о задачах пользователей.

    :ivar id: Уникальный идентификатор задачи.
    :type id: int
    :ivar user_id: Идентификатор пользователя-владельца.
    :type user_id: int
    :ivar description: Текстовое описание задачи.
    :type description: str
    :ivar completed: Флаг выполнения задачи.
    :type completed: bool
    :ivar created_at: Дата создания задачи.
    :type created_at: datetime
    :ivar completed_at: Дата выполнения задачи.
    :type completed_at: datetime | None
    :ivar deadline: Дедлайн задачи.
    :type deadline: datetime | None
    :ivar category: Категория задачи.
    :type category: str
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    description = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime, nullable=True)
    category = Column(String(50), nullable=False)

    user = relationship("User", back_populates="tasks")

class Storage:
    """
    Класс для работы с базой данных приложения.

    Предназначен для подключения к базе данных, выполнения операций, регистрации и авторизации пользователей.

    """
    def __init__(self):
        """
        Инициализирует соединение с базой данных.
        создает таблицы, сессию и инициализирует текущего пользователя.

        """
        self.engine = create_engine(DATABASE_URL, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

        self.current_user = None

    # -------------------- АВТОРИЗАЦИЯ ------------------------
        

    def register_user(self, username: str, password: str) -> bool:
        """
        Регистрирует нового пользователя, хеширует его пароль и сохраняет в базе данных

        :param username: Логин пользователя.
        :type username: str
        :param password: Пароль пользователя.
        :type password: str
        :return: True при успешной регистрации.
        :rtype: bool

        :raises EmptyUsernameError: если логин пустой.
        :raises EmptyPasswordError: если пароль пустой.
        :raises UserAlreadyExistsError: если пользователь уже существует.
        """
        username = username.strip()

        if not username:
            raise EmptyUsernameError("Имя пользователя не может быть пустым")

        if not password:
            raise EmptyPasswordError("Пароль не может быть пустым")

        with self.SessionLocal() as session:
            exists = session.query(User).filter_by(username=username).first()
            if exists:
                raise UserAlreadyExistsError(f"Пользователь '{username}' уже существует")

            password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
            ).decode("utf-8")

            user = User(
                username=username,
                password_hash=password_hash
            )
            session.add(user)
            session.commit()
            return True

    def check_login(self, username: str, password: str) -> bool:
        """
        Проверяет логин и пароль пользователя.

        :param username: Логин пользователя.
        :type username: str
        :param password: Пароль пользователя.
        :type password: str
        :return: True при успешной авторизации.
        :rtype: bool

        :raises UserNotFoundError: если пользователь не найден.
        :raises WrongPasswordError: если пароль неверный.
        """
        with self.SessionLocal() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise UserNotFoundError(f"Пользователь '{username}' не найден")

            if not bcrypt.checkpw(
                password.encode("utf-8"),
                user.password_hash.encode("utf-8")
            ):
                raise WrongPasswordError("Неверный пароль")

            return True

    # -------------------- РАБОТА С ЗАДАЧАМИ ------------------------

    def get_user(self, session, username):
        """
        Возвращает объект пользователя по логину.

        Вспомогательная функция для получения orm объекта о пользователе, либо None, если его нет.
        Будет возвращет объект User с информацией о его id, username и password_hash.

        предполагается, что сессия уже открыта 
        :param session: Активная сессия SQLAlchemy.
        :type session: sqlalchemy.orm.Session
        :param username: Логин пользователя.
        :type username: str
        :return: ORM-объект пользователя или None, если пользователь не найден.
        :rtype: User | None
        """
        return session.query(User).filter(User.username == username).one_or_none()

    def add_task(self, username, task, deadline=None, category="Учебная"):
        """
        Добавляет новую задачу пользователю.

        :param username: Логин пользователя.
        :type username: str
        :param task: Описание задачи.
        :type task: str
        :param deadline: Дедлайн задачи.
        :type deadline: datetime | None
        :param category: Категория задачи.
        :type category: str

        :raises UserNotFoundError: если пользователь не найден.
        """
        with self.SessionLocal() as session:
            user = self.get_user(session, username)
            if not user:
                raise UserNotFoundError(f"Пользователь '{username}' не существует")

            new_task = Task(
                user_id=user.id,
                description=task,
                deadline=deadline,
                category=category
            )
            session.add(new_task)
            session.commit()

    def get_tasks(self, username):
        """
            Возвращает список текущих задач пользователя.

            Метод ищет пользователя по логину, после чего выбирает все его
            невыполненные задачи из базы данных, сортируя их по дедлайну.

            :param username: Логин пользователя, для которого нужно получить задачи.
            :type username: str

            :raises UserNotFoundError: если пользователь с таким логином не существует.

            :return: Список строк с описанием задач пользователя.
            :rtype: list[str]
            """
        with self.SessionLocal() as session:

            user = self.get_user(session, username)
            

            rows = session.query(Task).filter(
                Task.user_id == user.id,
                Task.completed == False
            ).order_by(Task.deadline).all()

            result = []
            now = datetime.now()

            for r in rows:
                if r.deadline < now:
                    overdue = True
                else:
                    overdue = False

                text = f"[{r.category}] {r.description}"

                
                text += f" (до {r.deadline:%d.%m.%Y %H:%M})"

                if overdue:
                    text += "   ПРОСРОЧЕНО!"

                result.append(text)

            return result


    def delete_task(self, username, task):
        """
        Помечает задачу как выполненную.

        :param username: Логин пользователя.
        :type username: str
        :param task: Текст задачи.
        :type task: str
        """
        with self.SessionLocal() as session:
            user = self.get_user(session, username)

            rows = session.query(Task).filter(
                Task.user_id == user.id,
                Task.description == task,
                Task.completed == False
            ).all()

            for r in rows:
                r.completed = True
                r.completed_at = datetime.now()
            session.commit()

    def get_completed_tasks(self, username):
        """
        Возвращает список выполненных задач пользователя.

        :param username: Логин пользователя.
        :type username: str
        :return: Список выполненных задач.
        :rtype: list[str]
        """
        with self.SessionLocal() as session:
            user = self.get_user(session, username)
            if not user:
                raise UserNotFoundError(f"Пользователь '{username}' не существует")

            rows = session.query(Task).filter(
                Task.user_id == user.id,
                Task.completed == True
            ).order_by(Task.completed_at).all()

            return [r.description for r in rows]
        
    def search_tasks(self, username, text, date_from, date_to):
        """
        Выполняет поиск задач по описанию и диапазону дат.

        :param username: Логин пользователя.
        :type username: str
        :param text: Текст для поиска.
        :type text: str | None
        :param date_from: Начальная дата дедлайна.
        :type date_from: date | None
        :param date_to: Конечная дата дедлайна.
        :type date_to: date | None
        :return: Список найденных задач.
        :rtype: list[str]
        """
        with self.SessionLocal() as session:
            user = self.get_user(session, username)

            query = session.query(Task).filter(
                Task.user_id == user.id,
                Task.completed == False
            )

            if text:
                query = query.filter(
                    or_(
                        Task.description.ilike(f"%{text}%"),
                        Task.category.ilike(f"%{text}%")
                    )
                )

            if date_from:
                query = query.filter(Task.deadline >= date_from)

            if date_to:
                query = query.filter(Task.deadline <= date_to)

            rows = query.all()

            result = []
            for r in rows:
                if r.deadline:
                    result.append(
                        f"[{r.category}] {r.description} "
                        f"(до {r.deadline:%d.%m.%Y %H:%M})"
                    )
                else:
                    result.append(f"[{r.category}] {r.description}")

            return result