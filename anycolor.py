#! /usr/bin/env python

import sys
import os

import requests
from google.cloud import vision


def background(text, rgb):
    return f"\033[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}\033[0m"


def dominant_rgb_colors(image_content, num_colors):
    vision_client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_content)
    response = vision_client.annotate_image({"image": image})
    return [
        (int(c.color.red), int(c.color.green), int(c.color.blue))
        for c in response.image_properties_annotation.dominant_colors.colors
    ][:num_colors]


def download_image_for_query(query):
    search_key = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_KEY")
    search_engine_id = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
    resp = requests.get(
        f"https://www.googleapis.com/customsearch/v1?key={search_key}&cx={search_engine_id}&q={query}&searchType=image"
    )
    img_url = resp.json()["items"][0]["link"]
    img_content = requests.get(img_url).content
    # uncomment to save downloaded image
    # with open( "/tmp/anycolor_img", "wb") as img_file:
    #     img_file.write(img_content)
    return img_content


if __name__ == "__main__":
    query = sys.argv[1]
    num_colors = 5
    if len(sys.argv) > 2:
        num_colors = int(sys.argv[2])
    img_content = download_image_for_query(query)
    rgb_colors = dominant_rgb_colors(img_content, num_colors)
    for rgb_color in rgb_colors:
        hex_triplet = "#" + "".join(f"{i:02x}" for i in rgb_color)
        color_strip = background("                    ", rgb_color)
        print(f"{color_strip} {hex_triplet}")
