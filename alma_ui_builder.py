import tkinter as tk
from tkinter import ttk

class BuildUI:
	''' Build The Music Player's UI '''
	def __init__(self, app) -> None:
		''' Build The Main Aplication Window '''
		# Incase we run this module on its own
		try:
			self.main = app
			self.app = app.root
			app_title = 'Alma Music Player'
		except AttributeError:
			app_title = 'Application Name Here'
			self.app = app

		# <======== MAIN APPLICATION WINDOW ELEMENTS =======>
		# <=================================================>
		self.online_label = None
		self.status_label = None
		self.lib_label = None
		self.recommendations_btn = None
		self.settings_btn = None
		self.lib_btn = None
		self.paths_btn = None
		self.fav_btn = None
		self.playlists_btn = None
		self.playback_label = None
		self.volume_label = None
		self.vol_add_btn = None
		self.vol_less_btn = None
		self.play_btn = None
		self.next_btn = None
		self.pause_btn = None
		self.prev_btn = None
		self.listbox_label = None
		self.mode_label = None
		self.mode_btn = None
		self.search_frame = None
		self.search_label = None
		self.var = None
		self.search_entry = None
		self.clear_search_btn = None
		self.listbox = None
		self.context_menu = None
		self.time_label = None
		self.progress_bar = None
		self.song_label = None
		self.artist_label = None
		self.next_label = None
		self.canvas = None
		self.tooltip = None
		self.elapsed_label = None
		self.remaining_label = None
		self.background_label = None
		# <=================================================>
		# <=================================================>

		# <================ LAST PLAYED UI =================>
		# <=================================================>
		self.lst_played_frm = None
		self.last_played_label = None
		self.lst_btn = None
		# <=================================================>
		# <=================================================>

		# <============= PLAYLIST SELECTOR UI ==============>
		# <=================================================>
		self.selector_ui = None
		self.selector_title = None
		self.create_playlist_btn = None
		self.directory_btn = None
		self.del_btn = None
		self.edit_btn = None
		self.canvas = None
		self.scrollbar = None
		# <=================================================>
		# <=================================================>

		# <================== SETTINGS UI ==================>
		# <=================================================>
		self.settings_ui = None
		self.settings_title = None
		self.folder_label = None
		self.add_fd_btn = None
		self.folders_box = None
		self.apply_btn = None
		# <=================================================>
		# <=================================================>

		# -------
		self._build_application_elements(app_title)

	def _build_application_elements(self, app_title) -> None:
		''' Build The Main Apllication Window '''

		# ===================================================================================
		# ===================================================================================
		app_frame = tk.Frame(self.app, bg='black', width=1020, height=30)
		app_frame.pack(pady=(1, 0), anchor='w', padx=0)
		app_frame.pack_propagate(False)

		# -- App Name
		app_name = tk.Label(app_frame, text=app_title, bg='black', fg='white', font=('Playfair Display Black', 12, 'bold'))
		app_name.pack(fill='both', expand=True)

		#-- Online  state
		self.online_label = tk.Label(app_frame, bg='black')
		self.online_label.place(x=910, y=5)

		status_frame = tk.Frame(self.app, bg='black', width=501, height=23)
		status_frame.place(x=2, y=32)

		self.status_label = tk.Label(status_frame, text='-', bg='black')
		self.status_label.pack(side=tk.LEFT, padx=10, fill='both', expand=True)

		# ===================================================================================
		# ===================================================================================

		lib_frame = tk.Frame(self.app, bg='black', width=515, height=23)
		lib_frame.pack(pady=1, anchor='e', padx=0)
		lib_frame.pack_propagate(False)

		self.lib_label = tk.Label(lib_frame, text='-', bg='black')
		self.lib_label.pack(side=tk.LEFT, padx=5)

		self.recommendations_btn = ttk.Button(lib_frame, text='-', width=17)
		self.recommendations_btn.pack(side=tk.RIGHT, padx=(2, 5))

		self.settings_btn = ttk.Button(lib_frame, text='-', width=5)
		self.settings_btn.pack(side=tk.RIGHT, padx=1)
		# ===================================================================================
		# ===================================================================================

		# ===================================================================================
		# ===================================================================================
		lib_accessories = tk.Frame(self.app, bg='black', width=515, height=23)
		lib_accessories.pack(pady=3, anchor='e', padx=0)
		lib_accessories.pack_propagate(False)

		self.lib_btn = ttk.Button(lib_accessories, text='-', width=20)
		self.lib_btn.pack(padx=1, side=tk.LEFT)

		self.paths_btn = ttk.Button(lib_accessories, text='-', width=20)
		self.paths_btn.pack(padx=1, side=tk.LEFT)

		self.fav_btn = ttk.Button(lib_accessories, text='-', width=20)
		self.fav_btn.pack(padx=1, side=tk.LEFT)

		self.playlists_btn = ttk.Button(lib_accessories, text='-', width=20)
		self.playlists_btn.pack(padx=1, side=tk.LEFT)
		# ===================================================================================
		# ===================================================================================

		# ===================================================================================
		# ===================================================================================
		playback_frame = tk.Frame(self.app, bg='black', width=515, height=23)
		playback_frame.pack(pady=5, anchor='e', padx=0)
		playback_frame.pack_propagate(False)

		self.playback_label = tk.Label(self.app, text='-', bg='black')
		self.playback_label.place(x=525, y=90)

		self.volume_label = tk.Label(self.app, text='-', bg='black')
		self.volume_label.place(x=805, y=90)

		self.vol_add_btn = ttk.Button(self.app, text='-', width=8)
		self.vol_add_btn.place(x=905, y=90)

		# Used to Decrease Volume
		self.vol_less_btn = ttk.Button(self.app, text='-', width=8)
		self.vol_less_btn.place(x=965, y=90)
		# ===================================================================================
		# ===================================================================================

		# ===================================================================================
		# ===================================================================================
		playback_accessories = tk.Frame(self.app, bg='black', width=515, height=23)
		playback_accessories.pack(pady=1, anchor='e', padx=0)
		playback_accessories.pack_propagate(False)

		self.play_btn = ttk.Button(playback_accessories, text='-', width=20)
		self.play_btn.pack(padx=1, side=tk.LEFT)

		self.next_btn = ttk.Button(playback_accessories, text='-', width=20)
		self.next_btn.pack(padx=1, side=tk.LEFT)

		self.pause_btn = ttk.Button(playback_accessories, text='-', width=20)
		self.pause_btn.pack(padx=1, side=tk.LEFT)

		self.prev_btn = ttk.Button(playback_accessories, text='-', width=20)
		self.prev_btn.pack(padx=1, side=tk.LEFT)
		# ===================================================================================
		# ===================================================================================

		# ===================================================================================
		# ===================================================================================
		frame_6 = tk.Frame(self.app, bg='black', width=515, height=23)
		frame_6.pack(pady=(5, 0), anchor='e', padx=0)
		frame_6.pack_propagate(False)

		self.listbox_label = tk.Label(self.app, text='-', bg='black')
		self.listbox_label.place(x=525, y=148)

		self.mode_label = tk.Label(self.app, text='-', bg='black')
		self.mode_label.place(x=925, y=148)

		self.mode_btn = ttk.Button(frame_6, text='-', width=6)
		self.mode_btn.pack(side=tk.RIGHT)

		# ===================================================================================
		# ===================================================================================
		self.search_frame = tk.Frame(self.app, bg='black', width=515, height=30)
		self.search_frame.pack(pady=(1, 0), anchor='e', padx=0)
		self.search_frame.pack_propagate(False)

		self.search_label = tk.Label(self.app, text='-', bg='black')
		self.search_label.place(x=525, y=175)

		self.search_var = tk.StringVar()
		self.search_entry = tk.Entry(self.app, width=47)
		self.search_entry.place(x=630, y=178)

		self.clear_search_btn = ttk.Button(self.app, text='-', width=15)
		self.clear_search_btn.place(x=925, y=175)

		self.listbox = tk.Listbox(self.app, bg='slategray', width=85, height=19)
		self.listbox.place(x=505, y=203)

		self.context_menu = tk.Menu(self.app, tearoff=0)
		# ===================================================================================
		# ===================================================================================

		# ===================================================================================
		# ===================================================================================
		info_frame = tk.Frame(self.app, bg='black', width=501, height=50)
		info_frame.place(x=2, y=405)
		info_frame.pack_propagate(False)

		self.song_label = tk.Label(info_frame, text='-', fg='white', bg='black', font=('Congenial', 10))
		self.song_label.pack(side=tk.TOP, anchor='w', padx=10)

		self.artist_label = tk.Label(info_frame, text='-', bg='black', fg='white')
		self.artist_label.pack(side=tk.BOTTOM, anchor='w', padx=10, pady=(0, 6))

		self.next_label = tk.Label(self.app, padx=7, wraplength=390, justify='center')
		self.next_label.place(x=30, y=365, width=440,  height=36)

		# ===================================================================================
		# ===================================================================================

		# ===================================================================================
		# ===================================================================================
		self.canvas = tk.Canvas(self.app, width=501, height=79, bg="black", highlightthickness=0)
		self.canvas.place(x=2, y=458)

		margin: int = 20
		width = 501  # same as canvas width for initial draw
		usable_width = width - (2 * margin)

		self.buffer = self.canvas.create_rectangle(margin, 38, (margin + usable_width), 42)
		#self.knob = self.canvas.create_oval(margin - 5, 33, margin + 5, 48)

		self.tooltip = tk.Label(self.app)
		self.tooltip.place_forget()

		self.elapsed_label = tk.Label(self.app, text="-", fg="slategray", bg="black")
		self.elapsed_label.place(x=27, y=510)

		self.remaining_label = tk.Label(self.app, text="-", fg="slategray", bg="black")
		self.remaining_label.place(x=457, y=510)

		# ===================================================================================
		# ===================================================================================

		#self.background_label.place(x=130, y=100)

		self.main_artwork_label = tk.Label(self.app)
		self.main_artwork_label.place(x=132, y=100)

		self.next_artwork_label = tk.Label(self.app)
		self.next_artwork_label.place(x=380, y=160)

		self.prev_artwork_label = tk.Label(self.app)
		self.prev_artwork_label.place(x=5, y=160)

		#<_end of the method_>

	def build_last_played_ui(self) -> None:
		''' Build last played ui '''
		# ===================================================================================================
		# ===================================================================================================
		self.lst_played_frm = tk.Frame(self.app, bg='black', width=450, height=23)
		self.lst_played_frm.place(x=25, y=57)

		self.last_played_label = tk.Label(self.lst_played_frm, relief='raised', width=57)
		self.last_played_label.pack(side='left', fill='x', padx=(10, 5))

		self.lst_btn = ttk.Button(self.lst_played_frm, width=4)
		self.lst_btn.pack(side='right', padx=(0, 10))
		# ===================================================================================================
		# ===================================================================================================

		#<_end of the method_>


	def playlist_selector_ui(self) -> None:
		''' Build The Playlist Selector UI '''

		self.selector_ui = tk.Frame(self.app, bg='black', width=500, height=502)
		self.selector_ui.place(x=2.2, y=32)
		self.selector_ui.pack_propagate(False)

		# ===================================================================================================
		# ===================================================================================================
		frame_1 = tk.Frame(self.selector_ui, bg='green', width=497, height=20)
		frame_1.pack(anchor='w', pady=2, padx=2)
		frame_1.pack_propagate(False)

		self.selector_title = tk.Label(frame_1)
		self.selector_title.pack(side=tk.LEFT, padx=5)
		# ===================================================================================================
		# ===================================================================================================

		# ===================================================================================================
		# ===================================================================================================
		frame_2 = tk.Frame(self.selector_ui, bg='black', width=545, height=24)
		frame_2.pack(pady=2, anchor='w', padx=4)
		frame_2.pack_propagate(False)

		self.create_playlist_btn = ttk.Button(frame_2, width=18)
		self.create_playlist_btn.pack(side=tk.LEFT, padx=(4, 6))

		self.directory_btn = ttk.Button(frame_2, width=18)
		self.directory_btn.pack(side=tk.LEFT, padx=(0, 4))

		self.del_btn = ttk.Button(frame_2, width=18)
		self.del_btn.pack(side=tk.LEFT, padx=(0, 4))

		self.edit_btn = ttk.Button(frame_2, width=18)
		self.edit_btn.pack(side=tk.LEFT, padx=(0, 4))
		# ===================================================================================================
		# ===================================================================================================

		# ===================================================================================================
		# ===================================================================================================
		canvas = tk.Canvas(self.selector_ui, bg='green', width=475, height=510, highlightthickness=0)
		canvas.pack(pady=3, side='left', expand=True)

		scrollbar = ttk.Scrollbar(self.selector_ui, orient='vertical')
		scrollbar.pack(side='right', fill='y')
		canvas.configure(yscrollcommand=scrollbar.set)

		self.sel_scroll_frame = tk.Frame(canvas, bg='green')
		canvas.create_window((0, 0), window=self.sel_scroll_frame, anchor='nw')
		#canvas_window = canvas.create_window((0, 0), window=self.sel_scroll_frame, anchor='nw')

		# Configure Extension Elements
		self.main.uec._configure_selector_elements(canvas, scrollbar)
		# ===================================================================================================
		# ===================================================================================================

		#<__ end of the method __>

	def playlist_creator_ui(self) -> None:
		''' Create the playlist selector UI '''
		# ===================================================================================================
		# ===================================================================================================
		self.apc_menu = tk.Menu(self.app, tearoff=0)
		self.main.uec._configure_creator_elements()
		# ===================================================================================================
		# ===================================================================================================

		#<__ end of the method __>

	def restore_program_settings(self):
		''' Restore previous settings '''
		# ===================================================================================================
		# ===================================================================================================
		self.apc_menu = None
		self.main.uec.restore_general_settings()
		# ===================================================================================================
		# ===================================================================================================

		#<__ end of the method __>

	def program_settings_ui(self) -> None:
		''' Build Settings UI '''
		# ===================================================================================================
		# ===================================================================================================
		# -- Frame To Hold UI elements for settings UI
		self.settings_ui = tk.Frame(self.app, bg='black', width=500, height=502)
		self.settings_ui.place(x=2.2, y=32)
		self.settings_ui.pack_propagate(False)
		# ===================================================================================================
		# ===================================================================================================

		# ===================================================================================================
		# ===================================================================================================
		frame_1 = tk.Frame(self.settings_ui, bg='black', width=497, height=20)
		frame_1.pack(anchor='w', pady=(2, 0), padx=2)
		frame_1.pack_propagate(False)

		self.settings_title = tk.Label(frame_1, bg='green')
		self.settings_title.pack(fill='x')
		# ===================================================================================================
		# ===================================================================================================

		# ===================================================================================================
		# ===================================================================================================
		self.folder_label = tk.Label(self.settings_ui, bg='black', pady=4)
		self.folder_label.pack(padx=2, pady=(5, 0), anchor='w')

		self.add_fd_btn = ttk.Button(self.settings_ui, text='-', width=15)
		self.add_fd_btn.place(x=396, y=27)

		self.folders_box = tk.Listbox(self.settings_ui, width=83, height=3)
		self.folders_box.pack(padx=2, pady=(6, 0), anchor='w')

		self.apply_btn = ttk.Button(self.settings_ui, text='-', width=15)
		self.apply_btn.place(x=396, y=128)
		# ===================================================================================================
		# ===================================================================================================

		# -- Configure
		self.main.uec._configure_settings_elements()
		
		#<_end of the method_>

	def _obliterateSelector(self):
		''' Destroy The Selector Window '''
		# ===================================================================================================
		self.selector_ui.destroy()
		self.main.uec.give_cmd(self.playlists_btn, 'Playlist', self.playlist_selector_ui)
		# ===================================================================================================
		
		#<__ end of the method __>

	def _obliterateSettings(self):
		''' Destroy The Settings Window '''
		# ===================================================================================================
		self.settings_ui.destroy()
		self.settings_ui = None
		self.main.sgm.updates = self.main.sgm.data_bag.copy()
		self.main.uec.give_cmd(self.settings_btn, '⚙', self.program_settings_ui)
		# ===================================================================================================

		#<_end of the method_>

if __name__ == '__main__':
	# ======================================================================================
	# ======================================================================================
	app = tk.Tk()
	app.title('MUSIC PLAYER INTERFACE')          # Window Name
	app.geometry('1020x540')                     # width(1020 pixels) x height(540 pixels)
	app.resizable(False, False)                  # The window size should not be resizable
	app.configure(bg='olive')                    # Background colour will be black
	# ======================================================================================
	# ======================================================================================

	window = BuildUI(app)
	app.mainloop()