# <============ IMPORTS ===============>
import os
import random, threading
from typing import Optional
# <====================================>

class PlaylistManager:
	def __init__(self, app) -> None:
		self.app = app

		# =========================================================================
		# ========================================= UPDATED ON THE RUN
		self.favs = []                   # Fav paths
		self.playlist = []               # Master playlist
		self.song_names = []             # Contains basenames of the paths in the UI
		self.shuffle_bag = []            # Holds shuffled playlist
		self.shuffle_bag_names = []      # Holds shuffled playlist basenames
		self.filtered_playlist = []      # Mainly used for search feature and pos of selection
		# =========================================================================
		# =========================================================================

		#<__ end of the method __>

	def _on_wrong_format(self, is_favourites: bool, path) -> None:
		''' Delete Playlist of wrong formats '''
		# -- Corrupt data: Create new path
		if is_favourites:
			# -- favourites playlist should always be available
			self.app.createFavouriteBag()
		else:
			# -- Delete this playlist
			os.remove(path)

		#<_end of the method_>
	
	def playlist_format_okay(self, playlist_path) -> tuple[bool, list]:
		'''
		Determine if any playlist data is of the right format.
		Ensure data is available(mostly the playlist ID)
		Iniitiate deletion of the playlist if of wrong format.

		Playlist Fomart
		---------------
		['playlist_id', {}]
		'''
		# -- Data & favourites mark
		data = self.app.dbm.read_data(playlist_path)
		is_favourites: bool = True if str(playlist_path).lower().endswith('favourites.json') else False

		# -- The bag should be a list
		if isinstance(data, list):
			# -- Data must be of length 2
			if len(data) == 2:
				# -- Data at pos 0 should be a string
				if isinstance(data[0], str) and isinstance(data[1], dict):
					# -- Data of right format
					return True, data
				
		# -- Corrupt data: Create new path
		self._on_wrong_format(is_favourites, playlist_path)

		return False, []
		
		#<_end of the method_>

	def select_files_to_add(self, paths, randomise_paths: bool = False) -> None:
		'''
		Adds tracks to bags and Initiates the addition of the same tracks
		to the Listbox. It also ensures that duplicates are filtered out.
		'''
		add = []   # Bag to hold paths to be added to the UI
		# --- Loop to get files to add
		for p in paths:
			p_b: str = os.path.basename(p)  # basename of the current p
			# -- Determine whether to add it
			if p_b not in self.song_names and p_b.lower().endswith('.mp3'):
				add.append(p)                    # This can be added
				self.playlist.append(p)          # Add this to the master playlist
				self.song_names.append(p_b)      # Ensure we do not add this on the run
				self.filtered_playlist.append(p) # path will be availbale on search

		# --- Add paths to UI if there are to add
		if add:
			# --- Add the paths to UI
			self.app.root.after(0, lambda: self.app.uiu.display_paths_in('main_box', 'end', add))
			
			# -- Check if randomisation is necessary
			if randomise_paths:
				# -- Safe check before randomising
				self.app.root.after(
					0,
					self._safety_before_randomisation,
					add
				)
				#self._safety_before_randomisation(add)

		#<__ end of the method __>
	
	def _safety_before_randomisation(self, added: list) -> None:
		'''
		If on startup or after clearing bags and the user drags and drops or
		adds individual files, note that the method select_files_to_add only adds
		the files to playlists (excluding shuffle bags) and to the listbox. So,
		there's no where shuffle bag is filled unlike when the program loads a
		playlist or a folder. In this case, if the user selected shuffle mode,
		the program will the songs in the same order as repeat_all mode. In this
		case, if the user adds individual files, shuffle bag needs to be filled.

		Therefore, this method checks if shuffle bags are worthy to be filled and
		if they are, the ransomisation method is called.
		'''
		# -- Determine if main playlist and shuffle bags are equal
		if self.playlist == self.shuffle_bag:
			# -- Equal => Not randomised => Randomise
			self.randomise_paths()

		elif self.playlist != self.shuffle_bag:
			'''
			Recall that this method is called under the circumstance that the user
			drag and dropped or the user added individual files. So we consider some
			cases.
			The first is that the user had loaded a playlist or folder before and then
			drag and dropped or added some paths. In this case, we gotta shuffle the added
			playlist then extend it to shuffle bag.
			The second case is that the user had already dragged and dropped. Of course,
			this method would have been called and condition 1 executed. But If the user
			drag and drops again or adds files, the compared playlists shall not be the
			same.
			So in both cases, this condition 2 should be executed. The most suitable solution
			is randomising the passed added tracks, randomising and then extending the shuffle
			bags with this new tracks.
			'''
			# -- Get the shuffled list for the new additions
			new_paths: list = self.randomise_paths(added)
			new_bases: list = [os.path.basename(p) for p in new_paths]

			# -- Extend to the shuffled bags
			self.shuffle_bag.extend(new_paths)
			self.shuffle_bag_names.extend(new_bases)

		#<_end of the method_>
	
	def randomise_paths(self, paths: Optional[list] = None) -> Optional[list]:
		''' Randomise New Playlists or added paths '''
		# --
		shuffle = random.shuffle

		# -- Get paths if not provided
		if paths is None:
			# -- Copy main playlist and randomise
			paths: list = self.playlist.copy()
			shuffle(paths)

			# --  Fill main bags
			self.shuffle_bag = paths.copy()
			self.shuffle_bag_names = [os.path.basename(p) for p in paths]
		
		elif paths is not None:
			# -- Shuffle and return
			shuffle(paths)

			return paths

		#<_end of the method_>
	
	def repeat_all_mode_idx(self, path, value: int) -> int:
		''' Get next or previous song position based on the value '''
		# --
		base: str = os.path.basename(path)

		# --
		try:
			# -- Get new idx
			new_idx: int = (self.song_names.index(base) + value) % len(self.song_names)
		except Exception:
			'''
			The current playing is not in this new playlist for sure. We could make
			sure that the next song the plays after the current one is the first song
			in the main playlist.
			'''
			new_idx: int = 0
		
		# -- Return the position of the playable song
		return new_idx
	
		#<_end of the method_>
	
	def shuffle_mode_idx(self, path, value: int) -> int:
		''' Shuffle mode controller. Value tells the program whether to move foward or Backward'''
		# -- Use base
		base: str = os.path.basename(path)

		# -- Get the next or previous song
		try:
			# -- Get new idx
			new_idx: int = (self.shuffle_bag_names.index(base) + value) % len(self.shuffle_bag)
		except Exception:
			'''
			Even by using the basename, the song is still not available.
			An alternative is playing the first song in shuffle bags.
			'''
			new_idx: int = 0
		
		# -- Get the possible playbale song_name
		playable: str = self.shuffle_bag_names[new_idx]

		# -- Return position of playable in the main playlist
		return self.song_names.index(playable)

		#<_end of the method_>

	def clear_bags(self, event=None) -> None:
		''' Clear bags and listbox '''
		# ------------- Clear Bags
		self.playlist.clear()
		self.song_names.clear()
		self.filtered_playlist.clear()
		# -------------

		# --- Clear lisbox
		self.app.uiu.clear_object(self.app.bui.listbox)

		#<__ end of the method __>

	def get_next_or_previous_song(self, value: Optional[int] = None):
		''' Return the next song. Value tells whether it is next or previous song needed '''
		# -- Get playback state
		state: str = self.app.sgm.player_data['playback_state']

		# -- Return next song with respect to playback state
		if state == 'repeat_one':
			# -- Return the current playing song
			return self.app.pyr.current_song
		else:
			# -- State is either repeat_all or shuffle
			if state == 'repeat_all':
				# --
				try:
					# -- Get pos of currently playing
					curr_idx: int = self.song_names.index(os.path.basename(self.app.pyr.current_song))
				except Exception:
					# -- Song not available
					return self.playlist[0] # -- The first song in the playlist should play

				# -- Return the next song
				return self.playlist[(curr_idx + value) % len(self.app.pst.playlist)]
			else:
				# -- Shuffle mode: If not shuffled, shuffle
				try:
					# -- Get position of the playing song
					curr_idx: int = self.shuffle_bag_names.index(os.path.basename(self.app.pyr.current_song))
				except Exception:
					# -- Song still not available
					try:
						# -- Return first song in shuffle bags
						return self.shuffle_bag[0] # -- The first song in the playlist should play
					except Exception:
						# -- Return currently playing
						return self.playlist[0]

				# -- Return the next song
				return self.shuffle_bag[(curr_idx + value) % len(self.app.pst.shuffle_bag)]
		
		#<_end of the method_>

	def remove_selected_object(self, pos: int = None) -> None:
		''' Remove the selected object from playlists '''
		# -- Safety Gurad
		if pos is None:
			return     # Nothing to remove
		
		# -- Get Selected Path
		path = self.filtered_playlist[pos]

		# -- Deletion positions
		visible_idx: int = pos
		master_idx: int = self.playlist.index(path)
		shuff_idx: int = self.shuffle_bag.index(path)

		# ======================================================
		# =============== DELETION IN PROGRESS =================
		# -- From Display
		self.app.uiu.removeItemfromListbox(pos)

		# -- Playlist Bags
		self.playlist.pop(master_idx)
		self.song_names.pop(master_idx)
		self.filtered_playlist.pop(visible_idx)
		self.shuffle_bag.pop(shuff_idx)
		self.shuffle_bag_names.pop(shuff_idx)
		# --
		# ======================================================
		# ======================================================

		# --- Safeguard the current playing idx if not on startup
		if not self.app.on_startup:
			if master_idx < self.app.pyr.current_song_index:
				# -- Decrease current idx by 1
				self.app.pyr.current_song_index -= 1
			
			elif master_idx == self.app.pyr.current_song_index:
				# -- Fade out current and proceed with the next
				self.app.pyr.fade_out_song()
				self.app.pyr.trigger_playback()
			
			# -- Display the next song if affected
			if path == self.app.uiu.next_song:
				# -- Display another song as next
				threading.Thread(
					target=self.app.uiu.show_next_song,
					daemon=True
				).start()
			
		#<_end of the method_>


#<_ END OF PLAYLISTMANAGER>