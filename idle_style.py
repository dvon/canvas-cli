__author__ = 'David Owen'

from pygments.style import Style
from pygments.token import *

class IdleStyle(Style):
    '''
    Colors like IDLE's.
    '''

    default_style = ''

    styles = { Comment:       "#c00",
               Keyword:       "#f60",
               Operator.Word: "#f60",
               String:        "#090",
               Name.Builtin:  "#909",
               Name.Function: "#00f",
               Name.Class:    "#00f",

               # For Python shell highlighting.
               Generic.Prompt: "#700",
               Generic.Output: "#00f",
               Generic.Error:  "#f00" }
