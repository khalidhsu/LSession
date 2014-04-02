#!/usr/bin/python
# -*- coding: utf-8 -*-
#  FileName    : HttpProxyVerifier.py 
#  Author      : Fledna <fledna@ymail.com> 
#  Created     : Fri Mar 11 17:31:33 2011 by fledna 
#  Copyright   : Fledna Workshop (c) 2011 
#  Description : Verify http proxy 
#  Time-stamp: <2011-03-16 10:04:46 fledna> 
 
import urllib2
import socket
socket.setdefaulttimeout(4.)
import logging
import re

PROXY_ALL='proxy_all.txt'
 
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('proxy.verifier')
 
 
def newOpener(proxy=''):
    ph = urllib2.ProxyHandler(proxy)
    opener = urllib2.build_opener(ph)
    return opener
 
def verifyProxyAccess(proxy,
                res_url="http://m.baidu.com/static/l.gif",
                res_size=1012):    
    proxy = dict(http=proxy, https=proxy, ftp=proxy)
    try:
        opener = newOpener(proxy)
        req = opener.open(res_url)
        if len(req.read())== res_size: # trick
            return True
        else:
            return False
    #except urllib2.URLError:
    except Exception as e:    
        print "Opener Err:",e
        return False



# pf = open('./proxlist','w')
# cnt=0
# def write_to_file(p):
#     pf.write(p+'\n')
    

 
def verifyProxy(proxy):
    global cnt
    p = proxy.strip()
    log.info('Verifing %s', p)
    if verifyProxyAccess(p, "http://m.baidu.com/static/l.gif", 1012):
        log.info('http ok!')
        write_to_file(p)
        cnt+=1
        print '------------------%d\n'%cnt
        # if verifyProxyAccess(p, "https://mail.google.com/", 234):
        #     log.info('https ok!')
        # if verifyProxyAccess(p, "ftp://ftp.pku.edu.cn/welcome.msg", 51):
        #     log.info('ftp ok!')



def verifyProxy_(proxy):
    p = proxy.strip()
    if verifyProxyAccess(p, "http://m.baidu.com/static/l.gif", 1012):
        return True
    else:
        return False
      




def getProxyList():
    ret = []
    headers = {"User-Agent": 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'}
    url = "http://proxy.ipcn.org/proxylist.html"
    try:
        req = urllib2.Request(url, headers=headers)
        html = urllib2.urlopen(req).read()
        pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)')
        ret.extend( pattern.findall(html) )
        open(PROXY_ALL,'w').write('\n'.join(ret))
    except Exception as e:
        print e
        ret=map(lambda x:x.strip(), open(PROXY_ALL,'r').readlines())
    return ret
 
def main():
    proxies = filter(None, getProxyList())
    for p in proxies:
        verifyProxy(p)
def main2():
    # print getProxyList()
    # return
    print getOneValidProxy()

def getOneValidProxy():
    proxies = filter(None, getProxyList())
    for p in proxies:
       if verifyProxy_(p) == True:
           return p
       else:
           print 'Proxy not accessible:',p
    return None



 
if __name__ == '__main__':
    main2()





