
# import requests
# from authentication import *
# import elektrum_fetch
import mysql.connector
# import datetime
# from dotenv import dotenv_values
# import os
import logging
# from contextlib import contextmanager
# import mylib


class ElektrumReadingsModel:
    def __init__(self, config, logging):
        self.logging = logging
        self.config = config
        self.connection = mysql.connector.connect(
            user=self.config['DB_USER'], 
            password=self.config['DB_PASSWORD'],
            host=self.config['DB_HOST'],
            database=self.config['DB_NAME']
        )
        self.cursor = self.connection.cursor()



    def getLastReadingDate(self):
        try:
            self.cursor.execute("""
                SELECT 
                    MAX(time) AS last_reading_date 
                FROM 
                    elektrum_readings
            """)
            last_reading_date = self.cursor.fetchone()[0]

            if last_reading_date is None:
                return None  # Or raise an exception, depending on your requirement
            else:
                return last_reading_date
        except Exception as e:
            self.logging.error(f'Error occurred while fetching last reading date: {e}')
            return None  # Or raise an exception, depending on your requirement

    def fetchReadings(self, start, end):
        try:
            self.cursor.execute("""
                    SELECT 
                        time,
                        reading,
                        price_kwh
                    FROM
                        elektrum_readings
                    WHERE
                        time between %s and %s
                """, [start.isoformat(), end.isoformat()])
            rows = []
            for row in self.cursor:
                rows.append([row[0].isoformat(), row[1], None if row[2] is None else float(row[2]) ]) #, float(row[2])])
                # pass
            return rows

        except Exception as e:
            self.logging.error(f'Error occurred fetchReadings(): {e}')
            print(e)
            return [1]



    def insertReadings(self, readings, commit=False):
        try:
            if readings:
                self.logging.info(f'Inserting {len(readings)} readings')
                values = [(reading['datetime'].isoformat(), reading['kWh']) for reading in readings]
                insert_sql = """
                    INSERT INTO 
                        ha.elektrum_readings (time, reading) 
                    VALUES 
                        (%s, %s)
                """
                
                self.cursor.executemany(insert_sql, values)

                if commit:
                    self.connection.commit()
                    self.logging.info('COMMIT')
                    return len(readings)
                else:
                    self.connection.rollback()
                    self.logging.info('ROLLBACK')
                    return -len(readings)
            else:
                self.logging.info('Nothing to import')
                return 0
        except Exception as e:
            self.connection.rollback()
            self.logging.error(f'Error occurred during insertion: {e}')
            return 0

    def update_price_info(self, since, commit = False):

        
        self.logging.info(f'Updating price info')
        sql = """
            UPDATE elektrum_readings A 
            SET price_kwh = (
                SELECT state 
                FROM statistics 
                WHERE from_unixtime(start_ts) = A.time 
                AND metadata_id = 149
            ) 
            WHERE A.price_kwh IS NULL 
            AND A.time >= %s
        """
        self.cursor.execute(sql, (since.date().isoformat(),))

        if commit:
            self.connection.commit()
            self.logging.info(f'Price info: {self.cursor.rowcount} rows updated with [COMMIT]')
        else:
            self.connection.rollback()
            self.logging.info(f'Price info: {self.cursor.rowcount} rows updated with [ROLLBACK]')
        
        return self.cursor.rowcount
    def __del__(self):
        # self.cursor.close()
        # self.connection.close()
        pass