
from flask import Flask
from flask_restful import Resource, Api, reqparse
from dotenv import dotenv_values
import os
import logging
# import requests
# from authentication import *
from elektrum_ha import ElektrumFetch, ElektrumReadingsModel
# import mysql.connector
import datetime
# import pandas as pd


dir_path = os.path.dirname(os.path.realpath(__file__))

env_file = f"{dir_path}/.env"
config = dotenv_values(env_file)



app = Flask(__name__)
api = Api(app)



class Response(Resource):
	def get(self):
		



		logger = logging.getLogger(__name__)
		dir_path = os.path.dirname(os.path.realpath(__file__))
		config = dotenv_values(f"{dir_path}/.env")
		logging.basicConfig(
			filename='elektrum-fetch.log', 
			level=logging.INFO,
			format='%(asctime)s %(levelname)-8s %(message)s',
			datefmt='%Y-%m-%d %H:%M:%S'
		)


	# # print(config)
		model = ElektrumReadingsModel(config, logger)
		worker = ElektrumFetch(config, logger )

		logging.info('Starting import')
		t_start = model.getLastReadingDate() + datetime.timedelta(hours=1)
	# # t_end = t_start + datetime.timedelta(hours= 100)
		t_end = datetime.datetime.today() - datetime.timedelta(1)


		values = worker.fetchRange(t_start, t_end)
		model.insertReadings(values, True)
		model.update_price_info(t_start, True)
		logging.info('Import done!')


		return {
			'messge':'Done', 
			'start': t_start.isoformat(), 
			'end':t_end.isoformat(), 
			'count':len(values)
		}

	def post(self):
		pass

class Test(Resource):
	def get(self):
		return "This is a test!"


api.add_resource(Response, '/elektrum-fetch/')

api.add_resource(Test, '/test/')


if __name__ == "__main__":
  app.run(debug=True,host='0.0.0.0', port=config['PORT'])
  print(app)


