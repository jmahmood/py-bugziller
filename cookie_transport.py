import xmlrpclib


"""
The reason we are using this transport is to preserve cookies.

You may need to modify this file if the cookie names on bugzilla are changed :/

This is setup for Python 2.6 and 2.7.  xmlrpclib changes in Python 3.  
I may produce a Python3 version of this if there is any demand.
"""
class CookieTransport(xmlrpclib.Transport):
    def __init__(self, SESSION_ID_STRING='PHPSESSID'):
        xmlrpclib.Transport.__init__(self)
        self.mycookies=None
        self.mysessid=None
        self.SESSION_ID_STRING = SESSION_ID_STRING

    def extract_bugzilla_cookies(self,s):
        # print "Extracting Bugzilla Cookie Values: %s" % s
        if s is None:
            return {self.SESSION_ID_STRING:None}
        BugzillaCookieKeys = ['Bugzilla_logincookie','Bugzilla_login']
        headers = [t.replace('HttpOnly, ','').split("=") for t in s.split(';')]
        return dict(((k[0].strip(), k[1].strip())
            for k in headers if len(k) == 2 
            and k[0].strip() in BugzillaCookieKeys))

    def set_header_cookies(self,h):
        if self.mysessid:
            h.putheader("Cookie", "%s=%s" % (
                self.SESSION_ID_STRING,self.mysessid) )
        elif self.mycookies:
            for k,v in self.mycookies.iteritems():
                h.putheader("Cookie", "%s=%s" % (k,v) )

    def add_new_cookies(self,headers):
        if self.mysessid is None:
            self.mycookies = self.extract_bugzilla_cookies( 
                headers.getheader('set-cookie') )
            if self.mycookies.has_key(self.SESSION_ID_STRING):
                self.mysessid = self.mycookies[self.SESSION_ID_STRING]

    def check_error_codes(self,errcode):
        if errcode is not 200:
            raise xmlrpclib.ProtocolError(
                host + handler, errcode, errmsg, headers)
    
    def request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request
        h = self.make_connection(host)

        if verbose:
            h.set_debuglevel(1)
        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.set_header_cookies(h)
        self.send_user_agent(h)
        self.send_content(h, request_body)
        errcode, errmsg, headers = h.getreply()

        self.add_new_cookies(headers)
        self.check_error_codes(errcode)
        self.verbose = verbose
        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None
        return self._parse_response(h.getfile(), sock)