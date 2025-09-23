def load_audio_clips(folder_path):
    """Load audio clips from the specified folder and return a list of file paths."""
    import os
    audio_clips = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.mp3', '.wav', '.ogg')):
            audio_clips.append(os.path.join(folder_path, filename))
    return audio_clips

def is_valid_audio_file(file_path):
    """Check if the given file path is a valid audio file."""
    return file_path.lower().endswith(('.mp3', '.wav', '.ogg')) and os.path.isfile(file_path)