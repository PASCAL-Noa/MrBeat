import numpy as np
import sounddevice as sd
from audio_source_track import AudioSourceTrack

MAX_16BITS = 32767
MIN_16BITS = -32768


def sum_16bits(values):
    s = np.sum(values)
    return np.clip(s, MIN_16BITS, MAX_16BITS)


class AudioSourceMixer:
    def __init__(self, all_wav_samples, bpm, sample_rate, nb_steps, on_current_step_changed=None, min_bpm=60):
        self.tracks = []
        self.bpm = bpm
        self.min_bpm = min_bpm
        self.sample_rate = sample_rate
        self.nb_steps = nb_steps
        self.current_step_index = 0
        self.current_sample_index = 0
        self.is_playing = False
        self.on_current_step_changed = on_current_step_changed

        self.steps_per_beat = 4


        for wav in all_wav_samples:
            track = AudioSourceTrack(wav, bpm, sample_rate, min_bpm)
            track.set_steps([0] * nb_steps)
            self.tracks.append(track)

        self.step_nb_samples = self.tracks[0].step_nb_samples
        self.buffer_nb_samples = self.tracks[0].buffer_nb_samples
        self.silence = np.zeros(self.buffer_nb_samples, dtype=np.int16)

        self.stream = sd.OutputStream(
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            callback=self.audio_callback,
            blocksize=self.step_nb_samples
        )

    def set_steps(self, index, steps):
        if 0 <= index < len(self.tracks):
            self.tracks[index].set_steps(steps)

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.step_nb_samples = int((60 / bpm) * self.sample_rate / self.steps_per_beat)

        if self.stream:
            if self.stream.active:
                self.stream.stop()
            self.stream.close()

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            callback=self.audio_callback,
            blocksize=self.step_nb_samples
        )
        self.stream.start()

    def start(self):
        if self.stream is None or not self.stream.active:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                blocksize=self.step_nb_samples,
                channels=1,
                dtype='int16',
                callback=self.audio_callback
            )
        self.is_playing = True
        self.stream.start()

    def stop(self):
        if self.stream is not None and self.stream.active:
            self.stream.stop()
        self.is_playing = False

    def audio_callback(self, outdata, frames, time, status):
        if not self.is_playing:
            outdata[:] = self.silence[:frames].reshape(-1, 1)
            return


        buffers = [track.get_step_buffer() for track in self.tracks]

        stacked = np.vstack(buffers)
        mixed = np.clip(np.sum(stacked, axis=0), MIN_16BITS, MAX_16BITS).astype(np.int16)

        if mixed.size > frames:
            mixed = mixed[:frames]
        elif mixed.size < frames:
            mixed = np.pad(mixed, (0, frames - mixed.size), mode='constant')


        if self.on_current_step_changed is not None:
            display_index = self.current_step_index - 2
            if display_index < 0:
                display_index += self.nb_steps
            self.on_current_step_changed(display_index)

        self.current_step_index = (self.current_step_index + 1) % self.nb_steps

        outdata[:] = mixed.reshape(-1, 1)

