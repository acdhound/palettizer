from PIL import Image
from quantize import quantize
from palette import parse_palette
import sys

if __name__ != '__main__':
    print("The script isn't executed as main, terminating")
    exit(1)

if len(sys.argv) < 4:
    raise Exception('Expected 3 arguments: input image path, palette file path and output image path')
input_img = sys.argv[1]
palette = sys.argv[2]
output_img = sys.argv[3]

print('Parsing the palette from ' + palette + '...')
palette = parse_palette(palette)
print("Successfully parsed")

print('Opening image from ' + input_img + '...')
im = Image.open(input_img)
print('Image opened')
print(im.format, im.size, im.mode)

print('Quantizing the image...')
quantize(im, palette)
print('Quantization finished')

print('Saving the quantized image to ' + output_img + '...')
im.save(output_img)
print('Successfully saved')

exit(0)
