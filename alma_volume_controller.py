import pygame

class VolumeController:

    def __init__(self, app) -> None:
        self.app = app

        #<__ end of the method __>

    def set_volume(self, v) -> None:
        '''
            Takes the value 'v' (string or float), update the mixer volume, and
            refresh the label to display new volume perceentage
        '''
        pygame.mixer.music.set_volume(v) # Set th eplayback volume btn (0.0 - 1.0)

        # Safeguard
        if v >= 0.98:
            return

        elif v <= 0:
            return
        # -- Display current volume
        self.app.uiu.updateVolumeLabel(f"Volume: {int(v*100)}%") # Refresh the label text
        self.app.sgm.player_data['saved_volume'] = v

        #<_end of the method_>

    def increase_volume(self) -> None:
        ''' Increase Volume '''
        v = float(self.app.sgm.player_data['saved_volume']) + 0.02 # Ensure incomin gvalue is a float (Scale may pass a string)
        self.set_volume(v)

        #<__ end of the method __>

    def decrease_volume(self) -> None:
        ''' Decrease Volume '''
        v = float(self.app.sgm.player_data['saved_volume']) - 0.02  # Ensure incomin gvalue is a float (Scale may pass a string)
        self.set_volume(v)

        #<__ end of the method __>


#<_ END OF VOLUMECONTROLLER _>