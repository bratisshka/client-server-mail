ClientCommand = ("", 0)
import shelve


def get_command():
    d = shelve.open("command")
    if d.has_key("key"):
        return d['key']
    return "", 0


def set_command(name, wtf):
    d = shelve.open("command")
    d["key"] = (name, wtf)
    return True
