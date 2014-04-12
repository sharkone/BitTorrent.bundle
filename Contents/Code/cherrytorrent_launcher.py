###############################################################################
import atexit
import os
import platform
import stat
import subprocess
import time
import urllib2

###############################################################################
HTTP_PORT = 8042

###############################################################################
def start_cherrytorrent():
    Thread.Create(thread_proc)

###############################################################################
def thread_proc():
    while True:
        if not get_server_status(HTTP_PORT):
            os.chmod(get_exec_path(), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


            if Platform.OS == 'Windows':
                command =   [
                                '\"' + get_exec_path() + '\"',
                                '-hp', str(HTTP_PORT),
                                '-hl', '\"' + get_bin_dir() + '\"',
                                '-tp', Prefs['INCOMING_PORT'],
                                '-tdl', Prefs['MAX_DOWNLOAD_RATE'],
                                '-tul', Prefs['MAX_UPLOAD_RATE'],
                            ]

                if Prefs['KEEP_FILES']:
                    command.append('-tk')

                env = os.environ.copy()
                if 'PYTHONHOME' in env:
                   del env['PYTHONHOME']

                Log.Info('[BitTorrent][cherrytorrent][{0}] {1}'.format(HTTP_PORT, ' '.join(command)))
                process = os.spawnve(os.P_DETACH, get_exec_path(), command, env)
            else:
                command =   [
                                get_exec_path(),
                                '-hp', str(HTTP_PORT),
                                '-hl', get_bin_dir(),
                                '-tp', Prefs['INCOMING_PORT'],
                                '-tdl', Prefs['MAX_DOWNLOAD_RATE'],
                                '-tul', Prefs['MAX_UPLOAD_RATE'],
                            ]

                if Prefs['KEEP_FILES']:
                    command.append('-tk')

                env = os.environ.copy()
                if 'PYTHONHOME' in env:
                   del env['PYTHONHOME']

                Log.Info('[BitTorrent][cherrytorrent][{0}] {1}'.format(HTTP_PORT, ' '.join(command)))
                process = subprocess.Popen(command, env=env)
                process.communicate()

        time.sleep(10)

###############################################################################
def get_bin_dir():
    bundle_directory = os.path.join(os.getcwd(), '..', '..', '..', 'Plug-ins', 'BitTorrent.bundle')
    bundle_directory = bundle_directory.replace('\\\\?\\', '')
    return os.path.normpath(os.path.join(bundle_directory, 'Contents', 'Bin'))

###############################################################################
def get_exec_path():
    if Platform.OS == 'MacOSX':
        return os.path.join(get_bin_dir(), 'MacOSX', 'cherrytorrent')
    elif Platform.OS == 'Linux':
        if platform.architecture()[0] == '64bit':
            return os.path.join(get_bin_dir(), 'Linux', 'x64', 'cherrytorrent')
        elif platform.architecture()[0] == '32bit':
            return os.path.join(get_bin_dir(), 'Linux', 'x86', 'cherrytorrent')
    elif Platform.OS == 'Windows':
        return os.path.join(get_bin_dir(), 'Windows', 'cherrytorrent.exe')

    Log.Error('[BitTorrent][cherrytorrent] Unsupported OS: {0}'.format(Platform.OS))

###############################################################################
def get_url(port, page):
    return 'http://' + Network.Address + ':' + str(port) + '/' + page

###############################################################################
def get_server_status(port):
    try:
        status_json = JSON.ObjectFromURL(get_url(port, ''), cacheTime=0)
        return status_json
    except urllib2.URLError as exception:
        Log.Error('[BitTorrent][cherrytorrent][{0}] Server unreachable: {1}'.format(port, exception.reason))
    except Exception as exception:
        Log.Error('[BitTorrent][cherrytorrent][{0}] Unhandled exception: {1}'.format(port, exception))

    return None
