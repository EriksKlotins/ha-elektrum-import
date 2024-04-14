
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



# 2. Set up DB
# 3. Find last values in the db
# 4. Import missing readings
# 5. Insert missing readings



with mysql.connector.connect(user='root', password='Gobzems15',
                              host='192.168.8.129',
                              database='ha') as conn:

    with conn.cursor() as cur:


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
            print(f'Importing {len(buffer)} readings')
            insert_sql = "INSERT INTO ha.elektrum_readings (time, reading) VALUES"+','.join(list(map(lambda a: f"('{str(a['datetime'])}', {a['kWh'] if a['kWh']!=None else 'null'})", buffer)))
            # print(insert_sql)
            cur.execute(insert_sql)
            cur.execute('commit')
            print('Import done! [statistics]')
        else:
            print('Nothing to import')
            
        
            
            

