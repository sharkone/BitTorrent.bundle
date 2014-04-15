################################################################################
import cherrypy
import downloader
import json
import logging
import mimetypes
import os
import platform
import static
import subprocess
import time

from cherrypy import _cplogging

################################################################################
class ConnectionMonitor(cherrypy.process.plugins.Monitor):
    ############################################################################
    def __init__(self, bus, http_config):
        cherrypy.process.plugins.Monitor.__init__(self, bus, self._background_task, frequency=1)

        self.http_config         = http_config
        self.connections         = []
        self.torrent_connections = {}

    ############################################################################
    def start(self):
        cherrypy.process.plugins.Monitor.start(self)

    ############################################################################
    def stop(self):
        cherrypy.process.plugins.Monitor.stop(self)

    ############################################################################
    def add_torrent(self, info_hash):
        if info_hash not in self.torrent_connections:
            self.torrent_connections[info_hash] = { 'timestamp': time.time(), 'set': set() }
        else:
            self.torrent_connections[info_hash]['timestamp'] = time.time()

    ############################################################################
    def remove_torrent(self, info_hash):
        if info_hash in self.torrent_connections:
            del self.torrent_connections[info_hash]

    ############################################################################
    def add_video_connection(self, info_hash):
        current_connections = self._get_connections()
        for connection in current_connections:
            if connection not in self.connections:
                self.add_torrent(info_hash)

                if connection not in self.torrent_connections[info_hash]:
                    self.torrent_connections[info_hash]['set'].add(connection)

                self.connections.append(connection)

    ############################################################################
    def has_video_connections(self, info_hash):
        return info_hash in self.torrent_connections and self.torrent_connections[info_hash]['set']

    ############################################################################
    def get_last_video_connection_timestamp(self, info_hash):
        if info_hash not in self.torrent_connections:
            return 0
        return self.torrent_connections[info_hash]['timestamp']

    ############################################################################
    def _get_connections(self):
        connections = []

        if platform.system() == 'Linux':
            lines = subprocess.check_output(['netstat', '-ant']).split('\n')
            for line in lines:
                words = line.split()
                if len(words) == 6 and words[3].endswith(str(self.http_config['port'])) and words[5] == 'ESTABLISHED':
                    connections.append(line)

        elif platform.system() == 'Darwin':
            lines = subprocess.check_output(['lsof', '-nPi4TCP']).split('\n')
            for line in lines:
                if ':{0}->'.format(self.http_config['port']) in line and 'ESTABLISHED' in line:
                    connections.append(line)

        elif platform.system() == 'Windows':
            lines = subprocess.check_output(['netstat', '-anp', 'TCP']).split('\n')
            for line in lines:
                words = line.split()
                if len(words) == 4 and words[1].endswith(str(self.http_config['port'])) and words[3] == 'ESTABLISHED':
                    connections.append(line)
        
        return connections

    ############################################################################
    def _background_task(self):
        current_connections = self._get_connections()
        
        connection_sets_to_remove = []
        for info_hash, connection_set in self.torrent_connections.iteritems():
            connections_to_remove = []

            for connection in connection_set['set']:
                if connection not in current_connections:
                    connections_to_remove.append(connection)

            for connection in connections_to_remove:
                connection_set['timestamp'] = time.time()
                connection_set['set'].remove(connection)
                self.connections.remove(connection)

################################################################################
class Server:
    ############################################################################
    def __init__(self, http_config, torrent_config, custom_log_stream=None):
        self.http_config       = http_config
        self.torrent_config    = torrent_config
        self.custom_log_stream = custom_log_stream

        cherrypy.engine.connection_monitor = ConnectionMonitor(cherrypy.engine, self.http_config)
        cherrypy.engine.connection_monitor.subscribe()

        cherrypy.engine.downloader_monitor = downloader.DownloaderMonitor(cherrypy.engine, self.http_config, self.torrent_config)
        cherrypy.engine.downloader_monitor.subscribe()
        
    ############################################################################
    def run(self):
        cherrypy.config.update({'server.socket_host':'0.0.0.0'})
        cherrypy.config.update({'server.socket_port':self.http_config['port']})

        if self.custom_log_stream:
            handler = logging.StreamHandler(self.custom_log_stream)
            handler.setLevel(logging.INFO)
            handler.setFormatter(_cplogging.logfmt)
            cherrypy.log.error_log.addHandler(handler)

        cherrypy.quickstart(ServerRoot())

################################################################################
class ServerRoot:
    ############################################################################
    @cherrypy.expose
    def index(self):
        return json.dumps(cherrypy.engine.downloader_monitor.get_status())

    ############################################################################
    @cherrypy.expose
    def add(self, uri, download_dir='.'):
        return json.dumps(cherrypy.engine.downloader_monitor.add_torrent(uri, download_dir))

    ############################################################################
    @cherrypy.expose
    def video(self, info_hash):
        cherrypy.engine.connection_monitor.add_video_connection(info_hash)

        if cherrypy.engine.downloader_monitor.is_video_file_ready_from_info_hash(info_hash, True):
            video_file   = cherrypy.engine.downloader_monitor.get_video_file(info_hash)
            content_type = mimetypes.types_map.get(os.path.splitext(video_file.path), None)

            if not content_type:
                if video_file.path.endswith('.avi'):
                    content_type = 'video/avi'
                elif video_file.path.endswith('.mkv'):
                    content_type = 'video/x-matroska'
                elif video_file.path.endswith('.mp4'):
                    content_type = 'video/mp4'

            return static.serve_fileobj(video_file, content_length=video_file.size, content_type=content_type, name=os.path.basename(video_file.path))            
        else:
            time.sleep(2)
            raise cherrypy.HTTPRedirect('/video?info_hash={0}'.format(info_hash), 307)

    ############################################################################
    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
        return 'cherrytorrent stopped'
