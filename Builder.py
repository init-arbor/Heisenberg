import json
import os

try:
    from Utility import Utility, Defines
    from LogAgent import info
except:
    from Heisenberg.Utility import Utility, Defines
    from Heisenberg.LogAgent import info

class Builder:
    def __init__(self, codebase_path, codebase_dirs, target_dir, project_name):
        self.codebase_path = codebase_path
        self.codebase_dirs = codebase_dirs
        self.target_dir = target_dir
        self.project_name = project_name

    def BuildCscopeFiles(self, skip_words=[]):
        cscope_files_path = os.path.join(self.target_dir , self.project_name, "cscope.files")
        info("building cscope.files ... into {}".format(cscope_files_path))

        cscope_files = []

        #get all files in codebase_path/codebase_dirs
        for dir in self.codebase_dirs:
            wanted_dir = os.path.join(codebase_path, dir)
            for path, subdirs, files in os.walk(wanted_dir):
                for name in files:
                    if name.endswith(".c") or \
                        name.endswith(".h") or \
                        name.endswith(".cpp"):
                        cscope_files.append(os.path.join(path, name))
        info(len(cscope_files))
        #remove files that contain skip_words
        filtered_cscope_files =[]
        wanted = True
        for file in cscope_files:
            for word in skip_words:
                if word in file:
                    wanted = False
            if wanted:
                filtered_cscope_files.append(file)
            wanted = True
        info(len(filtered_cscope_files))
        cscope_files_content = "\n".join(filtered_cscope_files)
        self._write_file(cscope_files_path, cscope_files_content)

    def BuildCscopeLib(self):
        path_cscope_lib = self._get_cscope_lib_path()
        info("building cscope lib ... into {}".format(path_cscope_lib))

        args = [Utility.CscopeExe(), "-bqk"]
        cwd = os.path.dirname(path_cscope_lib)
        Utility.Cmd(args, cwd)

    def BuildSublimeProject(self, initial_files):
        setting = {}
        setting[Defines.TagSrcWinSyntax] = Defines.SrcWinSyntax
        setting[Defines.TagMainConsoleSyntax] = Defines.MainConsoleSyntax
        setting[Defines.TagPathCscopeLib] = self._get_cscope_lib_path()

        folder_list = []
        for f in self.codebase_dirs:
            d = {}
            d["path"] = os.path.join(self.codebase_path, f)
            folder_list.append(d)
        setting[Defines.TagProjectIncludeFolders] = folder_list


        #set preloaded files
        preloaded_files = []
        for f in initial_files:
            preloaded_files.append(os.path.join(self.codebase_path, f))
        setting[Defines.TagPreloadedFiles] = preloaded_files

        #write to disk
        filepath = os.path.join( self.target_dir, self.project_name,
                    self.project_name+".sublime-project")
        self._write_json(filepath, setting)
        info("building sublime-project ... into {}".format(filepath))


    def _write_file(self, filepath, content):
        self._make_sure_dir_exist(filepath)
        with open(filepath, 'w') as f:
            f.write(content)

    def _write_json(self, filepath, content):
        self._make_sure_dir_exist(filepath)
        with open(filepath, 'w') as f:  
            json.dump(content, f)
    def _get_cscope_lib_path(self):
        return os.path.join(self.target_dir, self.project_name, "cscope.out")

    def _make_sure_dir_exist(self, filepath):
        dir = os.path.dirname(filepath)
        if not os.path.exists(dir):
            os.makedirs(dir)

if __name__ == '__main__':
    #---------------------  
    # user config
    #--------------------- 
    build_cscope_files = True
    build_csocpe_out_flag = True
    build_sublime_project = True

    skip_words = []

    target_dir ="/Users/init/Documents/code"

    codebase_path = "/Users/init/Documents/mmcp"
    codebase_dirs = [
            "nas",
            "mmode/cm"
    ] 
    project_name = "Saymyname"
    initial_files = [
        "nas/mm/src/mmcm.c",
        "nas/mm/src/mmauth.h"
    ]

    builder = Builder(codebase_path, codebase_dirs, target_dir, project_name)
    #---------------------  
    #  build cscope.files
    #--------------------- 
    if build_cscope_files:
        builder.BuildCscopeFiles(skip_words)

    #---------------------  
    #  build cscpe.out
    #--------------------- 
    if build_csocpe_out_flag:
        builder.BuildCscopeLib()

    #---------------------  
    #  build .sublime-project
    #--------------------- 
    if build_sublime_project:
        builder.BuildSublimeProject(initial_files)


