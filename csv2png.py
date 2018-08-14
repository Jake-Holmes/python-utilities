import sys
import logging
import glob
import threading
import queue
import time
from datetime import date, datetime
import numpy as np
from PIL import Image


#---------------------------------------------------#
#													#
#	Author: Jake Holmes#							#
#	Last Updated: 2018-05-24						#
#	Version: 0.3									#
#													#
#---------------------------------------------------#


IN_DIR = './csv/'				# Directory containing only single column csv files with numerical data points
OUT_DIR = './images/'			# Output dir of all images
EXT = '.png'					# Saved image file extension
BACKGROUND = [255, 255, 255]	# RGB background colour (Default white)
DATA_POINT = [0,0,0]			# RGB colour of data points (Default black)
SIZE = 7						# Dimensions of each data point written to the image
THREADS = 12					# Number of threads to spawn and run
WARNING_TIMEOUT = 6				# The time after which a warning will be logged when generating an image.

file_queue = queue.Queue()		# Global queue for threads to pull file names from

def main():

	# Initiate logging for display output and file output
	log_path = './../logs/csv2png/csv2png-%s.log' % (datetime.now().strftime("%Y%m%d")) 
	log_format = logging.Formatter('[%(asctime)-10s] [%(levelname)s] [%(funcName)s] %(message)s')
	log_level = logging.INFO
	log_root = logging.getLogger()
	log_root.setLevel(log_level)
	# Initiate logger file handling
	log_file_handler = logging.FileHandler(log_path)
	log_file_handler.setFormatter(log_format)
	log_root.addHandler(log_file_handler)
	#Initiate logger console stream handling
	log_console_handler = logging.StreamHandler(sys.stdout)
	log_console_handler.setFormatter(log_format)
	log_root.addHandler(log_console_handler)
	
	logging.info('Starting csv2png')
	
	# Generate file lists into queues
	in_files = []	
	
	in_files = glob.glob(IN_DIR + '*.csv')
	
	for file in in_files:
		file_queue.put(file)
	
	# Initiate threads
	threads = []
	for id in range(THREADS):
		name = 'Thread ' + str(id)
		threads.append(ImageGenerator(name, IN_DIR, OUT_DIR))
		
	# Run threads
	for thread in threads:
		thread.start()
		
	# Wait for all threads to finish
	for thread in threads:
		thread.join()
		
	logging.info("All threads have completed execution.")
	
class ImageGenerator(threading.Thread):
	'''Class to instantiate an image generator object and build an image when ran.'''

	def __init__(self, threadID, in_dir, out_dir, ext=EXT, bckg=BACKGROUND, dp=DATA_POINT, size=SIZE):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.in_dir = in_dir
		self.out_dir = out_dir
		self.ext = ext
		self.bckg = bckg
		self.dp = dp
		self.size = size

	def run(self):
		
		while not file_queue.empty():
			
			start = time.time()
			csv = file_queue.get()
			
			# Read data from csv file
			data = np.genfromtxt(csv, delimiter=',', dtype=np.float64)
			
			# Get/calculate info for generating image
			data_max = int(max(data))
			data_min = int(min(data))
			data_range = data_max - data_min		# The variation in data values
			
			if data_max > abs(data_min):			# Range of pixels on the y-axis with added buffer
				y_range = int((2*data_max)*1.2)		# Calculated to ensure that data point y=0 is in the middle of the image
			else:
				y_range = int((2*abs(data_min))*1.2)
			
			y_mid = int(y_range/2)					# The mid point of the y-axis for the graph to be centred around
			
			x_entries = len(data)					# Nunmber of data points to plot
			x_range = int(x_entries*1.1) 				# Range of pixels on the x-axis with added buffer
			x_buffer = int((x_range - x_entries)/2) 	# Buffer when setting pixels to avoid touching the images edge
			
			# Build RGB pixel array of image
			pixels = np.full((y_range, x_range, 3), 255, dtype=np.uint8)
			
			# Only write background colour if not default to avoid processing overhead.
			if self.bckg != [255, 255, 255]:
				for y in range(y_range):
					for x in range(x_range):
						pixels[y][x] = bckg
			
			
			# Draw the data points over the background
			for c in range(x_entries):
				x = c + x_buffer
				y = 0 - (int(data[c]) + y_mid)
				self.draw_square(pixels, y, x, self.dp, size=self.size)
			
			# Build image
			image = Image.fromarray(pixels)
			
			# Save image 
			name = csv.replace(self.in_dir, self.out_dir)
			name = name.replace('.csv', self.ext)
			image.save(name)
			
			# Log warning if runtime exceeded threshold. May indicate a hung process or just a particularly large image generated.
			run_time = time.time() - start
			if run_time > WARNING_TIMEOUT:
				logging.warning('[%s] Saved %s with a processing time of %f.' % (self.threadID, name, run_time))
			else:
				logging.info('[%s] Saved %s with a processing time of %f.' % (self.threadID, name, run_time))
				
			# Signal that processing has completed for item pulled from the file queue
			file_queue.task_done()
			

	def draw_square(self, pixels, y, x, dp, size=3):
		'''Draw a square of pixels around the given centre coordinate in a
		3d array of RGB pixels'''
		
		y_start = y - int(size/2)
		x_start = x - int(size/2)
		
		for dy in range(size):
			for dx in range(size):
				pixels[y_start + dy][x_start + dx] = dp
	

if __name__ == "__main__":
	main()
	