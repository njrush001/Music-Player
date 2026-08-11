# <============ IMPORTS ===============>
import os, random, threading
from typing import Optional
from tkinter import filedialog
# <====================================>

class LibraryManager:
	def __init__(self, app) -> None:
		self.app = app

		#<__ end of the method __>
	
	# ======================================================================================================
	# ======================================================================================================

	def select_folder(self) -> Optional[str]:
		''' Allow the user to select a folder '''
		FOLDER: str = filedialog.askdirectory(title='Select Folder With Your Songs')
		# --- Determine if user selected a folder
		if not FOLDER:
			return None
		# --- Return the folder
		return FOLDER
		
		#<__ end of the method __>

	def add_paths(self, paths=None) -> None:
		''' Add the passed paths to UI '''
		if not paths:
			# --- User probably did not drag and drop: Allow user to select paths
			paths = filedialog.askopenfilenames(
					title='Select Your Files',           # Title of the window that pops up
					filetypes=[('MP3 Files', '*.mp3')]   # Type of files to be selected
				)
			if not paths:
				return    # Nothing to add to UI
			# ---

		# --- Add Paths To The Listbox Accordingly
		self.app.pst.select_files_to_add(paths, randomise_paths=True)

		#<__ end of the method __>

	def music_from_folder(self) -> None:
		''' Allow selection of a folder '''
		# --- Get the folder
		FOLDER: Optional[str] = self.select_folder()

		# -- Ensure it's safe to work with this playlist
		safe, paths = self._safety_check('folder_check', folder=FOLDER)
		if not safe:
			# -- Not safe to work with this folder
			return

		# -- Clear box & Add then Randomise The New Paths
		threading.Thread(
			target=self._complete,
			args=('unknown folder', paths),
			daemon=True
		).start()
		# --

		# -- Folders with Music Paths are scannable ones
		threading.Thread(
			target=self.app.sgm.add_music_folder,
			kwargs={'folder': FOLDER},
			daemon=False
		).start()

		#<__ end of the method __>

	# ======================================================================================================
	# ======================================================================================================

	# ======================================================================================================
	# ======================================================================================================

	def thread_worker_for_search(self, paths, title, last_play=False) -> None:
		''' Initiate thread worker for search '''
		# -- Create task
		_task = threading.Thread(
			target=self._get_paths,
			args=(paths, title), kwargs={'last_play': last_play},
			daemon=True)

		# -- Start the task
		_task.start()

		#<_end of the method_>

	def _search_file(self, song):
		''' Find the location of the given song '''
		# -- Folders To Search
		FOLDERS: list = self.app.sgm.player_data['music_folders'].copy()

		# -- Attempt search
		for _dir in FOLDERS:
			for r, _, files in os.walk(_dir):
				# -- Attempt search in this folder's files
				if song in files:
					# -- Return file path
					return os.path.join(r, song)
		
		# -- Song not available
		return None

		#<_end of the method_>

	def _get_paths(self, paths: list, title: str, last_play=False) -> None:
		''' Find paths in Know Folders '''
		# -- Will Hold All Paths That Are Found
		found = []

		# -- For Every Track, Attempt Finding its location
		for p in paths:
			# -- Attempt Search
			file = self._search_file(p)

			# -- Add Found paths to found
			if file is not None:
				# -- Add
				found.append(file)

		# -- If no found paths: Return
		if len(found) != 0:
			# --
			if last_play:
				# -- Only Last Played Track Required
				self.app.pyr.last_play = found[0]
				self.app.uiu.show_last_playback_prompt(paths[0])

				return
		
			# -- Otherwise, finalise Music From Playlist
			self._complete(title, found)
		
		# =================================================================
		# =================================================================

		#<_end of the method_>

	def _complete(self, title: str, paths: list) -> None:
		'''
		Finalise self.music_from_playlist objective or music_from_folder
		'''
		# -- Load favourites at first if applicable
		if title == 'favourites':
			# -- Load favourites
			self.app.fvs.load_favourites()
		# --

		# -- Clear bags & listbox
		self.app.pst.clear_bags()

		# -- Add files then randomise
		self.app.pst.select_files_to_add(paths)
		self.app.pst.randomise_paths()
		# --

		# -- Playlist Loaded Successfully
		self.app.pyr.current_song_index = 0
		threading.Thread(
			target=self.app.track_playing,
			daemon=True
		).start()

		# -- Feedback to user
		msg: str = f'{title.title()}: Successfully Added {len(paths)} song(s).'
		self.app.uiu.updateStatusLabel(msg)

		#<__ end of the method __>
	
	def _safety_check(self, check_type: str, data: Optional[list] = None, folder: Optional[str] = None) -> tuple[bool, list]:
		'''
		Ensure it is okay to open paths in folder or playlist.
		 - check_type: 'folder_check' or 'playlist_check'
		'''
		# -- Feedback to show incase of any issue
		feedback: dict[str, str] = {
			'GENERAL_MESSAGE': 'A Problem Occured!',
			'invalid_check_type': 'Invalid safety check type provided.',
			'no_tracks': 'No Tracks Found! Try Another Folder/Playlist.',
			'no_folders': 'Please Add Folders Before Loading Your Playlists!!'
		}
		try:
			# -- The data may have an issue in unapacking
			if check_type == 'folder_check':
				# -- Get Paths: Unlikely To Fail
				paths: list = [
					os.path.join(r, f)
					for r, _, files in os.walk(folder)
					for f in files if f.lower().endswith('.mp3')
				]
			
			elif check_type == 'playlist_check':
				# -- Check if music folders are available
				if not self.app.sgm.player_data['music_folders']:
					# -- Program won't scan for files: Not Safe
					msg: str = feedback['no_folders']
					self.app.uiu.updateStatusLabel(msg)

					return False, []
				
				# -- Get Paths: Like To Fail if the bag is messed up
				paths: list = [p for p in data[1].values()]
			
			else:
				# -- The Check Type Is Wrong
				msg: str = feedback['invalid_check_type']
				self.app.uiu.updateStatusLabel(msg)

				return False, []

		except Exception:
			# -- A problem in unpacking
			msg: str = feedback['GENERAL_MESSAGE']
			self.app.uiu.updateStatusLabel(msg)

			return False, []
		
		else:
			# -- Other Measures
			if len(paths) == 0:
				# -- Not okay to display
				msg: str = feedback['no_tracks']
				self.app.uiu.updateStatusLabel(msg)

				return False, []
			# --
			
			# -- Test Passed
			return True, paths

		#<_end of the method_>

	def music_from_playlist(self, path) -> None:
		''' Open Playlist path and collect info in it '''
		# --- Open the path passes by selector
		data: list[str, dict] = self.app.dbm.read_data(path)

		# -- Ensure it's safe to work with this playlist
		safe, paths = self._safety_check('playlist_check', data=data)
		if not safe:
			# -- Not Safe To Work With This Playlist
			return

		# -- Title & Randomisation
		title: str = os.path.basename(path).replace('.json', '')
		random.shuffle(paths)
		# ---
		
		# -- Start Search background task
		self.thread_worker_for_search(paths, title)

		#<__ end of the method __>


#<_ END OF LIBRARYMANAGER>