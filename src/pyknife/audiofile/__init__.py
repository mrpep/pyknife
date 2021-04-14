from pyknife.console import run_command

def ffmpeg_to_wav(in_file,out_file,sr=None):
    """
    Uses ffmpeg to turn any audio file into a .wav file
    in_file:  path to the audio to convert
    out_file: destination path of the converted audio
    sr:       desired sample rate of the converted audio
    """
    if sr is None:
        cmd = "ffmpeg -y -i {} {}".format(in_file,sr,out_file)
    else:
        cmd = "ffmpeg -y -i {} -ar {} {}".format(in_file,sr,out_file)
    run_command(cmd,silent=True)