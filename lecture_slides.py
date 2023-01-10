from PIL import Image
import os
import pyheif
import argparse
import random




class LectureSlides:
    def __init__(self, slide_directory):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./ai-transcription-369204-bd00007ecde8.json"
        if slide_directory.split(".")[1] == "heic" or slide_directory.split(".")[1] == "HEIC":

            heif_file = pyheif.read(f"./media/{slide_directory}")

            # Convert the image to a PIL Image object
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            image.save(f"./media/{slide_directory.split('.')[0]}.png", "PNG")
            os.remove(f"./media/{slide_directory}")
            self.slide_directory = f"{slide_directory.split('.')[0]}.png"

        else:
            self.slide_directory = slide_directory



