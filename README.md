# Alma Music Player

A Python-based desktop music player focused on playlist management, local music playback, persistent application state, and a responsive user experience.

## Features

* Play local music files.
* Create, edit, and delete playlists.
* Load music files into the application.
* Search and manage music within the player.
* Restore the last played song when the application is reopened.
* Display live playback progress.
* Locate music files when previously saved file paths are no longer valid.
* Provide feedback when problems occur during playback or file handling.
* Save playlists and application settings using JSON.
* Use a modular structure to separate different areas of application functionality.
* Continuously improve the interface and user experience.

## Technologies

* Python 3.12.10
* Tkinter
* Pygame
* Mutagen
* Pillow
* Requests
* tkinterdnd2
* JSON
* Git

## Project Structure

The application is divided into multiple Python modules, with different modules responsible for areas such as:

* Music playback
* Playlist management
* Library management
* Search
* Settings
* User interface
* Playback state
* Recommendations
* Error handling
* File discovery

Application-generated data such as playlists, settings, recommendations, and error logs are stored locally and are not included in the repository.

## Installation

### Requirements

* Python 3.12.10 or later
* The dependencies listed in `requirements.txt`

Clone the repository:

```bash
git clone https://github.com/njrush001/Music-Player.git
cd Music-Player
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the music player with:

```bash
python alma_music_player.py
```

## Development

Alma Music Player is a personal project developed while learning and improving Python programming.

Development focuses on writing clean and maintainable code, debugging problems, anticipating failure scenarios, maintaining stability between application components, and improving the user experience.

The project is still under active development.