
 
from collections import namedtuple
line_result = namedtuple("line_result", ["file",  "line_num", "scope", "code"])

class CscopeOutputFormatter:
    def __init__(self):
        pass
 
    #output: main_console_text, dfn_path, line_num 
    def Parse(self,dfn, symRef, word, root):
 

        definitions, dfn_file, dfn_line_num = self._parseDefFile(dfn)

        result = ["Directory ", root, "\n", 50 * "-", "\n\nSearch\n",
                  10 * ' ', word, "\n\nDefinition\n"]

        result.append(self._format_tuples(definitions))

        if symRef:        
            references = self._string_to_line_results(symRef) 

            #eliminate duplicate
            for d in definitions:
                for r in references:
                    if r.file == d.file and r.line_num == d.line_num:
                        references.remove(r)

            result.append('\n\nSymbolReference\n')
            result.append(self._format_tuples(references))

        main_console_text = ''.join(result)
  
        return main_console_text, dfn_file, dfn_line_num

 
    def _parseDefFile(self,dfn):

        definitions =self._string_to_line_results(dfn)

        def_file = None
        def_line_num = None

        for d in definitions:
            if d.file.endswith(".h"):
               return definitions, d.file, d.line_num
            else:
                def_file=d.file
                def_line_num = d.line_num
        return definitions, def_file, def_line_num

 

    def _string_to_line_results(self, str):
        lines = str.split('\n')
        results = []
        for line in lines:
            if len(line) < 5:
                continue
            results.append(self._get_tuple(line))
        return results

    def _format_tuples(self, tuples):
        pre_d = None
        result = []
        for d in tuples:
            if pre_d and pre_d.file == d.file:
                result.append(
                    " {0:>5} [{1}] {2}\n".format(d.line_num, d.scope, d.code))
            else:
                result.append(
                    "\n{0}:\n {1:>5} [{2}]  {3}\n".format(d.file, d.line_num, d.scope, d.code))
            pre_d = d
        return ''.join(result)

    def _get_tuple(self, cscope_result):

        idx_sp1 = cscope_result.index(" ")
        idx_sp2 = cscope_result.index(" ",  idx_sp1 + 1)
        idx_sp3 = cscope_result.index(" ",  idx_sp2 + 1)

        return line_result(file=cscope_result[:idx_sp1],
                           scope=cscope_result[idx_sp1 + 1:idx_sp2],
                           line_num=cscope_result[idx_sp2 + 1:idx_sp3],
                           code=cscope_result[idx_sp3 + 1:])