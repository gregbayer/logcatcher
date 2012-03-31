import urllib

params = urllib.urlencode({'category': 'application1', 'message': 'this is a test\nwith two lines even', 'hash': 'RlUP891xJUVC3cCxqlpTctjBzVk='})
f = urllib.urlopen("http://localhost:8080/put_logs?%s" % params)
print f.read()
