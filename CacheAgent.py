import logging
import os
import unittest
try:
    from CscopeAgent import CscopeAgent
    from LogAgent import log_init
except:
    from Heisenberg.CscopeAgent import CscopeAgent
    from Heisenberg.LogAgent import log_init



log = logging.getLogger(__name__)

class CacheAgent:
    def __init__(self, path_cscope_lib, path_buffer):
        self.dual_mode_bufer={}
        self.def_bufer={}
        self.history =[]
        self.path_cscope_lib =path_cscope_lib;
        self.cscopeAgent = CscopeAgent(path_cscope_lib)
        self.cscopeTime = 0
        self._update_buffer()

    def FindBoth(self, key):
        self._update_buffer()
        if key not in self.dual_mode_bufer:
            [dfn, symref]= self.cscopeAgent.FindBoth(key)
            self.dual_mode_bufer[key]=[dfn, symref]

        self._add_history(key)
        return self.dual_mode_bufer[key]

    def FindDef(self, key):
        #we do not implement FindDef buffer at this stage
        if key not in self.def_bufer:
            dfn = self.cscopeAgent.FindDef(key)
            self.def_bufer[key] = dfn
        self._add_history(key)
        return self.def_bufer[key]

    def Reset(self):
        self.dual_mode_bufer={}

    def _dump(self):
        log.info(str(self.dual_mode_bufer))

    def _add_history(self, key):
        if key in self.history:
            self.history.remove(key)
        self.history.append(key)

    def _update_buffer(self):
        cscopeTime = os.stat(self.path_cscope_lib).st_mtime
        if self.cscopeTime ==cscopeTime :
            return
        self.dual_mode_bufer={}
        self.cscopeTime =cscopeTime

    def History(self):
        return self.history

class TestCacheAgent(unittest.TestCase):
    def setUp(self):
        self.key = "cb_compare_fn"
        self.path_cscope_lib =  "/Users/init/Documents/code/Saymyname/cscope.out"
        self.path_buffer = os.path.join(os.getcwd(),"cacheAgent.buffer")
        self.assertTrue(os.path.isfile(self.path_cscope_lib))
        self.cacheAgent = CacheAgent(self.path_cscope_lib, self.path_buffer)

    def testFindBoth(self):
        ag = self.cacheAgent
        [dfn, symref] = ag.FindBoth(self.key)
        ag.Reset()
        self.assertTrue(len(symref)>0)
        log.info("found len "+str(len(symref)))

    def testCheckUpdate(self):
        old_file = "/Users/init/Documents/code/Saymyname/cscope.out.old"
        new_file = "/Users/init/Documents/code/Saymyname/cscope.out"
        old_time = os.stat(old_file).st_mtime
        new_file = os.stat(new_file).st_mtime
        self.assertTrue(old_time!=new_file)
        self.assertTrue(old_time==old_time)

    def testFindDef(self):
        ag = self.cacheAgent
        dfn= ag.FindDef(self.key)
        self.assertTrue(len(dfn)>0)


if __name__ == '__main__':
    log_init()
    unittest.main(verbosity=2)