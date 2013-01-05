#!/usr/bin/env python
# encoding: utf-8
# Samuel Hug, 2013

"""
Support for compiling LESS stylesheets into CSS.

Less Homepage: http://lesscss.org

===========================================================
EXAMPLE
===========================================================

def configure(ctx):
    ctx.load('less')

def build(ctx):
    ctx.load('less')
    ctx(source=ctx.path.find_node('test.less'))

===========================================================
"""
from waflib.Configure import conf
from waflib import TaskGen

def configure(ctx):
    ctx.less_configure()

@conf
def less_configure(ctx):
    ctx.find_program('lessc', var='LESSC')

TaskGen.declare_chain(name='less',
        rule='${LESSC} ${SRC} ${TGT}',
        ext_in='.less', ext_out='.css',
        color='BLUE',
    )
