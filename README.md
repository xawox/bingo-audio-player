# Bingo Audio Player

## Overview
Bingo Audio Player is a simple audio player application that allows users to play trimmed audio clips. The application features a graphical user interface (GUI) for easy interaction and control over audio playback.

## Project Structure
```
bingo-audio-player
├── src
│   ├── main.py          # Entry point of the application
│   ├── gui.py           # Contains the AudioPlayerGUI class for the GUI
│   ├── player.py        # Handles audio playback functionality
│   └── utils.py         # Utility functions for file handling
├── requirements.txt     # Lists the project dependencies
└── README.md            # Documentation for the project
```

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd bingo-audio-player
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python src/main.py
```

Once the application is running, you can load audio clips and control playback using the GUI.

## Dependencies
The project requires the following Python packages:
- `pydub` for audio playback
- `pygame` for handling audio playback events
- A GUI framework such as `tkinter` or `PyQt`

Make sure to install these packages using the `requirements.txt` file.

## Contributing
Contributions are welcome! If you have suggestions or improvements, feel free to create a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.