import os, sys, unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
log = open("/tmp/reflog.txt", "w", buffering=1)
_orig = unittest.TestCase.run
def run(self, result=None):
    rc0 = sys.getrefcount(None)
    r = _orig(self, result)
    rc1 = sys.getrefcount(None)
    log.write("%s\t%d\t%d\n" % (self.id(), rc0, rc1))
    return r
unittest.TestCase.run = run
suite = unittest.TestLoader().discover("tests")
res = unittest.TextTestRunner(verbosity=0, stream=open("/tmp/refrun.log", "w")).run(suite)
print("done", res.testsRun, "failures", len(res.failures), "errors", len(res.errors))
