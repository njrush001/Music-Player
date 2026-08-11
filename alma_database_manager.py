import json

class AlmaDatabaseManager:
	def __init__(self, app) -> None:
		self.app = app
		self._err = False # Flag to show that an error occured

	def read_data(self, path: str) -> dict:
		'''
		Return Data saved in a certain database:
		 - path -> represents the full path of the database to be read
		'''

		try:
			with open(path, 'r') as database:
				return json.load(database)

		except Exception:
			return {}

		#<__ end of the method __>

	def save_data(self, data, path: str) -> None:
		''' Save data to a file '''
		try:
			with open(path, 'w') as database:
				json.dump(data, database, indent=4)

		except Exception as e:
			self.app.ect.save_exceptions(str(e))
			self._err = True

		#<__ end of the method __>


#<_ END OF DATABASEMANAGER_>