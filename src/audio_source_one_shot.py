import numpy as np
import sounddevice as sd


class AudioSourceOneShot:
    def __init__(self, samplerate=44100, chunk_nb_samples=32):
        self.chunk_nb_samples = chunk_nb_samples
        self.current_sample_index = 0
        self.wav_samples = np.array([], dtype=np.int16)
        self.nb_wav_samples = 0
        self.stream = sd.OutputStream(
            samplerate=samplerate,
            channels=1,
            dtype='int16',
            callback=self.audio_callback,
            blocksize=self.chunk_nb_samples,
        )

    def set_wav_samples(self, wav_samples):
        self.wav_samples = np.array(wav_samples, dtype=np.int16)
        self.nb_wav_samples = len(wav_samples)
        self.current_sample_index = 0

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()
        self.stream.close()

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print('Status:', status)

        if self.current_sample_index < self.nb_wav_samples:
            remaining = self.nb_wav_samples - self.current_sample_index
            chunk = min(frames, remaining)
            outdata[:chunk, 0] = self.wav_samples[self.current_sample_index:self.current_sample_index + chunk]
            if chunk < frames:
                outdata[chunk:, 0] = 0
            self.current_sample_index += chunk
        else:
            outdata[:] = 0