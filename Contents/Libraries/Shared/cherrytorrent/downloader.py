################################################################################
import cherrypy
import filewrapper
import libtorrent
import math
import time
import utils

################################################################################
class DownloaderMonitor(cherrypy.process.plugins.Monitor):
    ############################################################################
    def __init__(self, bus, http_config, torrent_config):
        cherrypy.process.plugins.Monitor.__init__(self, bus, self._background_task, frequency=1)

        self.http_config     = http_config
        self.torrent_config  = torrent_config
        self.session         = None
        self.connections     = []
        self.monitor_running = False
        self.torrent_handles = []
        self.last_cleanup    = time.time()

        self.expected_alert_types    = []
        self.expected_alert_received = False

    ############################################################################
    def start(self):
        cherrypy.process.plugins.Monitor.start(self)

        self.bus.log('[Downloader] Starting session')
        self.session = libtorrent.session()
        self.session.set_alert_mask(libtorrent.alert.category_t.error_notification | libtorrent.alert.category_t.status_notification | libtorrent.alert.category_t.storage_notification)
        self.session.start_dht()
        self.session.start_lsd()
        self.session.start_upnp()
        self.session.start_natpmp()
        self.session.listen_on(self.torrent_config['port'], self.torrent_config['port'])

        # Session settings
        session_settings = self.session.settings()
        session_settings.announce_to_all_tiers = True
        session_settings.announce_to_all_trackers = True
        session_settings.connection_speed = 100
        session_settings.peer_connect_timeout = 2
        session_settings.rate_limit_ip_overhead = True
        session_settings.request_timeout = 5
        session_settings.torrent_connect_boost = 100

        if self.torrent_config['max_download_rate'] > 0:
            session_settings.download_rate_limit = self.torrent_config['max_download_rate'] * 1024
        if self.torrent_config['max_upload_rate'] > 0:
            session_settings.upload_rate_limit = self.torrent_config['max_upload_rate'] * 1024
        self.session.set_settings(session_settings)

        # Encryption settings
        encryption_settings = libtorrent.pe_settings()
        encryption_settings.out_enc_policy = libtorrent.enc_policy(libtorrent.enc_policy.forced)
        encryption_settings.in_enc_policy = libtorrent.enc_policy(libtorrent.enc_policy.forced)
        encryption_settings.allowed_enc_level = libtorrent.enc_level.both
        encryption_settings.prefer_rc4 = True
        self.session.set_pe_settings(encryption_settings)

    ############################################################################
    def stop(self):
        if not self.monitor_running:
            return

        self.bus.log('[Downloader] Stopping session')

        torrent_handles_to_remove = list(self.torrent_handles)
        for torrent_handle in torrent_handles_to_remove:
            self.remove_torrent(torrent_handle, True)

        self.session.stop_natpmp()
        self.session.stop_upnp()
        self.session.stop_lsd()
        self.session.stop_dht()

        self.monitor_running = False
        cherrypy.process.plugins.Monitor.stop(self)

    ############################################################################
    def add_torrent(self, uri, download_dir):
        add_torrent_params                 = {}
        add_torrent_params['url']          = uri
        add_torrent_params['save_path']    = download_dir
        add_torrent_params['storage_mode'] = libtorrent.storage_mode_t.storage_mode_sparse
        add_torrent_params['auto_managed'] = False

        torrent_handle = self.session.add_torrent(add_torrent_params)
        torrent_handle.set_sequential_download(True)
        torrent_handle.resume()
        self.bus.connection_monitor.add_torrent(str(torrent_handle.info_hash()))    

        if torrent_handle not in self.torrent_handles:
            self.torrent_handles.append(torrent_handle)

        return { 'name': torrent_handle.name(), 'info_hash': str(torrent_handle.info_hash()) }

    ############################################################################
    def remove_torrent(self, torrent_handle, wait_for_alert=False):
        remove_torrent_flags = libtorrent.options_t.delete_files if not self.torrent_config['keep_files'] else 0
        self.session.remove_torrent(torrent_handle, remove_torrent_flags)

        if wait_for_alert:
            self.expected_alert_received = False
            self.expected_alert_types    = ['torrent_removed_alert'] if self.torrent_config['keep_files'] else ['torrent_deleted_alert', 'torrent_delete_failed_alert']
            
            start_time = time.time()
            while not self.expected_alert_received:
                if (time.time() - start_time) > 30.0:
                    self.bus.log('[Downloader] Removing torrent took too long, skipping.')
                    break
                time.sleep(0.1)

        self.torrent_handles.remove(torrent_handle)

    ############################################################################
    def remove_paused_torrents(self):
        torrent_handles_to_remove = []
        for torrent_handle in self.torrent_handles:
            if torrent_handle.status().paused:
                torrent_handles_to_remove.append(torrent_handle)

        for torrent_handle in torrent_handles_to_remove:
            self.remove_torrent(torrent_handle)

    ############################################################################
    def get_status(self):
        result = {}

        if self.session:
            result['session'] = self.torrent_config
            
            result['session']['connection_sets'] = []
            for info_hash, connection_set in self.bus.connection_monitor.torrent_connections.iteritems():
                connection_set_status = { 'info_hash': info_hash, 'timestamp': connection_set['timestamp'], 'connections':[] }
                
                for connection in connection_set['set']:
                    connection_status = { 'info_hash': info_hash, 'remote_ip': connection.raddr[0], 'remote_port': connection.raddr[1] }
                    connection_set_status['connections'].append(connection_status)

                result['session']['connection_sets'].append(connection_set_status)

            result['session']['torrents'] = []
            for torrent_handle in self.torrent_handles:
                torrent_status = torrent_handle.status()

                torrent = {}
                
                try:
                    torrent['paused']        = torrent_status.paused
                    torrent['state']         = str(torrent_status.state)
                    torrent['state_index']   = int(torrent_status.state)
                    torrent['progress']      = math.trunc(torrent_status.progress * 100.0) / 100.0
                    torrent['download_rate'] = torrent_status.download_rate / 1024
                    torrent['upload_rate']   = torrent_status.upload_rate / 1024
                    torrent['num_seeds']     = torrent_status.num_seeds
                    torrent['total_seeds']   = torrent_status.num_complete
                    torrent['num_peers']     = torrent_status.num_peers
                    torrent['total_peers']   = torrent_status.num_incomplete
                    torrent['info_hash']     = str(torrent_handle.info_hash())

                    video_file = self._get_video_file_from_torrent(torrent_handle)
                    if video_file:
                        torrent['video_file']                          = {}
                        torrent['video_file']['path']                  = video_file.path
                        torrent['video_file']['size']                  = video_file.size
                        torrent['video_file']['start_piece_index']     = utils.piece_from_offset(torrent_handle, video_file.offset)
                        torrent['video_file']['end_piece_index']       = utils.piece_from_offset(torrent_handle, video_file.offset + video_file.size)
                        torrent['video_file']['total_pieces']          = utils.get_video_file_total_pieces(torrent_handle, video_file)
                        torrent['video_file']['preload_buffer_pieces'] = utils.get_preload_buffer_piece_count(torrent_handle, video_file)
                        torrent['video_file']['is_ready_fast']         = self.is_video_file_ready(torrent_handle, True, False)
                        torrent['video_file']['is_ready_slow']         = self.is_video_file_ready(torrent_handle, False, False)
                        torrent['video_file']['complete_pieces']       = utils.get_video_file_complete_pieces(torrent_handle, video_file)

                        piece_map = ''
                        for piece_index in range(torrent['video_file']['start_piece_index'], torrent['video_file']['end_piece_index'] + 1):
                            if torrent_handle.have_piece(piece_index):
                                piece_map = piece_map + '*'
                            elif torrent_handle.piece_priority(piece_index) == 0:
                                piece_map = piece_map + '0'
                            elif torrent_handle.piece_priority(piece_index) == 7:
                                piece_map = piece_map + '7'
                            else:
                                piece_map = piece_map + '.'
                        torrent['video_file']['piece_map'] = piece_map
                except RuntimeError:
                    pass

                result['session']['torrents'].append(torrent)

        return result

    ###########################################################################
    def is_video_file_ready_from_info_hash(self, info_hash, is_fast, log_enabled=True):
        for torrent_handle in self.torrent_handles:
            if str(torrent_handle.info_hash()) == info_hash:
                return self.is_video_file_ready(torrent_handle, is_fast, log_enabled)
        raise RuntimeError

    ###########################################################################
    def is_video_file_ready(self, torrent_handle, is_fast, log_enabled=True):
        if torrent_handle:
            status     = torrent_handle.status()
            video_file = self._get_video_file_from_torrent(torrent_handle)

            if int(status.state) >= 3 and video_file:
                complete_pieces = utils.get_video_file_complete_pieces(torrent_handle, video_file)
                total_pieces    = utils.get_video_file_total_pieces(torrent_handle, video_file)
                needed_pieces   = utils.get_preload_buffer_piece_count(torrent_handle, video_file)

                if is_fast or complete_pieces >= needed_pieces:
                    return True
                else:
                    if log_enabled:
                        self.bus.log('[Downloader] Not enough pieces yet: {0}/{1} (total: {2}) @ {3} kB/s'.format(complete_pieces, needed_pieces, total_pieces, status.download_rate / 1024))
            else:
                if log_enabled:
                    self.bus.log('[Downloader] Not ready yet: {0}'.format(str(status.state)))
        else:
            if log_enabled:
                self.bus.log('[Downloader] Not ready yet')

        return False

    ###########################################################################
    def get_video_file(self, info_hash):
        for torrent_handle in self.torrent_handles:
            if str(torrent_handle.info_hash()) == info_hash:
                video_file = self._get_video_file_from_torrent(torrent_handle)
                if video_file:
                    if torrent_handle.status().paused:
                        torrent_handle.resume()
                    return filewrapper.FileWrapper(self.bus, torrent_handle, video_file)
                else:
                    return None
        raise RuntimeError

    ############################################################################
    def _background_task(self):
        self.monitor_running = True

        while not self.session and self.monitor_running:
            time.sleep(0.1)

        while self.monitor_running:
            for torrent_handle in self.torrent_handles:
                if not self.bus.connection_monitor.has_video_connections(str(torrent_handle.info_hash())):
                    if not torrent_handle.status().paused:
                        torrent_handle.pause()

            if (time.time() - self.last_cleanup) > 18000: # 5 hours
                self.remove_paused_torrents()
                self.last_cleanup = time.time()

            self._alert_pump()

    ############################################################################
    def _alert_pump(self):
        while True:
            self.session.wait_for_alert(1000)
            alert = self.session.pop_alert()
            if alert:
                if alert.what() in ('cache_flushed_alert', 'external_ip_alert', 'hash_failed_alert', 'metadata_failed_alert', 'tracker_error_alert'):
                    continue

                self.bus.log('[Downloader][{0}] {1}'.format(alert.what(), alert.message()))

                if isinstance(alert, libtorrent.metadata_received_alert):
                    video_file = self._get_video_file_from_torrent(alert.handle)

                    if not video_file:
                        self.bus.log('[Downloader] No video file found, removing torrent')
                        self.remove_torrent(torrent_handle)

                elif alert.what() in self.expected_alert_types:
                    self.expected_alert_received = True
                    self.expected_alert_types    = []
                    break

            if not self.expected_alert_types:
                break

    ############################################################################
    def _get_video_file_from_torrent(self, torrent_handle):
        video_file = None
        
        try:
            for file in torrent_handle.get_torrent_info().files():
                if file.path.endswith('.mkv') or file.path.endswith('.mp4') or file.path.endswith('.avi'):
                    if not video_file or video_file.size < file.size:
                        video_file = file
        except RuntimeError:
            pass

        return video_file
