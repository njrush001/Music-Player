import random

class StatusManager:

    def __init__(self, app) -> None:
        self.app = app

        # =========================================== UPDATED ON THE RUN
        # ------Rotation control handles/states-------
        self.bag: list[str] = []        # randomised queue of reamining msgs for this round (refilled when empty)
        self.resume_job = None          # A scheduled call that resumes rotation after a temporary override
        self.rotation_job = None        # A scheduled call that advances the tip/fact
        self.current_message = None     # Last message displayed (avoid immediade repeats on reshuffle)
        # ===========================================

        # ============================================================================================
        # --------- Messages pool (Unlimited) ---
        self.messages = [
            
            "Tip: Save Your Favourite Tracks",
            "Tip: Use Artwork To Tell The Next Song",
            "Tip: Beautiful Design, Isn't it?",
            "Tip: Use The Playlist Function To Customise Your Playlists",
            "Tip: The App Tracks Your Playstyle.",
            "Tip: The App Can Get Exciting. Take A Break Sometimes",
            "Tip: Protect Your Ears From Outside Noise",
            "Tip: Alma Music Player, One You Need While Studying",
            "Tip: Forget About The Logic Behind & Enjoy",
            "Tip: Recommend The Upgrades You Desire To See",
            "Tip: Jump And Listen Where It Strucks You The Most",
            "Tip: Seeking Communicates A Lot",
            "Tip: Your Feedback Is Always Appreciated",
            "Tip: Alma Music Player ! The Best Personal Music Player ❤",
            "Coming Soon: Change The App Theme 😘"
        ]
        # =============================================================================================

        #<__ end of the method __>

    def rgb_to_hex(self, rgb):
        '''
            This method is used to convert an (R, G, B) tuple (0-255 each) into
            a Tk-friendly hex color string
        '''
        return "#%02x%02x%02x" % rgb

        # <_end of the method_>

    def fade_text_out(self, callback):
        '''
            This method - when called - fades the current label text from white to the
            background colour, then call 'callback'.

            Visual Flow
            -----------
              a) Gradually lower contrast (white -> bg) so the swap feels smooth
              b) After the fade completes, run the callback (usually to set new text and fade in)

            Timing Knobs:
             - steps: Number of interpolation steps (higher = smoother, slower)
             - delay: ms btn steps
        '''
        steps = 10
        delay = 50
        start = (255, 255, 255)     # white
        end = (46, 46, 46)          # #2E2E2E (matches bg of self.app.bui.status label)

        #Linear interpolation from start to end over 'steps' increments
        for step in range(steps + 1):
            r = int(start[0] + (end[0] - start[0]) * step / steps)
            g = int(start[1] + (end[1] - start[1]) * step / steps)
            b = int(start[2] + (end[2] - start[2]) * step / steps)

            # Cappture the computed color per iteraation (avoid late-binding in lambda)
            self.app.bui.status_label.after(

                    step * delay,
                    lambda col=self.rgb_to_hex((r, g, b)): self.app.bui.status_label.config(fg=col)
                )
        # After the last step, perform the swap via the provided callback
        self.app.bui.status_label.after((steps + 1) * delay, callback)

        # <_end of the method_>

    def fade_text_in(self, new_text):
        '''
            Fade the label from background color (#2E2E2E) to white, after setting
            'new_text'

            Flow:
             - Seet the new text first (while it's low contrast),
             - Then ramp up to white so the reveal feels natural
        '''
        steps = 10
        delay = 50
        start = (46, 46, 46)        # Matches bg color
        end = (255, 255, 255)       # White

        self.app.uiu.updateStatusLabel(new_text)
        
        # Compute color through iteration
        for step in range(steps + 1):
            r = int(start[0] + (end[0] - start[0]) * step / steps)
            g = int(start[1] + (end[1] - start[1]) * step / steps)
            b = int(start[2] + (end[2] - start[2]) * step / steps)

            self.app.bui.status_label.after(

                    step * delay,
                    lambda col=self.rgb_to_hex((r, g, b)): self.app.bui.status_label.config(fg=col)
                )

        #<_end of the method_>

    def _refill_bag(self):
        '''
            Used to rebuild 'bag' with a freshly shuffled copy of 'messages'.
            It ensures the first pick won't duplicate the last 'current message'
            when possible (avoids back-to-back repeats across boundaries).
        '''
        # Have a defensive copy so edits to 'self.messages' won't mutate the baag mid-round
        self.bag = self.messages.copy()
        if not self.bag: # Incase there are no messages
            return # Leave bag empty (rotations handles gracefully).

        random.shuffle(self.bag)

        # Avoid immediate repeat rounds: if the first equals last shown and
        # we have alternatives, swap with a different random index.
        if self.current_message is not None and len(self.bag) > 1 and self.bag[0] == self.current_message:
            # Pick any index != 0
            swap_idx = random.randrange(1, len(self.bag))
            self.bag[0], self.bag[swap_idx] = self.bag[swap_idx], self.bag[0]

        # <_end of the method_>

    def _next_message(self):
        '''
            Pop the next msg from self.bag
            Refill and reshuffle when the bag is empty (each round shows all items at one)
        '''
        if not self.bag: # Just incase there are no messages to show
            self._refill_bag()
        # If still empty (no messages configured), return a safe placeholder
        if not self.bag: # If no messages still
            return ""

        # Else return the next message
        return self.bag.pop(0)

        # <_end of the method_>

    # -----Rotation And Overrides-----
    def rotate_status(self):
        '''
            Advance to the next randomised tip/fact (no repeats until  all are shown)
            with a fade transition, and schedule the next rotation

            Schedule:
             - Immediately: fade out current -> swap to next message -> fade in
             - After 30,000 ms: call rotaate_status() again

            Note:
             - 'self.rotation_job' is stored so temporary statuses can cancel it cleanly.
        '''

        def _show_next():
            '''
                Get a new messaage from the shuffle bag and remember it as current
            '''
            next_msg = self._next_message()
            self.current_message = next_msg
            self.fade_text_in(next_msg)

        self.fade_text_out(_show_next)
        self.rotation_job: str = self.app.root.after(30000, self.rotate_status)  # every 30 seconds

        # <_end of the method_>

    def set_status_temporary(self, msg, duration=10000):
        '''
            Temporarily override rotation with a real-time status message, then resume.

            Parameters:
              - msg:       The status text to display (e.g., "Downloaading...", "Saved...")
              - duration:  How long (ms) the override stays up b4 rotation resumes

            Behaviour:
              a) Cancel any scheduled rotation so it doesn't interleave mid-message.
              b) Cancel any pending resume timer so rapid calls.
              c) Fade out current text -> show 'msg' -> fade in
              d) After 'duration', schedule rotation to resume.

            Notes:
             - This does not modify the shuffle-self.bag; rotation resumes where it left off
             - If 'self.messages' is empty, rotation will harmlessly show an empty string
        '''
        # Stop the pending rotation (if any)
        if self.rotation_job is not None:
            self.app.root.after_cancel(self.rotation_job)
            self.rotation_job = None

        # Coalesce multiple overrides by cancelling any previous resume jobs
        if self.resume_job is not None:
            self.app.root.after_cancel(self.resume_job)
            self.resume_job = None

        self.fade_text_out(lambda: self.fade_text_in(msg))

        # Schedule a single resume after the desired duration
        self.resume_job: str = self.app.root.after(duration, self.rotate_status)
        
        #<_end of the method_>

#<_ END OF STATUSMANAGER_