import wave
import contextlib
from django.core.files.storage import default_storage

def get_wav_file_duration(uploaded_file):
    file_path = default_storage.save(uploaded_file.name, uploaded_file)

    with contextlib.closing(wave.open(file_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    default_storage.delete(file_path)

    return duration