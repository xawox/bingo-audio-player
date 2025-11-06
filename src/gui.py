from tkinter import Tk, Frame, Button, Listbox, Scrollbar, END, messagebox, Label
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

        # Oculta la lista de canciones cargadas y su scrollbar.
        # Si quieres mostrarla luego, usa: self.clip_listbox.pack(...) y self.scrollbar.pack(...)
        self.clip_listbox.pack_forget()
        self.scrollbar.pack_forget()

        # Contenedor para historial + texto fijo a la derecha
        self.history_frame = Frame(self.master)
        self.history_frame.pack(fill="x", pady=10)

        # Caja de historial (izquierda)
        self.history_listbox = Listbox(self.history_frame, width=50, height=8)
        self.history_listbox.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Texto fijo grande a la derecha (SIEMPRE muestra "BINGO MUSICAL 2025")
        self.brand_label = Label(
            self.history_frame,
            text="BINGO MUSICAL 2025",
            font=("Helvetica", 24, "bold"),
            width=24,
            anchor="center"
        )
        self.brand_label.pack(side="right", fill="y")
        self.history_listbox.insert(END, "Historial de reproducción:")

        # Botones en una sola fila (debajo del historial)
        self.button_frame = Frame(self.master)
        self.button_frame.pack(pady=8)

        self.load_button = Button(self.button_frame, text="Load Clips", command=self.load_clips)
        self.load_button.pack(side="left", padx=6)

        self.play_button = Button(self.button_frame, text="Play", command=self.play_clip)
        self.play_button.pack(side="left", padx=6)

        self.pause_button = Button(self.button_frame, text="Pause", command=self.pause_clip)
        self.pause_button.pack(side="left", padx=6)

        self.stop_button = Button(self.button_frame, text="Stop", command=self.stop_clip)
        self.stop_button.pack(side="left", padx=6)

        self.random_button = Button(self.button_frame, text="Play Random", command=self.play_random_clip)
        self.random_button.pack(side="left", padx=6)

        self.next_button = Button(self.button_frame, text="Next", command=self.play_next_clip)
        self.next_button.pack(side="left", padx=6)

        self.played_clips = []  # Lista para guardar el historial

        self.audio_player = AudioPlayer()
        self.started = False
        self.just_resumed = False
        self.current_clip = None  # <- guarda el nombre de la pista actual

        # Label grande fijo debajo de los botones para mostrar la canción que está sonando
        self.now_playing_large = Label(self.master, text="No hay reproducción", font=("Helvetica", 30, "bold"), anchor="center")
        # empaquetar aquí (después de los botones) para que quede justo debajo de ellos
        self.now_playing_large.pack(fill="x", pady=(10, 20))

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

        # marcar y mostrar la pista actual SOLO en el label inferior
        was_resumed = self.just_resumed
        self.just_resumed = False
        self.current_clip = clip_name
        self.now_playing_large.config(text=clip_name)

        # Añade al historial solo si no es reanudación y no es repetición inmediata
        if not was_resumed and (not self.played_clips or self.played_clips[-1] != clip_name):
            self.played_clips.append(clip_name)
            self.update_history_listbox()

    def update_history_listbox(self):
        self.history_listbox.delete(0, END)
        self.history_listbox.insert(END, "Historial de reproducción:")
        for idx, name in enumerate(self.played_clips, 1):
            self.history_listbox.insert(END, f"{idx}. {name}")
        self.save_history_to_file()  # Guarda el historial en un archivo

    def save_history_to_file(self):
        with open("historial_reproducidas.txt", "w", encoding="utf-8") as f:
            for idx, name in enumerate(self.played_clips, 1):
                f.write(f"{idx}. {name}\n")

    def pause_clip(self):
        self.audio_player.pause()
        self.just_resumed = True
        if self.current_clip:
            # Sólo actualiza el label grande inferior
            self.now_playing_large.config(text=f"PAUSA — {self.current_clip}")

    def stop_clip(self):
        self.audio_player.stop()
        self.just_resumed = True
        self.current_clip = None
        # Sólo actualiza el label grande inferior
        self.now_playing_large.config(text="Detenido")

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
        # Simplemente llama a play_random_clip para que sea aleatoria y no repetida
        self.play_random_clip()

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