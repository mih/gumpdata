import os
import subprocess

def sid2anonid(sid):
    return int(subprocess.check_output(['./anon_id', sid]).strip())


