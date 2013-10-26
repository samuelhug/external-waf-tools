#!/usr/bin/env python
# encoding: utf-8

from waflib import TaskGen

def options(ctx):
    pass

def configure(ctx):
    find_tool('closure_linter/gjslint.py', 'CLOSURE_LINTER')
    find_tool('closure_linter/fixjsstyle.py', 'CLOSURE_LINTER_FIX')

@TaskGen.feature('gjslint')
def gjslint(self):

    command = self.env.PYTHON + [
            self.env.CLOSURE_LINTER,
            '--strict', '--summary',
            ]

    for root in self.roots:
        command += ['-r', root.abspath()]
    
    return self.bld.exec_command(command)

@TaskGen.feature('fixjsstyle')
def fixjsstyle(self):

    command = self.env.PYTHON + [
            self.env.CLOSURE_LINTER_FIX,
            '--strict'
            ]

    for root in self.roots:
        command += ['-r', root.abspath()]

    return self.bld.exec_command(command)
