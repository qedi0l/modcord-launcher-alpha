import eel
import os
import zipfile
import shutil
import time
from ftplib import FTP
import subprocess
import asyncio
import json
import uuid as uuid_lib

#consts
pc_userTMP = os.environ['TEMP'];
game_folder = "C:/Games/modcord"

#logics block \/\/\/\/\/

class Config:
	def __init__(self, nickname, uuid, jvm_args, accessToken):
		self.nickname = nickname
		self.uuid = uuid
		self.jvm_args = jvm_args
		self.accessToken = accessToken

	def toJSON(self):
		return json.dumps(self,default=lambda o: o.__dict__, sort_keys=True,indent=4)


#check file exist if not create it
if not(os.path.exists(game_folder+'/config.cfg')):
	shutil.copy(os.getcwd()+'/'+'launch.bat', game_folder+'/'+'launch.bat')
	open(game_folder+'/config.cfg', 'x');
	with open(game_folder+'/config.cfg', 'w') as file:
		tmp = Config('','','','')
		file.write(tmp.toJSON())
		file.close()

#read config.cfg
with open(game_folder+'/config.cfg', 'r') as file:

	cfg = json.load(file)

	#if first launch
	if cfg == '':
		cfg["nickname"] = 'err'
		cfg["uuid"]  = ''
		cfg["jvm_args"]  = ''
	else:
		nickname  = cfg["nickname"] 
		uuid = cfg["uuid"]
		jvm_args = cfg["jvm_args"]

	#uuid 4ver to hex (32 digit)
	if uuid == '': uuid = str(uuid_lib.uuid4().hex)
	# im so lazy to make input field
	if jvm_args == '': jvm_args = '-Xms2G -Xmx10G -XX:+UnlockExperimentalVMOptions -XX:G1RSetUpdatingPauseTimePercent=5 -XX:G1MixedGCLiveThresholdPercent=90 -XX:InitiatingHeapOccupancyPercent=15 -XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled -XX:+UseG1GC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M -XX:+UseNUMA -XX:+UseStringDeduplication -Daikars.new.flags=true -Dusing.aikars.flags=https://mcflags.emc.gs -XX:+ParallelRefProcEnabled -XX:+UseLargePages'
	# i dont know why
	accessToken = uuid

	#conf obj
	conf = Config(nickname,uuid,jvm_args,accessToken)

	file.close()



def setup_launch(season):
	#copy launch pattern to season #depricated!!
	#shutil.copy(game_folder+'/'+'launch.bat', game_folder+'/'+season+'/'+'launch.bat')

	#check file exist if not create it
	if not(os.path.exists(game_folder+'/'+season+'/'+'launch.bat')): open(game_folder+'/'+season+'/'+'launch.bat', 'x')
	
	#sheeeeeesh
	#read pattern file, modify, write to instance file
	file_r = open(game_folder+'/'+'launch.bat','r')
	with open(game_folder+'/'+season+'/'+'launch.bat','w') as file:

		f = file_r.read()

		f = f.replace('|nickname|', conf.nickname)
		f = f.replace('|accessToken|', conf.accessToken)
		f = f.replace('|uuid|', conf.uuid)
		f = f.replace('|jvm_args|', conf.jvm_args)

		file.write(f)
		file.close()

# launcher cgf from Config obj
def launcher_conf_write(confList: Config):
	with open(game_folder+'/config.cfg','w') as file:
		file.write(confList.toJSON())
		file.close()


def download(season):

	is_dir(game_folder+"/"+season)

	set_status("Connecting...")
	# change to private-hentai.sytes.net
	ftp = FTP('192.168.0.113') 
	ftp.login(user='qed', passwd='7691', acct='')
	ftp.cwd('/')

	zipped = season+".zip"
	out = game_folder

	set_status("Downloading...")

	with open(out+'/'+zipped, 'wb') as f:
		ftp.retrbinary('RETR ' + zipped, f.write)

	set_status("Download Complete!")
	time.sleep(1)
	unzip(season, zipped)


def unzip(season, zipped):
	set_status("Unpacking...")

	season_zip = game_folder +"/"+ zipped 
	season_folder = game_folder +"/"+ season

	is_dir(season_folder)

	if os.path.exists(season_zip):
		try:
			_zip = zipfile.ZipFile(season_zip)
			_zip.extractall(season_folder)
			_zip.close()
		except zipErr:
			pass
	else:
		pass

	set_status("Complete!")
	time.sleep(1)
	set_status("Ready to start!")
	os.remove(season_zip)	

def is_dir(path):
	if os.path.exists(path):
		pass
	else:
		os.mkdir(path)
		
# some magic staff
def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())


def check_game_status():
	while True:
		time.sleep(1)
		status = process_exists('javaw.exe')
		if status:
			set_status("Runned")
		else:
			set_status("Closed")
			break


def start_game(season):
	#os.startfile(game_folder+'/'+season+"/launch.bat") #depricated!!

	filepath = game_folder+'/'+season+"/launch.bat"
	p = subprocess.Popen(filepath, shell=True, stdout = subprocess.PIPE)
	stdout, stderr = p.communicate()

	
	check_game_status()


#ui block \/\/\/\/\/\/\/
	
#ui status
def set_status(status):
	eel.setStatus(status);	

@eel.expose
def set_nickname():
	return str(conf.nickname)

@eel.expose
def launch(nickname,season):

	is_dir(game_folder)

	#update nickname in Config obj from ui
	conf.nickname = nickname
	launcher_conf_write(conf)

	#java check
	if os.path.exists(game_folder+'/jdk-19'):
		pass
	else:
		download('jdk-19')

	#instance check
	if os.path.exists(game_folder+"/"+season):
		if conf.nickname != '':
			#print("startgame")

		#prepare launch
			set_status("Runned")
			setup_launch(season)
		#launch game
			start_game(season)
			check_game_status()

		else:
			set_status("Enter nickname")

		set_status("Ready")
	else:
		download(season)
	

eel.init("web")
eel.start("main.html", size=(460,640), position=(800,300))
