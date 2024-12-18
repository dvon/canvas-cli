__author__ = 'David Owen'

import re
from pygments.lexer import RegexLexer, bygroups, using, this
from pygments.token import *

class ProcessingLexer(RegexLexer):
    '''
    Lexer for Processing (https://processing.org).  Started
    with pygments.lexers.jvm.JavaLexer (BSD license), added
    Processing builtin globals, functions, constants.
    '''

    name = 'Processing'
    aliases = ['processing']
    filenames = ['*.pde']
    mimetypes = ['text/x-processing']

    flags = re.MULTILINE | re.DOTALL | re.UNICODE

    tokens = {
        'root': [
            (r'[^\S\n]+', Text),
            (r'//.*?\n', Comment.Single),
            (r'/\*.*?\*/', Comment.Multiline),

            # Processing built-in globals.
            (r'(displayHeight|displayWidth|focused|frameCount|'
             r'frameRate|height|width|Array|ArrayList|FloatDict|'
             r'FloatList|HashMap|IntDict|IntList|JSONArray|'
             r'JSONObject|Object|String|StringDict|StringList|'
             r'Table|TableRow|XML|PShape|mouseButton|mousePressed|'
             r'mouseX|mouseY|pmouseX|pmouseY|key|keyCode|'
             r'keyPressed|BufferedReader|PrintWriter|PImage|'
             r'PGraphics|PShader|PFont|PVector)\b',
             Name.Variable.Global),
            (r'(pixels)(\s*)(\[)',
             bygroups(Name.Variable.Global, Text, Operator)),

            # Processing built-in functions.
            (r'(draw|exit|loop|noLoop|popStyle|pushStyle|redraw|'
             r'setup|thread|cursor|frameRate|noCursor|size|binary|'
             r'boolean|byte|char|float|hex|int|str|unbinary|unhex|'
             r'join|match|matchAll|nf|nfc|nfp|nfs|split|'
             r'splitTokens|trim|append|arrayCopy|concat|expand|'
             r'reverse|shorten|sort|splice|subset|createShape|'
             r'loadShape|arc|ellipse|line|point|quad|rect|'
             r'triangle|bezier|bezierDetail|bezierPoint|'
             r'bezierTangent|curve|curveDetail|curvePoint|'
             r'curveTangent|curveTightness|box|sphere|'
             r'sphereDetail|ellipseMode|noSmooth|rectMode|smooth|'
             r'strokeCap|strokeJoin|strokeWeight|beginContour|'
             r'beginShape|bezierVertex|curveVertex|endContour|'
             r'endShape|quadraticVertex|vertex|shape|shapeMode|'
             r'mouseClicked|mouseDragged|mouseMoved|mousePressed|'
             r'mouseReleased|mouseWheel|keyPressed|keyReleased|'
             r'keyTyped|createInput|createReader|loadBytes|'
             r'loadJSONArray|loadJSONObject|loadStrings|loadTable|'
             r'loadXML|open|parseXML|selectFolder|selectInput|day|'
             r'hour|millis|minute|month|second|year|print|'
             r'printArray|println|save|saveFrame|beginRaw|'
             r'beginRecord|createOutput|createWriter|endRaw|'
             r'endRecord|PrintWriter|saveBytes|saveJSONArray|'
             r'saveJSONObject|saveStream|saveStrings|saveTable|'
             r'saveXML|selectOutput|applyMatrix|popMatrix|'
             r'printMatrix|pushMatrix|resetMatrix|rotate|rotateX|'
             r'rotateY|rotateZ|scale|shearX|shearY|translate|'
             r'ambientLight|drectionalLight|lightFalloff|lights|'
             r'lightSpecular|noLights|normal|pointLight|spotLight|'
             r'beginCamera|camera|endCamera|frustum|ortho|'
             r'perspective|printCamera|printProjection|modelX|'
             r'modelY|modelZ|screenX|screenY|screenZ|ambient|'
             r'emissive|shininess|specular|background|clear|'
             r'colorMode|fill|noFill|noStroke|stroke|alpha|blue|'
             r'brightness|color|green|hue|lerpColor|red|'
             r'saturation|createImage|image|imageMode|loadImage|'
             r'noTint|requestImage|tint|texture|textureMode|'
             r'textureWrap|blend|copy|filter|get|loadPixels|set|'
             r'updatePixels|blendMode|createGraphics|PGraphics|'
             r'loadShader|PShader|resetShader|shader|createFont|'
             r'loadFont|text|textFont|textAlign|textLeading|'
             r'textMode|textSize|textWidth|textAscent|textDescent|'
             r'abs|ceil|constrain|dist|exp|floor|lerp|log|mag|map|'
             r'max|min|norm|pow|sound|sq|sqrt|acos|asin|atan|'
             r'atan2|cos|degrees|radians|sin|tan|noise|'
             r'noiseDetail|noiseSeed|random|randomGaussian|'
             r'randomSeed)(\s*)(\()',
             bygroups(Name.Builtin, Text, Operator)),

            # Processing built-in constants.  (CENTER, RADIUS not
            # listed in https://www.processing.org/reference/ ??)
            (r'(HALF_PI|PI|QUARTER_PI|TAU|TWO_PI|CENTER|RADIUS)',
             Name.Constant),

            # From original Java lexer...

            # keywords: go before method names to avoid lexing "throw new XYZ"
            # as a method signature
            (r'(assert|break|case|catch|continue|default|do|else|finally|for|'
             r'if|goto|instanceof|new|return|switch|this|throw|try|while)\b',
             Keyword),
            # method names
            (r'((?:(?:[^\W\d]|\$)[\w.\[\]$<>]*\s+)+?)'  # return arguments
             r'((?:[^\W\d]|\$)[\w$]*)'                  # method name
             r'(\s*)(\()',                              # signature start
             bygroups(using(this), Name.Function, Text, Operator)),
            (r'@[^\W\d][\w.]*', Name.Decorator),
            (r'(abstract|const|enum|extends|final|implements|native|private|'
             r'protected|public|static|strictfp|super|synchronized|throws|'
             r'transient|volatile)\b', Keyword.Declaration),
            (r'(boolean|byte|char|double|float|int|long|short|void)\b',
             Keyword.Type),
            (r'(package)(\s+)', bygroups(Keyword.Namespace, Text), 'import'),
            (r'(true|false|null)\b', Keyword.Constant),
            (r'(class|interface)(\s+)', bygroups(Keyword.Declaration, Text), 'class'),
            (r'(import)(\s+)', bygroups(Keyword.Namespace, Text), 'import'),
            (r'"(\\\\|\\"|[^"])*"', String),
            (r"'\\.'|'[^\\]'|'\\u[0-9a-fA-F]{4}'", String.Char),
            (r'(\.)((?:[^\W\d]|\$)[\w$]*)', bygroups(Operator, Name.Attribute)),
            (r'^\s*([^\W\d]|\$)[\w$]*:', Name.Label),
            (r'([^\W\d]|\$)[\w$]*', Name),
            (r'[~^*!%&\[\](){}<>|+=:;,./?-]', Operator),
            (r'[0-9][0-9]*\.[0-9]+([eE][0-9]+)?[fd]?', Number.Float),
            (r'0x[0-9a-fA-F]+', Number.Hex),
            (r'[0-9]+(_+[0-9]+)*L?', Number.Integer),
            (r'\n', Text)
        ],
        'class': [
            (r'([^\W\d]|\$)[\w$]*', Name.Class, '#pop')
        ],
        'import': [
            (r'[\w.]+\*?', Name.Namespace, '#pop')
        ],
    }
