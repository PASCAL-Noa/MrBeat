import sounddevice as sd

from audio_source_one_shot import AudioSourceOneShot
from audio_source_track import AudioSourceTrack
from audio_source_mixer import AudioSourceMixer


class AudioEngine:
    NB_CHANNELS = 1
    SAMPLE_RATE = 44100
    BUFFER_SIZE = 1024

    def __init__(self):
        self.audio_source_one_shot = AudioSourceOneShot(self.SAMPLE_RATE)

    def play_sound(self, wav_samples):
        self.audio_source_one_shot.set_wav_samples(wav_samples)

    def create_track(self, wav_samples, bpm):
        source_track = AudioSourceTrack(wav_samples, bpm, self.SAMPLE_RATE)
        return source_track

    def create_mixer(self, all_wav_samples, bpm, nb_steps, on_current_step_changed, min_bpm):
        source_mixer = AudioSourceMixer(all_wav_samples, bpm, self.SAMPLE_RATE, nb_steps, on_current_step_changed, min_bpm)
        source_mixer.start()
        return source_mixer