# <============ IMPORTS ===============>
import os
from typing import Optional
from config import AlmaDataPaths
# <====================================>

class SettingsManager:
	def __init__(self, app) -> None:
		self.app = app

		# ===========================================================================
		# ========================================== UPDATED ON THE RUN
		self.data_bag: dict = {'music_folders': []}
		self.player_data: dict = {}                  # Has The Player Settings Or Data
		self.updates: dict = self.data_bag.copy()    # Holds data while user is updating settings
		# ===========================================================================
		# ===========================================================================		

		# --- Settings File
		self.settings_file = AlmaDataPaths.SETTINGS_DIR / 'player_data.json'
		# ---

		#<__ end of the method __>

	def loadStartupSettings(self) -> None:
		''' Load Crucial App Settings '''
		# --- Load Settings Data
		self.player_data = self.app.dbm.read_data(self.settings_file)

		# -- Check If All Must Be Data is there
		_required: list[str] = [
			'playback_state', 'saved_volume',
			'music_folders', 'last_played_data',
			'current_theme'
		]

		if any(item not in self.player_data for item in _required):
			# -- Some Data Is Missing. Reset The Data
			self.player_data = AlmaDataPaths.DEFAULT_PROGRAM_DATA.copy()

		# --- Display of playback state & Initiate volume set
		self.app.uiu.displayPlaybackState()
		self.app.vol.set_volume(self.player_data['saved_volume'])

		#<__ end of the method __>

	def saveAppSettings(self) -> None:
		''' Save settings '''
		# ---- Save data
		self.app.dbm.save_data(self.player_data, self.settings_file)
		# ----

		#<__ end of the method __>
	
	def get_folder(self) -> Optional[str]:
		''' Allow Users to select their Music Folders '''
		# -- Return
		return self.app.lib.select_folder()

		#<_end of the method_>
	
	def remove_nested_if_any(self, data: list[str]) -> list[str]:
		''' Remove Path already covered by a parent folder '''
		cleaned = []
		for p in sorted(data):
			if not any(p.startswith(other + os.sep) for other in cleaned):
				cleaned.append(p)
		return cleaned

		#<_end of the method_>
	
	def add_music_folder(self, folder: Optional[str] = None) -> None:
		''' Remember to scan this folder while scanning for music '''
		# -- If folder not given; Ask for folderr
		if folder is None:
			# -- User manually wants to add music libraries
			folder: Optional[str] = self.get_folder()

			if folder is None:
				return
			
		# -- Normalise path (Important)
		folder = os.path.abspath(folder)
		
		# -- Return if folder already saved
		if folder in self.player_data['music_folders']:
			# -- Don't add
			return
		
		else:
			# -- Implies folder not in data
			data: list[str] = self.player_data['music_folders'].copy()

			# -- Extend data in self.updates
			data.extend(self.updates['music_folders'])

			# -- Append the recently visited folder
			data.append(folder)

			# -- Remove Duplicates: Using set removes duplicates
			clean_data: list = list(set(data))

			# -- Get Cleaned Data
			self.updates['music_folders'] = self.remove_nested_if_any(clean_data)

			# -- If folder not in data, Implies it was nested; return
			if folder not in self.updates['music_folders']:
				# -- Do not dislay
				return

		# -- If settings UI active; display the new folder
		if self.app.bui.settings_ui is not None:
			# -- Clear the box to insert cleaned paths
			self.app.uiu.clear_object(self.app.bui.folders_box)

			# -- Insert the paths to box
			self.app.root.after(
				0,
				lambda: self.app.uiu.display_paths_in(
					'sett_box',
					'end',
					self.updates['music_folders']
				)
			)
		
			# -- Enable the apply button
			self.app.uiu.show_new_button_state_for(self.app.bui.apply_btn, 'normal')

		elif self.app.bui.settings_ui is None:
			# -- Just add the folder to music_folders
			self.player_data['music_folders'] = self.updates['music_folders']
			self.updates = self.data_bag.copy()

		#<_end of the method_>
	
	def show_all_settings(self) -> None:
		''' Display Folders '''
		# -- Display 'No Folder Available' if no added fds
		if not self.player_data['music_folders']:
			# -- Inser a message
			self.app.root.after(0, lambda: self.app.uiu.display_paths_in('sett_box', 'end', ['You Have Not Added Any Folders !']))
			return
		
		# -- Otherwise, show the folders
		self.app.root.after(
			0,
			self.app.uiu.display_paths_in(
				'sett_box',
				'end',
				self.player_data['music_folders']
			)
		)

		#<_end of the method_>
	
	def apply_changes(self) -> None:
		''' Apply any changes that the user may have made '''
		# -- Get original data
		self.player_data['music_folders'] = self.updates['music_folders'].copy()

		self.updates = self.data_bag.copy()

		# -- Disable apply btn
		self.app.uiu.show_new_button_state_for(self.app.bui.apply_btn, 'disabled')

		#<_end of the method_>

#<_ END OF SETTINGSMANAGER>