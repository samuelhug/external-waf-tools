#!/usr/bin/env python
# encoding: utf-8

from waflib import Build, Context, Utils, Logs
from waflib.Configure import conf

from subprocess import Popen
import os

@conf
def find_all_files(self, filename, path_list=[]):
    """
    Find all files in a list of paths

    :param filename: name of the file to search for
    :param path_list: list of directories to search
    """
    
    p_list = []

    for n in Utils.to_list(filename):
        for d in Utils.to_list(path_list):
            p = os.path.join(d, n)
            if os.path.exists(p):
                p_list.append(p)
    return p_list

@conf
def find_appengine_sdk(ctx, api, version=None, api_version=None, path_list=None):
    import ast

    def parse_version_file(fname):
        def parse_indent_block(lines, cursor):
            def parse_line(line):
                key, val = line.split(':', 1)
                return key.strip(), val.strip()
            def get_indent_level(line):
                return len(line) - len(line.lstrip())

            contents = {}

            block_indent = get_indent_level(lines[cursor])

            while cursor < len(lines):
                line_indent = get_indent_level(lines[cursor])
                if line_indent < block_indent:
                    return (cursor-1, contents)

                key, val = parse_line(lines[cursor])

                if val:
                    contents[key] = ast.literal_eval(val)
                else:
                    cursor, contents[key] = parse_indent_block(lines, cursor+1)
                cursor += 1
                    
            return (cursor, contents)

        with open(fname) as f:
            return parse_indent_block(f.readlines(), 0)[1]

    msg = 'Checking for the %s AppEngine SDK' % api
    if not api_version is None:
        msg += ' with api version %s' % api_version

    ctx.start_msg(msg)

    if path_list == None:
        path_list = os.environ['PATH'].split(os.pathsep)

    files = ctx.find_all_files('appcfg.py', path_list) 

    sdk_dir = None
    sdk_version = None

    for f in files:
        sdk_dir = os.path.dirname(f)
        version_file = os.path.join(sdk_dir, 'VERSION')

        if not os.path.exists(version_file):
            continue

        version_data = parse_version_file(version_file)

        #print version_file
        #print version_data

        if not api in version_data['supported_api_versions']:
            continue

        if (not api_version is None) and not api_version in version_data['supported_api_versions'][api]['api_versions']:
            continue

        sdk_version = version_data

    if sdk_version is None:
        ctx.fatal('Unable to locate an appropriate AppEngine SDK')

    ctx.end_msg(sdk_dir)

    ctx.env.APPENGINE_SDK_PATH = sdk_dir
    ctx.find_python_program('appcfg', path_list=[sdk_dir], var='APPENGINE_SDK_APPCFG')
    ctx.find_python_program('dev_appserver', path_list=[sdk_dir], var='APPENGINE_SDK_DEVAPPSERVER')

@conf
def find_appengine_app(ctx, path='.'):

    if isinstance(path, basestring):
        app_root = ctx.path.find_dir(path)
    else:
        app_root = path

    if not app_root:
        ctx.fatal('Unable to locate application directory ({0})'.format(path))

    yaml = app_root.find_node('app.yaml')
    if not yaml:
        ctx.fatal('Unable to locate application YAML in ({0})'.format(app_root.nice_path()))

    ctx.env.APPENGINE_APP_ROOT = app_root.abspath()
    ctx.env.APPENGINE_APP_YAML = yaml.abspath()


def options(ctx):
    ctx.add_option('--devserver-port', action='store',
                    help='Port for local development server')

    ctx.load('python')
    ctx.load('wurf_tools')

def configure(ctx):
    ctx.load('python')
    ctx.load('wurf_tools')

    ctx.load_external_tool('utils', 'utils')

def deploy(ctx):
    ctx.load('python')
    ctx.load('wurf_tools')

    print('Deploying Application to AppEngine...')

    app_root = ctx.root.find_dir(ctx.env.APPENGINE_APP_ROOT)
    if not app_root:
        ctx.fatal('Unable to locate application directory ({0})'.format(ctx.env.APPENGINE_APP_ROOT))

    cmd = ctx.env.PYTHON + [ctx.env.APPENGINE_SDK_APPCFG,
            'update', app_root.get_bld().abspath(),
            '--oauth2',
            '--no_cookies',
        ]

    proc = Popen(cmd)

    try:
        proc.wait()
    except KeyboardInterrupt:
        Logs.pprint('RED', 'Deployment Interrupted... Shutting Down')
        proc.terminate()

def serve(ctx):
    ctx.load('python')
    ctx.load('wurf_tools')

    print('Starting Development Server...')

    app_root = ctx.root.find_dir(ctx.env.APPENGINE_APP_ROOT)
    if not app_root:
        ctx.fatal('Unable to locate application directory ({0})'.format(ctx.env.APPENGINE_APP_ROOT))

    cmd = ctx.env.PYTHON + [ctx.env.APPENGINE_SDK_DEVAPPSERVER,
            app_root.get_bld().abspath(),
            #app_root.abspath(),
        ]

    #if not ctx.options.port is None:
    #    cmd += ['--port', str(ctx.options.port)]

    proc = Popen(cmd)

    try:
        proc.wait()
    except KeyboardInterrupt:
        Logs.pprint('RED', 'Development Server Interrupted... Shutting Down')
        proc.terminate()


Context.g_module.__dict__['deploy'] = deploy
Context.g_module.__dict__['serve'] = serve

class serve_cls(Build.InstallContext):
    cmd = 'serve'
    fun = 'serve'

class deploy_cls(Build.InstallContext):
    cmd = 'deploy'
    fun = 'deploy'
