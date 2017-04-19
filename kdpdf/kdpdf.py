import os
import os.path
import subprocess
import sys

LATEX_TEMPLATE = 'kd.latex'
KEEP_TEX_FILE = False

if __name__ == '__main__':
    path_to_this_file = os.path.dirname(os.path.realpath(__file__))
    tp_with_path = os.path.join(path_to_this_file, LATEX_TEMPLATE)
    kd_command = 'kramdown --template ' + tp_with_path + \
        ' -o latex ' + sys.argv[1]
    tex_lines = subprocess.check_output(
        kd_command.split()).decode().split('\n')
    
    no_ext_filename = sys.argv[1][:sys.argv[1].rfind('.')] 
    tex_filename = no_ext_filename + '.tex'
    tex_file = open(tex_filename, 'w')
    in_table = False
    
    for i in range(len(tex_lines)):
        if not in_table:
            if tex_lines[i] == '\\begin{document}':
                print('\\setlength{\\LTleft}{-\\tabcolsep}',
                    file=tex_file)
                print(tex_lines[i], file=tex_file)

            elif tex_lines[i].startswith('\\begin{longtable}'):
                print(tex_lines[i].replace('|', ''), file=tex_file)
                in_table = True
            else:
                print(tex_lines[i], file=tex_file)
        else:
            if tex_lines[i] != '\\hline':
                print(tex_lines[i], file=tex_file)

            if tex_lines[i] == ' \\end{longtable}':
                in_table = False

    tex_file.close()
    subprocess.call(['pdflatex', tex_filename])
    
    if not KEEP_TEX_FILE:
        os.remove(tex_filename)
    
    for e in ['.aux', '.log', '.out']:
        os.remove(no_ext_filename + e)
