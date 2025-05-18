import numpy as np
import sounddevice as sd


class AudioSourceTrack:
    def __init__(self, wav_samples, bpm, sample_rate, min_bpm):
        self.wav_samples = np.array(wav_samples).astype(np.int16)
        self.nb_wav_samples = len(wav_samples)
        self.bpm = bpm
        self.min_bpm = min_bpm
        self.sample_rate = sample_rate
        self.steps = np.zeros(16, dtype=np.int32)
        self.current_step_index = 0
        self.current_sample_index = 0
        self.last_sound_sample_start_index = 0
        self.step_nb_samples = self.compute_step_nb_samples(bpm)
        self.buffer_nb_samples = self.compute_step_nb_samples(min_bpm)
        self.silence = np.zeros(self.buffer_nb_samples, dtype=np.int16)

        self.stream = sd.OutputStream(
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            callback=self.audio_callback,
            blocksize=self.step_nb_samples
        )

    def compute_step_nb_samples(self, bpm_value):
        return int(self.sample_rate * 15 / bpm_value) if bpm_value != 0 else 0

    def set_steps(self, steps):
        self.steps = np.array(steps, dtype=np.int32)
        self.current_step_index = 0

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.step_nb_samples = self.compute_step_nb_samples(bpm)
        self.stream.blocksize = self.step_nb_samples

    def no_steps_activated(self):
        return not np.any(self.steps)

    def get_step_buffer(self):
        if self.no_steps_activated():
            return self.silence[:self.step_nb_samples].copy()

        if self.steps[self.current_step_index] == 1:
            self.last_sound_sample_start_index = self.current_sample_index
            if self.nb_wav_samples >= self.step_nb_samples:
                buf = self.wav_samples[0:self.step_nb_samples]
            else:
                silence_len = self.step_nb_samples - self.nb_wav_samples
                buf = np.concatenate([self.wav_samples, self.silence[:silence_len]])
        else:
            index = self.current_sample_index - self.last_sound_sample_start_index
            if index > self.nb_wav_samples:
                buf = self.silence[:self.step_nb_samples]
            elif self.nb_wav_samples - index >= self.step_nb_samples:
                buf = self.wav_samples[index:index + self.step_nb_samples]
            else:
                silence_len = self.step_nb_samples - (self.nb_wav_samples - index)
                buf = np.concatenate([self.wav_samples[index:], self.silence[:silence_len]])

        self.current_sample_index += self.step_nb_samples
        self.current_step_index = (self.current_step_index + 1) % len(self.steps)
        return buf

    def audio_callback(self, outdata, frames, time, status):
        step_buf = self.get_step_buffer()
        outdata[:] = step_buf.reshape(-1, 1)

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()
        self.stream.close()