import subprocess
import sys
import signal
import os

class color:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def main():
    process = subprocess.Popen("dev_appserver.py .", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.stderr

    def signal_handler(input_signal, frame):
        os.kill(process.pid, signal.SIGTERM)
        sys.stdout.write(output.readline())
        sys.stdout.write(output.readline())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while 1:
        line = output.readline().strip('\n')
	split_location = str.find(line, ']') + 1
	first_part = line[:split_location]
	second_part = line[split_location:]
	
        if 'WARNING' in line:
             print color.YELLOW + first_part + color.ENDC + second_part 
        elif 'DEBUG' in line:
            print color.BLUE + first_part + color.ENDC + second_part 
        elif 'INFO' in line:
            print color.GREEN + first_part + color.ENDC + second_part 
        elif 'ERROR' in line:
            print color.RED + first_part + color.ENDC + second_part 
        else:
            print line

if __name__ == '__main__':
    main()
