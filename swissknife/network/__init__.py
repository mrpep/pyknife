from pathlib import Path
import requests
import pafy
import subprocess
import paramiko
import time
import boto3
import copy

def download_url(url,download_path):
    """
    Download an url
    url:           url to download
    download_path: path where to save the downloaded url
    """
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
    """
    Download the audio from a youtube video
    url_id:         url of the video to download
    start:          start (in seconds) of the video fragment to download
    end:            end (in seconds) of the video fragment to download
    download_path:  path where to save the downloaded audio
    """
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

def run_ssh_commands_2(username,hostname,command,pem_file=None,ec2_instance_connect_data=None):
    if ec2_instance_connect_data:
        ec2_instance_connect_data = copy.deepcopy(ec2_instance_connect_data)
        client = boto3.client('ec2-instance-connect',ec2_instance_connect_data['region'])
        ec2_instance_connect_data.pop('region')
        client.send_ssh_public_key(**ec2_instance_connect_data)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privkey = paramiko.RSAKey.from_private_key_file(pem_file)
    if Path(command).exists():
        with open(command,'r') as f:
            command = f.read()

    failed = True
    while failed:
        try:
            ssh.connect(hostname, username=username, pkey=privkey)
            sleeptime = 0.1
            outdata, errdata = '', ''
            ssh_transp = ssh.get_transport()
            chan = ssh_transp.open_session()
            chan.setblocking(0)
            chan.exec_command(command)
            while True:  # monitoring process
                # Reading from output streams
                while chan.recv_ready():
                    outdata += chan.recv(1000).decode('utf-8')
                while chan.recv_stderr_ready():
                    errdata += chan.recv_stderr(1000).decode('utf-8')
                if chan.exit_status_ready():  # If completed
                    break
                time.sleep(sleeptime)
            retcode = chan.recv_exit_status()
            ssh_transp.close()
            failed = False
        except:
            failed = True
            time.sleep(1)
            print('Retrying connection')
    
    return outdata, errdata