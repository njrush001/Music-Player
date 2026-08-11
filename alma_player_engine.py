# <============ IMPORTS ===============>
import threading
import pygame, os, time
from mutagen.mp3 import MP3
from typing import Optional, Callable
# <====================================>

class PlayerEngine:
	def __init__(self, app) -> None:
		self.app = app
		# =========================================================================
		# ========================================== UPDATED ON THE RUN
		self.last_play = ''                          # Last Played Song
		self.current_song: str = ''                  # The song being played
		self.dragging: bool = False                  # Indicate if the user is currently dragging the seek knob
		self.is_paused: bool = False                 # Indicate whether we are in a paused state or in an unpaused state
		self.current_duration: int = 0               # Total duration of the 'now playing' track
		self.current_song_index: int = 0             # Pos of the song being played
		self._stopID: Optional[str] = None           # Timer to stop playback after some time delta
		self.start_time: Optional[float] = None      # Timestamp that tells the program when playback started
		self.interruptionID: Optional[str] = None    # Detect prob that would rather cause stopID to misbehave
		self.stop_play_schedule_data: Optional[dict] = None      # Holds data to help detect interruptions for stop play schedule
		# =========================================================================
		# =========================================================================

		# ---- Engine we use to play songs
		pygame.mixer.init()
		# ----
		# ---- Necessities
		self.FADE_OUT_TIME: int = 620           # Miilliseconds to fade into silence
		self.CROSSFADE_TIME: int = 2200         # Smooth start for 2.2 sec
		# ----

		# -- Data Saves
		self.data_lock = threading.Lock()

		# ==========================================================================
		# ==================================== ANONYMOUS FUNCS
		self.fade_out_song = lambda: pygame.mixer.music.fadeout(self.FADE_OUT_TIME)
		# ==========================================================================

		#<__ end of the method __>

	def ui_audio_info(self) -> None:
		''' Visual Info For The Current Audio '''
		# --- Config Fav Button Accordingly
		self.app.uiu.updateFavButton(self.current_song)
		# ---- 
		self.app.uiu.scroll_listbox()

		# --
		title, artist = self.app.uiu.extract_metadata_for_song()
	
		self.app.uiu.updateSongLabel(title)
		self.app.uiu.updateArtistLabel(artist)
		# --
		self.app.uiu.highlightCurrentPlaying()
		self.app.root.after(10, self.app.uiu.updateSongThumbnail)
		# ----

		# -- Show Next song
		threading.Thread(target=self.app.uiu.show_next_song, daemon=True).start()
		#self.app.uiu.show_next_song()

		# ---- Create new session for this song
		self.app.updateSongTimer()

		#<__ end of the method __>

	def get_audio_duration(self, path: str) -> int:
		''' Determine the len of the path passed '''
		# --- Get The Duration of the song that is about to be played
		try:
			audio = MP3(path) # Read metadata
		except Exception:
			return 0

		# -- Return the duration of this song
		return int(audio.info.length)
		# ---

		#<__ end of the method __>

	def play_song(self, start: float=0.0, fade_ms: int=0) -> None:
		'''
		Start Playback:
		 - start   : Represents the pos at which playback should be started
		 - fade_ms : Smooth start for new track
		'''
		# -- Trigger playback at the given pos: 0 by default
		pygame.mixer.music.play(start=start, fade_ms=fade_ms)

		#<_end of the method_>

	def get_last_play(self):
		'''
		Initiate Display of a label that requests the user to
		play the last played song from the last known position
		'''
		# -- Check if last_played is available
		if not self.app.sgm.player_data['last_played_data']:
			# -- Nothing to play
			return
			
		last_played = self.app.sgm.player_data['last_played_data']['song']

		# -- Find location for this track
		self.app.lib.thread_worker_for_search([last_played], '', last_play=True)

		#<_end of the method_>

	def continue_with_last_playback(self) -> None:
		'''
		If User selects 'Ok', the program should continue playing
		the song the user was playing before the program was closed.
		'''
		# -- Remove cmd from lst_btn
		self.app.uec.give_cmd(self.app.bui.lst_btn, '✅', None)

		# -- Get last played data
		played_duration: float = self.app.sgm.player_data['last_played_data']['progress_ratio']
		song_full_length: int = self.app.sgm.player_data['last_played_data']['song_length']

		# -- 
		start_pos = played_duration * song_full_length
		elapsed = time.time() - start_pos
		# -- Set start time
		self.start_time = elapsed

		self.current_song = self.last_play
		self.current_duration = song_full_length
		self.current_song_index = 0

		# -- Display File
		self.app.pst.select_files_to_add([self.last_play], randomise_paths=True)

		# -- Load and Initiate playback
		pygame.mixer.music.load(self.current_song)

		self.play_song(
			start=start_pos,
			fade_ms=self.CROSSFADE_TIME
		)

		self.app.on_startup = False

		# -- Display current playing's ui info
		self.app.root.after(
			0,
			self.ui_audio_info
		)

		# -- Cancel The schedule for destroying the frame
		self.app.root.after_cancel(self.app.uiu._dest_job)

		# -- Destroy the last_played_ui after 3 sec
		self.app.root.after(3000, lambda: self.app.bui.lst_played_frm.destroy())

		#<_end of the method_>

	def play_next(self, pos: Optional[int] = None) -> None:
		''' Set a song to be played next '''
		# -- Get playback state
		state: str = self.app.sgm.player_data['playback_state']

		# -- Get path and basename of the selected path
		path = self.app.pst.filtered_playlist[pos]
		base: str = os.path.basename(path)

		# -- Return if state or song doesn't apply
		if state == 'repeat_one' or path == self.current_song:
			# -- Any of this condition quits the method
			self.app.uiu.updateStatusLabel('Current Song Or Playback State Does Not Support This Feature!')
			# -- Quit
			return

		else:
			# -- Selected song is applicable for schedule: Schedule depending on the state

			# ==========================================================================
			# ==========================================================================
			def get_next_song_in_playlist() -> None:
				''' Set selected as next song using playlist '''
				# -- Get position of the previous song
				remove_pos: int = self.app.pst.playlist.index(path)

				# -- Remove obj at remove_pos & pos
				self.app.pst.playlist.pop(remove_pos)
				self.app.pst.song_names.pop(remove_pos)

				# -- Get Insertion Idx
				insertion_idx: int = (self.current_song_index + 1) % len(self.app.pst.playlist)

				# -- If remove_pos < self.current_song_idx; Decrease self.current_song_idx by 1
				if remove_pos < self.current_song_index:
					# -- Decrease current playing's pos
					self.current_song_index = (self.current_song_index - 1) % len(self.app.pst.playlist)

					# -- Get insertion_idx and box_idx under this condition
					insertion_idx: int = (self.current_song_index + 1) % len(self.app.pst.playlist)

					# -- Prevent weird highlights when next song plays
					self.app.uiu.prev_index = self.current_song_index


				# -- Insert obj to loop all pst first
				self.app.pst.playlist.insert(insertion_idx, path)
				self.app.pst.song_names.insert(insertion_idx, base)

				# -- Consider the situation b4 interfering with ft_pst
				if self.app.sch.placeholder_active:
					# -- User is not searching: filtered playlist should be the same as the master playlist
					self.app.pst.filtered_playlist = self.app.pst.playlist.copy()
					# -- Remove obj from listbox
					self.app.uiu.removeItemfromListbox(remove_pos)

					# -- Insert the obj to bags & listbox at the insertion_idx
					self.app.uiu.display_paths_in('main_box', insertion_idx, [path])
				else:
					# -- User is searching: No need to interfere with ft_pst
					pass

				#<_end of inner function_>
			# ==========================================================================
			# ==========================================================================
			def get_next_song_in_shuffleBag() -> None:
				''' Set selected as next song using shuffle_bag '''
				try:
					# -- Shuffle bags may not be filled
					remove_pos: int = self.app.pst.shuffle_bag.index(path)
				except ValueError:
					# -- Inititate randomisation
					self.app.pst.shuffle_mode_idx('randomise', '')

					# -- Get remove_pos now
					remove_pos: int = self.app.pst.shuffle_bag.index(path)

				# -- Get pos of the currently playing
				curr_pos: int = self.app.pst.shuffle_bag.index(self.current_song)

				# -- If remove_pos is lesser than curr_pos;  Decrease curr_pos
				if remove_pos < curr_pos:
					# -- Decrease curr_pos by 1
					curr_pos = (curr_pos - 1) % len(self.app.pst.shuffle_bag)

				# -- Remove obj at remove_pos
				self.app.pst.shuffle_bag.pop(remove_pos)
				self.app.pst.shuffle_bag_names.pop(remove_pos)

				# -- Get Insertion idx
				insertion_idx: int = (curr_pos + 1) % len(self.app.pst.shuffle_bag)

				# -- Insert path at insertion_idx
				self.app.pst.shuffle_bag.insert(insertion_idx, path)
				self.app.pst.shuffle_bag_names.insert(insertion_idx, base)

				#<_end of inner function_>
			# ==========================================================================
			# ==========================================================================

			if state == 'repeat_all':
				# --- Loop All State
				get_next_song_in_playlist()
				# --
			else:
				# -- Shuffle mode state
				get_next_song_in_shuffleBag()
			
			# -- Change next song label
			self.app.root.after(
				10,
				lambda: self.app.uiu.update_individual_label(

					self.app.bui.next_artwork_label,
					self.app.uiu.extractAlbumArt(path),
					(115, 115),
					'next_label'
				)
			)

			# -- Display Next song
			self.app.uiu.show_next_song()

		#<_end of the method_>

	def trigger_playback(self, fade_in: bool=False) -> None:
		''' Start Playback '''
		# ---- Guard: Ensure there is sth to play
		if not self.app.pst.playlist:
			# -- Nothing to to play
			return
		# ----
		# ---- Locate the path to load and play
		try:
			self.current_song: str = self.app.pst.playlist[self.current_song_index]
		except Exception:
			self.current_song_index = 0
			self.current_song = self.app.pst.playlist[self.current_song_index]
		# ----
		# ---- Get audio Info & Partition progress bar
		self.current_duration: int = self.get_audio_duration(self.current_song)
		# ----
		# ---- Load & Start & Playback
		pygame.mixer.music.load(self.current_song)
		self.play_song(fade_ms=self.CROSSFADE_TIME)
		# ----
		# -- Set start time
		self.start_time = time.time()

		# ---- Unmute if in muted state
		if self.is_paused:
			self.unpause_song()
		# ----
		self.app.on_startup = False # On search & reset, allow HIGHLIGHT

		# --- Update Current Playing Song In All Other Classes --
		self.app.fvs.new_fav_path = self.current_song
		self.app.fvs.current_fav_path = self.current_song
		self.app.pst.available_song = self.current_song   # Mainly used to track playing song
		# -------------------------      ------------------------

		# ---- Update audio info for UI
		self.ui_audio_info()
		# ----

		#<__ end of the method __>

	def pause_song(self) -> None:
		''' Pause the current song with a smooth fade-out '''
		# =========================================================================
		# ================================== FADE ANIMATIONS SETTINGS
		FADE_MS: int = 700                   # Total duration of fade animation in ms
		INTERVAL: int = 50                   # How often to step the fade (ms btn adjustments)
		steps = max(1, FADE_MS // INTERVAL)  # No. of small increments to perform during fade
		# =========================================================================
		if not pygame.mixer.music.get_busy():
			# No song is playing
			return  # Nothing to pause

		# ---- Determine hhow much to decrease volume per step
		delta: float = self.app.sgm.player_data['saved_volume'] / steps

		# =========================================================================
		# =========================================================================

		def fade_out_step(vol: float) -> None:
			'''
			Handle a single fade-out step. This function will repeatedly calll
			itself until vol approaches near 0x, then finalise the pause
			'''
			next_v: float = vol - delta
			if next_v > 0.01:
				# --- Lower volume and schedule another decrement
				pygame.mixer.music.set_volume(max(0.0, next_v))
				self.app.root.after(INTERVAL, lambda: fade_out_step(next_v))
				# ---
			else:
				# --- Finalise the pause, enable pause btn & Config pause btn
				pygame.mixer.music.pause()
				# -- Get Pause Time
				self.pause_time = time.time()
				pygame.mixer.music.set_volume(0.0)
				self.app.uiu.show_new_button_state_for(self.app.bui.pause_btn, 'normal')
				self.app.uec.give_cmd(self.app.bui.pause_btn, 'Resume', lambda: self.unpause_song(reset_start_time=True))
				# ---

				# --- Program In paused state
				self.is_paused = True
				# ---

			#<__ end of inner function __>
		# =========================================================================
		# =========================================================================

		# --- Disable pause_btn until pause is finalised
		self.app.uiu.show_new_button_state_for(self.app.bui.pause_btn, 'disabled')
		# ---

		# --- kick off the fade_out animation
		fade_out_step(self.app.sgm.player_data['saved_volume'])

		#<__ end of the method __>

	def unpause_song(self, reset_start_time: bool = False) -> None:
		''' Fade to the last volume and resume playback '''
		# =========================================================================
		# ================================== FADE ANIMATIONS SETTINGS
		FADE_MS: int = 700                   # Total duration of fade animation in ms
		INTERVAL: int = 50                   # How often to step the fade (ms btn adjustments)
		steps = max(1, FADE_MS // INTERVAL)  # No. of small increments to perform during fade
		# =========================================================================
		# --- Necessities
		delta: float = self.app.sgm.player_data['saved_volume'] / steps # Amount to increase per step
		# --- Unpause The Song & Indicate we are in unpaused stae
		pygame.mixer.music.unpause()
		#t = pause_time - self.start_time # --- elapsed

		self.is_paused = False
		# ---
		# =========================================================================
		# =========================================================================

		def fade_in_step(vol) -> None:
			'''
			Handle single fade_in step. It will repeaatedly call itself
			until the target volune is reached.
			'''
			next_v: float = vol + delta
			if next_v < self.app.sgm.player_data['saved_volume']:
				# --- Raise volume and schedule another increment
				pygame.mixer.music.set_volume(min(self.app.sgm.player_data['saved_volume'], next_v))
				self.app.root.after(INTERVAL, lambda: fade_in_step(next_v))
				# ---
			else:
				# --- Finalise the fade, enable pause btn
				pygame.mixer.music.set_volume(self.app.sgm.player_data['saved_volume'])
				# --- Finalise the pause, enable pause btn & Config pause btn
				self.app.uiu.show_new_button_state_for(self.app.bui.pause_btn, 'normal')
				self.app.uec.give_cmd(self.app.bui.pause_btn, 'Pause', self.pause_song)
				# ---
			
			#<__ end of inner function __>
		# =========================================================================
		# =========================================================================

		# --- Disable pause_btn until pause is finalised
		self.app.uiu.show_new_button_state_for(self.app.bui.pause_btn, 'disabled')
		# ---

		# --- kick off the fade_out animation fromm silence
		fade_in_step(0.0)

		# --- Update song timer if _job is None
		if reset_start_time:
			# -- Shows that since the user paused, no other song has played
			self.start_time = (time.time() - self.pause_time) + self.start_time

			# -- Continue Session Foor Current Song
			self.app.updateSongTimer()
		# ---

		#<__ end of the method __>

	def next_song(self, fade_in: bool=True) -> None:
		''' Advance to the next song in the playlist '''
		# --- Incase next is triggered from btns
		if not self.app.pst.playlist and not pygame.mixer.music.get_busy():
			# -- Ensure next song is applicable only when there is sth playing
			return   # Nothing to Play
		# ---
		# --- Fadeout the current playing track
		self.fade_out_song()
		# ---

		# ==========================================================================
		# ==========================================================================

		def delayed_next() -> None:
			''' Schedule next track after fade finishes '''
			# -- Get playback state
			song = self.current_song
			state: str = self.app.sgm.player_data['playback_state']

			# ===== Proceed to the next song wrt playback state
			if state == 'repeat_one':
				pass        # Stay on the same song
			elif state == 'shuffle':
				# -- Get the index of song that should play
				self.current_song_index = self.app.pst.shuffle_mode_idx(song, 1)
			else:
				# -- Get index of the song that should play
				self.current_song_index = self.app.pst.repeat_all_mode_idx(song, 1)

			# --- Initiate playback
			self.trigger_playback(fade_in=fade_in)

			#<__ end of inner function __>

		# ==========================================================================
		# ==========================================================================

		# --- Update necessitiies for the previous song
		self.app.finaliseSongSession(self.current_song)

		# --- Run delayed next after fade time
		self.app.root.after(100, delayed_next)
		# ---

		#<__ end of the method __>

	def previous_song(self, fade_in: bool=True) -> None:
		''' Advance to the next song in the playlist '''
		# --- Incase next is triggered from btns
		if not self.app.pst.playlist and not pygame.mixer.music.get_busy():
			# -- Ensure prev song is applicable only when there is sth playing
			return   # Nothing to Play
		# ---
		# --- Fadeout the current playing track
		self.fade_out_song()
		# ---

		# ==========================================================================
		# ==========================================================================

		def delayed_prev() -> None:
			''' Schedule next track after fade finishes '''
			# -- Get playback state
			song = self.current_song
			state: str = self.app.sgm.player_data['playback_state']

			# ===== Proceed to the next song wrt playback state
			if state == 'repeat_one':
				pass        # Stay on the same song
			elif state == 'shuffle':
				# -- Get the index of song that should play
				self.current_song_index = self.app.pst.shuffle_mode_idx(song, -1)
			else:
				# -- Get index of the song that should play
				self.current_song_index = self.app.pst.repeat_all_mode_idx(song, -1)

			# --- Initiate playback
			self.trigger_playback(fade_in=fade_in)

			#<__ end of inner function __>

		# ==========================================================================
		# ==========================================================================

		# --- Update necessitiies for the previous song
		self.app.finaliseSongSession(self.current_song)

		# --- Run delayed next after fade time
		self.app.root.after(100, delayed_prev)
		# ---

		#<__ end of the method __>

	#- ----- SEEK FEATURE !!!!!
	def get_time_from_x(self, x: int) -> float:
	    """
	    Convert a horizontal canvas coordinate (x-position) into
	    the corresponding playback time in seconds, respecting margins.
	    """

	    width = self.app.bui.canvas.winfo_width()
	    margin = 20  # horizontal padding on both sides
	    usable_width = width - 2 * margin

	    # Clamp x inside the bar region
	    x = max(margin, min(x, width - margin))

	    # Normalize: map margin → 0.0, (width - margin) → 1.0
	    ratio = (x - margin) / usable_width

	    return ratio * self.current_duration

	def seek_click(self, event) -> None:
	    '''
	    Handle the mouse click event on the seek bar.
	    This method calculates the playback time based on the click position,
	    updates the progress bar immediately, and prepares the waveform display
	    if available.
	    '''

	    # Convert the x-coordinate of the click into a playback time in seconds.
	    # This maps the click position proportionally to the song length.
	    t = self.get_time_from_x(event.x)

	    # Immediately update the progress bar to reflect the clicked position.
	    # This gives instant visual feedback to the user.
	    self.app.uiu.draw_progress(t)

	    # -- Remove tooltip
	    self.app.bui.tooltip.place_forget()

	    # Set the dragging flag to True.
	    # This tells the update loop not to auto-advance progress while the user is interacting.
	    self.dragging = True

	    #<_end of the method_>

	def seek_drag(self, event) -> None:
	    '''
	    Handle the mouse drag event on the seek bar.
	    This method continuously updates the progress bar position
	    as the user drags the knob across the canvas, providing
	    real-time visual feedback without committing playback yet.
	    '''

	    # Convert the current mouse x-coordinate into a playback time in seconds.
	    # This maps the drag position proportionally to the song length.
	    t = self.get_time_from_x(event.x)


	    # Update the progress bar and knob position to reflect the dragged location.
	    # This gives the user immediate visual feedback as they scrub through the track.
	    # Note: playback itself is not changed here — that happens in seek_release().
	    self.app.uiu.draw_progress(t)

	    #<_end of the method_>

	def seek_release(self, event) -> None:
	    '''
	    Handle the mouse release event on the seek bar.
	    This method commits the playback jump to the new position
	    after the user finishes dragging, resets timing state,
	    and fades out the waveform visualization for a polished UX.
	    '''
	    # Reset the dragging flag to False.
	    # This signals that user interaction has ended, allowing the update loop
	    # to resume automatic progress bar updates.
	    self.dragging = False

	    # -- Guard
	    if not self.current_duration and not self.current_song:
	    	return
	    # --
	    # -- Get ti after showing tooltip
	    # Convert the release x-coordinate into a playback time in seconds.
	    # This determines the exact point in the track where playback should resume.
	    t = self.app.uiu.show_tooltip(event)

	    # Restart playback from the calculated position.
	    # 'start=t' tells pygame.mixer.music to begin at the new timestamp.
	    self.play_song(start=t)
	    #pygame.mixer.music.play(start=t)

	    # Adjust the internal start_time so elapsed calculations remain accurate.
	    # Example: if you jump to 60s, start_time is shifted back so that
	    # (time.time() - start_time) correctly equals 60.
	    self.start_time = time.time() - t


	    # -- Resume Updating the time
	    self.app.updateSongTimer()

	    #<_end of the method_>


#<_ END OF PLAYERENGINE_>