# <============ IMPORTS =========================>
import os, threading
import tkinter as tk
from config import AlmaDataPaths
from tkinter import filedialog, simpledialog
# <==============================================>
class AlmaPlaylistCreator:
	'''
	Allow User To  Create, Delete Or Edit Playlists
	'''
	def __init__(self, app) -> None:
		self.app = app
		# ------------------------------- UPDATED ON THE RUN
		self.path: str = ''              # Path of the file currently on edit
		self._add: list[str] = []        # Holds paths of newly created playlists
		self.list: list[str] = []        # Holds paths that are displayed in the UI
		self.music: list[str] = []       # Helps to prevent adding duplicates to the UI
		self._in_edit_mode: bool = False # Indicate that we are editing a playist
		# -------------------------------

		self.data_folder = AlmaDataPaths.DATA_DIR
		self.playlist_folder = AlmaDataPaths.PLAYLIST_DIR

		#<__ end of the method __>

	def select_to_add_files(self, music_paths: list[str]) -> int:
		'''
		Avoid Adding duplicates
		'''
		add: list[str] = []
		# ------------
		for m in music_paths:
			name: str = os.path.basename(m)
			if name not in self.music and name.lower().endswith('.mp3'):
				add.append(m)
				self.list.append(m)
				self.music.append(name)
		# ------------
		if add:
			self.app.root.after(0, lambda: self.app.uiu.display_paths_in('main_box', 'end', add))

			return len(add)

		return 0

		#<__ end of the method __>

	def _edit(self, path) -> None:
		'''
		Allow Users to edit an already created playlist
		'''
		# -- Validate if path still exists
		if not os.path.exists(path):
			# Restore The Program Settings
			self.app.uec.aps.restore_previous_settings()
			return  # Nothing to work with
		
		# -- Path of the file currently on edit
		self.path = path

		# --- Read the path
		data = self.app.dbm.read_data(path)
		# ---

		# -- UPDATE !! Clear bags and box
		self.list.clear()
		self.music.clear()
		self.app.uiu.clear_object(self.app.bui.listbox)

		# -- Get Key for this playlist
		self.key = data[0]

		# ---- Collect Files
		music_paths = [p for p in data[1].values() if p.lower().endswith('.mp3')]
		# ----


		# --- Verify Files For Duplicate, then display them
		self.select_to_add_files(music_paths)

		# -- Allow file additions
		self.app.uiu.show_new_button_state_for(self.app.bui.next_btn, 'normal')

		#name: str = os.path.basename(path).replace('.json', '').title()
		#self.app.uiu.updateStatusLabel(f'Edit Your Playlist "{name}".')
		# ---

		#<__ end of the method __>

	def save_playlist_data(self, title: str, key: str, file: str = 'saved_data.json') -> None:
		'''
		Save the playlist data for any newly created playlist
		'''
		# ----- Load Saved Playlist Data
		path = self.data_folder / file            # Path of the playlist data file
		data = self.app.dbm.read_data(path)       # Saved playlist data

		if not data:
			data = {}                             # Assume that this is the first playlist to be created
		# -----
		
		# ---- Create The Bag For the new data &  Save
		data[key] = [title, False, self.music, len(self.music)]
		self.app.dbm.save_data(data, path)        # Save The New Playlist Data
		# ----
		# ---- Load playlist data to include the newly created one
		self.app.rcm.load_playlist_data()

		#<__ end of the method __>

	def _actualise_playlist(self) -> None:
		'''
		Create The playlist; whether it is new or it is an update
		'''
		if not self.list:
			return        # We cant allow creation of empty playlists

		# =======================================================================================================================
		# =======================================================================================================================

		def _write(path, key: str) -> None:
			'''
			Detect The Files that cannoot be added
			'''
			writeble = [key]
			data: dict[str, str] = {}         # Holds Files That will be saved for the new playlist

			# ----------- Collect & Save The New Data
			for i, p in enumerate(self.music, start=1):
				data[f'song {i}'] = p
			
			# --
			writeble.append(data)

			self.app.dbm.save_data(writeble, path)
			# ------------

			#<__ end of inner function __>

		# =======================================================================================================================
		# =======================================================================================================================

		# Determine Whether we are in edit mode
		if self._in_edit_mode:
			open(self.path, 'w').close()                                  # Clear everything in the file
			name: str = os.path.basename(self.path).replace('.json', '')
			path = self.playlist_folder / f'{name}.json'                  # Where the new playlist should be saved

			# Save The Paths
			threading.Thread(target=_write, args=(path, self.key), daemon=False).start()

			# ----- Necessary Update
			self.app.uec.aps.restore_previous_settings()              # Return the app into selector's state
			#self.app.uiu.updateStatusLabel(f'Playlist {name.title()} Was Updated Successfully. Exiting ...')
			# -----

			return  # We need not create a button here

		# --- NEW PLAYLIST CREATION SECTION !!
		name: str = simpledialog.askstring(
					'Playlist Name', 'Name:'
			)
		# Check if a name was supplied
		if not name or name == 'favourites':
			self.app.uiu.updateStatusLabel('Playlist Not Created!!')

			return    # No Name Was Supplied, hence do not create the playlist

		# -- Get the ID for this new playlist
		key: str = self.app.get_key()

		# ----- Save Files
		path = self.playlist_folder / f'{name}.json'     # Where the new playlist shall be saved
		threading.Thread(target=_write, args=(path, key), daemon=False).start()
		# -----

		# ----- Indicate that this is a new playlist & Save The Playlist Data
		self._add.append(path)                      # Newly created playlist
		name = name.replace('.json', '')            # Clean name

		#  --- Save the playlist data
		threading.Thread(
				target=self.save_playlist_data,
				args=(name, key),
				daemon=False
		).start()
		# -----

		self.app.uec.aps.restore_previous_settings()
		#self.app.uiu.updateStatusLabel(f'Playlist {name.title()} Created Successfully !!')

		#<__ end of the method __>

	def _escalate_files(self, paths=None) -> None:
		'''
		Called when the user drags and drops or when some songs
		were specifically chosen from the library
		'''
		if not paths:
			paths: list[str] = list(
					filedialog.askopenfilenames(
							title='Select Files',              # Title of the wondow that pops up
							filetypes=[('MP3 Files', '*.mp3')] # Limit only to mp3 files
						)
				)
			if not paths:
				return     # We need not proceed without paths

		added: int = self.select_to_add_files(paths)           # Total number of songs added to UI

		# -----
		if added != 0:
			# -- Show new btn state to allow creation or update
			self.app.uiu.show_new_button_state_for(self.app.bui.play_btn, 'normal')
			self.app.uiu.show_new_button_state_for(self.app.bui.next_btn, 'normal')
			self.app.uiu.updateStatusLabel(f"✅ Added {added} track(s)")
		# -----

		#<__ end of the method __>

	def show_context(self, event) -> None:
		'''
		Show available optiions on rright click for an item
		'''
		if not self.list:
			return        # We need not show context when there are no items in the UI
		# ---- Clear & Set selection
		self.app.bui.listbox.selection_clear(0, tk.END)
		self.app.bui.listbox.selection_set(self.app.bui.listbox.nearest(event.y))
		# ----

		self.app.bui.apc_menu.tk_popup(event.x_root, event.y_root)   # Display available options

		#<__ end of the method __>

	def _obliterateBox(self) -> None:
		'''
		Delete everythiing in the UI
		'''
		if not self.list:
			return     # we need not clear sth that is not available

		# ---- Clear Everything
		self.list.clear()
		self.music.clear()
		self.app.uiu.clear_object(self.app.bui.listbox)  # Clear Listbox
		# ----

		self.app.uiu.updateStatusLabel('Successfully Cleared! You Can Start Creating A New One.')

		#<__ end of the method __>

	def _obliteratePath(self) -> None:
		'''
		Delete the selected path
		'''
		sel: tuple[int] = self.app.bui.listbox.curselection()   # Returns a tuple
		idx: int = sel[0]                                       # Position of the selected item

		song: str = os.path.basename(self.list[idx])            # Song to be deleted

		# ----- Deletion
		del self.list[idx]
		del self.music[idx]
		self.app.uiu.removeItemfromListbox(idx) # Remove item
		# -----

		# -- Allow updates
		self.app.uiu.show_new_button_state_for(self.app.bui.play_btn, 'normal')

		self.app.uiu.updateStatusLabel(f'Removed {song[:40]} From The Playlist✅')

		#<__ end of the method __>


#<_END OF ALMA_PLAYLIST_CREATOR_>