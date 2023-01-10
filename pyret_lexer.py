import re
from pygments.lexer import RegexLexer
from pygments.token import *

class PyretLexer(RegexLexer):
    name = 'Pyret'
    aliases = ['pyret']
    filenames = ['*.arr']

    flags = re.MULTILINE

    tokens = {
        'root': [

            (r'(!|->|(?<!<)=>|\[|\]|{|}|:\s|;|,)', Punctuation),
            (r'(\(|\)|\.|::|:=| \^ | \+ | - | \/ | \*| >= | <= |'
             r' <> | == | <=> | =~ |=|>|<)', Operator),
            (r'(\|)', Punctuation),
            (r'(?<!-)(\b|^)[A-Z][A-Za-z]*(?!-)(\b|$)', Keyword.Type),
            (r'(?x)(?<!-)(\b|^) (end|type|type-let|newtype|include|'
             r'import|provide|provide-types|as| fun|lam|check|'
             r'examples|is|is-not|satisfies|violates| raises|'
             r'does-not-raise|raises-violates|raises-satisfies|'
             r'raises-other-than| data|deriving| for|from|and|or|'
             r'not| if|else|when|cases|ask| spy) (?!-)(\b|$)', Keyword),
            (r'(?x)(?<!-)(\b|^) (block:|doc:|where:|with:|sharing:|'
             r'then:|otherwise:| is==|is=~|is<=>|is-not==|is-not=~|'
             r'is-not<=>)', Keyword),
            (r'(?x)(?<!-)(\b|^) (var|ref|shadow|let|letrec|rec|'
             r'method) (?!-)(\b|$)', Keyword),
            (r'(?<!-)(\b|^)(true|false|nothing)(?!-)(\b|$)', Keyword.Constant),
            (r"'[^']*'", String),
            (r'"[^"]*"', String),
            (r'```', String, 'sml'),
            (r"'[^']*$", Error),
            (r'"[^"]*$', Error),
            (r'(?<![a-zA-Z0-9_-])-?[0-9]+([/.][0-9]+)?', Number),
            (r'(?<![a-zA-Z0-9_-])~-?[0-9]+(\.[0-9]+)?', Number.Float),
            (r'#([^|].*)?$', Comment.Single),
            (r'#\|', Comment.Multiline, 'cml'),

            (r'[^\s]', Text),
            (r'\s+', Whitespace)
        ],
        'sml': [
            (r'[^`]+', String),
            (r'```', String, '#pop'),
            (r'`', String)
        ],
        'cml': [
            (r'[^#|]+', Comment.Multiline),
            (r'#\|', Comment.Multiline, '#push'),
            (r'\|#', Comment.Multiline, '#pop'),
            (r'[|#]', Comment.Multiline)
        ],
    }

