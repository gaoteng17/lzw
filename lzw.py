# -*- coding: utf-8 -*- 
import os
from struct import *


def lzw_compress(string):
	#设ASCII码0~255均为初始化字符，编码中添加字符串下标从256开始
	dictionary = {chr(i) : i for i in range(0,256)}
	pos = 256
	p = ''                   #初始化前缀串与编码结果集
	result = []
	for c in string:            #遍历待编码文本
		pc = p + c				#取当前串为前缀串加后一字符
		if pc in dictionary:	#如果当前串在编码字典中
			p = pc				#更新前缀串为当前串
		else:					#否则前缀串下标对应码字输出
			result.append(dictionary[p])
			dictionary[pc] = pos#将当前串存到编码字典最后
			pos += 1			#编码字典位置指针加一
			p = c				#更新前缀串为当前遍历字符
	if p :						#保证最后一个字符串编码完成
		result.append(dictionary[p])
	return result				#返回编码结果

def lzw_decompress(array):
#设ASCII码0~255均为初始化字符，解码中添加字符串下标从256开始
	dictionary = {i : chr(i) for i in range(0,256)}
	pos = 256
	result = []						#初始化解码结果集
	p = array.pop(0)				#取首字符初始化前缀串
	result.append(dictionary[p])	#首字符解码输出
	for c in array:              #遍历待解码文本
		if c in dictionary:      #如果遍历字符在解码字典中
			entry = dictionary[c]#将该遍历字符赋给当前串
	#如果遍历字符不在字典中且与字典下表指针相同（即将加入解码字典）
		elif c == pos:			 #将前缀串加首字符赋给当前串
			entry = dictionary[p] + dictionary[p][0]
		else:					 #否则编码有误，抛出异常
			raise ValueError('Compressed Error : %s' % c)
		result.append(entry)	 #将当前串作为解码输出
		#将前缀串下标对应字符串加当前串首字符合并加入解码字典
		dictionary[pos] = dictionary[p] + entry[0]
		pos += 1				 #解码字典位置指针加一
		p = c					 #更新前缀串为当前遍历字符
	#结果存在list类中，可转换成字符串格式返回，即和原文本相同格式
	return ''.join(result)

if __name__ == '__main__':
	f1 = open("text.txt", "r")         #待编码文本
	f2 = open("compress.txt", "wb")    #编码后文本
	f3 = open("decompress.txt", "w")   #解码后文本

	Input = f1.read()                  #读取文本
	
	#lzw编码与解码部分
	compressed_string = lzw_compress(Input)
	decompressed_string = lzw_decompress(compressed_string)
	
	for i in compressed_string:        #将编码文本写入f2
		f2.write(pack("H", i))	  #二进制写入以获得更大压缩比
	f3.write(decompressed_string)      #将解码文本写入f3

	f1.close()                         #关闭文件，下同
	f2.close()
	f3.close()