# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\check\glcheck.py
import re
GLERR_PATT = re.compile('OpenGL error: (?P<code>0x[0-9]+)')
GLFWERR_PATT = re.compile('GLFWError #(?P<code>[0-9]+) Ha')

def OnGLError(errorInfo='Engine:OpenGL error: 0x0502 (w:56,h:22) in cocos2d\\cocos\\renderer\\CCTexture2D.cpp cocos2d::Texture2DProxy::initWithMipmaps 2751'):
    import statecheck
    mobj = GLERR_PATT.search(errorInfo)
    if mobj:
        code = mobj.group('code')
        statecheck.OnGLErr(code, errorInfo)
        return True
    mobj = GLFWERR_PATT.search(errorInfo)
    if mobj:
        code = mobj.group('code')
        statecheck.OnGLErr(code, errorInfo)
        return True
    if '> != mainctx<' in errorInfo:
        statecheck.OnGLErr('0x0000', errorInfo)
        return True
    return False
