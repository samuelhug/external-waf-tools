#!/usr/bin/env python
# encoding: utf-8

import os

tooldir = os.path.dirname(__file__)

def options(ctx):
    ctx.load('wurf_tools')
    ctx.load('python')

    ctx.load_external_tool('utils', 'utils')

def configure(ctx):
    ctx.load('wurf_tools')
    ctx.load('python')

    ctx.load_external_tool('utils', 'utils')

    tools_node = ctx.root.find_dir(tooldir)
    if not tools_node:
        ctx.fatal('Unable to locate the google_closure tool directory.')
    ctx.env.CLOSURE_TOOLS = tools_node.abspath()

    closure_library_node = tools_node.find_dir('closure-library')
    if not closure_library_node:
        ctx.fatal('Unable to locate the closure library directory.')
    ctx.env.CLOSURE_LIBRARY = closure_library_node.abspath() 

    # Locate closure library scripts
    closure_scripts_node = closure_library_node.find_dir('closure/bin/build')
    if not closure_scripts_node:
        ctx.fatal('''Unable to locate the closure library scripts directory.
Note: Did you run `git submodule init` and `git submodule update`''')
    ctx.env.CLOSURE_SCRIPTS = closure_scripts_node.abspath()

    try:
        ctx.find_python_program('closurebuilder', path_list=[ctx.env.CLOSURE_SCRIPTS], var='CLOSURE_BUILDER')
    except:
        ctx.fatal('Unable to locate the closurebuilder script in the closure library repository.')
