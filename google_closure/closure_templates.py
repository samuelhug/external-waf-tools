#!/usr/bin/env python
# encoding: utf-8

from waflib import TaskGen

import os, sys

def options(ctx):
    ctx.load('google_closure')

def configure(ctx):
    ctx.load('google_closure')

    templates_node = ctx.root.find_node(ctx.env.CLOSURE_TOOLS).find_node('closure-templates')
    if not templates_node:
        ctx.fatal('Unable to locate the closure templates root directory.')
    ctx.env.CLOSURE_TEMPLATES_ROOT = templates_node.abspath()

    # Locate closure compiler
    closure_templates_node = templates_node.find_node('SoyToJsSrcCompiler.jar')
    if not closure_templates_node:
        ctx.fatal('Unable to locate the closure templates jar.')
    ctx.env.CLOSURE_TEMPLATES_JAR = closure_templates_node.abspath()

    ctx.find_program('java', var='JAVA')

TaskGen.declare_chain(name='template',
    rule='${JAVA} -jar ${CLOSURE_TEMPLATES_JAR} \
            --shouldProvideRequireSoyNamespaces \
            --cssHandlingScheme GOOG \
            --outputPathFormat ${TGT} \
            ${SRC}',
    ext_in='.soy', ext_out='.soy.js',
    before='closure_compiler_task')
