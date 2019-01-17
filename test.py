import subprocess, os, sys, tempfile
import datetime
temp_file = tempfile.NamedTemporaryFile(mode='r+', suffix=".txt")

temp_file.write("Statistic Output created on "+str(datetime.datetime.now()))

temp_file.seek(0)

# open temp_file with default application (crossplatform)
if sys.platform.startswith('darwin'):
    subprocess.call(('open', temp_file.name))
elif os.name == 'nt': # For Windows
    os.startfile(temp_file.name)
elif os.name == 'posix': # For Linux, Mac, etc.
    subprocess.call(('xdg-open', temp_file.name))
