import sqlite3
import csv
from tabulate import tabulate


class database:
    @classmethod
    def commit(cls):
        cls.connection.commit()

    @classmethod
    def make_connection(cls):
        cls.connection = sqlite3.connect("teachers.db")
        cls.cursor = cls.connection.cursor()

    @classmethod
    def execute(cls, command, parameter=()):
        cls.cursor.execute(command, parameter)

    @classmethod
    def get_teachers_id(cls, id, TableName="teachers"):
        database.make_connection()
        command = "SELECT * FROM {} WHERE id={}".format(TableName, id)
        cls.execute(command)
        return cls.cursor.fetchall()
        database.close_connection()

    @classmethod
    def close_connection(cls):
        cls.connection.close()

    @classmethod
    def show_tables_name(cls):
        cls.cursor.execute(""" SELECT name FROM sqlite_master WHERE type='table' """)
        table_names = tuple(*cls.cursor.fetchall())
        return table_names

    @classmethod
    def create_table(cls, TableName="teachers"):
        cls.execute(
            """CREATE TABLE IF NOT EXISTS {}(
            id integer PRIMARY KEY,
            name text NOT NULL,
            link text NOT NULL
        ) """.format(
                TableName
            )
        )

    @classmethod
    def print_table(cls, TableName="teachers"):
        cls.make_connection()
        cls.execute("SELECT * FROM {}".format(TableName))
        print(tabulate(cls.cursor.fetchall(), headers=["id", "name", "link"]))
        cls.close_connection()

    @staticmethod
    def import_csv(file, TableName="teachers"):
        try:
            with open(file, "r") as f:
                database.make_connection()
                database.create_table()
                lines = csv.reader(f.readlines(), delimiter=";")
                command = " INSERT INTO {}(name,link) VALUES(?,?)".format(TableName)
                for line in lines:
                    database.execute(command, line)
        except Exception as e:
            print("unfurtally we have a error : {}".format(e))
        finally:
            database.commit()
            database.close_connection()
