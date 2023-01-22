from pytube import YouTube
import random
from io import BytesIO
import base64
import banana_dev as banana
import os

class YouTubeToMP3:

    def random_string(self):
        return random.randint(13674543, 12398576298437695276297640139652907860797560)
    def convert(self, link):
        yt = YouTube(link)
        download = yt.streams.first()
        print(download.default_filename)
        self.path = "./media"
        filename = f"{self.random_string()}{download.default_filename}"
        download.download(output_path=self.path, filename=filename)

        self.path = f"media/{filename}"
        print("DONE CONVERTING")

    def transcribe(self, path):
        api_key = "9318c758-09a8-4cc5-810f-65d48571baa4"
        model_key = "8dc38f14-f4f8-4b07-b1fc-ea29d7c1d83f"

        # Expects an mp3 file named test.mp3 in directory
        with open(path, 'rb') as file:
            mp3bytes = BytesIO(file.read())
        mp3 = base64.b64encode(mp3bytes.getvalue()).decode("ISO-8859-1")

        model_payload = {"mp3BytesString": mp3}

        out = banana.run(api_key, model_key, model_payload)["modelOutputs"][0]["text"]
        print(out)
        return out


