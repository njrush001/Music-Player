# <============ IMPORTS ===============>
import os, threading
import tkinter as tk
from config import AlmaDataPaths
from alma_playlist_creator import AlmaPlaylistCreator
# <====================================>

class AlmaPlaylistSelector:
	'''
	Allow Users to select their previously created playlists. In addition,
	create pathway where the users will be able to create new or edit their
	created playlists
	'''

	def __init__(self, app) -> None:
		self.app = app
		# --------------------------------- UPDATED ON THE RUN
		self.apc = None
		self.btn_counter: int = 0           # Communicates the number of Buttons created
		self.in_deletion: bool = False      # Tells if the user is deleting playlists or not
		self.embedded_paths: list = []      # Holds button foor which button has been created
		self.in_creator_mode: bool = False
		# ---------------------------------
		self.playlists_location = AlmaDataPaths.PLAYLIST_DIR

		#<__ end of the method __>
	
	def _get_playlists(self) -> None:
		''' Get playlists in the playlists Directory '''
		# ----
		_dir = self.playlists_location
		_found: list = []
		# ----

		# -- Get available playlists
		for r, _, files in os.walk(_dir):
			for f in files:
				# -- Add files ending with '.json'
				if f.lower().endswith('.json'):
					# -- Add this
					_found.append(os.path.join(r, f))
		
		# -- Return value: Favourites playlist always available
		return _found

		#<_end of the method_>
	
	def select_playlist(self, i: int) -> None:
		'''
		Map the selected button to the playlist it corresponds to:

			Conditions:
			----------
			If the user is not creating or editing any playlist, the program
			should scan the location of tracks for each track in the playlist
			and then make it ready for playback.

			If the prrogram determines that the user is only creating new pl-
			aylists, clicking of a button should not perform any action.

			Finally, we have the situation where the user is in creator mode
			but is editing an already existing playlist. In this case, the
			program won't scan folders on click but would insert the files
			to allow removal, addition or anything else.
		'''
		if not self.in_creator_mode and not self.in_deletion:
			# -- Load the playlist
			self.app.lib.music_from_playlist(self.embedded_paths[i])
		
		elif self.in_creator_mode and self.apc._in_edit_mode:
			# -- Clicking a button allows user to edit that particular playlist
			self.apc._edit(self.embedded_paths[i])
		
		elif self.in_deletion:
			# --  Allow deletion of this playlist
			threading.Thread(
				target=self._perform_actual_deletion,
				args=(self.embedded_paths[i],),
				daemon=False
				).start()
			# --
		
		else:
			# -- User is creating a playlist. Clicking has no effect
			pass

		#<_end of the method_>

	def show_users_playlists(self, args=None) -> None:
		''' Display Available Playlists '''
		if not args: # This method was not called with arguments
			# --- Reset states;
			self.btn_counter = 0     # All buttons will be cleared: Start count from zero
			self.embedded_paths = [] # Prevent opening playlist which the user doesn't intend to open

			# -- Get playlists: favourites playlist is always available
			args: list = self._get_playlists()

			# -- Clear everything in the scroll frame  
			for w in self.app.bui.sel_scroll_frame.winfo_children():
				w.destroy()

		# -- Create Buttons, each mapping to a file
		for i, path in enumerate(args, start=self.btn_counter + 1):
			# -- Get the name for the button
			n: str = os.path.basename(path).replace('.json', '')

			# -- Create btn
			tk.Button(
				self.app.bui.sel_scroll_frame, bg='gray', fg='white',
				width=76, font=('Comic Sans Ms', 7, 'bold'),
				text=f'{i}. {n.title()}',
				command=lambda i=i: self.select_playlist(i - 1) # Indexing in lists starts at zero
			).pack(pady=10, padx=5)

			# Update The Counter and insert the path
			self.btn_counter = i
			self.embedded_paths.append(path)

		#<__ end of the method __>

	def restore_previous_settings(self):
		'''
		Restore the app's general configurations
		'''
		self.app.bui.restore_program_settings()  # Build the menu
		self.app.root.after(0, lambda: self.app.uiu.display_paths_in('main_box', 'end', self.app.pst.playlist))
		self.app.getPauseState() # Config The pause button

		# --- Track the song that was playing
		if not self.app.on_startup:
			self.app.uiu.prev_index = 0
			self.app.uiu.highlightCurrentPlaying()
		# ---

		# -- Clicking a button will looad the playlist now
		self.apc._in_edit_mode = False
		self.in_creator_mode = False
		# --

		# -- Config selector's title to prompt the user to select the playlist to play
		self.app.uiu.show_text_on(self.app.bui.selector_title, 'Click Refresh & Select Your Playlist ❤')

		# --- NEW PLAYLISTS !!!
		if self.apc._add:
			# Implies the user created some new playlists
			self.show_users_playlists(args=self.apc._add)

			# -- Reset the _add state
			self.apc._add = []
		# ---

		#<__ end of the method __>

	def openCreator(self, new_pst: bool = True) -> None:
		'''
		Allow Creation or Editing of playlists
		'''
		self.apc = AlmaPlaylistCreator(self.app)
		# --- Enable Creator's UI
		self.app.bui.playlist_creator_ui()
		# ---
		# Buttons in the canvas should not function
		self.in_creator_mode = True

		if new_pst:
			# -- Config create button do display the text mathing to the mode we in
			self.app.uiu.show_text_on(self.app.bui.play_btn, 'Create')

			# -- Config create button do display the text mathing to the mode we in
			self.app.uiu.show_new_button_state_for(self.app.bui.next_btn, 'normal')

		#<__ end of the method __>

	def editPlaylist(self) -> None:
		'''
		Allow the user to edit already created playlists
		'''
		# Enable Creator's UI
		self.openCreator(new_pst=False)
		# -- Indicate user wants some edit
		self.apc._in_edit_mode = True

		# -- Display the available playlists
		self.show_users_playlists()

		# -- Config selector title to prompt the user to select the playlist to edit
		self.app.uiu.show_text_on(self.app.bui.selector_title, 'Select The Playlist To Edit ❤')

		# -- Config create button do display the text mathing to the mode we in
		self.app.uiu.show_text_on(self.app.bui.play_btn, 'Update')

		#<__ end of the method __>
	
	def _cancel_deletion(self) -> None:
		''' Clicking a button should not delete the playlist '''
		# -- User does not want to delete any more playlist
		self.in_deletion = False

		# -- Show selectors title
		self.app.uiu.show_text_on(self.app.bui.selector_title, 'Click Refresh & Select Your Playlist ❤')

		# -- Show deletion btn
		self.app.uec.give_cmd(self.app.bui.del_btn, 'Delete', self.deletePlaylist)

		#<_end of the method_>
	
	def _perform_actual_deletion(self, path) -> None:
		''' Delete the selected playlist '''

		try:
			# -- Delete the file
			os.remove(path)
		except Exception:
			pass
		else:
			# -- Get the playlist name
			_pst_name = os.path.basename(path).replace('.json', '')

			# -- Ensure favourites bag always exists
			if _pst_name == 'favourites':
				# -- Create bag
				self.app.createFavouriteBag()
		
		finally:
			# -- Display remaining playlists
			self.app.root.after(0, self.show_users_playlists)

		#<_end of the method_>
	
	def deletePlaylist(self) -> None:
		''' Clicking a button in selector UI allows users to delete that playlist '''
		# -- User wants to delete a playlist
		self.in_deletion = True

		# -- Display avaiable playlists if not displayed
		self.show_users_playlists()

		# -- Prompt user to delete a playlist
		self.app.uiu.show_text_on(self.app.bui.selector_title, 'Delete Your Playlist(s) Below ❤')

		# -- Allow users to cancel deletion if pressed the button
		self.app.uec.give_cmd(self.app.bui.del_btn, '❌', self._cancel_deletion)

		#<_end of the method_>

	def _idle_function(self, event) -> None:
		'''
		Prevent Double click feature from playing selected songs
		while the playlist creator is active.
		'''
		event = event

		return

		#<__ end of the method __>


#<_ END OF ALMAPLAYLISTSELECTOR_>