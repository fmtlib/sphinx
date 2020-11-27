"""
    test_ext_autocpp
    ~~~~~~~~~~~~~~~~

    Test sphinx.ext.autocpp extension.

    :copyright: Copyright 2007-2020 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import pytest


@pytest.mark.sphinx('text', testroot='ext-autocpp')
def test_autocpp(app, status, warning):
    app.builder.build_all()

    result = (app.outdir / 'index.txt').read_text()

    assert 'void fun()' in result
    assert 'Function *fun* description' in result
    assert '* item 1' in result
    assert '* item 2' in result

    assert 'template<typename T>\nvoid fun_template(T)' in result
    assert 'A function template' in result

    assert 'void fun_ref(int &a, int &b)' in result
    assert 'A function with reference parameters' in result

    assert 'void fun_ptr(int *a, int *b)' in result
    assert 'A function with pointer parameters' in result

    assert 'void fun_with_comments()' in result
    assert 'void fun_with_macro(int)' in result
    assert 'auto fun_with_trailing_return() -> int' in result

    assert 'Not an apidoc' not in result

    warn = warning.getvalue()
    assert 'index.rst:6: WARNING: Error in "autocppfunction" directive' in warn
    assert 'WARNING: Declaration not found: bad()' in warn
    assert 'test.h:18: WARNING: ' in warn
    assert 'bad_decl' in warn

    assert 'class cls' in result
    assert 'Class *cls* description' in result
