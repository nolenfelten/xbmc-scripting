if __name__ == '__main__':
    import os
    cwd = os.getcwd()
    if cwd[-1] == ';': # XBMC erroneously puts a trailing semicolon on this value
        cwd = cwd[:-1]
    sys.path.insert( 0, os.path.join( cwd, 'resources', 'lib' ) )
    import main