import wave
from array import array
import os


def get_sound_path(filename):
    base_path = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(base_path, "..", filename))


class Sound:
    nb_samples = 0
    samples = None

    def __init__(self, filename, displayname):
        self.filename = get_sound_path(filename)
        self.displayname = displayname
        self.load_sound()

    def load_sound(self):
        with wave.open(self.filename, mode='rb') as wav_file:
            self.nb_samples = wav_file.getnframes()
            frames = wav_file.readframes(self.nb_samples)
            self.samples = array('h', frames)


class SoundKit:
    sounds = ()

    def get_nb_tracks(self):
        return len(self.sounds)

    def get_all_samples(self):
        return [sound.samples for sound in self.sounds]


class SoundKit1(SoundKit):
    sounds = (
        Sound("res/sounds/kit1/kick.wav", "KICK"),
        Sound("res/sounds/kit1/clap.wav", "CLAP"),
        Sound("res/sounds/kit1/shaker.wav", "SHAKER"),
        Sound("res/sounds/kit1/snare.wav", "SNARE"),
    )


class SoundKit1All(SoundKit):
    sounds = (
        Sound("res/sounds/kit1/kick.wav", "KICK"),
        Sound("res/sounds/kit1/clap.wav", "CLAP"),
        Sound("res/sounds/kit1/shaker.wav", "SHAKER"),
        Sound("res/sounds/kit1/snare.wav", "SNARE"),
        Sound("res/sounds/kit1/bass.wav", "BASS"),
        Sound("res/sounds/kit1/effects.wav", "EFFECTS"),
        Sound("res/sounds/kit1/pluck.wav", "PLUCK"),
        Sound("res/sounds/kit1/vocal_chop.wav", "VOCAL"),
    )


class SoundKitService:
    soundkit = SoundKit1All()

    def get_nb_tracks(self):
        return self.soundkit.get_nb_tracks()

    def get_sound_at(self, index):
        if index >= len(self.soundkit.sounds):
            return None
        return self.soundkit.sounds[index]
