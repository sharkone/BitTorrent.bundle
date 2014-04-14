###############################################################################
import cherrytorrent
import os
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
            http_config = {
                            'port':     HTTP_PORT,
                            'log_dir':  get_bundle_dir(),
                          }

            torrent_config = {
                                'port':                 int(Prefs['INCOMING_PORT']),
                                'max_download_rate':    int(Prefs['MAX_DOWNLOAD_RATE']),
                                'max_upload_rate':      int(Prefs['MAX_UPLOAD_RATE']),
                                'keep_files':           Prefs['KEEP_FILES']
                             }
            
            server = cherrytorrent.Server(http_config, torrent_config)
            server.run()
        else:
             Log.Info('[BitTorrent][cherrytorrent][{0}] Server is running'.format(port))

        time.sleep(10)

###############################################################################
def get_bundle_dir():
    bundle_directory = os.path.join(os.getcwd(), '..', '..', '..', 'Plug-ins', 'BitTorrent.bundle')
    bundle_directory = bundle_directory.replace('\\\\?\\', '')
    return os.path.normpath(bundle_directory)

###############################################################################
def get_server_status(port):
    try:
        status_json = JSON.ObjectFromURL('http://{0}:{1}'.format(Network.Address, port), cacheTime=0)
        return status_json
    except urllib2.URLError as exception:
        Log.Error('[BitTorrent][cherrytorrent][{0}] Server unreachable: {1}'.format(port, exception.reason))
    except Exception as exception:
        Log.Error('[BitTorrent][cherrytorrent][{0}] Unhandled exception: {1}'.format(port, exception))

    return None
