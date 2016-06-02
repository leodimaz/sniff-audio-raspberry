#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import signal
import sys
import os
import time
import smtplib
from email.mime.text import MIMEText
control=0
dimension_record=0
iter_state_size=0
iter_state_tcp=0
iter_state_exist=0
mail_sent=0

def sendEmail():
	to = "MYEMAIL"
	gmail_user = "MYUSER"
	gmail_password = "MYPASSWORD"
	smtpserver = smtplib.SMTP("smtp.myemail.com", 587)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.login(gmail_user, gmail_password)
	msg = MIMEText("Go to http://newl2mr.listen2myradio.com/login-free")
	msg["Subject"] = "Need to activate icecast"
	msg["From"] = gmail_user
	msg["To"] = to
	smtpserver.sendmail(gmail_user, [to], msg.as_string())
	smtpserver.quit()
def correctDarkice():
	try:
		subprocess.Popen(["sudo", "killall", "-9", "darkice"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except:
		print ""
def controlDarkiceConfig():
	f = open("/etc/darkice.cfg", "r")
	r = f.read()
	pos1 = r[0:1756]
	pos2 = r[1756:]
	f.close()
	if pos2 != "recording.mp3\n":
        	print "[ ] Darkice initial configuration error"
		correct = pos1+"recording.mp3\n"
        	f = open("/etc/darkice.cfg","w")
        	f.write(correct)
        	print "[+] Correct file"
        	f.close()

def run():
    global control, dimension_record, iter_state_size, iter_state_tcp, iter_state_exist, mail_sent
    i = time.strftime("%d-%m-%Y")
    j = time.strftime("%I_%M_%S")
    current_date = i+"-"+j
    while True:
	if control==0:
		print "[ ] Control 0"
		time.sleep(3)
		controlDarkiceConfig()
		try:
			config = open("/etc/darkice.cfg","r")
			data = config.read()
			data_correct = data.replace("recording.mp3",current_date+".mp3")
			print data_correct
			config.close()
			config = open("/etc/darkice.cfg","w")
			config.write(data_correct)
			config.close()
			control=1
			print "[+] /etc/darkice.cfg modified"
		except:
			control=0
			print "[-] Config writing error, retrying. Are you superuser?"
	if control==1:
		time.sleep(2)
		print "[ ] Control 1"
		try:
			subprocess.Popen(['sudo', 'darkice'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		except OSError:
            		print "[-] Darkice error, retrying"
		time.sleep(2)
		if os.path.isfile("records/"+current_date+".mp3"):
			print "[ ] I'm controlling if darkice works..."
			actual_dimension = os.path.getsize("records/"+current_date+".mp3")
			if iter_state_size==0:
				dimension_record=actual_dimension
				iter_state_size = iter_state_size + 1
			elif iter_state_size==1:
				if actual_dimension>dimension_record:
					control=2
					print "[+] STREAMING STARTED!"
				else:
					if iter_state_tcp == 3:
						print "[ ] Sending mail for activating icecast on linsten2myradio.com"
						sendEmail()
						mail_sent=1
					print "[-] Dimension file not increased, correcting darkice process..."
					iter_state_tcp = iter_state_tcp + 1
					correctDarkice()
	
	if control==2:
		print "[ ] Control 2"
		time.sleep(3)
		try:
			config = open("/etc/darkice.cfg","w")
			data_correct = data.replace(current_date+".mp3","recording.mp3")
			config.write(data_correct)
			config.close()
			control=3
			print "[+] /etc/darkice.cfg restored"
		except:
			control=2
			print "[-] Config rewriting error, retrying. Are you superuser?"

def exit_gracefully(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    try:
        if raw_input('\nReally quit? (y/n)> ').lower().startswith('y'):
            sys.exit(1)
    except KeyboardInterrupt:

        print 'Ok ok, quitting'
    sys.exit(1)

    signal.signal(signal.SIGINT, exit_gracefully)


if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    run()
