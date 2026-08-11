# <============ IMPORTS ===============>
import os, random
# <====================================>

class LiveSearchUpdates:
    ''' Animates text in the search area '''
    def __init__(self, app) -> None:
        self.app = app
        self.placeholder_active: bool = True  # True if placeholder is currently visible (not real user input)

        # -- Search Hints
        self.search_hints = [

            'Search by song title...',
            'Try an artist name...',
            'Looking for a track?',
            'Search by album name...',
            'Find a song for your mood...',
            'Type a lyric you remember...',
            'Play an old favorite...',
            'Dig up a hidden gem...',
            'Music just feels right...',
            "Type if you can't find it...",
            "Drag & Drop Functional😍",
            "Add Files Using The Button Below👇",
            "Add Songs To Favoutites👇"

        ]

    def fade_out_step(self, i: int, steps: int = 10, delay: int = 10) -> None:
        '''
            Gradually fade OUT the placeholder text by lightening its color toward
            the background

             - steps: These are the no of fade increments
             - delay: delay (ms) btn each step
             - on_complete: function to call when fade-out finishes

            Start from a darker grey (100) for better contrast, then lighten
            toward white (255) over 'steps' frames.
            The range (100->255) gives a wider brightness sweep.
        '''
        # -- Build hex color string i.e., '#a0a0a0'
        fade_level: int = 100 + int((155 / steps) * i)
        colour: str = f'#{fade_level:02x}{fade_level:02x}{fade_level:02x}'

        # -- Apply new color
        self.app.uiu.show_text_colour_on(self.app.bui.search_entry, colour)

        # -- Schedule next step or fade in next hint
        if i < steps:
            # --
            self.app.bui.search_entry.after(delay, lambda: self.fade_out_step(i + 1))
        else:
            # -- Fade out is complete, Fade in next search hint
            self.fade_placeholder_in()

        #<_end of the method_>

    def fade_placeholder_out(self) -> None:
        '''
            Start the fade-out process
        '''
        self.fade_out_step(0)

        #<_end of the method_>
    
    def fade_in_step(self, i: int, steps=10, delay=30) -> None:
        '''
            Gradually fade IN placeholder text from light grey toward a darker final tone
             - text: the string to insert as the placeholder
             - steps: number of fade increments
             - delay: delay (ms) btn each steps

            Start from almost-white (255) and darken toward 100
        '''
        # -- Build hex color string
        fade_level: int = 255 - int((155 / steps) * i)
        colour: str = f'#{fade_level:02x}{fade_level:02x}{fade_level:02x}'

        # -- Apply colour
        self.app.uiu.show_text_colour_on(self.app.bui.search_entry, colour)

        # -- Schedule (if applicable)
        if i < steps:
            # --
            self.app.bui.search_entry.after(delay, lambda: self.fade_in_step(i + 1))

        #<_end of the method_>
    
    def fade_placeholder_in(self) -> None:
        '''
            Start the fade in processs
        '''
        # -- Set New Text: Not currently visible though
        self.app.bui.search_entry.delete(0, 'end')
        self.app.bui.search_entry.insert(0, random.choice(self.search_hints))

        # -- Fade in new text
        self.fade_in_step(0)

        #<_end of the method_>
    
    def _see_playlist(self, data: list) -> None:
        ''' Show results of the filtered playlist '''
        # -- Clear box
        self.app.uiu.clear_object(self.app.bui.listbox)

        # -- Insert
        self.app.root.after(
            0,
            lambda: self.app.uiu.display_paths_in(
                'main_box', 'end',
                self.app.pst.filtered_playlist
            )
        )

        #<_end of the method_>
    
    def filter_playlist_view(self, *args) -> None:
        '''
            Live filter playlist basesd on user's query (case-insensitive)
        '''
        # -- If placeholder active, don't filter
        if self.placeholder_active:
            # --
            return

        # -- Get User entry
        entry: str = self.app.bui.search_var.get().strip().lower()

        # -- Show full playlist while entry is empty
        if len(entry) < 1:
            # -- If user clears query
            self.reset_search()

            # -- Stop running this method
            return
        
        else:
            # --
            self.app.pst.filtered_playlist = [
                p for p in self.app.pst.playlist
                if entry in os.path.basename(p).lower()
            ]

        # -- Display results
        self._see_playlist(self.app.pst.filtered_playlist)

        #<_end of the method_>


class SearchController(LiveSearchUpdates):
    def __init__(self, app) -> None:
        super().__init__(app)
        # --
        self.app = app

        #<_end of the method_>

    def show_placeholder(self, text: str = '🔍 Search') -> None:
        '''
            Restore the placeholder visually.
            Used:
             - On Initialisation
        '''
        self.app.bui.search_entry.insert(0, text)

        #<_end of the method_>
    
    def hide_placeholder(self, event=None):
        '''
            Remove placeholder when entry gains focus if it's acive.
            Switch text color to black for real user input
        '''
        # -- Allow hiding only if no user input available
        if self.placeholder_active:
            # --
            self.app.bui.search_entry.delete(0, 'end')
            self.app.uiu.show_new_button_state_for(self.app.bui.clear_search_btn, 'normal')
            self.app.uiu.show_text_colour_on(self.app.bui.search_entry, 'black')

            self.placeholder_active = False

        #<_end of the method_>
    
    def restore_placeholder_if_empty(self, event=None) -> None:
        '''
            On focus loss:
             - If entry is empty, restore placeholder
             - If there's input, leave it alone
        '''
        # -- Get entry
        entry: str = self.app.bui.search_entry.get().strip()

        # --
        if len(entry) < 1:
            # -- Show new placeholder
            self.app.uiu.show_text_colour_on(self.app.bui.search_entry, 'white')
            self.fade_placeholder_in()

            # -- Reset search
            self.reset_search()

        #<_end of the method_>
    
    def cycle_default_hint(self, delay: int = 20000) -> None:
        '''
            Rotate placeholder hints every 20 sec when search is idle.
            It:
             - Runs Regardless of whether playlist is filtered or empty.
             - Skips cycling if user is actively typing (self.placeholder_active == False)
        '''
        # -- Animate if no user input
        if self.placeholder_active:
            # -- Animate
            self.fade_placeholder_out()

        # -- Schedule next animation
        self.app.bui.search_entry.after(delay, self.cycle_default_hint)

        #<_end of the method_>

    def reset_search(self, btn_trigger: bool = False) -> None:
        '''
            Show full playlist and restore placeholdere, removing focus from entry
            Also return the Index of The playing song (--- if focus was set while
            there was a playback ---)
        '''
        # -- Clear search area if btn trigger
        if btn_trigger:
            # -- Clear
            self.app.uiu.show_text_colour_on(self.app.bui.search_entry, 'white')
            self.fade_placeholder_in()

        # -- Remove focus on the search entry
        self.app.root.after(
            0,
            self.app.bui.search_frame.focus_set
        )

        # -- Fill filtered playlist
        self.app.pst.filtered_playlist = self.app.pst.playlist.copy()

        # -- USER FEEDBACK
        self._see_playlist(self.app.pst.playlist)
        self.app.uiu.show_new_button_state_for(self.app.bui.clear_search_btn, 'disabled')

        # -- Clear search area
        self.placeholder_active = True

        self.app.track_playing()

        #<_end of the method_>


#<_END OF SEARCHC0NTROLLER_>