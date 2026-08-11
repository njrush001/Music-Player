# <============ IMPORTS ===============>
import os, io
from typing import Optional
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL import Image, ImageTk
from config import AlmaDataPaths
from mutagen.easyid3 import EasyID3
# <====================================>

class UIUpdates:
	def __init__(self, app) -> None:
		self.app = app

		# ==========================================================================
		# =============================================== UPDATED ON THE RUN
		#self.waveform = []                           # Precomputed list of normalised amplitude values from the audio samples.
		#self.waveform_items = []                     # Canvas item IDs for each drawn waveform line.
		self._animejob = None                         # Used in animating nest song label
		self.progress_img = None                      # used as a reference to the PhotoImage object created by create_gradient
		self.progress_item = None                     # stores the canvas item ID returned by create image
		self.current_progress = 0                     # smoothed progress value (a blend of old and new value)
		self.next_song: Optional[str] = None          # Indicates the next song that will be played
		self.prev_index: Optional[int] = None         # Index of the previous song
		# ==========================================================================
		# ==========================================================================

		# -- Default background picture
		self.bg_img = AlmaDataPaths.BG_DIR / 'alma_bgd.png'

		#<__ end of the method __>
	
	'''
		ORDER OF DEEFINED METHODS
		-------------------------
		Dependencies
		============
		 . clean_title

		 Category 1
		 ==========
		- Updates to;
			. time_label
		    . status_label
			. volume_label
			. song_label & artist_label
			. _text_to_show
			. displayPlaybackState
			. next_label
			. show_text_on
		
		Category 2
		==========
		- Updates to the listbox
			. scroll_listbox
		    . display_paths_in
			. remeoveItemfromListbox
			. clear_object
			. highlightCurrentPlaying
		
		Category 3
		==========
		- Updates to the background_label
			. setBackground
			. crossfadeImages
		    . extractAlbumart
			. updateSongThumbnail
		
		Category 4
		==========
		- Other Updates;
		    . show_last_playback_prompt
			. show_new_button_state_for
			. updateFavButton
			. extract_metadata_for_song
		
		Category 5
		==========
		- Updates to the canvas that shows song progress
		    . create_gradient
			. draw_progress
			. show_tooltip
	'''

	# ========= DEPENDENCIES

	def clean_title(self, path, max_lmt: int = 55, max_show: int = 53) -> str:
		''' Return a song name to be displayed in the UI '''
		base: str = os.path.basename(path)
		clean_base: str = base.replace('.mp3', '').title()

		# --- Characters should not exceed max_lmt
		if len(clean_base) > max_lmt:
			# -- Return max_show of specified characters
			return clean_base[:max_show] + ' ...'
		
		return clean_base

		#<_end of the method_>

	# ====================================================================================
	# ====================================================================================
	# ====================================================================================
	# =================================== Cate. 1 ========================================

	def updateTimeLabel(self, label, time: str) -> None:
		'''
		Update both;
		 - elapsed_label &
		 - remaining label
		'''
		try:
			# -- Display time
			self.app.root.after(0, lambda: label.config(text=time))
		except Exception:
			pass

		#<_end of the method_>

	def updateStatusLabel(self, text: str) -> None:
		''' Display a feedback '''
		try:
			# -- Config status label to display the new text
			self.app.root.after(0, lambda: self.app.bui.status_label.config(text=text))
		except Exception:
			pass

		#<__ end of the method __>

	def updateVolumeLabel(self, vol: str) -> None:
		''' Display the current volume percentage '''
		try:
			# -- Show Volume
			self.app.root.after(0, lambda: self.app.bui.volume_label.config(text=vol))
		except Exception:
			pass

		#<_end of the method_>

	def updateSongLabel(self, title: str) -> None:
		''' Display the name of the current playing song '''
		try:
			# -- Show the song name
			self.app.root.after(0, lambda: self.app.bui.song_label.config(text=title))
		except Exception:
			pass

		#<_end of the method_>
	
	def updateArtistLabel(self, artist: str) -> None:
		''' Display the artist of the current song '''
		try:
			# -- Show artist name
			self.app.root.after(0, lambda: self.app.bui.artist_label.config(text=artist))
		except Exception:
			pass

		#<_end of the method_>
	
	def _text_to_show(self) -> str:
		''' Determine Text representing the current playback state '''
		# --- Determine state
		state: str = self.app.sgm.player_data['playback_state'].replace('_', ' ')

		# --- Determine what to display
		if state == 'repeat all':
			# -- Text should be loop all icon
			return '🔁'
		elif state == 'repeat one':
			# -- Text should be loop one icon
			return  '🔂'
		else:
			# -- State is at shuffle mode
			return  '🔀'

		#<_end of the method_>
		
	def displayPlaybackState(self) -> None:
		''' Display the current playback state '''
		try:
			# --- Display the current playback state
			self.app.root.after(0, self.app.bui.mode_btn.config(text=self._text_to_show()))
		except Exception:
			pass

		#<__ end of the method __>
	
	def show_next_song(self, next_song=None) -> None:
		''' Display the song that would be played next '''
		# -- Get Next Song if not given
		if not next_song:
			# -- Get next song
			self.next_song = self.app.pst.get_next_or_previous_song(value=1)
		else:
			# -- Next song is the passed one
			self.next_song = next_song
		
		# --- Get displayable title
		title: str = 'Up Next: ' + self.clean_title(self.next_song)

		# -- Display
		self.show_text_on(self.app.bui.next_label, title)

		#<_end of the method_>
	
	def show_text_on(self, object, text: str) -> None:
		''' Show the text on the passed object '''
		try:
			# -- Show text
			self.app.root.after(0, lambda: object.config(text=text))
		except Exception:
			pass

		#<_end of the method_>

	def show_text_colour_on(self, object, colour: str) -> None:
		''' Show the new color of text on the passed object '''
		try:
			# -- Show text
			self.app.root.after(0, lambda: object.config(fg=colour))
		except Exception:
			pass

		#<_end of the method_>
	
	# ====================================================================================
	# ====================================================================================
	# ====================================================================================
	# =================================== Cate. 2 ========================================

	def scroll_listbox(self):
		''' See the Currently Playing Track Name in Listbox '''
		try:
			# -- Scroll listbox
			self.app.root.after(
				100,
				lambda: self.app.bui.listbox.see(self.app.pyr.current_song_index)
			)
		except Exception:
			pass

		#<_end of the method_>
	
	def display_paths_in(self, box: str, insertion_idx, paths: list) -> None:
		'''`
		Display the passed items in the specified box:

		 - Specifications:
		   . main_box -> Implies the box where user can view loaded tracks
		   . sett_box -> Settings box. Mainly used to view saved folders
		'''
		# -- Determine the type of box
		if box == 'main_box':
			# -- Insert items in the main listbox
			for p in paths:
				# -- Get Basename
				base: str = os.path.basename(p)
				clean_base: str = base.replace('.mp3', '')

				# -- Display favourites with a star
				if base in self.app.pst.favs:
					# -- Implies the song in favourites
					clean_base = '✨' + clean_base # -- Clean Visual

				# -- Display the track name
				self.app.bui.listbox.insert(insertion_idx, clean_base)

		elif box == 'sett_box':
			# -- User's folders are required
			for p in paths:
				# --
				self.app.bui.folders_box.insert(insertion_idx, p)

		#<_end of the method_>

	def removeItemfromListbox(self, pos: int) -> None:
		''' Remove Item From The Listbox '''
		try:
			# -- Remove  from listbox
			self.app.root.after(0, lambda: self.app.bui.listbox.delete(pos))
		except Exception:
			pass

		#<_end of the method_>

	def clear_object(self, object) -> None:
		''' Clear Everything from the listbox '''
		try:
			# -- Clear everything from the passed box
			self.app.root.after(0, lambda: object.delete(0, 'end'))
		except Exception:
			pass

		#<_end of the method_>

	def highlightCurrentPlaying(self) -> None:
		''' Display a highlight on the current playing song '''
		# --- Reset previous highlight
		try:
			# --- If on startup, this block might fail
			self.app.bui.listbox.itemconfig(self.prev_index, {'bg': 'slategray', 'fg': 'black'})
		except Exception:
			# --- Highlight current playing instead
			pass
		# ---

		# --- Try highlighting the current playing song
		try:
			# --- Highlight current playing
			self.app.bui.listbox.itemconfig(self.app.pyr.current_song_index, {'bg': 'grey', 'fg': 'white'})
			# --- Match prev index to the current idx
			self.prev_index = self.app.pyr.current_song_index
		except Exception:
			# --- User could be creating some playlist. No need to highlight
			pass
		# ----

		#<__ end of the method __>

	# ====================================================================================
	# ====================================================================================
	# ====================================================================================
	# =================================== Cate. 3 ========================================

	def setBackground(self, main_img=None, next_img=None, prev_img=None) -> None:
		''' Display default background or artwork for song if available '''
		_labels = {
			self.app.bui.main_artwork_label: (main_img, (235, 235)),
			self.app.bui.next_artwork_label: (next_img, (115, 115)),
			self.app.bui.prev_artwork_label: (prev_img, (115, 115))
		}

		# ==================================================================
		# ==================================================================
		def _get_photo(img, size: tuple[int, int]) -> ImageTk.PhotoImage:
			''' Open an image and resize it '''
			# -- Open image and resize to fit
			_image = Image.open(img).resize(size)
			_photo = ImageTk.PhotoImage(_image)
			# --

			return _photo

			#<_end of inner function_>
		# ==================================================================
		# ==================================================================

		for label, (_img, size) in _labels.items():
			# --  If image is None: Continue
			if _img is None:
				continue
			# --
			# -- Get image and photo
			_photo = _get_photo(_img, size)
			# --
			try:
				# -- Update thumbnail
				label.config(image=_photo)
				label.image = _photo
				# --
			except Exception:
				pass

		#<__ end of the method __>

	def crossfadeImages(self, old, new, label, size: tuple[int, int]) -> None:
		'''
		Display a smooth transition from one image to another:
		 - Old: previous img for particular label
		 - new: new img for this label
		 - label: label to be updated
		'''
		# ==========================================
		# =======----- Crossfade animations settings
		steps: int = 5
		delay: int = 13
		old = old.resize(size).convert('RGBA')
		new = new.resize(size).convert('RGBA')
		# =================       =================

		# ==========================================================================
		# ==========================================================================

		def _step(i: float) -> None:
			''' Blend old with new image with steps '''
			# --- Determine if crossfade is complete
			if i > steps:
				# --- Crossfade already complete
				return

			# --- Continue crossfade with a lil step
			alpha: float = i / steps
			blended = Image.blend(old, new, alpha)
			photo = ImageTk.PhotoImage(blended)
			# --- Update this step in the background label
			label.config(image=photo)
			label.image = photo
			# --- This is a Complete step

			# -- Make this a repetitive loop til blending is complete
			self.app.root.after(delay, lambda: _step(i + 1))

			#<__ end of inner function __>

		# ==========================================================================
		# ==========================================================================

		# --- Crossfade smoothly
		_step(0)

		#<__ end of the method __>

	def extractAlbumArt(self, path: str):
		''' Extract the thumbnail of the current playing '''
		try:
			audio = ID3(path)
			for tag in audio.values():
				if tag.FrameID == 'APIC':
					img = Image.open(io.BytesIO(tag.data)).resize((235, 235))

					# -- Return the img
					return img

		except Exception:
			# --- Such songs do not start with an ID3 Tag
			pass

		# --- Return None Value
		return None

		#<__ end of the method __>
	
	def _get_all_artworks(self) -> dict:
		''' Get artwork for main, next & prev artwork labels '''
		# -- Get next and previous song
		_main = self.app.pyr.current_song
		_next = self.app.pst.get_next_or_previous_song(value=1)
		_prev = self.app.pst.get_next_or_previous_song(value=-1)

		# -- Get required artwork
		_main_img = self.extractAlbumArt(_main)
		_next_img = self.extractAlbumArt(_next)
		_prev_img = self.extractAlbumArt(_prev)

		_img_data: dict = {
			self.app.bui.main_artwork_label: (_main_img, (235, 235), 'main_label'),
			self.app.bui.next_artwork_label: (_next_img, (115, 115), 'next_label'),
			self.app.bui.prev_artwork_label: (_prev_img, (115, 115), 'prev_label')
		}

		return _img_data

		#<_end of the method_>
	
	def update_individual_label(self, label, img, size, type) -> None:
		''' Update the individual label using the given image '''
		# -- If img is None display default background artwork
		if img is None:
			# -- Get the reference label image
			if type == 'main_label':
				func = lambda img: self.setBackground(main_img=img)
			elif type == 'next_label':
				func = lambda img: self.setBackground(next_img=img)
			elif type == 'prev_label':
				func = lambda img: self.setBackground(prev_img=img)
			
			func(self.bg_img)

		elif img:
			# -- Crossfade Images
			# --- Get embeded img and blend it with new img
			current_img = ImageTk.getimage(label.image).convert('RGBA')
			self.crossfadeImages(current_img, img, label, size)

		#<_end of the method_>

	def updateSongThumbnail(self) -> None:
		''' Update The artwork for the current playing '''
		# --- Pull embeded cover arts if available
		img_data: dict = self._get_all_artworks()

		# --- Embed the thumbnail if availbale
		for _label, (_img, size, _type) in img_data.items():
			# -- Update Individually
			self.update_individual_label(_label, _img, size, _type)

		#<__ end of the method __>

	# ====================================================================================
	# ====================================================================================
	# ====================================================================================
	# =================================== Cate. 4 ========================================

	def show_last_playback_prompt(self, last_played: str) -> None:
		''' Display the prompt the user to play last known playback '''
		# -- Format visible
		visible: str = 'Continue: ' + last_played[:55].replace('.mp3', '')

		# -- Build & Config UI for last playback
		self.app.bui.build_last_played_ui()
		self.app.uec._configure_last_played_ui(visible)

		# -- Schedule to destroy this UI if no  response from the user
		self._dest_job = self.app.root.after(7000, lambda: self.app.bui.lst_played_frm.destroy())

		#<_end of the method_>

	def show_new_button_state_for(self, btn, state: str) -> None:
		'''
		Show new state of a button:
		 - If the state arg == 'disabled', disable the button
		 - and vice versa.
		'''
		try:
			# -- Change state to the required one
			self.app.root.after(0, lambda: btn.config(state=state))
		except Exception:
			pass

		#<_end of the method_>

	def updateFavButton(self, path) -> None:
		''' Toggle the fav button wrt current playing '''
		# -- Get Basenames
		name: str = os.path.basename(path)

		if name in self.app.pst.favs:
			# --- Toggle fav btn to remove_from_fav if clicked
			self.app.uec.give_cmd(self.app.bui.fav_btn, 'Remove Fav', self.app.fvs.remove_from_favourites)

			return # Exit
		# -- Otherwise config to add to favourites when clicked
		self.app.uec.give_cmd(self.app.bui.fav_btn, 'Add Fav', self.app.fvs.add_to_favourites)

		#<__ end of the method __>

	def extract_metadata_for_song(self) -> tuple[str]:
		'''
		Extract the following info from a track
		 - Song's Title
		 - Song's Artist
		'''
		audio = MP3(self.app.pyr.current_song, ID3=EasyID3)

		# -- Get title and artist (if available)
		title: str = audio.get('title', 'Unknown Title')
		artist: str = audio.get('artist', 'Unknown Artist')
		# --

		# ========================== Check Availability
		# ==========================
		if title == 'Unknown Title':
			# -- Use Basename
			title: str = self.app.pyr.current_song
		else:
			title: str = title[0]
		
		if artist == 'Unknown Artist':
			# -- Use App owner name
			artist: str = 'Alma'
		else:
			# -- Artist Name Found
			artist: str = artist[0]
		# ==========================
		# ==========================
		
		# -- Clean Title
		clean_title: str = self.clean_title(title, max_lmt=52, max_show=48)

		return clean_title, artist

		#<_end of the method_>

	# ====================================================================================
	# ====================================================================================
	# ====================================================================================
	# =================================== Cate. 5 ========================================

	def create_gradient(self, width, height, start_color, end_color) -> ImageTk.PhotoImage:
		''' Create Gradient '''

		# Create a base image filled entirely with the start_color.
		# This acts as the "background" of the gradient.
		base = Image.new("RGB", (width, height), start_color)

		# Create another image filled with the end_color.
		# This will be blended on top of the base using a mask.
		top = Image.new("RGB", (width, height), end_color)

		# Create a mask image in "L" mode (grayscale, 0–255 values).
		# This mask controls how much of 'top' is visible at each pixel.
		mask = Image.new("L", (width, height))

		# Fill the mask with a horizontal gradient from black (0) to white (255).
		# For each x position across the width:
		# - At x=0, value = 0 → only start_color shows.
		# - At x=width, value = 255 → only end_color shows.
		for x in range(width):
			mask.putpixel((x, 0), int(255 * (x / width)))
			# Note: only the first row is set here.
			# The mask will be resized to fill the full height below.

		# Resize the mask to cover the full height of the image.
		# This duplicates the gradient row vertically, so the gradient
		# spans the entire rectangle height.
		mask = mask.resize((width, height))

		# Paste the 'top' image onto the 'base' using the mask.
		# Where mask=0 → only base (start_color) is visible.
		# Where mask=255 → only top (end_color) is visible.
		# Values in between blend the two colors smoothly.
		base.paste(top, (0, 0), mask)

		# Convert the final PIL image into a Tkinter-compatible PhotoImage.
		# This allows it to be displayed on a Canvas.
		return ImageTk.PhotoImage(base)

	   	#<_end of the method_>

	def draw_progress(self, value: float) -> None:
		'''
		Update the seek bar visualization (buffer fill, gradient progress bar, and knob position)
		based on the current playback time.
		'''

		# Get the current width of the canvas (seek bar).
		# This ensures the progress bar scales correctly if the window is resized.
		width = self.app.bui.canvas.winfo_width()

		# --- BUFFER BAR ---
		#buffer_ratio: float = 1.0
		# Draw the "buffered" portion of the track (e.g., preloaded audio).
		# Here it's hardcoded to 70% of the track width for demonstration.
		#self.app.bui.canvas.coords(self.app.bui.buffer, 20, 38, width - 20, 42)

		# --- PROGRESS CALCULATION ---
		# Calculate playback progress as a ratio of song length.
		# If song_length is 0 (no song loaded), default to 0.
		progress = value / self.app.pyr.current_duration if self.app.pyr.current_duration else 0
		prog_width = int(width * progress)  # Convert ratio into pixel width.
		prog_width = max(1, min(prog_width, width))

		margin: int = 20 # Horizontal padding

		# --- PROGRESS BAR (GRADIENT) ---
		if prog_width > 0:
			# -- Scale progress width to exclude margins
			usable_width = width - (2 * margin)
			scaled_width = int(usable_width * progress)
			# Create a gradient image representing the progress bar fill.
			gradient = self.create_gradient(
				scaled_width, 4, (30, 220, 96), (30, 180, 220)
			)

			# If a previous progress image exists, delete it to avoid overlap.
			if self.progress_item:
				self.app.bui.canvas.delete(self.progress_item)

			# Draw the new gradient image at the left edge of the seek bar.
			self.progress_item = self.app.bui.canvas.create_image(
				margin, 40, anchor="w", image=gradient
	        )

			# Keep a reference to the PhotoImage object.
			# Without this, Tkinter may garbage-collect the image and it won't display.
			self.progress_img = gradient

		# --- KNOB POSITION ---
		# Calculate the knob's x-position based on playback progress.
		#knob_x = margin + (width - (2 * margin)) * progress

		# Update knob coordinates so it moves along the seek bar.
		# The knob is drawn as a small oval centered at knob_x.
		#self.app.bui.canvas.coords(self.app.bui.knob, knob_x - 6, 32, knob_x + 6, 48)

	    #<_end of the method_>

	def show_tooltip(self, event) -> None:
		"""
		Display a tooltip above the seek bar showing the timestamp
		corresponding to the current mouse position.
		"""
		width = self.app.bui.canvas.winfo_width()
		margin = 20  # same margin used for seek bar

		# Convert mouse x → playback time
		t = self.app.pyr.get_time_from_x(event.x)
		mins, secs = divmod(int(t), 60)

		# Update tooltip text
		self.app.bui.tooltip.config(text=f'{mins}:{secs:02d}')

		# Default offset: place tooltip to the right of cursor
		offset = 20
		tooltip_width = self.app.bui.tooltip.winfo_reqwidth()

		# If placing to the right would overflow canvas, flip to left
		if event.x + offset + tooltip_width > width - margin:
			x_pos = event.x - offset - tooltip_width
		else:
			x_pos = event.x + offset

		# Place tooltip vertically aligned with canvas
		self.app.bui.tooltip.place(x=x_pos, y=self.app.bui.canvas.winfo_y())

		return t

		#<_end of the method_>



#<_ END OF UIUPDATES>