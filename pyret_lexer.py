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
            # (r'(?!-)(\b|^)[A-Z]\w*(?!-)(\b|$)', Keyword.Type),
                # Highlight capitalized identifiers assuming
                # they're data types.  (Atom & VS Code
                # highlighters do this; CPO editor does not.)

            (r'(?<!-)(\b|^)(block|check|doc|else|examples|'
             r'otherwise|provide|row|sharing|source|table|then|'
             r'where|with)(?=:)', Keyword),
            (r'(?<!-)(\b|^)(and|as|ascending|ask|by|cases|'
             r'check|data|descending|do|does-not-raise|else|'
             r'else if|end|examples|extend|extract|for|from|fun|'
             r'hiding|if|import|include|is|is==|is=~|is-not|'
             r'is-not==|is-not=~|is-not<=>|is-roughly|is<=>|'
             r'because|lam|lazy|let|letrec|load-table|method|'
             r'module|newtype|of|or|provide|provide-types|'
             r'raises|raises-other-than|raises-satisfies|'
             r'raises-violates|reactor|rec|ref|sanitize|'
             r'satisfies|select|shadow|sieve|spy|order|'
             r'transform|type|type-let|using|use|var|violates|'
             r'when)(?!-)(\b|$)', Keyword),

            (r'(?<!-)(\b|^)(true|false)(?!-)(\b|$)',
                Name.Constant),
                # Name.Constant, rather than Keyword.Constant,
                # because it's more likely to be assigned a
                # different color by pygments styles.
                # (Atom & VS Code highlighters include
                # "nothing" here but it isn't highlighted as
                # a keyword by the CPO editor.)

            (r'(\[|\]|{|}|\(|\)|;|\\|\.\.\.|,|->|\||:=|:)',
                Punctuation),
            (r'\.(?!\d)', Punctuation),
            (r'=(?![~>])', Punctuation),

            (r'(!|%)', Operator),
            (r'(?<=\s)(\^|\+|-|\*|/|<=>|<=|>=|==|=~|<>|<|>|=>)'
             r'(?=\s)', Operator),

            (r'(?<!-)(\b|^)-?\d+([/.]\d+)?', Number),
            (r'(?<!-)(\b|^)~-?\d+([/.]\d+)?', Number.Float),
                # Number.Float used for Roughnum; might be
                # assigned a different color than Number.

            (r"'[^']*'", String),
            (r'"[^"]*"', String),
            (r'```', String, 'multiline string'),

            (r'#(?!\|).*$', Comment),
            (r'#\|', Comment.Multiline, 'multiline comment'),

            (r'\S', Text),
            (r'\s+', Whitespace)
        ],

        'multiline string': [
            (r'```', String, '#pop'),
            (r'([^`]|`(?!`)|``(?!`))', String)
        ],

        'multiline comment': [
            (r'#\|', Comment.Multiline, '#push'),
            (r'\|#', Comment.Multiline, '#pop'),
            (r'([^\|]|\|(?!#))', Comment.Multiline)
        ]
    }
