import json
import logging
import os
import unittest
try:
    from CscopeAgent import CscopeAgent
    from LogAgent import log_init
except:
    from Heisenberg.CscopeAgent import CscopeAgent
    from  Heisenberg.LogAgent import log_init
 


log = logging.getLogger(__name__)

class CacheAgent:
    def __init__(self, path_cscope_lib, path_buffer):
 
        self.dual_mode_bufer={}
        self.def_bufer={}

        self.path_buffer = path_buffer
        self.cscopeAgent = CscopeAgent(path_cscope_lib)

        if os.path.isfile(self.path_buffer):
            self._read_from_disk()
        else:
            self.SaveToDisk()

    def FindBoth(self, key):
        if key not in self.dual_mode_bufer:
            [dfn, symref]= self.cscopeAgent.FindBoth(key)
            self.dual_mode_bufer[key]=[dfn, symref]


        return self.dual_mode_bufer[key]

    def FindDef(self, key):
        #we do not implement FindDef buffer at this stage
        if key not in self.def_bufer:
            dfn = self.cscopeAgent.FindDef(key)
            self.def_bufer[key] = dfn
            
        return self.def_bufer[key]

    def Reset(self):
        self.dual_mode_bufer={}
        self.SaveToDisk()

    def SaveToDisk(self):
        with open(self.path_buffer, 'w') as f:
            json.dump(self.dual_mode_bufer, f)

    def _read_from_disk(self):
        with open(self.path_buffer, 'r') as f:
            self.dual_mode_bufer = json.load(f)

    def _dump(self):
        log.info(str(self.dual_mode_bufer))

class TestCacheAgent(unittest.TestCase):
    def setUp(self):
 
        self.key = "cb_compare_fn"
        self.path_cscope_lib = os.path.join(os.getcwd(),"cscope.out")
        self.path_buffer = os.path.join(os.getcwd(),"cacheAgent.buffer")
        self.assertTrue(os.path.isfile(self.path_cscope_lib))
        self.cacheAgent = CacheAgent(self.path_cscope_lib, self.path_buffer)

    def testFindBoth(self):
        ag = self.cacheAgent
        [dfn, symref] = ag.FindBoth(self.key)
        ag.Reset()
        self.assertTrue(len(symref)>0)

    def testFindDef(self):
        ag = self.cacheAgent
        dfn= ag.FindDef(self.key)
        self.assertTrue(len(dfn)>0)


if __name__ == '__main__':
    log_init()
    unittest.main(verbosity=2)