import sublime
import sublime_plugin
import os
import re
from Heisenberg.ProjectCentral import ProjectCentral
from Heisenberg.LogAgent import info
from Heisenberg.CscopeOutputFormatter import CscopeOutputFormatter
from Heisenberg.FileReader import FileReader

class WindowManger:
    DefWin = "DEFINITION"
    MainWin = "MAIN CONSOLE"

    def __init__(self, win):
        self.win = win
        self.project_name = self.win.project_file_name()
        
        project_data = self.win.project_data()
        self.src_win_syntax = project_data["src_win_syntax"]
        self.main_win_syntax = project_data["main_win_syntax"]

        path_cscope_lib = project_data["path_cscope_lib"]
        self.root_directory =  os.path.dirname(path_cscope_lib) 


    def PrintMain(self, text):
        self._print(WindowManger.MainWin, text)

    def PrintDef(self, text):
        self._print(WindowManger.DefWin, text)
 
    def InitWindow(self):
        active_view = self.win.active_view()
        self.win.set_layout({
            "cols": [0,  1],
            "rows": [0, 1],
            "cells": [[0, 0, 1, 1]]
        })
 
        self.win.set_layout({
            "cols": [0.0, 0.75, 1.0],
            "rows": [0.0, 0.5, 1.0],
            "cells":
            [[0, 0, 1, 2], [1, 0, 2, 1], [1, 1, 2, 2]]
        })
        self._put_view_into_win(WindowManger.DefWin, 1, self.src_win_syntax)
        self._put_view_into_win(WindowManger.MainWin, 2, self.main_win_syntax)
        if active_view:
            self.win.focus_view(active_view)

    def Root(self):
        return self.root_directory

    def Highlight(self, line_num, word, view=None):
        if view is None:
            view = self._get_view(WindowManger.DefWin)
        view.run_command("scroll_highlight", 
            {"line_num": line_num, "key": word})

    def _print(self, win_type, text):
        view = self._get_view(win_type)
        if not view:
            self.InitWindow()
            view = self._get_view(win_type)

        view.run_command("display_text", {"text": text})

    def _get_view(self, name):
        for view in self.win.views():
            if view.name() == name:
                return view
        return None

    def _createView(self, group, index, name, syntax):
        view = self.win.new_file()
        self.win.set_view_index(view, group, index)
        view.set_scratch(True)
        view.set_name(name)
        if syntax:
            view.set_syntax_file(syntax)

    def _put_view_into_win(self, name, idx, syntax):
        view = self._get_view(name)
        if view:
            self.win.set_view_index(view, idx, 0)
        else:
            self._createView(idx, 0, name, syntax)
 
    def confirm_initiated(self):
        if not ProjectCentral.Exist(self.project_name):
            info("confirm_initiated ")
            self.win.run_command("init_heisenberg")


class InitHeisenbergCommand(sublime_plugin.WindowCommand):

    def __init__(self, win):
        self.win = win
        self.win_manager = None 

    def _load_project_data(self):
        project_data = self.win.project_data()
        self.project_name = self.win.project_file_name()
         
        self.path_cscope_lib = project_data["path_cscope_lib"]
        self.init_files = project_data["initial_files"] if "initial_files" in project_data else []

        info("Initiated: {}".format(os.path.basename(self.project_name)))
        #info("path_cscope_lib {}".format(self.path_cscope_lib))
 
    def _load_initial_files(self):
        idx = 0
        for f in self.init_files:
            if os.path.isfile(f):
                view = self.win.open_file(f)
                self.win.set_view_index(view, 0, idx)
                idx += 1

    def run(self):
        if not self.win_manager:
            self.win_manager = WindowManger(self.win)
        #data control
        self._load_project_data()
        ProjectCentral.AddProject(self.project_name, self.path_cscope_lib)

        #window control
        active_view = self.win.active_view()
        self.win_manager.InitWindow()

        #file control
        self._load_initial_files()

        if active_view:
            self.win.focus_view(active_view)


class Validator:
    @staticmethod 
    def _invalid_word(view, word):
        if len(word)<2 or not word[0].isalpha():
            return True

        scope_name = view.scope_name(view.sel()[0].begin())
        if "keyword.control" in scope_name or \
            "storage.type" in scope_name or \
            "source.c" == scope_name or \
            "constant." in scope_name:
            return True
        return False

    def WantedLookup(view):
 
        region = view.word(view.sel()[0])
        word = view.substr(region).strip()
        if Validator._invalid_word(view, word):
            return False, None
        return True, word


class LookupWordCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        self.view = view
        self.project_name = view.window().project_file_name()
        self.win_manager = None
        self.formatter = CscopeOutputFormatter()
        self.proj_central =None
    def run(self, edit, mode=None, word=None):

        if not self.win_manager:
            self.win_manager = WindowManger(self.view.window())
            self.win_manager.confirm_initiated()
            self.proj_central = ProjectCentral.Get(self.project_name)
        if not word:
            valid, word = Validator.WantedLookup(self.view)
            if not valid:
                return
        info(word)
        #lookup mode selection

        if mode =="def_only":
            info("Lookup Def: {}".format(word))
            dfn = self.proj_central.FindDef(word)
            symref = ""

        else:
            info("Lookup Both: {}".format(word))
            [dfn, symref]= self.proj_central.FindBoth(word)


        #parse result
        main_console_text, dfn_path, line_num = self.formatter.Parse(
            dfn, symref, word, self.win_manager.Root())
 
        #print on main console
        self.win_manager.PrintMain(main_console_text)

        
        #read dfn file and scroll to that line
        self.view.run_command("load_win", {
                "filepath": dfn_path,
                "line_num": line_num,
                "word": word,
                "mode":"load_def"}
                )


class LoadWinCommand(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.view = view
        self.win_manager = None
        self.line_pattern = re.compile('^([\d]+) \[')
        self.filename_pattern = re.compile('^([\w\/.]+):')

    #triggered by LookupWordCommand (with valid dfn_path, line_num, word)
    #triggered by User presses Fn in Main console (without valid dfn_path, line_num, word)
    def run(self, edit, mode, filepath=None, line_num=None, word=None):
        if not self.win_manager:
            self.win_manager = WindowManger(self.view.window())
            self.win_manager.confirm_initiated()
        if not filepath:
            #triggerred by User presses Fn in Main console
            #we have to find dfn_path and line_num
            if self.view.name() !=WindowManger.MainWin:
                self.win_manager.PrintDef("No definition found")
                return 
            [filepath, line_num, word] = self._get_filepath_line_no_word()

        if not filepath:
            #info("cannot find dfn path")
            return

        #read file
        filepath = os.path.join( self.win_manager.Root() , filepath)

        if mode=="load_def":
            file_content = FileReader.ReadFile(filepath)

            #show file on def win
            self.win_manager.PrintDef(file_content)

            #highlight word on line_no
            self.win_manager.Highlight(line_num, word)
        else:
            #mode is "load_src"
            win = self.view.window()
            view = win.open_file(filepath)
            win.set_view_index(view, 0, 0)
            self.win_manager.Highlight(line_num, word, view)
 
    def _get_filepath_line_no_word(self):
        #based on user cursor position in main console, 
        #we get dfn path and line_no
        view = self.view
        line = view.substr(view.line(view.sel()[0].begin())).strip()

        result = self.line_pattern.match(line)
        if not result:
            return None, 0, ""

        line_num = int(result.group(1))
        filename = None
        (row, col) = view.rowcol(view.sel()[0].begin())

        while row >= 1:
            pre_line = self._get_line(view, row)
            result = self.filename_pattern.match(pre_line)
            if result:
                filename = result.group(1)
                break
            row = row - 1
        if filename is None:
            return None, 0, ""

        word =  self._get_line(self.view, 5).strip()

        return filename, line_num, word

    def _get_line(self, view, row_count):
        line_region = sublime.Region(view.text_point(row_count - 1, 0),
                                     view.text_point(row_count, 0))
        line = view.substr(line_region)

        return line


class InputLookupCommand(sublime_plugin.WindowCommand):

    def __init__(self, win):
        self.win = win

    def run(self):
        CLIPBOARD_SIZE = 16
        clipboard = sublime.get_clipboard(CLIPBOARD_SIZE).strip()
 
        initial = clipboard if len(clipboard) < CLIPBOARD_SIZE else ""

        self.win.show_input_panel(
            "Search Symbol", initial, self.on_done, None, None)

    def on_done(self, word): 
        self.win.active_view().run_command("lookup_word", {"mode":"def_and_sym", "word": word})


class SaveCahcheToDiskCommand(sublime_plugin.WindowCommand):
    def __init__(self, win):
        self.win = win
        self.project_name = self.win.project_file_name()

    def run(self):
        ProjectCentral.Get(self.project_name).SaveToDisk()
        info("")


#[non public] used in WindowManger
class DisplayTextCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        self.view = view

    def run(self, edit, text, line_num=None):

        view = self.view
        view.erase(edit,  sublime.Region(0, self.view.size()))
        view.insert(edit, 0, text)
        if line_num:
            view.show_at_center(view.text_point(int(line_num) - 1, 0))

 
#[non public]  
class ScrollHighlightCommand(sublime_plugin.TextCommand):
    MAX_RETRY = 5

    def __init__(self, view):
        self.view = view
        self.line_num = None
        self.key = None
        self.wait_count = 0

    def callback(self):
        line_num = self.line_num
        key = self.key
        view = self.view
        # info(":callback: line {0} key {1} point{2}".format(
        #      line_num,  key,  view.text_point(line_num - 1, 0)))
        # sublime has some bug and this is a workaround
        #use case: when load src, if file is too large, scoll will not work
        #wkr: temp wait when file completes loading
        if view.text_point(line_num - 1, 0) == 0 and \
            self.wait_count < ScrollHighlightCommand.MAX_RETRY:
            sublime.set_timeout(self.callback, 200)
            self.wait_count += 1
            return

        sel_start = view.text_point(line_num - 1, 0)
        sel_end = view.text_point(line_num, 0) - 1

        line_region = sublime.Region(view.text_point(line_num - 1, 0),
                                     view.text_point(line_num, 0))
        line = view.substr(line_region)
        # info("Region {0}   row_count {2}".format(
        #     line_region, line, line_num))

        if not key in line:
            info("no key '{0}' in line '{1}' view {2}' ".format(
                key, line, view.file_name()))
        else:
            st_idx = line.rindex(key)
            sel_start += st_idx
            sel_end = sel_start + len(key)

        view.sel().clear()
        view.sel().add(sublime.Region(sel_start, sel_end))
        view.show_at_center(view.text_point(line_num - 1, 0))

    def run(self, edit, line_num, key):
        line_num = int(line_num)
 
        self.line_num = line_num
        self.key = key

        self.callback()