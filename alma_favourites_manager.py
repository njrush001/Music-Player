# <============ IMPORTS ===============>
import os
from config import AlmaDataPaths
# <====================================>

class FavouritesManager:

	def __init__(self, app) -> None:
		self.app = app

		# ===============================================================
		# =====================================  UPDATED ON THE RUN
		self.path_to_add = None                  # A path to be added to favourites                              ***
		self.path_to_delete = None               # A path to obliterate from favourites                          ***
		self.sel_add: bool = False               # Bool to Differentiate btn triggers of right-click and fav_vtn ***
		self.selected: bool = False              # Determines whether trigger is righ-click or not               ***
		self.is_playing_fav: bool = False        # Flag Indicating whether favourites are being played or not
		# ===============================================================
		# ===============================================================

		self.favourites_path = AlmaDataPaths.PLAYLIST_DIR / 'favourites.json'

		#<__ end of the method __>

	def load_favourites(self) -> None:
		'''
		Load Users Favourite Song paths
		'''
		# -- Determine if favourites file is of good format
		is_safe, data = self.app.pst.playlist_format_okay(self.favourites_path)

		if is_safe and len(data[1]) > 0:
			# -- Some songs are available in this playlist
			self.app.pst.favs = [p for p in data[1].values()]

		#<__ end of the method __>

	def add_to_favourites(self) -> None:
		'''
		Add a path to favourites
		'''
		# -- Guard incase of app startup
		if not self.sel_add or self.app.on_startup:
			# -- User just started
			return
		
		# -- Determine if favourites file is of good format
		is_safe, data = self.app.pst.playlist_format_okay(self.favourites_path)

		if is_safe:
			# -- Get the song to be added
			track = os.path.basename(self.app.pyr.current_song)

			if self.path_to_add is not None:
				# --
				track = os.path.basename(self.path_to_add)
				self.path_to_add = None

			# -- Add song
			try:
				# --- Get the last counter: If 'song 16', return int('16') = 16
				pos: int = int(list(data[1].keys())[-1].split(' ')[-1])
			except Exception:
				# -- First time save
				pos: int = 0
			finally:
				# -- Append & Save
				data[1][f'song {pos + 1}'] = track
				self.app.pst.favs.append(track)
				self.app.dbm.save_data(data, self.favourites_path)

			# -- USER FEEEDBACKK !!
			title: str = self.app.uiu.clean_title(track, max_lmt=55, max_show=52)
			self.app.uiu.updateStatusLabel(f'{title}: Added To Favourites.')

			# -- Config fav button accordingly
			curr_play: str = os.path.basename(self.app.pyr.current_song)

			if track == curr_play:
				# -- Config
				self.app.uec.give_cmd(self.app.bui.fav_btn, 'Remove Fav', self.remove_from_favourites)
		
		#<_end of the method_>

	def remove_from_favourites(self) -> None:
		''' Remove A Track From Favourites '''
		# -- Get track to remove
		if self.app.pyr.current_song:
			# -- Button trigger
			track: str = os.path.basename(self.app.pyr.current_song)

		if self.path_to_delete is not None:
			# -- Right-click trigger
			track: str = os.path.basename(self.path_to_delete)
			self.path_to_delete = None

		# -- Remove
		self.app.pst.favs.remove(track)

		# -- Create new data & Save
		data = [
			self.app.rcm.mappings['favourites'],
			{}
		]

		for num, p in enumerate(self.app.pst.favs, start=1):
			# -- Create data
			data[1][f'song {num}'] = p

		self.app.dbm.save_data(data, self.favourites_path)

		# -- USER FEEDBACK
		title: str = self.app.uiu.clean_title(track, max_lmt=55, max_show=52)
		self.app.uiu.updateStatusLabel(f'{title}: Removed From Favourites.')

		# -- Config fav button accordingly
		curr_play: str = os.path.basename(self.app.pyr.current_song)
		if track == curr_play:
			# -- Config
			self.app.uec.give_cmd(self.app.bui.fav_btn, 'Add Fav', self.add_to_favourites)

		#<_end of the method_>


#<_END OF FAVOURITESMANAGER_>