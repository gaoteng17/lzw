[TOC]

# 1 概述

LZW 压缩技术由以色列人 Lempel 和 Ziv 共同提出，美国人 Welch 将其从概念发展到实用阶段。LZW使用字典库查找方案。它读入待压缩的数据并与一个字典库（库开始是空的）中的字符串对比，如有匹配的字符串，则输出该字符串数据在字典库中的位置索引，否则将该字符串插入字典中。LZW广泛应用于**无损数据压缩**，包括无损图像压缩领域，包括 GIF、TIFF、PNG 等格式图像文件。

本篇文章使用Python3.6工具、win10(64bit)环境，实现LZW的编码及解码流程，并测试编解码效果。除此之外，提出一些改进的想法，并作简单分析与思考。

# 2 算法思想

## 2.1 编码

LZW的编码思想如以下流程所示：
1. 初始化编码字典，其中含有所有可能出现的单字符。
2. 从字典中查找匹配当前字符串前缀的最长字符串W。
3. 将W的字典下标作为编码输出并从当前字符串中删去W。 
4. 将W和W在当前字符串中的后续字符合并添加到编码字典中。
5. 重复步骤2。

举例如下：

__输入数据流__

| 位置   | 1    | 2    | 3    | 4    | 5    | 6    | 7    | 8    | 9    |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| 字符   | A    | B    | B    | A    | B    | A    | B    | A    | C    |

__编码过程__

| 序号   | 位置   | 索引   | 字典   | 输出   |
| ---- | ---- | ---- | ---- | ---- |
|      |      | 1    | A    |      |
|      |      | 2    | B    |      |
|      |      | 3    | C    |      |
| 1    | 1    | 4    | AB   | 1    |
| 2    | 2    | 5    | BB   | 2    |
| 3    | 3    | 6    | BA   | 2    |
| 4    | 4    | 7    | ABA  | 4    |
| 5    | 6    | 8    | ABAC | 7    |
| 6    |      |      |      | 3    |


## 2.2 解码

LZW的解码思想如以下流程所示：
1. 初始化解码字典，其中含有所有可能出现的下标(对应编码字典)。
2. 从字典中查找匹配当前待解码字符的下标W。
3. 将P和W对应字符串首字符合并添加到解码字典中。
4. 将W在解码字典中对应的字符串作为解码输出并把输出存为旧字符串P。 
5. 重复步骤2。

举例如下：

__输入数据流__

| 位置   | 1    | 2    | 3    | 4    | 5    | 6    |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| 字符   | 1    | 2    | 2    | 4    | 7    | 3    |

__解码过程__

| 序号   | 数据   | 旧字符串 | 输出   | 索引   | 字典   |
| ---- | ---- | ---- | ---- | ---- | ---- |
|      |      |      |      | A    | 1    |
|      |      |      |      | B    | 2    |
|      |      |      |      | C    | 3    |
| 1    | 1    |      | A    |      |      |
| 2    | 2    | A    | B    | AB   | 4    |
| 3    | 2    | B    | B    | BB   | 5    |
| 4    | 4    | B    | AB   | BA   | 6    |
| 5    | 7    | AB   | ABA  | ABA  | 7    |
| 6    | 3    | ABA  | C    | ABAC | 8    |

# 3 实现

## 3.1 文件操作

待编码原文本存在text.txt中；将lzw编码后的文本存到compress.txt中；之后再次通过lzw解码的文本存到decompress.txt中：

``` python
	import os
	from struct import *
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
```

## 3.2 编码部分

首先建立编码字典，其中含有所有可能出现的单字符：

``` python
	#设ASCII码0~255均为初始化字符，编码中添加字符串下标从256开始
	dictionary = {chr(i) : i for i in range(0,256)}
	pos = 256
	p = ''                   #初始化前缀串与编码结果集
	result = []
```

然后依次对字符串进行编码，动态更改编码字典：

``` python
	for c in string:            #遍历待编码文本
		pc = p + c				#取当前串为前缀串加后一字符
		if pc in dictionary:	#如果当前串在编码字典中
			p = pc				#更新前缀串为当前串
		else:					#否则前缀串下标对应码字输出
			result.append(dictionary[p])
			dictionary[pc] = pos#将当前串存到编码字典最后
			pos += 1			#编码字典位置指针加一
			p = c				#更新前缀串为当前遍历字符
```

最后返回编码结果：

``` python
	if p :						#保证最后一个字符串编码完成
		result.append(dictionary[p])
	return result				#返回编码结果
```

## 3.3 解码部分

首先建立解码字典，其中含有所有可能出现的单字符：

``` python
	#设ASCII码0~255均为初始化字符，解码中添加字符串下标从256开始
	dictionary = {i : chr(i) for i in range(0,256)}
	pos = 256
	result = []						#初始化解码结果集
	p = array.pop(0)				#取首字符初始化前缀串
	result.append(dictionary[p])	#首字符解码输出
```

然后依次对字符串进行解码，动态更改解码字典：

``` python
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
```

最后返回解码结果：

``` python
	#结果存在list类中，可转换成字符串格式返回，即和原文本相同格式
	return ''.join(result)
```

# 4 结果

本文使用了17.8KB的《I have a dream》与635KB的《Wuthering Heights》作为测试文本对上一章节的LZW编码进行测试，测试结果如下表：

| 文件名称                | 大小    | 字符数    | 编码码字   | 编码大小   | 压缩比   |
| ------------------- | ----- | ------ | ------ | ------ | ----- |
| 《I have a dream》    | 17.8K | 18138  | 5674   | 9.0K   | 50.6% |
| 《Wuthering Heights》 | 635K  | 645611 | 143912 | 281.0K | 44.3% |

由此表可以看出，LZW编码存在**文本量越大，编码压缩效果越好**的特性。

# 5 思考

在第3章实现了LZW的编码和解码后，自然对LZW压缩算法产生一些思考。通过网络查询，发现了以下几种提高LZW压缩率的改进途径：

1. 混合使用LZ77和LZ78。即在发现标记匹配结束后，不立即结束匹配，而是再在一个滑动窗口中寻找是否有更好的匹配，如果有就以{位置，匹配长度}组的形式写入输出流中，并把该字符串逐个增加为标记。
2. 使用固定长度字节的编码，即设定编码字典的长度，当编码字典满了之后清空字典。
3. 实时检测压缩率，当压缩率下降到一定阈值时，清空编码字典。

这些途径都各有优缺。

第一种途径可以很大地提高压缩比。但滑动窗口的选择是个复杂的问题。而且匹配长字符串会增加很多标记，使字典增加过快。

第二种途径压缩速度快，压缩效率较高，该方法也广为使用。

第三种途径在一般情况下应该有不错效果，但在源文件的统计规律发生较大变化大情况下，等发现字典不合适后再重建可能就来不及了。如果和其它的方法结合使用可能更好。

综合各点，可以看出，在不特别考虑速度的情况下，LZW的编码压缩率主要集中于**码字长度**与**码字个数**上。

结合第二种途径分析，我觉得可以在清空字典这一环节上加以改进。比如并不完全清空字典，只清空掉使用率低的码字。但这种方法实现复杂，会增加很大开销。因此采用比较折中的方法，即清空时只清空一半，保留一半原编码字典。

针对此方法，修改LZW编码部分关键代码如下：

``` python
	for c in string:
		pc = p + c
		if pc in dictionary and dictionary[pc]<pos: 
			p = pc				#避免访问到字典已清空部分
		else:
			result.append(dictionary[p])
			dictionary[pc] = pos
			pos += 1
			p = c
		if pos == 65536:        #设定编码字典长度16位
			pos = pos>>1		#超过长度时清空一半字典
```

使用《Wuthering Heights》测试此方法压缩效果并与原LZW压缩算法对比如下表：

| 压缩方法    | 码字个数   | 码字长度     | 编码大小   | 压缩比   |
| ------- | ------ | -------- | ------ | ----- |
| 不清空字典编码 | 125909 | 3(17bit) | 368.9K | 50.6% |
| 全清空字典编码 | 143912 | 2(16bit) | 281.0K | 44.3% |
| 半清空字典编码 | 129694 | 2(16bit) | 253.3K | 39.9% |

可以看到，该方法针对全清空字典方案压缩率有小幅度提升。但同时也承认，在极端情况下，即**未清空部分字典出现频率极低（甚至只出现一次）的情况下，只清空一半的方式反而不会得到太好的压缩效率。**

# *附录*

此处给出第3章节LZW编解码部分完整代码：
``` python
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
```
``` python
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
```

由于篇幅问题，LZW改进部分只在第5章节给出了核心代码，如需查阅**改进部分完整代码**及**测试文本**《I have a dream》、《Wuthering Heights》，请访问我的github页面：https://github.com/gaoteng17/lzw