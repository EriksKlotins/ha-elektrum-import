
import requests
from authentication import *
import elektrum_fetch
import mysql.connector
import datetime
import pandas as pd
from dotenv import dotenv_values
import os



dir_path = os.path.dirname(os.path.realpath(__file__))

env_file = f"{dir_path}/.env"
config = dotenv_values(env_file)




session = requests.session()
token = get_auth_token(session)
auth_result = authenticate(config['USERNAME'], config['PASSWORD'], token, session)


with mysql.connector.connect(user='root', password='Gobzems15',
                              host='192.168.8.129',
                              database='ha') as conn:

    with conn.cursor() as cur:
        # cur.execute(f"""select id FROM statistics_meta where statistic_id = '{config['STATISTIC_ID']}' """)
        # row = cur.fetchone()
        # if  row == None:
        #     print(f"Sensor ID {config['STATISTIC_ID']} not found in statistics_meta.")
        # else:
        #     metadata_id = row[0]

            # cleaning up statistics records that may be inserted by HA
            # cur.execute(f"""
            # delete FROM statistics where metadata_id = {metadata_id} and start>= (SELECT max(time) FROM `elektrum_readings`);
            # """)

        # Finding the last entry in readings
        # [todo]: this step may not be needed, if we import directly into stats
        #         I am keeping this in case something goes wrong and I need to repeat the import  
        cur.execute(""" select  year(t), month(t), day(t), hour(t) from ( select max(time) t from elektrum_readings) a """)
        buffer = []
        for (y,m,d,h) in cur:
            start_t = datetime.datetime(y,m,d,h,0) + datetime.timedelta(hours=1)
            end_t = datetime.datetime.today()
            print('Importing readings since:', start_t)

            # [todo]: get rid of pandas dependency
            for day, month, year in [(d.day, d.month, d.year) for d in pd.date_range(start=start_t, end=end_t)]:
                # print(day, month, year)
                result = elektrum_fetch.fetch_daily_consumption(year,month,day, session)
                if result == None:
                    print('Failed to fetch results')
                    buffer = []
                else:
                    if 'data' in result.keys():
                        data = result['data']['A+']
                        for row in data:
                            dt = datetime.datetime(year,month,day, int(row['date'][0:2]))
                            buffer.append({'datetime':dt, 'kWh':list(row.values())[1]})
                    else:
                        print(f'No readings for {day}/{month}/{year}')

            # Actual inserts
        if len(buffer)>0:

            insert_sql = "INSERT INTO ha.elektrum_readings (time, reading) VALUES"+','.join(list(map(lambda a: f"('{str(a['datetime'])}', {a['kWh'] if a['kWh']!=None else 'null'})", buffer)))
            # print(insert_sql)
            cur.execute(insert_sql)
            cur.execute('commit')
                # print('Import done! [elektrum_readings]', len(buffer))
                # import_sql = f"""
                #     insert into 
                #         statistics (created, start, mean, min, max,metadata_id) 
                    
                #     select 
                #         time, 
                #         date_sub(time, interval 1 hour), 
                #         reading, 
                #         reading, 
                #         reading, 
                #         {metadata_id} 
                #     FROM 
                #         elektrum_readings 
                #     WHERE
                #         exported_at is null
                    
                #     ON DUPLICATE KEY UPDATE 
                #         mean = reading, 
                #         max = reading, 
                #         min = reading;
                #     """
                # update_sql = f"""
                #     update 
                #         elektrum_readings 
                #     set 
                #         exported_at = now() 
                #     where 
                #         exported_at is null
                    
                # """
                # cur.execute(import_sql)
                # cur.execute('commit')

            print('Import done! [statistics]')
        else:
            print('Nothing to import')
            
        
            
            

