################################################################################
import platform

################################################################################
if platform.system() == 'Darwin':
    from macosx.libtorrent import *
elif platform.system() == 'Windows':
    from windows.libtorrent import *