# <============ IMPORTS ===============>
import requests, threading
from requests.exceptions import ConnectionError, Timeout, RequestException
# <====================================>

class Online:
    def __init__(self, app):
        # -- Indicates whether the computer is connected to the internet
        self.is_online: bool = False
        self.app = app

        #<_end of the method_>
    
    def _display_network_state(self, ui_state: str) -> None:
        ''' Initiate the display '''
        # --
        self.app.uiu.show_text_on(
            self.app.bui.online_label,
            ui_state
        )
        # --

        #<_end of the method_>
    
    def _get_network_state(self) -> None:
        '''
        Determine whether we are connected to the internet or not.
        Status code of 200 implies connection was successfull.
        '''
        try:
            # Make a GET request to an API endpoint
            resp = requests.get(
                'https://jsonplaceholder.typicode.com/posts/1',
                timeout=5
            )

            # Check if the response was successful
            if resp.status_code == 200:
                # -- Internet connection available
                ui_state: str = '📶 Connected'
                self.is_online = True
            else:
                # -- Some other error
                ui_state: str = '-'
                self.is_online = False

        except Timeout:
            ui_state: str = 'Slow Internet ...'
            self.is_online = True

        except ConnectionError:
            ui_state: str = '✖ Not Connected'
            self.is_online = False

        except RequestException:
            ui_state: str = 'Getting Status ...'
            self.is_online = False

        # --
        self._display_network_state(ui_state)

        #<_end of the method_>

    def online_worker(self) -> None:
        '''
        Intiate search for network state via a thread, It also schedules
        the search every 15 sec.
        '''
        # -- The state search should work in the background
        threading.Thread(
            target=self._get_network_state,
            daemon=True
        ).start()

        # -- Schedule run after 15 sec
        self.app.root.after(
            15000,
            self.online_worker
        )
        # --

        #<_end of the method_>


#<_END OF ONLINE_>