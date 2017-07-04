# -*- coding: gbk -*- 
import os
from struct import *


def lzw_compress(string):

	dictionary = {chr(i) : i for i in range(0, 256)}

	pos = 256
	p = ''
	result = []

	for c in string:
		pc = p + c
		if pc in dictionary and dictionary[pc]<pos:
			p = pc
		else:
			result.append(dictionary[p])
			dictionary[pc] = pos
			pos += 1
			p = c
		if pos == 65536:
			pos = pos>>1
			
	if p :
		result.append(dictionary[p])

	return result

if __name__ == '__main__':
	f1 = open("text.txt", "r")
	f2 = open("compress.txt", "wb")

	Input = f1.read()
	compressed_string = lzw_compress(Input)

	for i in compressed_string:
		f2.write(pack("H", i))

	print(len(compressed_string))

	f1.close()
	f2.close()