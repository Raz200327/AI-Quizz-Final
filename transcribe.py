from pytube import YouTube
import random
from io import BytesIO
import base64
import openai
import os

class YouTubeToMP3:

    def random_string(self):
        return random.randint(13674543, 12398576298437695276297640139652907860797560)
    def convert(self, link):
        yt = YouTube(link)
        download = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        print(download.default_filename)
        self.path = "./media"
        filename = f"{self.random_string()}{download.default_filename}"
        download.download(output_path=self.path, filename=filename)

        self.path = f"media/{filename}"
        print("DONE CONVERTING")

    def transcribe(self, path, api_key):
        openai.api_key = api_key
        audio_file = open(path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

        print(transcript)
        return transcript["text"]


