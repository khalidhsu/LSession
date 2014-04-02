#!/usr/bin/env python  
#-*-coding:utf-8-*-'  
  
import sys, os
import io, socket
from cookielib import MozillaCookieJar, CookieJar
import cookielib
from urllib2 import Request, build_opener, HTTPHandler, HTTPCookieProcessor, ProxyHandler
from urllib2 import HTTPError
from urllib import urlencode,urlretrieve
import urllib2
from time import sleep
import traceback
try:
    from ipcnproxy import getOneValidProxy
except ImportError as e: print e

###TODO test_proxy
###TODO getProxyList may occur err,dowload the file first
###TODO cookie jar add lwcookie

class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        print "Cookie Manip Right Here"
        print req.url
        ret = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        ret.status = 404
        return ret


class LSession():
    def __init__(self, cookiefile=None, proxy=None, timeout=10, retime=30, sleept=3):
        """
        retime :retry time
        sleept: sleep time before retrying
        """
        self.timeout = timeout
        self.retime = retime
        self.sleept = sleept
        self._text = ''
        #proxy '1.234.77.96:80'
        if cookiefile is None:
            self.cookiejar = CookieJar()
        else:
            self.cookiejar = MozillaCookieJar(filename=cookiefile)
            #self.cookiejar =cookielib.LWPCookieJar(filename=cookiefile)
            if not os.path.isfile(cookiefile):
                open(cookiefile, 'w').write(MozillaCookieJar.header)
                #open(cookiefile, 'w').write('#abc\n')
                pass
            self.cookiejar.load(filename=cookiefile,ignore_discard=True)
            #print "ck:",self.cookiejar 
        self.cookie_processor = HTTPCookieProcessor(self.cookiejar)
        self.opener = build_opener(urllib2.HTTPRedirectHandler(),self.cookie_processor)
        if proxy: self.opener.add_handler(ProxyHandler({"http" : proxy}))
        #for posting a file
        try:
            import MultipartPostHandler #for posting a file,need installed
            self.opener.add_handler(MultipartPostHandler.MultipartPostHandler())
        except NameError as e:print e
            
        self.resp = None
        self.req = None
        self.header = []

    def add_header(self, k, v): self.header.append((k,v))

    def build_request(self,url,params=None):
        self.req = Request(url,params)
        if not self.resp is None:self.req.add_header('Referer',self.url())
        #self.request.add_header('User-Agent',
        #                        'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 \
        #                        (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25')
        #NokiaE63/UC Browser7.9.0.102/28/355/UCWEB
        #self.request.add_header('User-Agent','NokiaE63/UC Browser7.9.0.102/28/355/UCWEB')
        #self.request.add_header('User-Agent','Opera/9.80 (J2ME/MIDP; Opera Mini/1.0/886; U; en) Presto/2.4.15')
        #        User-Agent:
        # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36
        self.req.add_header('User-Agent', ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                                          '(KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'))

        for _k, _v in self.header: self.req.add_header(_k,_v)
        #Mobile/7B405
        #self.request.add_header('User-Agent','Mobile/7B405')
        return self.req

    def __del__(self): self.save_cookie()

    def _urlopen(self, req):
        retime = self.retime
        while retime > 0:
            try:
                return self.opener.open(req, timeout=self.timeout)
            except Exception as e:
                retime -= 1
                traceback.print_exc(file=sys.stdout)
                print 'Wait %ss and retry...%d' % (self.sleept, self.retime - retime)
                sleep(self.sleept)

    def savefile(self, filename, url):
        self.resp = self._urlopen(self.build_request(url))
        CHUNK = 50 * 1024
        with open(filename, 'wb') as fp:
            while True:
                chunk = self.resp.read(CHUNK)
                if not chunk: break
                fp.write(chunk)

    def post(self, url, post_data):
        """
        post_data:  {k1:v2,k2:v2}
        """
        self.resp = self._urlopen(self.build_request(url,urlencode(post_data)))
        return self.resp

    def post_raw(self, url, post_data):
        """
        post_data:  k1=v1&k2=v2
        """
        self.resp = self._urlopen(self.build_request(url,post_data))
        return self.resp

    def post_file(self, url, params):
        """
        params:  {k1:v2, k2:v2，filename1：filepath1}
        """
        self.resp = self._urlopen(self.build_request(url, params))
        return self.resp

    def get(self, url):
        self.resp = self._urlopen(self.build_request(url))
        #import urllib
        #print  urllib.urlopen('http://mrozekma.com/302test.php').geturl()
        # import requests
        # r=requests.get(url)
        # print r.content
        return self.resp
    #def getx(self): return self._x
    #def setx(self, value): self._x = value
    #def delx(self): del self._x
    #x = property(getx)

    def text(self, dec='gbk', enc='utf8'):
        _n = self.resp.read()
        if len(_n) > 0: self._text = _n
        return self._text.decode(dec).encode(enc)

    def url(self): return self.resp.url

    def logout(self): self.cookiejar.clear()

    def verify_proxy(self):
        pass

    def show_cookie(self):
        #print self.cookiejar
        for i in self.cookiejar:
            print i

    def save_cookie(self):
        # if  hasattr(self.cookiejar,'save'):#in case non cookiejar
        #     self.cookiejar.save(ignore_discard=True, ignore_expires=False)
        try: 
            self.cookiejar.save(ignore_discard=True, ignore_expires=False)
        except Exception as e:
            pass
            #traceback.print_exc(file=sys.stdout)
        

def write_log(_file, log):
    f = io.open(_file, 'a', encoding='utf-8')
    f.write(log)

ls = LSession()

def change_ls_proxy():
    global ls
    p = getOneValidProxy()
    if p is None:
        raise Exception("Proxy Error")
    else: 
        print "Got a proxy:", p
    #ls=LSession(proxy='58.32.208.251:8080')
        ls = LSession(proxy=p)


def main(argv):
    ls.get('http://www.baidu.com')
    print ls.text(dec = 'utf8')
    

def back_script_dir():
    os.chdir(os.path.dirname(__file__))


if __name__=="__main__":  
    back_script_dir()
    main(sys.argv[1:])  











