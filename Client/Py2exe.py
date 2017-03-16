from distutils.core import setup
import py2exe
 
setup(
    windows=[{"script":"client.py"}],
    options={"py2exe": {"includes":["Tkinter","ttk","time","os","Image", "tkMessageBox", "tkFileDialog", "PostNetwork", "random", "base64", "CryptUnit", "Crypto", "socket", "ssl", "cPickle", "ConfigParser"]}},
    zipfile=None
)