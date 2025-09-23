# File: /bingo-audio-player/bingo-audio-player/src/main.py

import tkinter as tk
from gui import AudioPlayerGUI

def main():
    root = tk.Tk()
    root.title("Bingo Audio Player")
    app = AudioPlayerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()