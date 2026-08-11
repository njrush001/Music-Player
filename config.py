# <============ IMPORTS =========================>
from pathlib import Path
# <==============================================>

class AlmaDataPaths:
	''' Create Directories For Various Data Files '''

	# -- Get Base Directory
	BASE_DIR = Path(__file__).resolve().parent
	# -- Recommendations and Playlists Data Files Live Here
	DATA_DIR = BASE_DIR / 'data'
	# -- Exceptions Files
	ERROR_DIR = BASE_DIR / 'errors'
	# -- Background Dir
	BG_DIR = BASE_DIR / 'background'
	# -- Created Playlists Stay Here
	PLAYLIST_DIR = BASE_DIR / 'playlists'
	# -- Player Settings File Stays Here
	SETTINGS_DIR = BASE_DIR / 'settings_data'

	# -- Used incase player settings is corrupted
	DEFAULT_PROGRAM_DATA = {
		# -- Playback State: Loop all is the default
		'playback_state': 'repeat_all',
		
		# -- Startup volume 20%
		'saved_volume': 0.2,

		# -- Song that played last before the app was closed
		'last_played_data': {},

		# -- Folders to scan
		'music_folders': []
	}

#<_ END OF ALMADATAPATHS_>

# --- This part runs once
_bag = [
	AlmaDataPaths.BG_DIR,       # -- Has the default background artwork for the app
	AlmaDataPaths.DATA_DIR,     # -- Has 'saved_data.json' & 'recommendations.json'
	AlmaDataPaths.ERROR_DIR,    # -- Has 'exceptions.txt'
	AlmaDataPaths.PLAYLIST_DIR, # -- This is where the program store created playlists
	AlmaDataPaths.SETTINGS_DIR  # -- This is where users' preferences are saved
]

for _dir in _bag:
	# -- Create the directory if not available
	_dir.mkdir(parents=True, exist_ok=True)