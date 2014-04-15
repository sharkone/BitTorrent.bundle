################################################################################
import platform

################################################################################
if platform.system() == 'Darwin':
    from macosx.libtorrent import *
elif platform.system() == 'Linux' and platform.architecture()[0] == '32bit':
    from linux_x86.libtorrent import *
elif platform.system() == 'Windows':
    from windows.libtorrent import *
