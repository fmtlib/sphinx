"""
    sphinx.ext.autocpp
    ~~~~~~~~~~~~~~~~~~

    Automatically insert apidocs for C++ functions into the doctree, thus
    avoiding duplication between apidocs and documentation.

    Usage::

        .. autocppfunction:: fun()

    :copyright: Copyright 2007-2020 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from typing import Any, Dict, List, Mapping

from docutils import nodes
from docutils.statemachine import StringList

import re
import os
import sphinx
import textwrap
from sphinx.addnodes import desc_signature
from sphinx.application import Sphinx
from sphinx.domains import cpp


class DocEntry:
    """An entry in an apidoc dictionary that describes a single C++ entity
       such as a function, class or macro."""
    def __init__(self, decl: str, apidoc: StringList):
        self.decl = decl
        self.apidoc = apidoc


def normalize(sig: str) -> str:
    """Normalize the function signature `sig` for matching."""
    sig = sig.replace(' &', '&').replace('& ', '&')
    sig = sig.replace(' *', '*').replace('* ', '*')
    return re.sub(r'\s*->.*', '', sig)


def extract_apidocs(obj: cpp.CPPObject) -> Mapping[str, DocEntry]:
    """
    Extract apidocs from the source code, cache them in obj.env.temp_data and
    return.
    """

    APIDOCS_KEY = 'autocpp:apidocs'
    apidocs = obj.env.temp_data.get(APIDOCS_KEY)
    if apidocs:
        return apidocs

    macros = {}
    for macro in obj.config.autocpp_macros:
        m = re.match(r'([^(]*)(\(.*\))?=(.*)', macro)
        if not m:
            raise Exception('Invalid autocpp_macros item: ' + macro)
        macros[m.group(1)] = m.group(3)
    macros_re = re.compile(r'({})(\([^()]*\))?'.format('|'.join(macros.keys())))

    src = ''
    input = obj.config.autocpp_input
    if input:
        filename = os.path.join(obj.env.srcdir, input)
        with open(filename) as f:
            src = f.read()

    # Find all apidoc comments.
    apidocs = {}
    start = 0
    lineno = 1
    for match in re.finditer(r'/\*\*(.*?)\*/\s*(.*?)[;{]', src, re.DOTALL):
        decl =  re.sub(r'//.*\n', '\n', match[2])
        decl = macros_re.sub(lambda m: macros[m.group(1)], decl).strip()
        apidoc = textwrap.dedent(match[1].lstrip('\n')).split('\n')
        class_decl = re.sub(r'class ', '', decl)
        is_class = decl != class_decl
        if is_class:
            decl = class_decl
        parser = cpp.DefinitionParser(decl, location=None, config=obj.config)
        try:
            if is_class:
                parsed_decl = parser.parse_declaration('class', 'class')
            else:
                parsed_decl = parser.parse_declaration('function', 'function')
        except cpp.DefinitionError as e:
            end = match.start(2)
            lineno += src.count('\n', start, end)
            start = end
            obj.state.document.reporter.warning(
                str(e), source=filename, line=lineno)
            continue
        if is_class:
            key = str(parsed_decl.declaration)
        else:
            key = normalize(str(parsed_decl.declaration.decl))
        apidocs[key] = DocEntry(decl, StringList(apidoc))
    obj.env.temp_data[APIDOCS_KEY] = apidocs
    return apidocs


class AutoCppFunction(cpp.CPPFunctionObject):
    def handle_signature(self, sig: str, signode: desc_signature) -> cpp.ASTDeclaration:
        self.objtype = 'function'
        apidocs = extract_apidocs(self)
        entry = apidocs.get(normalize(sig))
        if entry:
            self.content = entry.apidoc
            sig = entry.decl
        else:
            self.state.document.reporter.warning(
                'Declaration not found: ' + sig, line=self.lineno)
        return cpp.CPPFunctionObject.handle_signature(self, sig, signode)


class AutoCppClass(cpp.CPPClassObject):
    def handle_signature(self, sig: str, signode: desc_signature) -> cpp.ASTDeclaration:
        self.objtype = 'class'
        apidocs = extract_apidocs(self)
        entry = apidocs.get(sig)
        if entry:
            self.content = entry.apidoc
            sig = entry.decl
        else:
            self.state.document.reporter.warning(
                'Declaration not found: ' + sig, line=self.lineno)
        return cpp.CPPClassObject.handle_signature(self, sig, signode)


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_config_value('autocpp_input', None, 'env')
    app.add_config_value('autocpp_macros', [], 'env')
    app.add_directive('autocppfunction', AutoCppFunction)
    app.add_directive('autocppclass', AutoCppClass)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
