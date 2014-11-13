#!/usr/bin/env python

import os
import cStringIO
import urllib2
import re
import sys
import time
from threading import Thread
import HTMLParser


def ret_enc_fmt(url): # returns the encoded info

	q = re.split('v=',url)[1]
	if '&' in q:
		q = q[:q.index('&')-1]
	a = ''
	buf = ''
	cnt = 0
	print 'Fetching the video info (might take a while)...'
	while not 'url_encoded_fmt_stream_map=itag' in a:
		try:
			cnt += 1
			# print cnt
			# time.sleep(0.5)
			try:
				buf = urllib2.urlopen('https://www.youtube.com/get_video_info?&video_id='+q).read()
			except:
				pass
			a = buf
		except KeyboardInterrupt:
			print 'Exiting...'
			sys.exit(1)
	print cnt
	return a


def parse(fin):

	print 'Parsing the info for video urls...'
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
		s[x] = 'itag='+s[x]
	k = s[n-2].split('&')
	k1 = len(k)
	param = k[k1-1].split('=')[0]
	k2 = len(s[n-1]) - s[n-1][::-1].index(param[::-1]) - len(param)
	k3 = s[n-1][k2:].find('&')
	if k3 != -1:
		s[n-1] = s[n-1][:k2+k3]
	return s,n


def prettify(size):

	if 0<size<1024: # bytes
		size = size+'B'
	elif 1024<size<1024*1024: # KB
		size = "%.2f"%(size/1024.)+'KB'
	elif 1024*1024<size<1024*1024*1024: # MB
		size = "%.2f"%(size/(1024*1024.))+'MB'
	else: # GB
		size = "%.2f"%(size/(1024*1024*1024.))+'GB'
	return size


def getsize(url):

    site = urllib2.urlopen(url)
    meta = site.info()
    size = int(meta.getheaders("Content-Length")[0])
    return size


def getquality(s): # returns quality of the video

	try:
		a = re.findall(r"quality=(.*?)&",s)[0]
	except:
		try:
			a = re.findall(r"quality=(.*?),",s)[0]
		except:
			a = s.split('quality=')[1]
	return a


def gettype(s): # returns filetype of the video

	try:
		a = re.findall(r"type=video/(.*?)&",s)[0]
	except:
		try:
			a = re.findall(r"type=video/(.*?);",s)[0]
		except:
			a = 'flv'
	if 'codecs' in a:
		i = a.index(';')
		a = a[:i]
	if a == 'x-flv':
		a = 'flv'
	return a


def download(url,filename):

	try:
		u = urllib2.urlopen(url)
		f = open(filename,"wb")
		block = 8192
		while True:
			buf = u.read(block)
			if not buf:
				break
			f.write(buf)
		f.close()
		u.close()
    #handle errors
	except urllib2.HTTPError, e:
		print "HTTP Error:", e.code, url
	except urllib2.URLError, e:
		print "URL Error:", e.reason, url
	except:
		print "Error!"


def gettitle(url):	

	site = urllib2.urlopen(url)
	data = site.read()
	site.close()
	title = re.findall(r'<title>(.*?)</title>',data)
	hp = HTMLParser.HTMLParser()
	name = hp.unescape(title[0])
	return name


def progressbar(filename, size):
    sizes = 0
    limit = 1
    prev = 0
    t = 0
    kb = 1024
    mb = 1024 * kb
    gb = 1024 * mb
    totspeed = 0
    prev10 = 0
    while (True):
		time.sleep(limit)
		t += limit
		sizes = os.path.getsize(filename)
		percent = (sizes / float(size)) * 100
		dloaded = float(sizes - prev)
		if t % 10 == 0 and sizes == prev10:
		    break
		if dloaded <= kb:
		    speed = str(dloaded)
		    val = 'bps'
		elif kb < dloaded <= mb:
		    speed = str(dloaded / kb)
		    val = 'kbps'
		elif mb < dloaded <= gb:
		    speed = str(dloaded / mb)
		    val = 'mbps'
		print '\r',
		sys.stdout.flush()
		print sizes, 'bytes done', "%2.2f" % (percent), '%', 'done.', "%3.2f" % (float(speed)), "%s" % (val),
		print '\r',
		sys.stdout.flush()
		if sizes == size:
		    print '\n'
		    avspeed = size / float(t)
		    if avspeed <= kb:
		        avspeed = avspeed
		        val = 'bps'
		    elif kb < avspeed <= mb:
		        avspeed = avspeed / kb
		        val = 'kbps'
		    elif mb < avspeed <= gb:
		        avspeed = avspeed / mb
		        val = 'mbps';
		    print 'Download completed in %d seconds at %0.2f %s ' % (t, avspeed, val)
		    break
		prev = sizes
		if t % 10 == 0:
			prev10 = sizes


def main():

	url = raw_input("Enter the youtube 'video' url of any format:\n")
	name = gettitle(url)
	print "Videoname: \"%s\"" % name

	fin = urllib2.unquote(ret_enc_fmt(url))
	while '%25' in fin:
		fin = urllib2.unquote(fin)
	fin = urllib2.unquote(fin)
	fin = fin.replace("\"","\'")

	f = open("log.txt","w") # writes the info to log file
	f.write(fin)
	f.close()

	s,n = parse(fin) # get all the strings and no. og urls
	# lists to hold attributes of each video
	urls = []
	types = []
	qual = []
	sizes = []

	for i in s: # get attributes of each video
		l = i.split("&url=")
		# print l[1]
		types.append(gettype(i))
		qual.append(getquality(i))
		urls.append(l[1])
		try:
			sizes.append(prettify(getsize(l[1])))
		except:
			sizes.append(0)

	print 'Found',n,'videos associated with the link. Ordering them as follows:'
	print 'id\tquality\ttype\tsize'
	for i in range(n):
		print "%d\t%s\t%s\t%s"%(i+1,qual[i],types[i],sizes[i])
	vid = int(raw_input('Enter id of video you want to download:\n')) - 1

	filename = name+'.'+types[vid]
	size = sizes[vid]
	durl = urls[vid]
	print "Preparing to download the video..."
	dl = Thread(target=download, args=[durl,filename])
	dl.setDaemon(True)
	dl.start()

	progress = Thread(target=progressbar, args=[filename, getsize(durl)])
	progress.setDaemon(True)
	progress.start()
	progress.join()
	
	dl.join()
	# print 'Finished Donwloading. :)'
if __name__ == '__main__':
	main()