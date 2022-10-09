import azure.cognitiveservices.speech as speech_sdk
import librosa
import os
import soundfile
import wave


def _speech_config():
    speech_key, service_region = (
        os.environ["AZURE_SPEECH_KEY"],
        os.environ["AZURE_SPEECH_LOC"],
    )
    return speech_sdk.SpeechConfig(subscription=speech_key, region=service_region)


class WavFileReaderCallback(speech_sdk.audio.PullAudioInputStreamCallback):
    def __init__(self, filename: str):
        super().__init__()
        x, _ = librosa.load(filename, sr=16000)
        soundfile.write(filename, x, 16000)
        self._file_h = wave.open(filename, mode=None)

        self.sample_width = self._file_h.getsampwidth()

        assert self._file_h.getnchannels() == 1
        assert self._file_h.getsampwidth() == 2
        assert self._file_h.getframerate() == 16000
        assert self._file_h.getcomptype() == "NONE"

    def read(self, buffer: memoryview) -> int:
        """read callback function"""
        size = buffer.nbytes
        frames = self._file_h.readframes(size // self.sample_width)

        buffer[: len(frames)] = frames

        return len(frames)

    def close(self):
        """close callback function"""
        self._file_h.close()


def to_text(filename):
    speech_config = _speech_config()

    wave_format = speech_sdk.audio.AudioStreamFormat(
        samples_per_second=16000, bits_per_sample=16, channels=1
    )
    callback = WavFileReaderCallback(filename)
    stream = speech_sdk.audio.PullAudioInputStream(callback, wave_format)
    audio_config = speech_sdk.audio.AudioConfig(stream=stream)

    speech_recognizer = speech_sdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    result = speech_recognizer.recognize_once()

    if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
        return result.text
    if result.reason == speech_sdk.ResultReason.NoMatch:
        raise Exception("No speech could be recognized: {}".format(result.no_match_details))
    if result.reason == speech_sdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speech_sdk.CancellationReason.Error:
            raise Exception("Error details: {}".format(cancellation_details.error_details))


def to_speech(text: str, filename: str, voice: str):
    speech_config = _speech_config()
    audio_config = speech_sdk.audio.AudioOutputConfig(filename=filename)

    # https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=stt-tts
    speech_config.speech_synthesis_voice_name = voice
    speech_synthesizer = speech_sdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    speech_synthesis_result = speech_synthesizer.speak_text(text)

    if speech_synthesis_result.reason == speech_sdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        raise Exception("Speech synthesis canceled: {}".format(cancellation_details.reason))
