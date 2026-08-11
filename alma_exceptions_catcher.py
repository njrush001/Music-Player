# <============ IMPORTS =========================>
from config import AlmaDataPaths
# <==============================================>

class GetExceptions:
	''' Gets Errors From The System '''

	def __init__(self, app) -> None:
		self.app = app
		self.exceptions_log = AlmaDataPaths.ERROR_DIR / 'exceptions_log.txt'

	def save_exception_log(self, log: list) -> None:
		'''
			This function will be used to save the path the user followed
			till an error occured. Necessary for solving bugs.
		'''
		pass

	#<__ end of the method __>

	def save_exceptions(self, error: str) -> None:
		''' Temporary method to save exceptions. Necessary for solving Bugs '''
		#self.app.dbm.save_data(error, self.exceptions_log, 'a')
		return

		#<__ end of the method __>


#<_ END OF GETEXCEPTIONS_>