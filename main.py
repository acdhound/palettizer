from quantize import quantize
from palette import parse_palette
from skimage import io
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

print('Quantizing the image from file ' + input_img + '...')
# result = quantize(input_img, palette)
result = quantize(input_img, palette)
print('Quantization finished')

print('Saving the quantized image to ' + output_img + '...')
io.imsave(output_img, result)
print('Successfully saved')

exit(0)
