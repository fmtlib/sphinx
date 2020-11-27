extensions = ['sphinx.ext.autocpp']
exclude_patterns = ['_build']
autocpp_input = 'test.h'
autocpp_macros = ['MACRO1=', 'MACRO2()=int']
