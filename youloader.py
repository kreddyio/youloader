#!/usr/bin/python
from bs4 import BeautifulSoup as bs
import re
import urllib2
import sys
from prettytable import PrettyTable as pt
from threading import Thread
import os
import time


def getsize(url):

    site = urllib2.urlopen(url)
    meta = site.info()
    size = int(meta.getheaders("Content-Length")[0])
    return size


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


def gettype(s): # returns filetype of the video

	s = urllib2.unquote(s)
	try:
		a = re.findall(r"video/(.*?)&",s)[0]
	except:
		try:
			a = re.findall(r"video/(.*?);",s)[0]
		except:
			a = 'flv'
	if 'codecs' in a:
		i = a.index(';')
		a = a[:i]
	if a == 'x-flv':
		a = 'flv'
	return a


def download(url,dest,size):
	try:
		print 'started'
		u = urllib2.urlopen(url)
		f = open(dest,"wb")
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
	except Exception,e:
		print "Error!",e


def main(url):
	html = urllib2.urlopen(url).read()
	soup = bs(html)
	title = soup.title.string.replace(' - YouTube','')
	encoded_links = re.findall(r"\"url_encoded_fmt_stream_map\":\"(.*?)\"",html)[0]
	encoded_links2 = re.findall(r"\"adaptive_fmts\":\"(.*?)\"",html)[0]
	link_list = encoded_links.split(',')
	ll2 = encoded_links2.split(',')
	for i in ll2:
		if '1920x1080' in i:
			link_list.append(i)
			break
	fin_list = []
	for i in link_list:
		d = {'url':'','quality':'','type':''}
		if '1920x1080' in i:
			d['quality'] = '1080p'
		l = i.split('\u0026')
		for j in l:
			dct = j.split('=')
			d[dct[0]] = dct[1]
		fin_list.append(d)
	for i in fin_list:
		while '%25' in i['url']:
			i['url'] = urllib2.unquote(i['url'])
		i['url'] = urllib2.unquote(i['url'])
	# print fin_list
	print 'Found %d videos.' % (len(fin_list))
	id = 0
	table = pt(["id","quality","type","size"])
	for i in fin_list:
		table.add_row([id,i['quality'],gettype(i['type']),prettify(getsize(i['url']))])
		id += 1
	print table
	print 'Select any one of the above videos using id:'
	a = int(raw_input())
	# print fin_list[a]
	print "Preparing to download the video..."
	sz = getsize(fin_list[a]['url'])
	size = prettify(sz)
	dest = title+'.'+gettype(fin_list[a]['type'])
	dl = Thread(target=download, args=[fin_list[a]['url'],dest,sz])
	dl.setDaemon(True)
	dl.start()
	progress = 0
	while progress != 100:
		time.sleep(2)
		progress = 100 * os.path.getsize(dest)/float(sz)
		sys.stdout.write("\r [%s%s] %0.2f%% done of %s" % ("#"*int(progress/10),
                    "-"*(10-int(progress/10)),progress,size))
		sys.stdout.flush()
	dl.join()
	print '\nDownload Finished.\n'
if __name__ == '__main__':
	url = sys.argv[1]
	main(url)
