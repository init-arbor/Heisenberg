
import logging
import os
import unittest
try:
    from CacheAgent import CacheAgent
    from LogAgent import log_init
except:
    from Heisenberg.CacheAgent import CacheAgent
    from Heisenberg.LogAgent import log_init

log = logging.getLogger(__name__)


 

    
class ProjectCentral:
    
    cacheAgents={}
 
    @staticmethod
    def AddProject(project_name, path_cscope_lib):
        if project_name in ProjectCentral.cacheAgents:
            del ProjectCentral.cacheAgents[project_name]
        ProjectCentral.cacheAgents[project_name] = CacheAgent(path_cscope_lib, project_name)
 
    @staticmethod
    def Get(project_name):
        return ProjectCentral.cacheAgents[project_name]

    @staticmethod
    def Exist(project_name):
        return project_name in ProjectCentral.cacheAgents



class TestProjectCentral(unittest.TestCase):
    def setUp(self):
 
        self.path_cscope_lib = os.path.join(os.getcwd(),"cscope.out")
        self.key = "cb_compare_fn"

    def testInit(self):
 
        ProjectCentral.AddProject("testPC", self.path_cscope_lib)
        ProjectCentral.AddProject("testPC2", self.path_cscope_lib)
        ProjectCentral.AddProject("testPC", self.path_cscope_lib)
        dfn = ProjectCentral.Get("testPC2").FindDef(self.key) 
 
        log.info(dfn)

if __name__ == '__main__':
    log_init()
    unittest.main(verbosity=2)