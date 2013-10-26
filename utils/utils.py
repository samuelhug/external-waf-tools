#!/usr/bin/env python
# encoding: utf-8


from waflib import Utils, Task
from waflib.Configure import conf

import os
import shutil

class copy_file(Task.Task):
    """Copies files """
    color = 'GREEN'

    def run(self):
        target_dir = self.outputs[0].parent.abspath()
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
            except OSError:
                pass

        shutil.copy(self.inputs[0].abspath(), self.outputs[0].abspath())
        return 0

@conf
def copy(self, source, target=None, **kw):
    kw['env'] = self.env

    target = target or source.get_bld()
    tsk = copy_file(**kw)
    tsk.set_inputs(source)
    tsk.set_outputs(target)
    self.add_to_group(tsk)
    return tsk

@conf
def find_python_program(self, filename, exts='.py', **kw):
    """
    Search for a python program on the operating system

    :param filename: file to search for
    :type filename: string
    :param path_list: list of paths to look into
    :type path_list: list of string
    :param var: store the results into *conf.env.var*
    :type var: string
    :param environ: operating system environment to pass to :py:func:`waflib.Configure.find_program`
    :type environ: dict
    :param exts: extensions given to :py:func:`waflib.Configure.find_program`
    :type exts: list
    """

    self.load('python')

    try:
        app = self.find_program(filename, exts=exts, **kw)
    except:

        self.start_msg('Checking for python program %r' % filename)
        app = self.find_file(filename + '.py', os.environ['PATH'].split(os.pathsep))
        if not app:
            raise

        var = kw.get('var', '');
        if var:
            self.env[var] = Utils.to_list(self.env.PYTHON) + [app]

        self.end_msg(app)
