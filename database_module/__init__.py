from __future__ import annotations

import datetime
from enum import Enum
import psycopg2
from fastapi.responses import JSONResponse
import json


class PostgreSQLWrapper:
    def __init__(self, path_to_config):
        """Class that acts as a wrapper to everything related to database. Connections and any other operations
        should only be done by calling this wrapper class. """
        self._query = None
        self._conn = None
        self._path = path_to_config
        del path_to_config

    def check_connection(self, establish=False):
        """ Connect to PostgreSQL database. Provide the path for the configuration file for the PostgreSQL server to
        this function as an input. """
        try:
            with open(self._path) as f:
                data = json.load(f)
        except (json.decoder.JSONDecodeError, FileExistsError):
            response = JSONResponse(status_code=418, content=dict(message="Illegal configuration file. Please enter "
                                                                          "your credentials as a JSON in the given "
                                                                          "file"))
        except FileNotFoundError:
            # print("No database was found to connect to.")
            fp = open(self._path, 'x')
            fp.close()
            response = JSONResponse(status_code=404, content=dict(message="No configuration file was found. As a "
                                                                          "response, a configuration file has been "
                                                                          "created at '{}'. Please enter the necessary "
                                                                          "details for the server as a JSON.".format(self._path)))

        try:
            self._conn = psycopg2.connect(**data)
            status = True
            response = JSONResponse(status_code=200, content=dict(message="Connected to database."))
        except psycopg2.OperationalError as e:
            response = JSONResponse(status_code=400, content=dict(message=str(e.args[0])))
            status = False
        finally:
            if not establish:
                self.close_connection()
        return status, response

    def close_connection(self):
        if self._conn is not None:
            self._conn.close()

    def insert_into(self, table: str, columns: list, values: list) -> PostgreSQLWrapper:
        self._query = f'INSERT INTO {table} ({format_columns(columns)}) VALUES ({format_values(values)})'
        return self

    def update(self, table: str) -> PostgreSQLWrapper:
        self._query = f'UPDATE {table}'
        return self

    def set(self, columns: list, values: list) -> PostgreSQLWrapper:
        assert len(columns) == len(values)
        self._query += f' SET ' + format_set_values(columns, values)

        return self

    def returning(self, column: Enum) -> PostgreSQLWrapper:
        self._query += f' RETURNING {str(column)}'
        return self

    def on_conflict(self, columns: list) -> PostgreSQLWrapper:
        self._query += f' ON CONFLICT ({format_columns(columns)})'
        return self

    def do_nothing(self) -> PostgreSQLWrapper:
        self._query += ' DO NOTHING'
        return self

    def do_update(self, column: str, value: object) -> PostgreSQLWrapper:
        self._query += f' DO UPDATE SET {column} = {format_single_value(value)}'
        return self

    def select(self, columns: list, table: str) -> PostgreSQLWrapper:
        self._query = f'SELECT {format_columns(columns)} FROM {table}'
        return self

    def delete_from(self, table: str) -> PostgreSQLWrapper:
        self._query = f'DELETE FROM {table}'
        return self

    def join(self, table: str) -> PostgreSQLWrapper:
        self._query += f' JOIN {table}'
        return self

    def left_join(self, table: str) -> PostgreSQLWrapper:
        self._query += f' LEFT JOIN {table}'
        return self

    def on(self, column: str) -> PostgreSQLWrapper:
        self._query += f' ON {column}'
        return self

    def eq(self, column: str) -> PostgreSQLWrapper:
        self._query += f' = {column}'
        return self

    def using(self, column: str) -> PostgreSQLWrapper:
        self._query += f' USING ({column})'
        return self

    def where(self, conditions: list) -> PostgreSQLWrapper:
        if len(conditions) == 0:
            return self

        self._query += f' WHERE {format_conditions(conditions, " AND ")}'
        return self

    def order_by(self, column: str) -> PostgreSQLWrapper:
        self._query += f' ORDER BY {column}'
        return self

    def asc(self) -> PostgreSQLWrapper:
        self._query += ' ASC'
        return self

    def desc(self) -> PostgreSQLWrapper:
        self._query += ' DESC'
        return self

    def limit(self, limit: int) -> PostgreSQLWrapper:
        self._query += f' LIMIT {str(limit)}'
        return self

    def truncate(self, table: str) -> PostgreSQLWrapper:
        self._query = f'TRUNCATE {table}'
        return self

    def cascade(self) -> PostgreSQLWrapper:
        self._query += ' CASCADE'
        return self

    def execute(self) -> str:
        return self._query

    @staticmethod
    def equals(column: Enum, value: object) -> str:
        return f'{str(column)} = {format_single_value(value)}'

    @staticmethod
    def not_equals(column: Enum, value: object) -> str:
        return f'{str(column)} <> {format_single_value(value)}'

    @staticmethod
    def greater_than(column: Enum, value: object) -> str:
        return f'{str(column)} > {format_single_value(value)}'

    @staticmethod
    def greater_or_equal(column: Enum, value: object) -> str:
        return f'{str(column)} >= {format_single_value(value)}'

    @staticmethod
    def less_than(column: Enum, value: object) -> str:
        return f'{str(column)} < {format_single_value(value)}'

    @staticmethod
    def less_or_equal(column: Enum, value: object) -> str:
        return f'{str(column)} <= {format_single_value(value)}'

    @staticmethod
    def count(table: str, column: str) -> str:
        return f'count({table}.{column})'

    @staticmethod
    def _in(column: Enum, values: list) -> str:
        return f'{str(column)} IN ({format_values(values)})'

    @staticmethod
    def is_null(column: [Enum, str]) -> str:
        return f'{str(column)} IS NULL'

    @staticmethod
    def is_not_null(column: [Enum, str]) -> str:
        return f'{str(column)} IS NOT NULL'


def format_conditions(conditions: list, separator: str) -> str:
    return separator.join(str(condition) for condition in conditions)


def format_columns(columns: list) -> str:
    separator = ', '
    return separator.join(str(column) for column in columns)


def format_values(values: list) -> str:
    separator = ', '
    return separator.join(format_single_value(value) for value in values)


def format_set_values(columns: list, values: list) -> str:
    assert len(columns) == len(values)
    separator = ', '

    operations = list()
    for (column, value) in zip(columns, values):
        operations.append(f'{column} = {format_single_value(value)}')

    return separator.join(operations)


def format_single_value(value: object) -> str:
    if isinstance(value, str):
        return f'\'{value}\''
    elif isinstance(value, datetime.date) or isinstance(value, datetime.datetime):
        return f'\'{str(value)}\''
    elif isinstance(value, bool):
        return f'\'{str(value).lower()}\''
    elif value is None:
        return 'null'
    return str(value)


if __name__ == "__main__":
    path_config = "./sql_config.json"
    db1 = PostgreSQLWrapper(path_to_config=path_config)
    print(db1.check_connection())
    db1.close_connection()