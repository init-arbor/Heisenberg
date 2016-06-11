import datetime
import logging
import os
import platform
import subprocess
import unittest
try:
    from LogAgent import log_init, info
except:
    from  Heisenberg.LogAgent import log_init, info

log = logging.getLogger(__name__)

class CscopeAgent:
    SymRef = 0
    Def = 1

    def __init__(self, path_cscope_lib):
        self.path_cscope_lib = path_cscope_lib

        if platform.system() == "windows":
            self.path_cscope_exe = "/Users/init/Documents/cscope"
        else:
            self.path_cscope_exe = "/Users/init/Documents/cscope"

    def _findSymRef(self, key):
       args = self._build_cmd_arg(CscopeAgent.SymRef, key)
       cwd = os.path.dirname(self.path_cscope_lib)
       return self._cmd(args, cwd)
        

    def FindDef(self, key):
       args = self._build_cmd_arg(CscopeAgent.Def, key)
       cwd = os.path.dirname(self.path_cscope_lib)
       return self._cmd(args, cwd)
     

    def FindBoth(self,key):
        #in this mode, we find both symRef and Def
        #the dirty part is remove Def from symRef

        dfn = self.FindDef(key)
        symRef = self._findSymRef(key)
        #def_lines = dfn.split('\n')

        #We regard the first entry as "real" def 
        #for simplicity.  
        #if len(def_lines) >=1:
        #    symRef=symRef.replace(def_lines[0],"")

        return [dfn, symRef]

    def _cmd(self, args,cwd):
        start_time = datetime.datetime.now()
        popen_arg_list = {
            "shell": False,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "cwd": cwd,
        }

        if platform.system() == "windows":
            popen_arg_list["creationflags"] = 0x08000000

        proc = subprocess.Popen(args, **popen_arg_list)
        output, erroroutput = proc.communicate()
        if len(erroroutput) > 0:
            return erroroutput.strip()
        output = str(output, encoding="ISO-8859-1").replace("\r", "")
        end_time = datetime.datetime.now()
        elapsed_time = end_time-start_time
        info("cscope took {0:0.2f} ms".format(elapsed_time.total_seconds() * 1000.0))
        return output.strip()


    def _build_cmd_arg(self, mode, key):
        args = [self.path_cscope_exe, "-dL", "-f",
                self.path_cscope_lib, "-" + str(mode) + key]
        return args


class TestCscopeAgent(unittest.TestCase):
    def setUp(self):
        self.key = "cb_compare_fn"
        self.path_cscope_lib = os.path.join(os.getcwd(),"cscope.out")
        self.assertTrue(os.path.isfile(self.path_cscope_lib))
        self.cscopeAgent = CscopeAgent(self.path_cscope_lib)
    def testInit(self):
        log.info(str(self.cscopeAgent))

    def testCmd(self):
        args = ["pwd"]
        cwd  =os.path.dirname(self.path_cscope_lib)
        result = self.cscopeAgent._cmd(args, cwd)
        log.info(result)
        self.assertTrue(len(result)>0)

    def testFindSymRef(self):
        log.info(" \n\ntestFindSymRefn")
        result= self.cscopeAgent._findSymRef(self.key)
        #log.info(result)
        self.assertTrue(len(result)>0)

    def testFindDef(self):
        log.info(" \n\ntestFindDef\n")
        result= self.cscopeAgent.FindDef(self.key)
        #og.info(result)
        self.assertTrue(len(result)>0)

    def testFindBoth(self):
        [dfn, symref] = self.cscopeAgent.FindBoth(self.key)
        self.assertTrue(len(dfn)>0)
        self.assertTrue(len(symref)>0)

if __name__ == '__main__':
    log_init()
    unittest.main(verbosity=2)