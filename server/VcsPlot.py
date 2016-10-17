
from PlotManager import PlotManager
import json
import vcs
import sys
import gc


class VcsPlot(object):

    def __init__(self, *arg, **kw):
        self._width = kw.get('width', 800)
        self._height = kw.get('height', 600)
        self._canvas = vcs.init()
        self._canvas.geometry(self._width, self._height)
        self._plot = PlotManager(self._canvas)
        self._plot.graphics_method = vcs.getisofill()              # default
        self._plot.template = vcs.elements['template']['default']  # default

    def render(self, opts={}):
        self._width = opts.get('width', self._width)
        self._height = opts.get('height', self._height)

        if not self.getWindow():
            return
        self.getWindow().SetSize(self._width, self._height)
        self._canvas.backend.configureEvent(None, None)
        self._canvas.update()
        return True

    def setGraphicsMethod(self, gm):
        for t in vcs.elements:
            if len(vcs.elements[t]):
                o = vcs.elements[t].values()[0]
                if hasattr(o, "g_name"):
                    if o.g_name == gm["g_name"]:
                        break
        else:
            return False
        my_gm = vcs.creategraphicsmethod(t)
        for k in gm:
            if k == "name":
                continue
            if gm[k] == 100000000000000000000L:
                gm[k] = 1e20
            if isinstance(gm[k], list):
                conv = []
                for v in gm[k]:
                    if v == 100000000000000000000L:
                        conv.append(1e20)
                    else:
                        conv.append(v)
                gm[k] = conv
            if hasattr(my_gm, k):
                try:
                    setattr(my_gm, k, gm[k])
                except:
                    print "Could not set attribute %s on graphics method of type %s" % (k, t)
        self._plot.graphics_method = my_gm

    def setTemplate(self, template):
        if template in vcs.elements['template']:
            self._plot.template = vcs.elements['template'][template]
            return True
        else:
            return False

    def loadVariable(self, var, opts={}):
        """Load a variable into the visualization.

        Returns success or failure.
        """
        self._plot.variables = var
        return True

    def getWindow(self):
        return self._canvas.backend.renWin

    def close(self):
        print 'VcsPlot.close(): %s'%self._canvas
        print 'refcount: %s'%str(sys.getrefcount(self.getWindow()))
        self._canvas.close()