from __future__ import annotations

import psycopg2
from fastapi.responses import JSONResponse
import json


class PostgreSQLWrapper:
    def __init__(self, path='./sql_config.json'):
        super(PostgreSQLWrapper, self).__init__()
        self.conn = None
        try:
            with open(path) as f:
                self.data = json.load(f)
        except (json.decoder.JSONDecodeError, FileExistsError):
            response = JSONResponse(status_code=418, content=dict(message="Illegal configuration file. Please enter "
                                                                          "your credentials as a json in the given "
                                                                          "file"))
        except FileNotFoundError:
            # print("No database was found to connect to.")
            fp = open(path, 'x')
            fp.close()
            response = JSONResponse(status_code=404, content=dict(message="No configuration file was found. As a "
                                                                          "response, a configuration file has been "
                                                                          "created at '{}'. Please enter the necessary "
                                                                          "details for the MySQL server.".format(path)))

    def check_connection(self, establish=False):
        """ Connect to database. Provide the path for the configuration file for the server to this function
        as an input."""
        try:
            self.conn = psycopg2.connect(**self.data)
            response = JSONResponse(status_code=200, content=dict(message="Connected to database."))
        except psycopg2.Error as e:
            response = JSONResponse(status_code=400, content=dict(message=e.args[0]))
        finally:
            if not establish:
                if self.conn is not None:
                    self.conn.close()
        return response

    def close_connection(self):
        try:
            if self.conn is not None:
                self.conn.close()
                response = JSONResponse(status_code=200, content=dict(message="Connected to database closed."))
        except Exception as e:
            response = JSONResponse(status_code=400, content=dict(message=str(e)))
        return response

    def add_row(self, table: str, column_list: list[str], data_list: list[str]):
        query_datatype = "SELECT " \
                         "column_name, data_type " \
                         "FROM " \
                         "information_schema.columns " \
                         "WHERE table_name = '{}';".format(table)
        assert len(column_list) == len(data_list)
        try:
            with self.conn.cursor() as my_cursor:
                my_cursor.execute(query_datatype)
                tmp = my_cursor.fetchall()
                columns = " ".join(column_list).strip().replace(" ", ", ")
                data = " ".join(data_list).strip().replace(" ", ", ")
                query = "INSERT INTO {0} ({1}) VALUES ({2});".format(table, columns, data)
                my_cursor.execute(query)
                response = JSONResponse(status_code=200, content=dict(message="Row entered successfully."))
            self.conn.commit()
        except psycopg2.Error as e:
            response = JSONResponse(status_code=400, content=dict(message=str(e)))
        # print(query)
        return response

    def return_row(self,table, conditional_param):
        query = "SELECT " \
                "f.film_id, title, inventory_id " \
                "FROM " \
                "film f " \
                "LEFT JOIN " \
                "inventory i " \
                "ON " \
                "i.film_id = f.film_id " \
                "WHERE " \
                "i.film_id " \
                "IS NULL " \
                "ORDER BY title;"


if __name__ == "__main__":
    path_config = "./sql_config.json"
    wrapper = PostgreSQLWrapper()
    wrapper.check_connection(establish=False)
    wrapper.add_row("call_history", ["hash_value", "user_id", "unix_timestamp"],
                           ["dummy", "why", "1523456.45673"])
