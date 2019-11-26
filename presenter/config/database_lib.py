import sqlite3
from presenter.config.files_paths import database_file
from presenter.config.log import Loger, log_to

log = Loger(log_to)


class Database:
    """Управление базой данных"""

    def __init__(self):
        """Подключается к базе данных"""
        log.log_print("Init database")
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def __del__(self):
        """Отключается от базы данных"""
        log.log_print("Closing database")
        self.connection.close()  # Закрываем БД

    def get(self, table, *column_value):
        """Получает запись из БД"""
        sql = f"SELECT * FROM {table} WHERE "
        reqs = []
        for value in column_value:
            reqs.append(f"{value[0]}='{value[1]}'")
        sql += " AND ".join(reqs)
        log.log_print("[SQL]: " + sql)
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def get_many(self, value, table='chats', column='purpose'):  # TODO Добавить поиск по нескольким ключам
        """Читает несколько записей в базе данных"""
        sql = "SELECT * FROM {} WHERE {}='{}'".format(table, column, value)
        log.log_print("[SQL]: "+sql)
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all(self, table, order_by='id', how_sort='DESC'):  # TODO Добавить поиск по нескольким ключам
        """Читает все записи в одной таблице базы данных"""
        sql = "SELECT rowid, * FROM {} ORDER BY {} {}".format(table, order_by, how_sort)
        log.log_print("[SQL]: "+sql)
        all_list = []
        for element in self.cursor.execute(sql):
            all_list.append(element[1:])  # Первый элемент это бесполезный номер
        return all_list

    def change(self, set_what, set_where, table, *column_value):
        """Меняет что-то в базе данных"""
        reqs = []
        for value in column_value:
            reqs.append(f"{value[0]}='{value[1]}'")
        # Одинарные кавычки в sql очень важны
        sql = f"UPDATE {table}\n"
        sql += f"SET {set_where} = '{set_what}'\n"
        sql += "WHERE " + " AND ".join(reqs)
        log.log_print("[SQL]: "+sql)
        self.cursor.execute(sql)
        self.connection.commit()  # Сохраняем изменения

    def append(self, values, table='members'):
        """Добавляет запись в базу данных"""
        try:
            sql = """
            INSERT INTO {}
            VALUES {}
            """.format(table, values)
            log.log_print("[SQL]: "+sql)
            self.cursor.execute(sql)
        except Exception as e:
            print(e)
        self.connection.commit()  # Сохраняем изменения

# TODO Добавление колонки
# TODO Удаление колонки
# TODO Удаление одной записи
