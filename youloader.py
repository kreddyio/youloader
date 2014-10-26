#!/usr/bin/env python

import pycurl
import cStringIO
import urllib2
import re
import sys
import time


def ret_enc_fmt(url):
	q = re.split('v=',url)[1]
	if '&' in q:
		q = q[:q.index('&')-1]
		# print q
	a = ''
	buf = ''
	# cnt = 0
	print 'Fetching the video info...'
	while not 'url_encoded_fmt_stream_map=itag' in a:
		try:
			# cnt += 1
			time.sleep(0.5)
			# c.setopt(c.WRITEFUNCTION, buf.write)
			# print a
			try:
				buf = urllib2.urlopen('https://www.youtube.com/get_video_info?&video_id='+q).read()
			except:
				pass
			a = buf
			# print cnt,'-',len(a)
		except KeyboardInterrupt:
			print 'Exiting...'
			sys.exit(1)
	return a


def parse(fin):
	print 'Parsing the info for video urls'
	i = fin.index('url_encoded_fmt_stream_map=itag')
	i1 = fin.index('adaptive_fmts')
	if i1>i:
		fin = fin[i:i1]
	else:
		fin = fin[i:]
	s = fin.split(',itag=')
	n = len(s)
	s[0] = s[0].replace("url_encoded_fmt_stream_map=",'')
	for x in xrange(1,n):
		# i = s[x].index('http://')
		# s[x] = s[x][i:]
		s[x] = 'itag='+s[x]
	k = s[n-2].split('&')
	k1 = len(k)
	param = k[k1-1].split('=')[0]
	k2 = len(s[n-1]) - s[n-1][::-1].index(param[::-1]) - len(param)
	k3 = s[n-1][k2:].find('&')
	if k3 != -1:
		s[n-1] = s[n-1][:k2+k3]
	# for i in xrange(n):
		# s[i] = "\""+s[i]+"\""
	return s,n


def prettify(size):
	return "%.2f"%size


def getsize(url):
    site = urllib2.urlopen(url)
    meta = site.info()
    size = int(meta.getheaders("Content-Length")[0])
    if 0<size<1024: # bytes
    	size = prettify(size)+'bytes'
    elif 1024<size<1024*1024: #KB
    	size = prettify(size/1024.)+'KB'
    elif 1024*1024<size<1024*1024*1024: # MB
    	size = prettify(size/(1024*1024.))+'MB'
    else:
    	size = prettify(size/(1024*1024*1024.))+'GB'
    return size


def getquality(s):
	try:
		a = re.findall(r"quality=(.*?)&",s)[0]
	except:
		a = re.findall(r"quality=(.*?),",s)[0]
	return a


def gettype(s):
	try:
		a = re.findall(r"type=video/(.*?)&",s)[0]
	except:
		try:
			a = re.findall(r"type=video/(.*?);",s)[0]
		except:
			# a = re.findall(r"type=video/(.*?)",s)[0]
			a = 'flv'
	if 'codecs' in a:
		i = a.index(';')
		a = a[:i]
	return a


def download(url,filename):
	print "Preparing to download the video..."
	try:
		f = urllib2.urlopen(url)

		# Open our local file for writing
		with open(filename, "wb") as local_file:
		    local_file.write(f.read())
    #handle errors
	except urllib2.HTTPError, e:
		print "HTTP Error:", e.code, url
	except urllib2.URLError, e:
		print "URL Error:", e.reason, url


if __name__ == '__main__':
	url = raw_input("Enter the youtube 'video' url of any format:\n")
	site = urllib2.urlopen(url)
	data = site.read()
	site.close()
	title = re.findall(r'<title>(.*?)</title>',data)
	name = title[0]
	print name
	fin = urllib2.unquote(ret_enc_fmt(url))
	while '%25' in fin:
		fin = urllib2.unquote(fin)
	fin = urllib2.unquote(fin)
	fin = fin.replace("\"","\'")
	f = open("log","w") 
	f.write(fin)
	f.close()
	s,n = parse(fin)
	urls = []
	types = []
	qual = []
	sizes = []
	for i in s:
		l = i.split("&url=")
		print l[1]
		types.append(gettype(i))
		qual.append(getquality(i))
		urls.append(l[1])
		sizes.append(getsize(l[1]))
	# sys.exit(1)
	print 'Found',n,'videos associated with the link. Ordering them as follows:'
	print 'id\tquality\ttype\tsize'
	for i in range(n):
		print "%d\t%s\t%s\t%s"%(i+1,qual[i],types[i],sizes[i])
	vid = int(raw_input('Enter id of video you want to download:')) - 1
	download(urls[vid],name+'.'+types[vid])
	print 'Finished Donwloading. :)'