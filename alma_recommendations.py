# <============ IMPORTS ===============>
import os, threading
from config import AlmaDataPaths
# <====================================>

class Recommendations:
	def __init__(self, app) -> None:
		# -- MAIN
		self.app = app

		# ===================================================================================
		# ========================================= UPDATED ON THE RUN
		self.incrementable = ''          # Song to increment points for
		self.mappings = {}               # Easy way to map playlist IDs to their playlist names
		self.rcm_data = {}               # Holds recommendations data
		self.playlist_data = {}   # Holds saved playlist data
		# ===================================================================================
		# ===================================================================================

		# ==========================================================================
		self.pst_folder = AlmaDataPaths.PLAYLIST_DIR                     # Playlists location
		self.pst_data_file = AlmaDataPaths.DATA_DIR / 'saved_data.json'  # Playlist data file location
		self.rcm_file = AlmaDataPaths.DATA_DIR / 'recommendations.json'  # Recommendations file location
		# ==========================================================================

		#<__ end of the method __>

	def load_playlist_data(self) -> None:
		''' Load already saved playlist data '''
		self.playlist_data = self.app.dbm.read_data(self.pst_data_file)

		# -- Load mappings
		for ID in self.playlist_data:
			# -- Map ID to playlist name
			# Sample format: {'favourites': '3re4-bfrd-44fg', ...}
			title: str = self.playlist_data[ID][0]
			self.mappings[title] = ID
		
		#<__ end of the method __>

	def load_recommendables(self) -> None:
		''' Load data in the recommendables file '''
		# --- Read recommendable file
		self.rcm_data = self.app.dbm.read_data(self.rcm_file)

		#<__ end of the method __>

	def save_recommendable(self, points: int) -> None:
		''' Add points to a song and save the data '''
		# --- Get recommendable points initially b4: Default 0
		freq: float = self.rcm_data.get(self.incrementable, 0)
		# --- Add the new points
		self.rcm_data[self.incrementable] = freq + points
		# --- Save the new data
		self.app.dbm.save_data(self.rcm_data, self.rcm_file)

		#<__ end of the method __>

	def update_played_song_data(self, path: str) -> None:
		''' Update recomendable point for the previous playing song '''
		# --- Get the incrementable name
		self.incrementable = os.path.basename(path)

		# --- Determine points for incrementable & Finally Save
		self.determine_points_for_song(self.app.data)
		
		#<__ end of the method __>

	def determine_points_for_song(self, score: float) -> None:
		''' Determine a recomendable point based on the score of play '''

		if 5 <= score < 17:
			score: float = 0.24

		elif 17 <= score < 29:
			score: float = 0.36

		elif 29 <= score < 41:
			score: float = 0.48

		elif 41 <= score < 53:
			score: float = 0.60

		elif 53 <= score < 65:
			score: float = 0.72

		elif 65 <= score < 78:
			score: float = 0.84

		elif 78 <= score < 85:
			score: float = 0.96

		elif 85 <= score <= 105:
			score: float = 1.00

		# --- Update Incrementable freq with score
		self.save_recommendable(score)
		# ---

		#<__ end of the method __>

	def get_number_of_songs(self, path: str) -> int:
		''' Get the number of songs in a particular path '''
		return len(self.app.dbm.read_data(path)[1])

		#<__ end of the method __>

	def get_added_tracks(self, path: str, in_playlist: list[str]) -> list[str]:
		'''
		Return tracks that have been added to this partiicular
		path on the run.
		'''
		# --- Define Bags & Get tracks in database
		data = self.app.dbm.read_data(path)
		saved: list[str] = [p for p in data[1].values()]
		# ---
		added: list[str] = []   # Bag for added tracks

		# --- Loop through data's values to get added tracks
		for p in saved:
			if p not in in_playlist:
				# --- Implies this path is an added one
				added.append(p)
		# ---

		# --- Return added tracks
		return added

		#<__ end of the method __>

	def get_obliterated_tracks(self, path: str, in_playlist: list[str]) -> list[str]:
		'''
		Return tracks that have been removed from this particular
		path on the run
		'''
		# --- Define Bags & Get tracks in database
		data = self.app.dbm.read_data(path)
		saved: list[str] = [p for p in data[1].values()]
		# ---
		new_paths: list[str] = []     # Will hold tracks that have not been obliterated
		obliterated: list[str] = []   # Bag for obliterated tracks

		# --- Loop through data's values to get obliterated tracks
		for p in in_playlist:
			if p not in saved:
				# --- Implies this path is an obliterated one
				obliterated.append(p)
			else:
				# --- Not obliterated
				new_paths.append(p)
		# ---

		# --- Return obliterated tracks
		return obliterated, new_paths

		#<__ end of the method __>

	def get_playlist_paths(self) -> list[str]:
		''' Return playlist files in the playlist folder '''
		paths: list[str] = []    # Hold paths if available
		# --- Find playlist files
		for r, _, files in os.walk(self.pst_folder):
			if not files:
				# --- Create the favourites file & Update playlist data
				self.app.createFavouriteBag()

				# --- return empty list
				return []

			if 'favourites.json' not in files:
				# --- Create a new favourite bag
				self.app.createFavouriteBag()

			# --- Return these paths
			for f in files:
				paths.append(os.path.join(r, f))
			# ---

		return paths

		#<__ end of the method __>

	def points_for_all(self, points: int, paths: list[str]) -> None:
		''' Add points for all paths in the given list '''
		# --- Loop & add points for all
		for q in paths:# -> This pos matches songs in the playlist
			self.incrementable = q
			self.save_recommendable(points)
		# ---

		#<__ end of the method __>

	def updates_data(self) -> None:
		'''
		Delegates actual update with necessary data for current playlist.
		'''
		# ----
		paths = self.get_playlist_paths()
		# --- Do not proceed if files is empty
		if not paths:
			# ----
			return  # -- No further checks neeeded

		# ====== LOOP THROUGH EACH PATH AND UPDATE ACCORDINGLY
		for path in paths:
			# --- p is a full path
			# --- Do not proceed if not json file
			if not path.lower().endswith('.json'):
				continue   # Proceed to the next item if any
			# --- Determine points to deduct or remove
			if path.lower().endswith('favourites.json'):
				add: int = 3.0     # Add three points for any new fav song
				less: int = -0.5
			else:
				add: int = 1.5    # Add 1.5 points for Regular songs
				less: int = -0.2
			# ---

			# -- Get ID of this playlist
			base: str = os.path.basename(path).replace('.json', '') # Name of the playlist
			ID: str = self.mappings[base]

			# -- Apply the update for the current playlist
			self._apply_updates(path, ID, add, less)
			# --

		#<_end of the method_>

	def _apply_updates(self, path, ID: str, add: float, less: float) -> None:
		'''
		Apply updates to playlist_data and recommendation data
		'''
		# --- Determine whether to add points for all or specific or None
		if not self.playlist_data[ID][1]: # -> This pos matches a bool
			# --- This is a new playlist: Add points for all
			new_paths: list[str] = self.playlist_data[ID][2]
			self.points_for_all(add, new_paths)
			# ---
		else:
			# --- Already read playlist: Check for any updates
			current: int = self.get_number_of_songs(path)
			if current != self.playlist_data[ID][3]:
				# --- Get tracks already in playlist
				in_playlist: list[str] = self.playlist_data[ID][2]
				# --- Check if removal or additions occured
				if current > self.playlist_data[ID][3]: # -> This pos maps to total no. of songs
					# --- Get the paths that were added & add points for all
					added: list[str] = self.get_added_tracks(path, in_playlist)
					self.points_for_all(add, added)
					# ---
					# --- Extend playlist data with added and update total
					self.playlist_data[ID][2].extend(added)
					self.playlist_data[ID][3] += len(added)
					# ---
				elif current < self.playlist_data[ID][3]:
					# --- Get the paths that were obliiterated & deduct points for all
					obliterated, new_paths = self.get_obliterated_tracks(path, in_playlist)
					self.points_for_all(less, obliterated)
					# ---
					# --- Replace playlist data with new_paths and update total
					self.playlist_data[ID][2] = new_paths
					self.playlist_data[ID][3] -= len(obliterated)
				# ---
		# --- Save Data
		self.playlist_data[ID][1] = True
		self.app.dbm.save_data(self.playlist_data, self.pst_data_file)

		#<_end of the method_>

	def schedule_updates(self) -> None:
		''' Update Playlist & Recomendation Data Every 15 minutes '''
		# --
		threading.Thread(target=self.updates_data, daemon=True).start()
		self.app.root.after(900000, self.schedule_updates)
		# --

		#<__ end of the method __>


#<_ END OF RECOMMENDATIONS>