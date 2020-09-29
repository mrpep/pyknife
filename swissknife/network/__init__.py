from pathlib import Path
import requests
import pafy
import subprocess
import paramiko
import time
import boto3

def download_url(url,download_path):
    r = requests.get(url, stream = True)
    if not Path(download_path).exists():
        print("Downloading file {}".format(url)) 
        with open(download_path,"wb") as dest_file: 
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: 
                    dest_file.write(chunk)
        return 1
    else:
        return 0

def download_audio_from_yt(url_id,start=None,end=None,download_path=None):
    video_page_url='https://www.youtube.com/watch?v={}'.format(url_id)
    #Obtengo la URL del archivo de video con mejor audio:
    video = pafy.new(video_page_url)
    video_duration = video.length
    best_audio = video.getbestaudio().url
    #Descargo la parte deseada usando ffmpeg y la guardo en un mkv sin reencodear
    cmd = ['ffmpeg','-i',best_audio,'-vn','-ss','{}'.format(int(start)),'-to','{}'.format(int(end)),'-acodec','copy','temp_out.mkv']
    subprocess.call(cmd,timeout=15)
    if Path('temp_out.mkv').exists():
        return 'temp_out.mkv'
    else:
        return None

def run_ssh_commands(username,hostname,pem_file,command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privkey = paramiko.RSAKey.from_private_key_file(pem_file)
    if Path(command).exists():
        with open(command,'r') as f:
            command = f.read()

    failed = True
    while failed:   
        try:
            ssh_client.connect(hostname=hostname,username=username,pkey=privkey)
            failed = False
        except:
            failed = True
            time.sleep(1)
            print('Retrying connection')

    stdin, stdout, stderr = ssh_client.exec_command(command)
    ssh_client.close()
    return stdin, stdout, stderr