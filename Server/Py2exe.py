from distutils.core import setup
import py2exe
 
setup(
    console=[{"script":"server.py"}],
    options={"py2exe": {"includes":["os","sys","socket","ssl","threading", "time", "sqlite3", "datetime", "cPickle", "hashlib", "base64", "CryptUnit"]}},
    zipfile=None
)