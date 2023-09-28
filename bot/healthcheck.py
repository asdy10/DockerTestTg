import asyncio
import os
import sys
import time


def health_update():
    with open('healthcheck.txt', 'r') as f:
        res = f.read()
    with open('healthcheck.txt', 'w') as f:
        if res == '0':
            f.write('1')
        else:
            f.write('0')


def health_check():
    while True:
        filename = "healthcheck.txt"
        mtime = os.path.getmtime(filename)
        print(time.time() - mtime)
        if time.time() - mtime > 7:
            print('wtf')
            #loop = asyncio.get_event_loop()
            #loop.stop()
            quit(os.system("python /bot/app.py"))


        time.sleep(5)


if __name__ == '__main__':
    health_check()