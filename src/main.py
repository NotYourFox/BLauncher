#!/usr/bin/python3

import minecraft_launcher_lib
import os
import sys
import json
from threading import Thread
import subprocess
import requests
from tkinter import *
from tkinter import ttk
from time import sleep
from tkinter import messagebox as mb
from tkinter import simpledialog as sd
import random
import string
import uuid

import lang # language module

# =================== #
#      SETTINGS       #
# =================== #

path = 'game' # folder to install Minecraft
version_code = 2 # do not change this
check_for_updates = True 

# =================== #
#      FUNCTIONS      #
# =================== #

# get versions
if not(os.path.isdir(os.path.join(path, 'versions'))):
	os.mkdir(path)
	os.mkdir(os.path.join(path, 'versions'))

installed_ver = []
all_ver = []
ver_list = []

for i in minecraft_launcher_lib.utils.get_installed_versions(path):
	installed_ver.append(i.get("id"))

for i in minecraft_launcher_lib.utils.get_version_list():
	all_ver.append(i.get("id"))

ver_list.append(lang.installed + ":")
ver_list.extend(installed_ver)
ver_list.append(lang.ready_to_install + ":")
ver_list.extend(all_ver)

def logger(string):
    log.configure(state="normal")
    log.insert(END, string + "\n")
    log.yview(END)
    log.configure(state="disabled")
    root.update()

def downloader(url, name):
	file = open(name, "wb")
	request = requests.get(url)
	file.write(request.content)
	file.close()

def show_settings():
	pass

def setProgress(value, max_value):
	progresspersent = max_value[0] / 100
	progr = value / progresspersent
	progress["value"] = progr
	root.update()

def setMax(max_value, value):
	max_value[0] = value

def run():
	if version.get() in installed_ver or version.get() in all_ver:
		runbtn.configure(state='disabled')
		nick.configure(state='disabled')
		version.configure(state='disabled')
		nickname = nick.get()
		ver = version.get()
		rp = open(os.path.join(path, 'profile.json'), 'r')
		try:
			profile = json.load(rp)
		except Exception as e:
			createProfile()
			rp = open(os.path.join(path, 'profile.json'), 'r')
			profile = json.load(rp)

		rp.close()

		with open(os.path.join(path, 'profile.json'), 'w') as pj:
			pj.write(json.dumps({
				'nick': nickname,
				'version': ver,
				'uuid': profile['uuid'],
				'token': profile['token']
				}))
		max_value = [0]
		callback = {
			"setStatus": lambda text: logger(text),
			"setProgress": lambda value: setProgress(value, max_value),
			"setMax": lambda value: setMax(max_value, value)
		}
		minecraft_launcher_lib.install.install_minecraft_version(ver, path, callback)
		
		options = {
			'username': nickname,
			'uuid': profile['uuid'],
			'token': profile['token']
		}
		command = minecraft_launcher_lib.command.get_minecraft_command(ver, path, options)
		subprocess.Popen(command)
		runbtn.configure(state='normal')
		nick.configure(state='normal')
		version.configure(state='normal')

	else:
		mb.showerror(lang.error, lang.version_is_not_detected)
def runner():
	try:
		run()
	except Exception as e:
		raise e

def mojanglogin():
    login = sd.askstring('BLauncher', lang.ask_mojang_login)
    password = sd.askstring('BLauncher', lang.ask_mojang_password)
    try:
        login_data = minecraft_launcher_lib.account.login_user(login, password)
        isl = True
		
    except Exception as e:
        logger(lang.error_during_login)
        isl = False
    if isl:
        try:
            exc = login_data["error"]
            errmessage = login_data["errorMessage"]
            if errmessage == 'Invalid credentials. Invalid username or password.':
                logger('Invalid username or password.')
        except KeyError as ke:
            exc = None
        if exc == None:
            with open(os.path.join(path, 'profile.json'), 'w') as pj:
                pj.write(json.dumps({
			    	'nick': login_data["selectedProfile"]["name"],
				    'version': version.get(),
				    'uuid': login_data["selectedProfile"]["id"],
				    'accToken': login_data["accessToken"]
				    }))


def update_check():
	logger("Checking for updates...")
	version_c = requests.get("https://raw.githubusercontent.com/maxgrt/BLauncher/master/src/version_code.txt")
	last = int(version_c.content.decode("utf-8"))
	if last > version_code:
		logger("Update found! Downloading...")
		thread1 = Thread(target=downloader, args=("https://github.com/maxgrt/BLauncher/archive/master.zip", "update.zip"))
		thread1.start()
		thread1.join()
		#downloader("https://github.com/maxgrt/BLauncher/archive/master.zip", "update.zip")
		logger("Update.zip downloaded.")
		if mb.askyesno('BLauncher', lang.can_i_upgrade):

			root.destroy()
			py_executable = sys.executable
			os.system(py_executable + " update.py")
	else:
		logger("No updates found")

def createProfile():
	with open(os.path.join(path, 'profile.json'), 'w') as rp:
		rp.write(json.dumps({
			'nick': 'Steve',
			'uuid': str(uuid.uuid1()),
			'token': str(uuid.uuid1())
			}))

# =================== #
#       TKINTER       #
# =================== 

WIDTH = 1280 #Screen resolution settings.
HEIGHT = 800
root = Tk()
root.title("BLauncher")
root.minsize(width=WIDTH, height=HEIGHT)
root.resizable(False, False)

# MENUBAR
#menubar = Menu(root)
#root.config(menu=menubar)

#file_menu = Menu(menubar)
#file_menu.add_command(label=lang.settings, command=show_settings)
#file_menu.add_command(label=lang.exit, command=exit)
#menubar.add_cascade(label=lang.file, menu=file_menu)

f_top = Frame(root)
f_top.place(width = WIDTH, relheight = 500/800)
f_bottom = Frame(root)
f_bottom.place(rely=500/800, width = WIDTH, relheight = 300/800)

log = Text(f_top, state='disabled', font='TkFixedFont {}'.format(int(20*(HEIGHT/800))))
log.place(relx = 0.03125, rely = 0.125, relwidth = 0.9375, relheight = 0.72)
progress = ttk.Progressbar(f_top, length=100)
progress.place(relwidth = 0.9375, relx = 0.03125, rely = 0.845)

# SECTION OPTIONS
f_account_relwidth = 0.3125 # 1280 -> 400, WIDTH -> f_width
f_version_relwidth = 0.3125 # 1280 -> 400, WIDTH -> f_width
f_run_relwidth = 0.078125 # 1280 -> 100, WIDTH -> f_width
f_account_width = WIDTH*f_account_relwidth
f_version_width = WIDTH*f_version_relwidth
f_run_width = WIDTH*f_run_relwidth
summary_width = f_account_width + f_version_width + f_run_width
dmx = ((WIDTH - summary_width)/2 - 0.03125*WIDTH)/WIDTH

# ACCOUNT SECTION
f_account = LabelFrame(f_bottom, text=lang.account)
f_account.place(relx = 0.03125 + dmx, width=f_account_width)

txt1 = Label(f_account, text=lang.nick)
txt1.pack()
nick = Entry(f_account, width = 25)
nick.pack()
mlogin = Button(f_account, text=lang.mojang_login, command=mojanglogin)
mlogin.pack(fill='x')

# VERSION SECTION
f_version = LabelFrame(f_bottom, text=lang.version)
f_version.place(relx = 0.03125 + f_account_width/WIDTH + dmx, width = f_version_width)

version = ttk.Combobox(f_version, values=ver_list)
version.pack()

# RUN SECTION
f_run = LabelFrame(f_bottom, text=lang.run)
f_run.place(relx = 0.03125 + f_account_width/WIDTH + f_version_width/WIDTH + dmx, width = f_run_width)

runbtn = Button(f_run, text=lang.run, comman=runner)
runbtn.pack()

# =================== #
#        FINAL        #
# =================== #

# load profile
if os.path.isfile(os.path.join(path, 'profile.json')):
	rp = open(os.path.join(path, 'profile.json'), 'r')
	try:
		profile = json.load(rp)
		nick.insert(0, profile['nick'])
		version.insert(0, profile['version'])
	except Exception as e:
		pass
else:
	createProfile()
	

# launcher-profiles.json
jsonstr = """
{
  "authenticationDatabase": {},
  "clientToken": \"""" + "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for x in range(16)) + """\",
  "profiles": {
    "comment": "This is workaround to make Forge and OptiFine installers work properly"
  }
}
"""
if not(os.path.isfile(os.path.join(path, 'launcher_profiles.json'))):
	with open(os.path.join(path, 'launcher_profiles.json'), 'w') as lp:
		lp.write(jsonstr)

logger('''
 ____    __      
|  _    \   |   |     
| |_)   /   |   |     
|  _  <    |   |     
| |_)   \   |   |_____ 
|____/   |_______|   v 0.2 by maxgrt
	''')

update_check()
root.mainloop()
