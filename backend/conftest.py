# Полный код для файла backend/conftest.py

import pytest
import os
import tempfile

from main import app as flask_app
from database import db_session, init_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope='function')
def app():
    """
    Фикстура для создания экземпляра приложения Flask для тестов.
    Использует временную базу данных SQLite в памяти.
    """
    # Создаем временный файл для SQLite базы данных
    db_fd, db_path = tempfile.mkstemp()

    # Конфигурируем приложение для использования тестовой БД
    flask_app.config.update({
        "TESTING": True,
        "DATABASE_URI": "sqlite:///" + db_path,
    })

    # Переопределяем движок базы данных на тестовый
    test_engine = create_engine("sqlite:///" + db_path)
    Base.metadata.create_all(test_engine) # Создаем все таблицы
    
    # Переопределяем сессию, чтобы она использовала тестовую БД
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db_session.registry.set(TestingSessionLocal)

    yield flask_app

    # --- Очистка после теста ---
    db_session.close()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """
    Фикстура для создания тестового клиента, который отправляет запросы.
    """
    return app.test_client()


@pytest.fixture(autouse=True)
def setup_db(app):
    """
    Фикстура для очистки и наполнения БД перед каждым тестом.
    'autouse=True' означает, что она будет запускаться автоматически.
    """
    # Перед тестом база данных уже чиста благодаря созданию нового файла
    yield 
    # После теста дополнительная очистка не требуется, так как файл удаляется