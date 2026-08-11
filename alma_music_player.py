# <============ IMPORTS ===============>
import os
import re, uuid
import pygame, time
import tkinter as tk
import threading as td
from typing import Optional, Callable
from tkinterdnd2 import TkinterDnD
from alma_ui_builder import BuildUI
from alma_ui_updater import UIUpdates
from alma_online_worker import Online
from alma_player_engine import PlayerEngine
from alma_status_manager import StatusManager
from alma_library_manager import LibraryManager
from alma_recommendations import Recommendations
from alma_settings_manager import SettingsManager
from alma_playlist_manager import PlaylistManager
from alma_exceptions_catcher import GetExceptions
from alma_volume_controller import VolumeController
from alma_search_controller import SearchController
from alma_favourites_manager import FavouritesManager
from alma_database_manager import AlmaDatabaseManager
from alma_ui_configurer import UIElementsConfiguration
# <====================================>

class MusicApp:
	def __init__(self, app) -> None:
		# ======================================================================================
		# ============================================ MAIN APPLICATION WINDOW
		self.root = app
		self.root.title('Alma Music Player')           # Window name
		self.root.geometry('1020x540')                 # width(1020 piixels) x height(540 piixels)
		self.root.resizable(False, False)              # The window size is not resizable
		self.root.configure(bg='black')                # Background colour to be black
		# ======================================================================================
		# ======================================================================================

		# ======================================================================================
		# ============================================ ALL DEPENDENCIES
		self.olw = Online(self)                        # -- 0) Online --
		self.bui = BuildUI(self)                       # -- 1) BuildUI --
		self.uiu = UIUpdates(self)                     # -- 2) UIUpdates --
		self.pyr = PlayerEngine(self)                  # -- 3) PlayerEngine --
		self.ect = GetExceptions(self)                 # -- 4) GetExceptions --
		self.stm = StatusManager(self)                 # -- 5) StatusManager --
		self.lib = LibraryManager(self)                # -- 6) LibraryManager --
		self.sgm = SettingsManager(self)               # -- 7) SettingsManager --
		self.rcm = Recommendations(self)               # -- 8) Recommendations --
		self.pst = PlaylistManager(self)               # -- 9) PlaylistManager --
		self.sch = SearchController(self)              # -- 10) SearchController --
		self.vol = VolumeController(self)              # -- 11) VolumeController --
		self.fvs = FavouritesManager(self)             # -- 12) FavouritesManager --
		self.dbm = AlmaDatabaseManager(self)           # -- 13) AlmaDatabaseManager --
		self.uec = UIElementsConfiguration(self)       # -- 14) UIElementsConfiguration --
		# ======================================================================================
		# ======================================================================================

		# ======================================================================================
		# ============================================ UPDATED ON THE RUN
		self._job = None                               # Store the after() ID for update song timer
		self.data: int = 0                             # Holds percentage of the part of the song played
		self._anime_work = None                        # Indicate schedule of artwork change
		self.on_startup: bool = True                   # Indicate that the program just ran
		# ======================================================================================
		# ======================================================================================

		# -- Safe data saves
		self.data_lock = td.Lock()

		# --- Run Crucial Startup Functions
		self.sgm.loadStartupSettings()                                 # Load crucial startup settings
		self.root.after(0, self.startup_UI_show)                       # -- Necessary startup UI displays
		td.Thread(target=self.startup_DATA_load, daemon=True).start()  # -- Necessary data used on the run
		# ---

		#<__ end of the method __>

	def startup_DATA_load(self) -> None:
		''' Run Crucial functions on startup '''
		# ---------------------------- Run Startup Funcs
		self.fvs.load_favourites()                     # Load favourites data
		self.pyr.get_last_play()                       # Prompt the user to play last known playback
		self.rcm.load_playlist_data()                  # Load playlist data
		self.rcm.load_recommendables()                 # Load recommendables data
		self.rcm.schedule_updates()                    # ---
		# ----------------------------

		#<__ end of the method __>

	def startup_UI_show(self) -> None:
		''' Necessary UI show on startup '''
		# ---------------------------- Run startup func
		self.sch.show_placeholder()                    # Display search placeholder text
		# -- Set default background on startup
		self.uiu.setBackground(
				main_img=self.uiu.bg_img,
				next_img=self.uiu.bg_img,
				prev_img=self.uiu.bg_img
			)
		# --
		# -- Display Online state
		self.olw.online_worker()
		self.root.after(13000, self.stm.rotate_status) # Live Updates
		self.bui.search_entry.after(20000, self.sch.cycle_default_hint)
		# ----------------------------

		#<__ end of the method __>
	
	def track_playing(self) -> None:
		''' If current playing in this playlist, Highlight it '''
		# --
		try:
			# -- Get basename
			base: str = os.path.basename(self.pyr.current_song)
			# -- Find the position
			pos: int = self.pst.song_names.index(base)
		except Exception:
			# -- Currently playing is not in this playlist/folder
			return
		else:
			# -- Highlight the song
			self.initiateHighlight(pos)

			# -- Update Next Song label Together with Song artworks
			self.uiu.show_next_song()

			self.root.after(
				10,
				self.uiu.updateSongThumbnail
			)

		#<_end of the method_>

	def finaliseSongSession(self, path: str) -> None:
		''' Stop Updating Timer and Initiate addition of points for prev song '''
		# --- Stop session for timer if self._job is not None
		if self._job is not None:
			'''
			Implies the previous song was not paused: User clicked next or
			the program just switched to the next song
			'''
			self.root.after_cancel(self._job)

		# --- Initiate addition of points
		td.Thread(target=self.rcm.update_played_song_data, args=(path,), daemon=True).start()

		#<__ end of the method __>

	def getPauseState(self) -> None:
		''' Determine if paused or unpaused & initiate configuration of pause_btn '''
		# --- Initiate set to pause or resume based on state
		if self.pyr.is_paused:
			# --- In paused state: 'Resume'; Command: unapuse the song
			self.uec.give_cmd(self.bui.pause_btn, 'Resume', self.pyr.unpause_song)

			# --- Already configured; Return
			return
		# --- In Unpaused State: 'Pause'; Command: pause the song
		self.uec.give_cmd(self.bui.pause_btn, 'Pause', self.pyr.pause_song)

		#<__ end of the method __>
	
	def formatTime(self, sec: int) -> str:
		''' Convert time into minutes & seconds '''
		# --- Get Seconds & Minutes played
		secs: int = sec % 60       # Seconds played in the current min
		minutes: int = sec // 60   # Total minutes played
		# ---
		# --- Return formatted time
		return f'{minutes:02}:{secs:02}'

		#<__ end of the method __>

	def getSelection(self, func: Callable[[int], None]) -> None:
		'''
		On listbox double click, get pos of the selection:
		After, call the func argument with the pos.
		'''
		try:

			# -- Get selection pos
			sel: tuple[int] = self.bui.listbox.curselection()
			pos: int = sel[0] # Position of the selected item
			# -- Clear Selection
			self.bui.listbox.selection_clear(0, tk.END)

		except Exception as e:
			# --- Return Nothing
			raise e
			
		else:
			# -- Call the argument with this pos
			func(pos=pos)
		
		#<__ end of the method __>

	def playSelected(self, pos: int = None) -> None:
		''' Initiate playback of the selected song '''
		# --- Return if pos is None
		if pos is None:
			# --- Nothing to play
			return
		# ---

		# --- Get path name in filtered view
		path: str = self.pst.filtered_playlist[pos]

		# --- Update Current Song Index
		self.pyr.current_song_index = self.pst.playlist.index(path)
		# ---
		# --- Trigger playback
		self.pyr.trigger_playback(fade_in=True)

		#<__ end of the method __>
	
	def _initiate_artwork_change(self, state: str) -> None:
		''' 
		After a period of time after changing the playback state,
		if the state is still the same, change the artworks.
		'''
		# --
		if state == self.sgm.player_data['playback_state']:
			# -- Change artwork
			self.root.after(10, self.uiu.updateSongThumbnail)
			# --
			self._anime_work = None

		#<_end of the method_>

	def nextPlayMode(self) -> None:
		''' Switch to the next playback mode '''
		# --- Define cycle order
		order: list[str] = ['repeat_all' , 'repeat_one', 'shuffle']
		# --- Get pos of the current state
		pos: int = order.index(self.sgm.player_data['playback_state'])
		# --- Switch to the next state (wrap around)
		state: str = order[(pos + 1) % len(order)]
		self.sgm.player_data['playback_state'] = state

		# --- Initiate display of the new state
		self.uiu.displayPlaybackState()

		# -- Show Next Song if app not on startup
		if not self.on_startup:
			# -- Safe to display next track
			#td.Thread(target=self.uiu.show_next_song, daemon=False).start()
			self.uiu.show_next_song()

			# -- Schedule artwork change
			if self._anime_work is not None:
				# -- Cancel and schedule
				self.root.after_cancel(self._anime_work)

			# -- Schedule
			self._anime_work = self.root.after(
					3500,
					lambda: self._initiate_artwork_change(state)
				)
		#<__ end of the method __>

	def updateSongTimer(self) -> None:
		'''Update playback timer, progress bar, and labels during song playback.'''

		if not pygame.mixer.music.get_busy() and not self.pyr.is_paused:
			# Song ended naturally → cancel job and move to next track
			self.root.after_cancel(self._job)
			self.pyr.next_song()

		elif self.pyr.is_paused:
			# Paused → stop scheduling until unpaused
			try:
				# --
				self.root.after_cancel(self._job)
			except ValueError:
				# -- Collision maybe
				pass
				# --
			finally:
				# -- Give a None value to self.._job
				self._job = None

		elif self.pyr.dragging:
			# -- User is dragging: No need to schedule.
			self.root.after_cancel(self._job)

		else:
			# Only update progress if user is not dragging the knob
			elapsed = time.time() - self.pyr.start_time
			progress = elapsed / self.pyr.current_duration
			self.data = progress   # Recommendation % tracking

			# --- Smooth progress blending (prevents jitter) ---
			# Instead of jumping directly to the raw progress value,
			# we blend the new progress with the previous one:
			#   - 80% of the old value
			#   - 20% of the new value
			# This weighted average smooths out sudden jumps caused by
			# timing inconsistencies or small delays in the update loop.
			#self.uiu.current_progress = self.uiu.current_progress * 0.8 + progress * 0.2
			self.uiu.current_progress = progress
			#print(progress * self.pyr.current_duration)

			# Draw the progress bar at the smoothed position.
			# Multiplying by song_length converts the normalized progress ratio
			# back into seconds for accurate placement on the seek bar.
			self.uiu.draw_progress(self.uiu.current_progress * self.pyr.current_duration)

			# --- Update elapsed time label ---
			# 'elapsed' is the number of seconds since playback started.
			# divmod splits it into minutes and seconds for display.
			mins, secs = divmod(int(elapsed), 60)
			# Update the label to show elapsed time in MM:SS format.
			self.uiu.updateTimeLabel(self.bui.elapsed_label, f'Played: {mins}:{secs:02d}')

			# --- Update remaining time label ---
			# Calculate how many seconds are left until the song ends.
			remain = max(0, int(self.pyr.current_duration - elapsed))
			# Split remaining time into minutes and seconds.
			rm_m, rm_s = divmod(remain, 60)
			# Update the label to show remaining time in "-MM:SS" format.
			# The leading minus sign indicates countdown style.
			self.uiu.updateTimeLabel(self.bui.remaining_label, f'Ends In: {rm_m}:{rm_s:02d}')

			# Schedule next update (every 90 ms for smoothness)
			self._job = self.root.after(90, self.updateSongTimer)

	    #<_end of the method_>

	def get_key(self) -> str:
		''' Generate a unique ID for new playlists '''
		# --
		return str(uuid.uuid4())
	
		#<_end of the method_>

	def createFavouriteBag(self) -> None:
		''' Create favs file and update playlist data '''
		# --- Define file_path of the favs file & and save it as empty
		path: str = self.rcm.pst_folder / 'favourites.json'

		# -- Get ID for favourites.json
		ID: str = self.rcm.mappings.get('favourites', '')
		if not ID:
			# -- Create new ID & Map
			ID: str = self.get_key()
			self.rcm.mappings['favourites'] = ID

		# --- Clear favourites playlist
		td.Thread(
			target=self.dbm.save_data,
			args=([ID, {}], path),
			daemon=True
		).start()
		# ---

		# --- Clear favourites bag in playlist data
		if ID in self.rcm.playlist_data:
			# --- Delete this data
			del self.rcm.playlist_data[ID]

		# --- Create new bag
		self.rcm.playlist_data[ID] = ['favourites', False, [], 0]
		
		# --- Save the playlist data
		td.Thread(
			target=self.dbm.save_data,
			args=(self.rcm.playlist_data, self.rcm.pst_data_file),
			daemon=True
		).start()
		# ---

		#<__ end of the method __>

	def initiateHighlight(self, pos: int) -> None:
		''' Track the playing song incase the items in the listbox were changes '''
		# --- Update current song index and prev index
		self.pyr.current_song_index = pos
		self.uiu.prev_index = None
		# --- Initite highlight after 50 ms (0.05 sec)
		self.root.after(50, self.uiu.highlightCurrentPlaying)
		
		#<__ end of the method __>

	def add_selected_to_favourites(self, pos: int = None) -> None:
		''' Initiate addition of the selected to favourites playlist '''
		# --- Return if pos is None
		if pos is None:
			# --- Nothing to add
			return
		# ---
		# --- Get the path name in filtered playlist
		path: str = self.pst.filtered_playlist[pos]
		# ---
		# --- Determine if really to add
		if os.path.basename(path) not in self.pst.favs:
			# --- Implies this song is not in favs
			self.fvs.sel_add = True

			# -- Indicate path to add
			self.fvs.path_to_add = path

			# -- Initiate addition
			td.Thread(target=self.fvs.add_to_favourites, daemon=True).start()

		#<__ end of the method __>

	def obliterate_selected_from_favourites(self, pos: int = None) -> None:
		'''  Initiate removal of the selected to favourites playlist '''
		# --- Return if pos is None
		if pos is None:
			# --- Nothing to add
			return
		# ---
		# --- Get the path name in filtered playlist
		path: str = self.pst.filtered_playlist[pos]
		# ---
		# --- Determine if really to add
		if os.path.basename(path) in self.pst.favs:
			# --- Implies this song is in favs
			# -- Indicate trigger as right_click
			self.fvs.selected = True
			# -- Indicate path to obliterate
			self.fvs.path_to_delete = path
			
			# -- Initiate addition
			td.Thread(target=self.fvs.remove_from_favourites, daemon=True).start()
		
		#<__ end of the method __>

	def check_for_recommendations(self) -> None:
		''' Check if there are any recommendable songs for play '''
		# --- This feature is not yet available
		return

		#<__ end of the method __>

	def parse_dnd_string(self, dnd_str: str) -> list[str]:
		''' Parse dnd string '''
		pattern: str = r'\{([^}]*)\}|([^\s]+)'
		matches = re.findall(pattern, dnd_str)
		results: list[str] = []
		for a, b in matches:
			if a:
				results.append(a)
			elif b:
				results.append(b)

		return results

		#<__ end of the method __>

	def onDrop(self, event) -> None:
		''' Initiate additions of the dropped paths to the UI '''
		data: str = ''
		try:
			data: str = event.data
		except Exception:
			data: str = event
		# --- Get paths to be added
		paths: list[str] = self.parse_dnd_string(data)

		# --- Initiate addition of paths to the UI
		if self.uec.aps.in_creator_mode:
			# --- The user might be editing or creating a playlist
			# --- Schedule the addition
			self.root.after(0, lambda: self.uec.aps.apc._escalate_files(paths))

			# --- We should not update the playlists
			return

		# --- Schedule the addition
		self.root.after(0, lambda: self.lib.add_paths(paths))

		#<__ end of the method __>

	def clear_selection(self, event) -> None:
		''' Clear Selection in the listbox '''
		self.bui.listbox.selection_clear(0, tk.END)

		#<__ end of the method __>

	def onRightClick(self, event, bag: Optional[list[str]]=None, menu=None) -> None:
		''' Display the Context Menu '''
		# --- Work with the filtered view
		if not bag:
			# -- Implies no songs added or the search has yielded 0 results
			return # --- Nothing to act on
		# --- Context menu pop up
		try:
			self.clear_selection(event)  # Clear Selection in the listbox
			self.bui.listbox.selection_set(self.bui.listbox.nearest(event.y))
			menu.tk_popup(event.x_root, event.y_root)
		except Exception:
			# -- Rare Occurence
			pass
		finally:
			menu.grab_release()
			# ---- Set a timer to remove the selection after 0.4 sec
			self.root.after(400, lambda: self.clear_selection(event))
		
		#<__ end of the method __>

	def on_app_close(self) -> None:
		''' Save Important Data Before Closing '''
		# -- Guard If User Opened the program and quited before playing anything
		if not self.pyr.current_song:
			# --
			self.sgm.saveAppSettings()

			self.root.destroy()

			return
		
		self.sgm.player_data['last_played_data'] = {

			'song': os.path.basename(self.pyr.current_song),
			'progress_ratio': self.uiu.current_progress,
			'song_length': self.pyr.current_duration
		}

		# -- Save this data
		self.sgm.saveAppSettings()

		self.root.destroy()

		#<_end of the method_>


#<_ END OF MUSICAPP>

if __name__ == '__main__':
	# --- Create Window
	root = TkinterDnD.Tk()
	# --- Start the program
	app = MusicApp(root)

	# ---
	root.mainloop()