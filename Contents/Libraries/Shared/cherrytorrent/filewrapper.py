################################################################################
import io
import os
import string
import time
import utils

################################################################################
class FileWrapper(io.RawIOBase):
    ############################################################################
    def __init__(self, bus, torrent_handle, torrent_file):
        self.bus            = bus
        self.torrent_handle = torrent_handle
        self.piece_length   = self.torrent_handle.get_torrent_info().piece_length()
        self.torrent_file   = torrent_file

        # Weird bad character on MacOSX
        save_path = self.torrent_handle.save_path()
        save_path = save_path if save_path[-1] in string.printable else save_path[:-1]

        self.path = os.path.join(save_path, torrent_file.path)
        self.size = torrent_file.size

        while not os.path.isfile(self.path):
            time.sleep(0.1)

        self.file = open(self.path, 'rb')
        self.virtual_read = False

    ############################################################################
    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            new_position = offset
        elif whence == io.SEEK_CUR:
            new_position = self.file.tell() + offset
        elif whence == io.SEEK_END:
            new_position = self.size + offset

        piece_index = utils.piece_from_offset(self.torrent_handle, self.torrent_file.offset + new_position)
        self.bus.log('[FileWrapper] Seeking to piece {0}'.format(piece_index))
        self._wait_for_piece(piece_index)
        return self.file.seek(offset, whence)
        
    ############################################################################
    def read(self, size=-1):
        if self.virtual_read:
           self.virtual_read = False
           return ''

        if size == -1:
            size = self.size - self.file.tell()
        
        result = ''
        while size > 0:
            part_read_size = min(size, self.piece_length)
            piece_index    = utils.piece_from_offset(self.torrent_handle, self.torrent_file.offset + self.file.tell() + part_read_size)
            self._wait_for_piece(piece_index)
            result = result + self.file.read(part_read_size)
            size   = size - part_read_size

        return result            

    ############################################################################
    def close(self):
        return self.file.close()

    ############################################################################
    def _wait_for_piece(self, piece_index):
        if not self.torrent_handle.have_piece(piece_index):
            end_piece_index = utils.piece_from_offset(self.torrent_handle, self.torrent_file.offset + self.torrent_file.size)
            if (end_piece_index - piece_index) <= utils.get_preload_buffer_piece_count(self.torrent_handle, self.torrent_file):
               self.bus.log('[FileWrapper] Virtual read for piece {0}'.format(piece_index))
               self.virtual_read = True
               return

            self.bus.log('[FileWrapper] Waiting for piece {0}'.format(piece_index))
            while not self.torrent_handle.have_piece(piece_index):
                time.sleep(0.1)
            self.bus.log('[FileWrapper] Piece {0} downloaded'.format(piece_index))
