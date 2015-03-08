################################################################################
import math

################################################################################
PRELOAD_RATIO  = 0.005

################################################################################
def piece_from_offset(torrent_handle, offset):
    return offset / torrent_handle.get_torrent_info().piece_length()

############################################################################
def get_video_file_total_pieces(torrent_handle, video_file):
    start_piece_index = piece_from_offset(torrent_handle, video_file.offset)
    end_piece_index   = piece_from_offset(torrent_handle, video_file.offset + video_file.size)
    return max(1, end_piece_index - start_piece_index)

############################################################################
def get_video_file_complete_pieces(torrent_handle, video_file):
    complete_pieces = 0

    if not video_file:
        return 0

    start_piece_index = piece_from_offset(torrent_handle, video_file.offset)
    end_piece_index   = piece_from_offset(torrent_handle, video_file.offset + video_file.size)

    for piece_index in range(start_piece_index, end_piece_index + 1):
        if torrent_handle.have_piece(piece_index):
            complete_pieces = complete_pieces + 1
        else:
            break

    return complete_pieces

################################################################################
def get_preload_buffer_piece_count(torrent_handle, video_file):
    piece_count     = get_video_file_total_pieces(torrent_handle, video_file)
    high_prio_count = min(piece_count, int(math.ceil(piece_count * PRELOAD_RATIO)))
    return high_prio_count
