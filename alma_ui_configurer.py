# <============ IMPORTS ===============>
from tkinterdnd2 import DND_FILES
from alma_playlist_selector import AlmaPlaylistSelector
# <====================================>

class UIElementsConfiguration:
	''' Configures UIElements On Stsrtup '''
	def __init__(self, app) -> None:
		self.app = app

		# --- Font Family That The App Uses
		self.font: str = 'Playfair Display Black'
		self.font_1: str = 'Comic Sans Ms'
		self.font_2: str = 'Berlin Sans FB Demi'
		self.font_3: str = 'Franklin Gothic Demi'
		self.font_4: str = 'Segoe Print'
		self.font_5: str = 'Candara'
		self.font_6: str = 'Tahoma'

		# --- Playlist Selector
		self.aps = AlmaPlaylistSelector(self.app)

		# ---  Configure UI Elements
		self._configure_main_elements()

		# =============================================================================================================
		# ====================== Anonymous Functions ==================================================================
		self.give_cmd = lambda obj, txt, cmd: obj.config(text=txt, command=cmd)          # Switch commands and text
		# =============================================================================================================
		# =============================================================================================================

		#<__ end of the method __>

	def _configure_main_elements(self) -> None:
		''' Configure main elements '''
		# <===================================>
		# <========== BUTTONS ================>
		self.app.bui.recommendations_btn.config(text='Suggestions', command=self.app.check_for_recommendations)
		self.app.bui.settings_btn.config(text='⚙', command=self.app.bui.program_settings_ui)

		self.app.bui.lib_btn.config(text='Use Folder', command=self.app.lib.music_from_folder)
		self.app.bui.paths_btn.config(text='Add Songs', command=self.app.lib.add_paths)
		self.app.bui.fav_btn.config(text='Add Fav', command=self.app.fvs.add_to_favourites)
		self.app.bui.playlists_btn.config(text='Playlist', command=self.app.bui.playlist_selector_ui)

		self.app.bui.vol_add_btn.config(text='🔊 +', command=self.app.vol.increase_volume)
		self.app.bui.vol_less_btn.config(text='🔊 -', command=self.app.vol.decrease_volume)

		self.app.bui.play_btn.config(text='Play', command=self.app.pyr.trigger_playback)
		self.app.bui.next_btn.config(text='Next', command=self.app.pyr.next_song)
		self.app.bui.pause_btn.config(text='Pause', command=self.app.pyr.pause_song)
		self.app.bui.prev_btn.config(text='Prev', command=self.app.pyr.previous_song)

		self.app.bui.mode_btn.config(text='-', command=self.app.nextPlayMode)

		self.app.bui.clear_search_btn.config(text='Clear', state='disabled', command=lambda: self.app.sch.reset_search(btn_trigger=True))
		# <===================================>
		# <===================================>

		# <===================================>
		# <=========== LABELS ================>
		self.app.bui.online_label.config(text='Getting Status ...', fg='white', font=(self.font, 9, 'bold'))
		self.app.bui.status_label.config(text='Alma Music Player ! The Best Personal Music Player ❤', fg='white', font=(self.font_4, 8, 'bold'))
		self.app.bui.lib_label.config(text='Library:', fg='white', font=(self.font, 10))
		self.app.bui.playback_label.config(text='Playback Controls:', fg='white', font=(self.font, 10))
		self.app.bui.volume_label.config(text='Volume: -', fg='white', font=(self.font, 10))
		self.app.bui.listbox_label.config(text='Current Music:', fg='white', font=(self.font, 10))
		self.app.bui.mode_label.config(text='Mode:', fg='white', font=(self.font, 10))
		self.app.bui.search_label.config(text='Search Music  :', fg='white', font=(self.font, 10))
		self.app.bui.song_label.config(text='-', fg='white', font=(self.font_1, 11, 'bold'))
		self.app.bui.artist_label.config(text='-', font=(self.font_1, 10, 'bold'))
		self.app.bui.next_label.config(bg='black', fg='yellow', font=(self.font_4, 8, 'bold'))
		self.app.bui.tooltip.config(fg='white', bg='#333', font=(self.font_1, 8))
		self.app.bui.elapsed_label.config(text='Played: 0:00', font=(self.font_3, 9))
		self.app.bui.remaining_label.config(text='Ends In: 0:00', font=(self.font_3, 9))
		self.app.bui.remaining_label.place(x=405, y=510)
		# <===================================>
		# <===================================>

		# <===================================>
		# <=========== SEARCH ================>
		self.app.bui.search_entry.config(textvariable=self.app.bui.search_var, fg='grey')
		self.app.bui.search_entry.bind('<FocusIn>', self.app.sch.hide_placeholder)
		self.app.bui.search_entry.bind('<FocusOut>', self.app.sch.restore_placeholder_if_empty)

		# TRACE CHANGES IN SEARCH_VAR
		self.app.bui.search_var.trace_add('write', self.app.sch.filter_playlist_view)
		# <===================================>
		# <===================================>

		# <===================================>
		# <========== CONTEXT ================>
		self.app.bui.context_menu.add_command(label='Play Next', command=lambda: self.app.getSelection(self.app.pyr.play_next))
		self.app.bui.context_menu.add_command(label='Remove Track', command=lambda: self.app.getSelection(self.app.pst.remove_selected_object))
		self.app.bui.context_menu.add_command(label='Add Fav', command=lambda: self.app.getSelection(self.app.add_selected_to_favourites))
		self.app.bui.context_menu.add_command(label='Remove From Favourites', command=lambda: self.app.getSelection(self.app.obliterate_selected_from_favourites))
		self.app.bui.context_menu.add_command(label='Stop After This Song', command=lambda: self.app.getSelection(self.app.pyr.stop_after_this_song))
		self.app.bui.context_menu.add_command(label='Clear Playlist', command=self.app.pst.clear_bags)
		# <===================================>
		# <===================================>

		# <===================================>
		# <========== LISTBOX ================>
		self.app.bui.listbox.config(fg='black', font=(self.font_1, 8, 'bold'))
		self.app.bui.listbox.bind('<Double-Button-1>', lambda event: self.app.getSelection(self.app.playSelected))
		self.app.bui.listbox.bind('<Button-3>', lambda event: self.app.onRightClick(event, bag=self.app.pst.filtered_playlist, menu=self.app.bui.context_menu))
		self.app.bui.listbox.drop_target_register(DND_FILES)
		self.app.bui.listbox.dnd_bind('<<Drop>>', self.app.onDrop)
		# <===================================>
		# <===================================>

		# <===================================>
		# <============= CANVAS ==============>
		self.app.bui.canvas.itemconfig(self.app.bui.buffer, fill='#555555', outline='')
		#self.app.bui.canvas.itemconfig(self.app.bui.knob, fill='#1ed760', outline='')

		# --- Bindings
		self.app.bui.canvas.bind("<Button-1>", self.app.pyr.seek_click)
		self.app.bui.canvas.bind("<B1-Motion>", self.app.pyr.seek_drag)
		self.app.bui.canvas.bind("<ButtonRelease-1>", self.app.pyr.seek_release)
		self.app.bui.canvas.bind("<Motion>", self.app.uiu.show_tooltip)
		self.app.bui.canvas.bind("<Leave>", lambda e: self.app.bui.tooltip.place_forget())
		# <===================================>
		# <===================================>	

		# <===================================>
		# <============= WINDOW ==============>
		self.app.root.drop_target_register(DND_FILES)
		self.app.root.dnd_bind('<<Drop>>', self.app.onDrop)
		self.app.root.protocol('WM_DELETE_WINDOW', self.app.on_app_close)
		# <===================================>
		# <===================================>

	def _configure_last_played_ui(self, to_play: str) -> None:
		''' Configure last played UI elements '''
		# <===================================>
		# <===================================>
		self.app.bui.lst_btn.config(text='Ok', command=self.app.pyr.continue_with_last_playback)
		self.app.bui.last_played_label.config(text=to_play, bg='white', fg='black', anchor='w', font=(self.font_5, 9, 'bold'))
		# <===================================>
		# <===================================>

		#<_end of the method_>

	def _configure_selector_elements(self, canvas, scrollbar) -> None:
		''' Give Elements In The Extension Identity '''
		# <===================================>
		# <============ BUTTONS ==============>
		self.app.bui.create_playlist_btn.config(text='New +', command=self.aps.openCreator)
		self.app.bui.directory_btn.config(text='Refresh', command=self.aps.show_users_playlists)
		self.app.bui.del_btn.config(text='Delete', command=self.aps.deletePlaylist)
		self.app.bui.edit_btn.config(text='Edit', command=self.aps.editPlaylist)
		self.app.bui.playlists_btn.config(text='❌', command=self.app.bui._obliterateSelector)
		# <===================================>
		# <===================================>

		# <===================================>
		# <============= LABEL ===============>
		self.app.bui.selector_title.config(text='Click Refresh & Select Your Playlist ❤', fg='white', bg='green', font=(self.font_2, 12))
		# <===================================>
		# <===================================>

		# <===================================>
		# <============= CANVAS ==============>
		scrollbar.config(command=canvas.yview)
		canvas.configure(yscrollcommand=scrollbar.set)
		self.app.bui.sel_scroll_frame.bind('<Configure>', lambda event: self._updateScrollRegion(event, canvas))
		canvas.configure(scrollregion=canvas.bbox('all'))
		# <===================================>
		# <===================================>

	def _updateScrollRegion(self, event, canvas):
		''' Update scroll region dynamically whenever scroll scroll_frame changes size'''
		canvas.configure(scrollregion=canvas.bbox('all'))

		#<__ end of the method __>

	def _configure_creator_elements(self) -> None:
		''' Configure elements that the playlist creator uses'''
		# ==========================================================================================
		#                                    BUTTONS
		# ==========================================================================================
		self.app.bui.create_playlist_btn.config(state='disabled')
		self.app.bui.directory_btn.config(state='disabled')
		self.app.bui.del_btn.config(state='disabled')
		self.app.bui.edit_btn.config(state='disabled')
		self.app.bui.lib_btn.config(state='disabled')
		self.app.bui.paths_btn.config(state='disabled')
		self.app.bui.fav_btn.config(state='disabled')
		self.app.bui.settings_btn.config(state='disabled')
		self.app.bui.recommendations_btn.config(state='disabled')
		self.app.bui.play_btn.config(text='-', state='disabled', command=self.aps.apc._actualise_playlist)
		self.app.bui.next_btn.config(text='Add Files', state='disabled', command=self.aps.apc._escalate_files)
		self.app.bui.pause_btn.config(text='Clear View', state='disabled', command=self.aps.apc._obliterateBox)
		self.app.bui.prev_btn.config(state='disabled')
		self.app.bui.playlists_btn.config(text='Quit', command=self.aps.restore_previous_settings)
		# ==========================================================================================
		# ==========================================================================================

		# ==========================================================================================
		#                                    MENU & LISTBOX
		# ==========================================================================================
		self.app.bui.apc_menu.add_command(label='Remove From Playlist', command=self.aps.apc._obliteratePath)
		self.app.bui.listbox.bind('<Button-3>', lambda event: self.app.onRightClick(event, bag=self.aps.apc.list, menu=self.app.bui.apc_menu))
		self.app.bui.listbox.bind('<Double-Button-1>', self.aps._idle_function)
		self.app.uiu.clear_object(self.app.bui.listbox)
		# ==========================================================================================
		# ==========================================================================================

		# ==========================================================================================
		#                                   SEARCH FEATURE
		# ==========================================================================================
		# ==========================================================================================
		# ==========================================================================================

		#<__ end of the method __>
	
	def _configure_settings_elements(self) -> None:
		''' Configure elements in the settings UI '''
		# <===================================>
		# <============ BUTTONS ==============>
		self.app.bui.add_fd_btn.config(text='Add Folder', command=self.app.sgm.add_music_folder)
		self.app.bui.apply_btn.config(text='Apply', state='disabled', command=self.app.sgm.apply_changes)
		# <===================================>
		# <===================================>

		# <===================================>
		# <============= LABELS ==============>
		self.app.bui.settings_title.config(text='MUSIC PLAYER SETTINGS', fg='black', font=(self.font_6, 8, 'bold'))
		self.app.bui.folder_label.config(text='1. Add Your Music Folders:', fg='white', font=(self.font_6, 8, 'bold'))
		# <===================================>
		# <===================================>

		# <===================================>
		# <=========== FOLDERS VIEW ==========>
		self.app.bui.folders_box.config(bg='brown', fg='black', font=(self.font_6, 10, 'bold'))
		# <===================================>
		# <===================================>

		self.app.uec.give_cmd(self.app.bui.settings_btn, '❌', self.app.bui._obliterateSettings)

		# -- Display Available Settings
		self.app.root.after(5, self.app.sgm.show_all_settings)
		#self.app.sgm.show_all_settings()

		#<_end of the method_>

	def restore_general_settings(self) -> None:
		''' Restore general app settings '''
		# ==========================================================================================
		#                                    BUTTONS
		# ==========================================================================================
		self.app.bui.create_playlist_btn.config(state='normal')
		self.app.bui.directory_btn.config(state='normal')
		self.app.bui.del_btn.config(state='normal')
		self.app.bui.edit_btn.config(state='normal')
		self.app.bui.lib_btn.config(state='normal')
		self.app.bui.paths_btn.config(state='normal')
		self.app.bui.fav_btn.config(state='normal')
		self.app.bui.settings_btn.config(state='normal')
		self.app.bui.recommendations_btn.config(state='normal')
		self.app.bui.play_btn.config(text='Play', state='normal', command=self.app.pyr.trigger_playback)
		self.app.bui.next_btn.config(text='Next', state='normal', command=self.app.pyr.next_song)
		self.app.bui.pause_btn.config(state='normal')
		self.app.bui.prev_btn.config(text='Prev', state='normal', command=self.app.pyr.previous_song)
		self.app.bui.playlists_btn.config(text='❌', command=self.app.bui._obliterateSelector)
		# ==========================================================================================
		# ==========================================================================================

		# ==========================================================================================
		#                                    LISTBOX
		# ==========================================================================================
		self.app.bui.listbox.bind('<Button-3>', lambda event: self.app.onRightClick(event, bag=self.app.pst.filtered_playlist, menu=self.app.bui.context_menu))
		self.app.bui.listbox.bind('<Double-Button-1>', lambda event: self.app.getSelection(self.app.playSelected))
		self.app.uiu.clear_object(self.app.bui.listbox)
		# ==========================================================================================
		# ==========================================================================================

		# ==========================================================================================
		#                                   SEARCH FEATURE
		# ==========================================================================================
		# ==========================================================================================
		# ==========================================================================================

		#<__ end of the method __>
		

#<_ END OF UIELEMENTSCONFIGURATION_>