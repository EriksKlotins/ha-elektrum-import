import requests
from authentication import *
# import elektrum_fetch
# import mysql.connector
import datetime
# from dotenv import dotenv_values
# import os
import logging
# from contextlib import contextmanager
# import mylib



class ElektrumFetch:

    def __init__(self, config,logging):
        self.session = requests.session()
        self.config = config
        self.logging = logging
        self.setElektrumSession()
     

    def fetch_daily_consumption(self, y,m,d):

        fromDate = f'{y}-{m}-{d}'
        url = f"https://mans.elektrum.lv/lv/majai/mani-parskati/viedo-skaititaju-paterinu-parskats/consumption.json?step=D&fromDate={fromDate}"
        headers = {
             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9,lv;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"96\", \"Google Chrome\";v=\"96\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        try:
            response = self.session.get(url, headers=headers, allow_redirects=True)
       
            if response.status_code == 200:
                return response.json()
            else:
                
                self.logging.error(f'Something went wrong with response! {url} HTTP {response.status_code}')
                # raise  Exception(f'Something went wrong! HTTP {response.status_code}')
                return None
        except:
            self.logging.error(f'Something went wrong with calling the url! {url}')


    def setElektrumSession(self):
        try:
            token = get_auth_token(self.session)
            auth_result = authenticate(self.config['USERNAME'], self.config['PASSWORD'], token, self.session)
        except:
            self.logging.error('Auth failed!')
        return self.session

    def fetchOne(self, year, month, day):
        try:
            result = self.fetch_daily_consumption(year, month, day)
            buffer = []

            if result is None:
                error_msg = f'Failed to fetch results {year}/{month}/{day}'
                self.logging.error(error_msg)
                raise FetchDataError(error_msg)
            elif 'data' in result:
                data = result['data'].get('A+', [])
                for row in data:
                    hour = int(row['date'][:2])
                    dt = datetime.datetime(year, month, day, hour)
                    buffer.append({'datetime': dt, 'kWh': list(row.values())[1]})
            else:
                warning_msg = f"No readings for {year}/{month}/{day}"
                self.logging.warning(warning_msg)

            return buffer
        except FetchDataError as e:
            # Handle specific error condition if needed
            self.logging.error(str(e))
            return []
        except Exception as e:
            self.logging.error(f"An unexpected error occurred: {str(e)}")
            return []



    def fetchRange(self, t_start, t_end):
        try:
            # Generate a list of dates within the specified range
            date_range = [t_start + datetime.timedelta(days=x) for x in range((t_end - t_start).days + 1)]
            
            self.logging.info(f"Fetching results between {t_start.strftime('%Y-%m-%d')} and {t_end.strftime('%Y-%m-%d')}")
            
            buffer = []
            for date in date_range:
                buffer += self.fetchOne(date.year, date.month, date.day)
            
            return buffer
        except Exception as e:
            self.logging.error(f"Error fetching data: {e}")
            return []







