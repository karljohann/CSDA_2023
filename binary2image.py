
import os, math
import argparse
from PIL import Image
from queue import Queue
from threading import Thread


def getBinaryData(filename):

	binary_values = []

	with open(filename, 'rb') as fileobject:

		# read file byte by byte
		data = fileobject.read(1)

		while data != b'':
			binary_values.append(ord(data))
			data = fileobject.read(1)

	return binary_values


def createGreyScaleImage(filename, width=None):

	greyscale_data  = getBinaryData(filename)
	size            = get_size(len(greyscale_data), width)
	if size[0] == 512:
		save_file(filename, greyscale_data, size, 'L')


def save_file(filename, data, size, image_type):

	try:
		image = Image.new(image_type, size)
		image.putdata(data)

		# setup output filename
		dirname     = os.path.dirname(filename)
		name, _     = os.path.splitext(filename)
		name        = os.path.basename(name)
		imagename   = dirname + os.sep + image_type + os.sep + name + '_'+image_type+ '.png'
		os.makedirs(os.path.dirname(imagename), exist_ok=True)

		image.save(imagename)
		print('The file', imagename, 'saved.')
	except Exception as err:
		print(err)


def get_size(data_length, width=None):

	if width is None: # with don't specified any with value

		size = data_length

		if (size < 10240):
			width = 32
		elif (10240 <= size <= 10240 * 3):
			width = 64
		elif (10240 * 3 <= size <= 10240 * 6):
			width = 128
		elif (10240 * 6 <= size <= 10240 * 10):
			width = 256
		elif (10240 * 10 <= size <= 10240 * 20):
			width = 384
		elif (10240 * 20 <= size <= 10240 * 50):
			width = 512
		elif (10240 * 50 <= size <= 10240 * 100):
			width = 768
		else:
			width = 1024

		height = int(size / width) + 1

	else:
		width  = int(math.sqrt(data_length)) + 1
		height = width

	return (width, height)


def run(file_queue, width):

	while not file_queue.empty():
		filename = file_queue.get()
		createGreyScaleImage(filename, width)
		file_queue.task_done()


def main(input_dir, width=None, thread_number=7):

	# Get all executable files in input directory and add them into queue
	file_queue = Queue()
	for root, directories, files in os.walk(input_dir):
		for filename in files:
			file_path = os.path.join(root, filename)
			file_queue.put(file_path)

	# Start thread
	for index in range(thread_number):
		thread = Thread(target=run, args=(file_queue, width))
		thread.daemon = True
		thread.start()
	file_queue.join()


if __name__ == '__main__':

	parser = argparse.ArgumentParser(prog='binar2image.py', description="Convert binary file to image")
	parser.add_argument(dest='input_dir', help='Input directory path is which include executable files')

	args = parser.parse_args()

	main(args.input_dir, width=None)

