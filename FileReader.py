import os
from collections import namedtuple
try:
    from LogAgent import info
except:
    from  Heisenberg.LogAgent import info

cached_file = namedtuple("cached_file", ["mod_time", "data"])

class FileReader:
  
    buf = {}
    count = {}
    BUF_SIZE = 10

    @staticmethod
    def ReadFile(file_path):

        if file_path in FileReader.buf:
            cached = FileReader.buf[file_path]
            last_mod_time = os.path.getmtime(file_path)
            if cached.mod_time == last_mod_time:
                info("return cache data {}".format(file_path))
                return cached.data

        with open(file_path, 'r', encoding="ISO-8859-1") as f:
            data = f.read()
            last_mod_time = os.path.getmtime(file_path)
            cached = cached_file(mod_time=last_mod_time, data=data)
            if len(FileReader.buf) > FileReader.BUF_SIZE:
                FileReader.buf = {}
            FileReader.buf[file_path] = cached

            return data