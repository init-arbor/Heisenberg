import datetime
import logging
import sys
import os

def info(msg=""):

    frame = sys._getframe(1)
    classname = ""
    if 'self' in frame.f_locals:
        classname = frame.f_locals['self'].__class__.__name__
    line_num = frame.f_lineno
    function_name = frame.f_code.co_name
    filename = os.path.basename(frame.f_code.co_filename)

    time = datetime.datetime.now().strftime(' %H:%M:%S ')
    print("{0}{1:15}{2:4} {3:20} {4:28} {5}".format(time,
                                                    filename,
                                                    line_num,
                                                    classname,
                                                    function_name,
                                                    str(msg)))



def log_init(log_name='myapp.log', filemode='w'):
    logging.basicConfig(
    filename=log_name,
    level=logging.INFO,
    format=u"(%(asctime)s) %(levelname)-7s (%(filename)s:%(lineno)3s) %(message)s",
    datefmt='%m/%d %H:%M:%S',
    filemode = filemode)