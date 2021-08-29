import os
import shutil

def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
        
def check_file_size(file):
    return convert_bytes(os.path.getsize(file))


def check_disksize():
    total, used, free = shutil.disk_usage(".")
    return convert_bytes(free) + " / " + convert_bytes(total)