import requests
from PIL import Image
import os
import shutil
import json
from stitching import *
from tqdm import tqdm

# Google Maps API key
api_key = "AIzaSyC0aGWmn6L-QNmddeOxgqFAxdYDViqZkn0"
n = 0.0095

# query URL
url = "https://maps.googleapis.com/maps/api/staticmap?" + "center={}" + "&zoom={}" + \
      "&size=400x400&key=" + \
      api_key + "&sensor=false" + "&maptype=satellite" + "&language=RU"

# function to clear temp folder
def clear_temp():
    folder = './temp/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            return 1

def crop_image(path):
    original = Image.open(path)
    width, height = original.size
    cropped_example = original.crop((0, 0, width, height - 25))
    cropped_example.save(path)

def read_data():
    with open("./data.json", "r") as data:
        return json.load(data)

def calculate_pieces_num(x1, y1, x2, y2, k):
    rows = 0
    columns = 0
    while (y1 > y2):
        rows += 1
        y1 -= k
    while (x1 < x2):
        columns += 1
        x1 += k
    return rows * columns

# downloading images
def parse_data():
    clear_temp()
    data = read_data()
    y1, x1 = data["coord_a"].split(",")
    y2, x2 = data["coord_b"].split(",")
    x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
    # print(x1, y1, x2, y2)
    while True:
        try:
            zoom = int(input("input zoom k(16-19): "))
            break
        except:
            pass

    if zoom == 19:
        k = 0.0005
    elif zoom == 18:
        k = 0.001
    elif zoom == 17:
        k = 0.0028
    elif zoom == 16:
        k = 0.005

    pieces_num = calculate_pieces_num(x1, y1, x2, y2, k)

    count = 0
    columns_num = 0
    rows_num = 0
    print("downloading pieces...")
    pbar = tqdm(total=pieces_num)
    while (y1 > y2):
        columns_num = 0
        x1_temp = x1
        rows_num += 1
        while (x1_temp < x2):
            coord = str(y1) + ',' + str(x1_temp)
            request = requests.get(url.format(coord, zoom))
            with open("./temp/{}.png".format(count), "wb") as image:
                image.write(request.content)
            crop_image("./temp/{}.png".format(count))
            columns_num += 1
            count += 1
            x1_temp += k
            pbar.update(1)
            # print("downloaded {}/{} pieces".format(count, pieces_num))
        y1 -= k
    pbar.close()
    print("\ndownloaded {} pieces\n".format(count))
    return rows_num, columns_num

def stitching_images(rows, columns):
    print("init stitching process...")
    pieces_num = rows * columns - 1
    pbar1 = tqdm(total=pieces_num)
    for i in range(rows):
        row = []
        for j in range(columns):
            row.append("./temp/{}.png".format((i * columns) + j))
        for z in range(len(row) - 1):
            stitch_image(["./temp/{}.png".format(i * columns), row.pop(1)], "./temp/{}.png".format(i * columns))
            pbar1.update(1)
    paths = []
    for i in range(rows):
        paths.append("./temp/{}.png".format(i * columns))
    for i in range(rows - 1):
        stitch_image(["./temp/{}.png".format(i * columns), paths.pop(1)], "./temp/{}.png".format(i * columns))
        pbar1.update(1)
    pbar1.close()
    shutil.copyfile("./temp/0.png", "./output.png")
    print("stitching completed!")

if __name__ == "__main__":
    rows, columns = parse_data()
    stitching_images(rows, columns)
    clear_temp()






