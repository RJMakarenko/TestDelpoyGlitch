import logging

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Не указан файл БД.")

    try:
        conn_str = f'sqlite:///db/mars.db?check_same_thread=False'
        logging.info(f"Подключение к БД: {conn_str}")
        engine = sa.create_engine(conn_str, echo=False)
        __factory = orm.sessionmaker(bind=engine)

        # Импорт моделей (убедитесь, что они доступны)
        from data import __all_models

        SqlAlchemyBase.metadata.create_all(engine)
    except Exception as e:
        logging.info(f"Ошибка инициализации БД: {e}")
        raise


def create_session() -> Session:
    global __factory
    return __factory()
