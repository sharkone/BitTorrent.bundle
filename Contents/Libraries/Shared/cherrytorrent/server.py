################################################################################
import cherrypy
import downloader
import json
import mimetypes
import os
import psutil
import static
import time

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
    def add_video_connection(self, info_hash):
        current_connections = self._get_connections()
        for connection in current_connections:
            if connection not in self.connections:
                if info_hash not in self.torrent_connections:
                    self.torrent_connections[info_hash] = { 'timestamp': time.time(), 'set': set() }

                if connection not in self.torrent_connections[info_hash]:
                    self.torrent_connections[info_hash]['set'].add(connection)

                self.connections.append(connection)

    ############################################################################
    def has_video_connections(self, info_hash):
        return info_hash in self.torrent_connections

    ############################################################################
    def _get_connections(self):
        connections = []
        current_process = psutil.Process()
        for connection in current_process.connections('tcp'):
            if connection.laddr[1] == self.http_config['port'] and connection.status == 'ESTABLISHED':
                connections.append(connection)
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

            if not connection_set['set'] and (time.time() - connection_set['timestamp']) > 30.0:
                connection_sets_to_remove.append(info_hash)

        for info_hash in connection_sets_to_remove:
            del self.torrent_connections[info_hash]

        current_process = psutil.Process()
        if (not current_process.parent() or current_process.parent().pid == 1) or (not current_process.parent().parent() or current_process.parent().parent().pid == 1):
            self.bus.log('Parent process is dead, exiting')
            cherrypy.engine.exit()

################################################################################
class Server:
    ############################################################################
    def __init__(self, http_config, torrent_config):
        self.http_config    = http_config
        self.torrent_config = torrent_config

        cherrypy.engine.connection_monitor = ConnectionMonitor(cherrypy.engine, self.http_config)
        cherrypy.engine.connection_monitor.subscribe()

        cherrypy.engine.downloader_monitor = downloader.DownloaderMonitor(cherrypy.engine, self.http_config, self.torrent_config)
        cherrypy.engine.downloader_monitor.subscribe()

        self.log_path = os.path.abspath(os.path.join(self.http_config['log_dir'], 'cherrytorrent.log'))
        
    ############################################################################
    def run(self):
        if os.path.isfile(self.log_path):
            os.remove(self.log_path)

        cherrypy.config.update({'log.error_file':self.log_path})
        cherrypy.config.update({'server.socket_host':'0.0.0.0'})
        cherrypy.config.update({'server.socket_port':self.http_config['port']})

        cherrypy.quickstart(ServerRoot(self.log_path))

################################################################################
class ServerRoot:
    ############################################################################
    def __init__(self, log_path):
        self.log_path = log_path

    ############################################################################
    @cherrypy.expose
    def index(self):
        return json.dumps(cherrypy.engine.downloader_monitor.get_status())

    ############################################################################
    @cherrypy.expose
    def log(self):
        result = ''
        with open(self.log_path, 'r') as f:
            for line in iter(f.readline, ''):
                result = result + line + '<br/>'
        
        return result

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
