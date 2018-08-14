import sys
import scipy.io as sio
import numpy as np

dir = '/home/pi/capstone/data/training2017/'

def main():
	
	read_mat(sys.argv[1])
	print('%s.csv created' % sys.argv[1])

	#for i in range(1, 8529):
		
	#	try:
	#		file = dir + 'A' + format(i, '05d') + '.mat'
	#		read_mat(file)
	#		print('%s.csv created' % file)
	#	except:
	#		print('ERROR: ' + dir + 'A' + format(i, '05d') + '.mat')	


def read_mat(filename):
	
	mat_contents = sio.loadmat(filename)	
	#print('%s\n%s' % (filename,mat_contents))
	for i in mat_contents:
		if '__' not in i and 'readme' not in i:
			np.savetxt((filename + '.csv'),mat_contents[i],delimiter=',')
	

main()
