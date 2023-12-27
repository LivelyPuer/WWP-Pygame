# importing PIL Module
import os

from PIL import Image

for file in os.listdir("/home/maxim/PycharmProjects/soccet_client/data/animations"):
    original_img = Image.open("/home/maxim/PycharmProjects/soccet_client/data/animations/" + file)

    # Flip the original image vertically
    vertical_img = original_img.transpose(method=Image.FLIP_LEFT_RIGHT)
    vertical_img.save("/home/maxim/PycharmProjects/soccet_client/data/animations/" + file)
    original_img.close()
    vertical_img.close()
