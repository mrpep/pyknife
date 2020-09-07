from swissknife.console import run_command

def ffmpeg_to_wav(in_file,out_file,sr=None):
    if sr is None:
        cmd = "ffmpeg -i {} {}".format(in_file,sr,out_file)
    else:
        cmd = "ffmpeg -i {} -ar {} {}".format(in_file,sr,out_file)
    run_command(cmd,silent=True)