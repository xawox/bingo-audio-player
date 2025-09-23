from tkinter import Tk, Frame, Button, Listbox, Scrollbar, END, messagebox
import os
import random
from player import AudioPlayer
from pydub import AudioSegment
import tempfile
import pygame

def recortar_mas_potente(clip_path, duracion_ms=30000):
    audio = AudioSegment.from_file(clip_path)
    # Algoritmo simple: buscar la ventana de 30s con mayor RMS (energía)
    max_rms = -1
    start_max = 0
    for start in range(0, len(audio) - duracion_ms, 1000):  # paso de 1s
        segmento = audio[start:start+duracion_ms]
        rms = segmento.rms
        if rms > max_rms:
            max_rms = rms
            start_max = start
    return audio[start_max:start_max+duracion_ms]

class AudioPlayerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Bingo Audio Player")
        self.master.geometry("600x500")  # Ventana más grande

        self.frame = Frame(self.master)
        self.frame.pack(pady=10)

        # Caja de lista de canciones cargadas más grande
        self.clip_listbox = Listbox(self.frame, width=70, height=18)
        self.clip_listbox.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")

        self.clip_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.clip_listbox.yview)

        self.load_button = Button(self.master, text="Load Clips", command=self.load_clips)
        self.load_button.pack(pady=5)

        self.play_button = Button(self.master, text="Play", command=self.play_clip)
        self.play_button.pack(pady=5)

        self.pause_button = Button(self.master, text="Pause", command=self.pause_clip)
        self.pause_button.pack(pady=5)

        self.stop_button = Button(self.master, text="Stop", command=self.stop_clip)
        self.stop_button.pack(pady=5)

        self.random_button = Button(self.master, text="Play Random", command=self.play_random_clip)
        self.random_button.pack(pady=5)

        self.next_button = Button(self.master, text="Next", command=self.play_next_clip)
        self.next_button.pack(pady=5)

        self.played_clips = []  # Lista para guardar el historial

        # Caja de historial más grande
        self.history_listbox = Listbox(self.master, width=70, height=8)
        self.history_listbox.pack(pady=10)
        self.history_listbox.insert(END, "Historial de reproducción:")

        self.audio_player = AudioPlayer()
        self.started = False
        self.just_resumed = False
        self.master.after(100, self.check_music_end)

    def load_clips(self):
        self.clip_listbox.delete(0, END)
        clips_folder = "clips"  # Adjust this path if necessary
        if not os.path.exists(clips_folder):
            messagebox.showerror("Error", "Clips folder does not exist.")
            return

        for filename in os.listdir(clips_folder):
            if filename.lower().endswith(".mp3"):
                self.clip_listbox.insert(END, filename)

    def play_clip(self):
        selected = self.clip_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a clip to play.")
            return
        clip_name = self.clip_listbox.get(selected)
        clips_folder = "clips"
        clip_path = os.path.join(clips_folder, clip_name)

        # Recorta los 30 segundos más potentes
        recorte = recortar_mas_potente(clip_path)

        # Guarda el recorte en un archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
            recorte.export(tmpfile.name, format="mp3")
            tmpfile_path = tmpfile.name

        # Reproduce el archivo recortado
        self.audio_player.load(tmpfile_path)
        self.audio_player.play()
        self.started = True
        self.just_resumed = False  # Es una reproducción nueva

        # Añade al historial solo si no es una reanudación
        if not self.just_resumed and (not self.played_clips or self.played_clips[-1] != clip_name):
            self.played_clips.append(clip_name)
            self.update_history_listbox()

    def update_history_listbox(self):
        self.history_listbox.delete(0, END)
        self.history_listbox.insert(END, "Historial de reproducción:")
        for idx, name in enumerate(self.played_clips, 1):
            self.history_listbox.insert(END, f"{idx}. {name}")

    def pause_clip(self):
        self.audio_player.pause()
        self.just_resumed = True  # Marca que la próxima vez puede ser reanudación

    def stop_clip(self):
        self.audio_player.stop()
        self.just_resumed = True  # Marca que la próxima vez puede ser reanudación

    def play_random_clip(self):
        count = self.clip_listbox.size()
        if count == 0:
            messagebox.showwarning("Warning", "No clips loaded.")
            return

        # Calcula los índices de las canciones no reproducidas
        all_indices = set(range(count))
        played_indices = set()
        for name in self.played_clips:
            try:
                idx = self.clip_listbox.get(0, END).index(name)
                played_indices.add(idx)
            except ValueError:
                continue
        available_indices = list(all_indices - played_indices)

        if not available_indices:
            messagebox.showinfo("Info", "Todas las canciones ya han sido reproducidas.")
            return

        random_index = random.choice(available_indices)
        self.clip_listbox.selection_clear(0, END)
        self.clip_listbox.selection_set(random_index)
        self.clip_listbox.activate(random_index)
        self.play_clip()

    def play_next_clip(self):
        count = self.clip_listbox.size()
        if count == 0:
            messagebox.showwarning("Warning", "No clips loaded.")
            return
        selected = self.clip_listbox.curselection()
        if not selected:
            next_index = 0
        else:
            next_index = (selected[0] + 1) % count
        self.clip_listbox.selection_clear(0, END)
        self.clip_listbox.selection_set(next_index)
        self.clip_listbox.activate(next_index)
        self.play_clip()

    def check_music_end(self):
        # Solo busca la siguiente si ya se ha empezado a reproducir alguna,
        # la música NO está pausada NI detenida, y quedan canciones por reproducir
        if (
            self.started
            and not pygame.mixer.music.get_busy()
            and not self.audio_player.is_paused
            and self.audio_player.is_playing
        ):
            # ¿Quedan canciones sin reproducir?
            count = self.clip_listbox.size()
            played = set(self.played_clips)
            all_names = set(self.clip_listbox.get(0, END))
            if played >= all_names:
                self.started = False  # Resetea para no seguir intentando
            else:
                self.play_random_clip()
        self.master.after(1000, self.check_music_end)