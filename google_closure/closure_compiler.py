#!/usr/bin/env python
# encoding: utf-8

from waflib import Task
from waflib.Configure import conf

import os, sys

def options(ctx):
    ctx.load('python')
    ctx.load('google_closure')

def configure(ctx):
    ctx.load('google_closure')

    # Locate closure compiler
    closure_compiler_node = ctx.root.find_node(ctx.env.CLOSURE_TOOLS).find_node('closure-compiler/compiler.jar')
    if not closure_compiler_node:
        ctx.fatal('Unable to locate the closure compiler jar.')
    ctx.env.CLOSURE_COMPILER_JAR = closure_compiler_node.abspath()

    ctx.find_program('java', var='JAVA')

    ctx.load('python')


class closure_compiler_task(Task.Task):

    vars = ['PYTHON', 'CLOSURE_BUILDER', 'CLOSURE_LIBRARY', 'CLOSURE_COMPILER']
    color = 'CYAN'

    def __init__(self, namespaces, roots, target, inputs=None, compile_type=None, compiler_flags=[], *k, **kw):
        Task.Task.__init__(self, *k, **kw)

        sys.path.append(self.env.CLOSURE_SCRIPTS)

        self.depstree = __import__('depstree')
        self.treescan = __import__('treescan')
        self.closurebuilder = __import__('closurebuilder')

        self.namespaces = namespaces
        self.compiler_flags = compiler_flags

        self.paths = None

        self.input_nodes = inputs or []

        self.set_outputs(target)

        self.compile_type = compile_type
        if compile_type == 'whitespace':
            compiler_flags += ['--compilation_level=WHITESPACE']
        elif compile_type == 'simple':
            compiler_flags += ['--compilation_level=SIMPLE_OPTIMIZATIONS']
        elif compile_type == 'advanced':
            compiler_flags += ['--compilation_level=ADVANCED_OPTIMIZATIONS']
        elif compile_type == 'concat' or compile_type is None:
            pass # Default
        else:
            raise Execption('Unrecognized compile_type ({0})'.format(compile_type))

        # Set the default compliation roots
        self.roots = [
            os.path.join(self.env.CLOSURE_LIBRARY, 'closure/goog'),
            os.path.join(self.env.CLOSURE_LIBRARY, 'third_party/closure/goog')
        ]
        
        self.roots += roots

    def jscompiler(self):
        args = [self.env.JAVA, '-jar', self.env.CLOSURE_COMPILER_JAR]

        for node in self.inputs:
            args += ['--js', node.abspath()]

        args += ['--js_output_file', self.outputs[0].abspath()]

        args += self.compiler_flags

        return self.bld.exec_command(args)

    def run(self):

        if self.compile_type == 'concat':
            ## Concatenate
            compiled_source = ''.join([s.read()+'\n' for s in self.inputs])
            self.outputs[0].write(compiled_source)
            return 0
        else:
            ## Compile
            return self.jscompiler()


    def scan(self):

        sources = set()

        for path in self.roots:
            for js_path in self.treescan.ScanTreeForJsFiles(path):
                sources.add(self.closurebuilder._PathSource(js_path))

        tree = self.depstree.DepsTree(sources)

        input_namespaces = set()
        for ns in self.namespaces:
            input_namespaces.add(ns)

        # The Closure Library base file must go first.
        base = self.closurebuilder._GetClosureBaseFile(sources)
        deps = [base] + tree.GetDependencies(input_namespaces)

        dep_paths = (os.path.relpath(s.GetPath(), self.bld.path.srcpath()) for s in deps)
        dep_nodes = [self.bld.path.find_resource(p) for p in dep_paths]
        
        self.set_inputs(dep_nodes)
        self.set_inputs(self.input_nodes)

        return (dep_nodes, [])

@conf
def closure_compiler(self, *k, **kw):
    kw['env'] = self.env
    tsk = closure_compiler_task(*k, **kw)
    self.add_to_group(tsk)
    return tsk
