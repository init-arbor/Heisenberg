import datetime
import platform
import subprocess
try:
    from LogAgent import info
except:
    from Heisenberg.LogAgent import info

class Utility:
    def Cmd(args, cwd):
        start_time = datetime.datetime.now()
        popen_arg_list = {
            "shell": False,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "cwd": cwd,
        }

        if platform.system() == "Windows":
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
    def CscopeExe():
        if platform.system() == "Windows":
            return "cscope"
        #put path of cscope on Mac/Linux/Unix here
        return "/Users/init/Documents/cscope"

class Defines:
    TagSrcWinSyntax = "src_win_syntax"
    TagMainConsoleSyntax = "main_win_syntax"
    TagPathCscopeLib = "path_cscope_lib"
    TagProjectIncludeFolders = "folders"
    TagPreloadedFiles = "inital_files"
    SrcWinSyntax = "A12.tmLanguage"
    MainConsoleSyntax = "Lookup Results.tmLanguage"