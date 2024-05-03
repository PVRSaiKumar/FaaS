from PIL import Image
import sys

def convert_to_negative(image):
    img = Image.open(image)
    inverted_img = img.transpose(Image.FLIP_LEFT_RIGHT)
    inverted_img.save(f"a.png")

if len(sys.argv) < 4:
    print("Usage: python script.py <number_of_arguments> <arguments> <number_of_files> <file1> <file2> ...")
    sys.exit(1)

num_args = int(sys.argv[1])
args = sys.argv[2:num_args+2]
num_files = int(sys.argv[num_args+2])
files = sys.argv[num_args+3:]

if len(files) != num_files:
    print("Error: Number of files provided does not match the specified count")
    sys.exit(1)

for file in files:
    convert_to_negative(file)
    print(f"Flipped {file}.")
