__author__ = 'David Owen'

import os
import os.path
import shutil
import sys
import subprocess

import pygments.formatters
import pygments.lexers

from processing_lexer import ProcessingLexer
from pyret_lexer import PyretLexer
from idle_style import IdleStyle

INLINE_STYLES = True
HTML_FOR_CANVAS = True
ADD_CANVAS_CSS = not True
ADD_CIS487_CSS = not True
MATHJAX_OR_MATHML = True
DEFAULT_OUTPUT = 'html'
DEFAULT_STYLE = 'trac'
PYTHON_STYLE = 'trac' # 'idle'
C_STYLE = DEFAULT_STYLE
JAVA_STYLE = DEFAULT_STYLE
PROCESSING_STYLE = 'default'
PYRET_STYLE = DEFAULT_STYLE
PYTHON3 = True
USE_PDF_TEMPLATE = True
USE_DZSLIDES_TEMPLATE = not True
DEBUG_PDFLATEX = not False
XELATEX = False
DELETE_HLINES = True
USE_WKHTMLTOPDF = not True

TEMP = 'pdpm_py_temp'

HTML_COMMAND = 'pandoc -s -t html5 --email-obfuscation=none'
SLIDES_COMMAND = 'pandoc -s -t dzslides --no-highlight \
    --email-obfuscation=none -c dzslides.css'

if HTML_FOR_CANVAS:
    INLINE_STYLES = True

if ADD_CANVAS_CSS:
    HTML_COMMAND += ' -c canvas.css'

if ADD_CIS487_CSS:
    HTML_COMMAND += ' -c ../cis487.css'

if MATHJAX_OR_MATHML:
    if HTML_FOR_CANVAS:
        HTML_COMMAND += ' --mathml'
    else:
        HTML_COMMAND += ' --mathjax'

    SLIDES_COMMAND += ' --mathjax'

if USE_DZSLIDES_TEMPLATE:
    SLIDES_COMMAND += ' --template=pdpm.dzslides'

FONTSIZE = 11
MARGIN = 0.9
PDF_COMMAND = 'pandoc -V fontsize=' + str(FONTSIZE) + \
        'pt -V margin=' + str(MARGIN) + 'in'

WKHTMLTOPDF_COMMAND = 'wkhtmltopdf -q -s Letter ' + \
        '-T {0}in -L {0}in -B {0}in -R {0}in'.format(MARGIN)
        # Font size set in CSS.

if USE_PDF_TEMPLATE:
    PDF_COMMAND += ' --template=pdpm.latex'

def pygmentize(md, out_format, md_is_filename=True, ext='txt'):
    """
    Use pygments to highlight source code blocks in pandoc
    input file.  (If file is source code, put it in a fenced
    code block to make a pandoc input file, then use pygments
    to add highlighting.)

    :param filename: pandoc input file.
    :param out_format: html, slides (html for dzslides) or pdf.

    :return: pandoc input with pygments' highlighting (as html
             tags) in fenced code blocks.
    """

    if md_is_filename:
        pd = open(md).read().split('\n')
        ext = md[md.rfind('.') + 1:]
    else:
        pd = md.split('\n')

    if not (ext in ('txt', 'md')):
        # if md_is_filename:
        #     pd = ['## ' + md] + ['\n'] + ['~~~' + ext] + \
        #             pd + ['~~~']
        # else:
            pd = ['~~~' + ext] + pd + ['~~~']

    style_defs_for_pdf = ''
    pd_new = []
    i = 0

    while i < len(pd):
        s = pd[i].strip()

        if not s.startswith('~~~') or s == '~~~':
            pd_new.append(pd[i])
            i += 1

        # Block to highlight.
        else:
            indent = pd[i].find('~~~')

            # Set language, style.
            language = pd[i][indent + 3:].rstrip()

            if 'py' in language:
                style = PYTHON_STYLE

                if PYTHON3 and language == 'py' or \
                        language == 'python':
                    language = 'python3'

            elif language == 'c':
                style = C_STYLE
            elif language == 'java':
                style = JAVA_STYLE
            elif language == 'processing':
                style = PROCESSING_STYLE
            elif language == 'pyret':
                style = PYRET_STYLE
            else:
                style = DEFAULT_STYLE

            # Set lexer.
            if PYTHON3 and language == 'pycon':
                lexer = pygments.lexers.PythonConsoleLexer(
                    python3=True)
            elif language == 'processing':
                lexer = ProcessingLexer()
            elif language == 'arr' or language == 'pyret':
                lexer = PyretLexer()
            else:
                lexer = pygments.lexers.get_lexer_by_name(
                    language)

            # Set formatter for html / slides.  If not
            # INLINE_STYLES write css file and update
            # HTML_COMMAND / SLIDES_COMMAND.
            if out_format == 'html' or out_format == 'slides':
                if style == 'idle':
                    formatter = pygments.formatters.HtmlFormatter(
                        style=IdleStyle, noclasses=INLINE_STYLES)
                else:
                    formatter = pygments.formatters.HtmlFormatter(
                        style=style, noclasses=INLINE_STYLES)

                if not INLINE_STYLES:
                    css_filename = style + '.css'
                    css_file = open(css_filename, 'w')
                    print(formatter.get_style_defs(), file=css_file)
                    css_file.close()

                    if out_format == 'html':
                        global HTML_COMMAND

                        if not ('css' in HTML_COMMAND):
                            HTML_COMMAND += ' -c ' + css_filename
                    else:  # slides
                        global SLIDES_COMMAND

                        if not ('css' in SLIDES_COMMAND):
                            SLIDES_COMMAND += ' -c ' + css_filename

            # Set formatter for pdf.
            else:
                if style == 'idle':
                    formatter = pygments.formatters.LatexFormatter(
                        style=IdleStyle)
                else:
                    formatter = pygments.formatters.LatexFormatter(
                        style=style)

                style_defs_for_pdf = formatter.get_style_defs()

            # Highlight code block.
            cb = []
            i += 1

            while pd[i].strip() != '~~~':
                cb.append(pd[i][indent:])
                i += 1

            i += 1

            hb = pygments.highlight('\n'.join(cb), lexer, formatter)

            for line in hb.split('\n'):
                pd_new.append(' ' * indent + line)

    return '\n'.join(pd_new), style_defs_for_pdf


def html_canvas_fixes(filename, slides=False):
    html = open(filename).read()

    if not slides:
        html = html[html.find('<body>') + 6:html.find('</body>')]

    # Get rid of code tags.  (Ideally pygmentize above would
    # catch these if followed by, e.g., {.python}.)
    html = html.replace(
        '<code', '<span style="font-family:monospace;" class="code"')
    html = html.replace('</code>', '</span>')

    # Align table cell contents vertically to match
    # latex tables.
    html = html.replace('<td>', '<td style="vertical-align: top">')
    html = html.replace(
        '<td style="text-align: left;">',
        '<td style="text-align: left; vertical-align: top">')
    html = html.replace(
        '<td style="text-align: center;">',
        '<td style="text-align: center; vertical-align: top">')
    html = html.replace(
        '<td style="text-align: right;">',
        '<td style="text-align: right; vertical-align: top">')

    # More little fixes.
    # html = html.replace('h3', 'h4')
    html = html.replace('<code class="url">', '<span class="url">')
    html = html.replace(
        '<pre style="line-height: 125%">',
        '<pre style="font-family:monospace;">')
    html = html.replace('</table>', '</table>&nbsp;')
    
    temp_file = open(TEMP, 'w')
    print(html, file=temp_file)
    temp_file.close()
    shutil.copy(TEMP, filename)
    os.remove(TEMP)


def run_pandoc(in_filename, out_filename, out_format,
               canvas_fixes, style_defs_for_pdf, options=''):

    if out_format == 'slides':
        subprocess.call(SLIDES_COMMAND.split() + options.split() +
                        [in_filename, '-o', out_filename, '--metadata',
                        'pagetitle=' + out_filename])
        
        if canvas_fixes:
            html_canvas_fixes(out_filename, slides=True)

    elif out_format == 'html':
        subprocess.call(HTML_COMMAND.split() + options.split() +
                        [in_filename, '-o', out_filename, '--metadata',
                        'pagetitle=' + out_filename])
        
        if canvas_fixes:
            html_canvas_fixes(out_filename)

    else:  # pdf
        subprocess.call(PDF_COMMAND.split() + options.split() +
                        [in_filename, '-o', 'temp.tex', '--metadata',
                        'pagetitle=' + out_filename])

        try:
            tex = open('temp.tex').read()
        except UnicodeDecodeError:
            tex = open('temp.tex', encoding="latin-1").read()

        os.remove('temp.tex')

        if DELETE_HLINES:
            # Get rid of horizontal lines at the beginning and
            # at the end of the table (to make latex version
            # look like html version).

            # For older pandoc version (Debian)...
            tex = tex.replace('\FL', '')
            tex = tex.replace('\LL', '')

            # For newer pandoc version (OS X)...
            tex = tex.replace('\\hline', '')

            # For still newer pandoc version (Arch)...
            tex = tex.replace('{longtable}[c]', '{longtable}[l]')
            # tex = tex.replace('\\toprule', '')
            # tex = tex.replace('\\bottomrule', '')
            
            # For still newer pandoc version (macOS) ...
            tex = tex.replace('\\toprule()', '')
            tex = tex.replace('\\bottomrule()', '')

        if style_defs_for_pdf != '':
            i = tex.find('\\begin{document}')
            tex = (tex[:i] + '\\usepackage{fancyvrb}' +
                   '\\usepackage{color}' + style_defs_for_pdf
                   + tex[i:])

        # tex_file = open('temp.tex', 'w', encoding='utf-8')
        tex_file = open('temp.tex', 'w')
        print(tex, file=tex_file)
        tex_file.close()

        if XELATEX:
            c = 'xelatex'
        else:
            c = 'pdflatex'

        if DEBUG_PDFLATEX:
            subprocess.call([c, 'temp.tex'])
        else:
            so_file = open(TEMP, 'w')
            subprocess.call([c, 'temp.tex'], stdout=so_file)
            so_file.close()
            os.remove(TEMP)

            os.remove('temp.tex')  # Move back to preceding else and
                               # DEBUG_PDFLATEX will mean the tex
                               # file is kept for inspection.

        shutil.move('temp.pdf', out_filename)
        os.remove('temp.aux')
        os.remove('temp.log')
        # os.remove('temp.out')


def run_wkhtmltopdf(input_file, output_file=False):
    c = WKHTMLTOPDF_COMMAND.split()
    c.append(input_file)

    if output_file:
        c.append(output_file)
    else:
        c.append(input_file.replace('.html', '.pdf'))

    subprocess.call(c)


if __name__ == '__main__':
    out_format = DEFAULT_OUTPUT
    processed_args = []
    filename = ''

    if USE_PDF_TEMPLATE:
        PDF_COMMAND += " --template=" + \
            os.path.abspath(os.path.dirname(sys.argv[0])) + \
            "/pdpm.latex"

    for a in sys.argv[1:]:
        if a.startswith('--'):
            out_format = a[2:]
            processed_args.append(a)
        else:
            filename = a

    temp_file = open(TEMP, 'w')
    pg, style_defs_for_pdf = pygmentize(filename, out_format)
    print(pg, file=temp_file)
    temp_file.close()

    out_filename = filename[:filename.rfind('.')]

    if out_format == 'slides':
        out_filename += '_slides.html'
    else:
        out_filename += '.' + out_format

    run_pandoc(TEMP, out_filename, out_format,
               HTML_FOR_CANVAS, style_defs_for_pdf)
