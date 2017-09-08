from PlotManager import PlotManager
import json
import vcs
import sys
import gc


class VcsPlot(object):

    def __init__(self, canvas, *arg, **kw):
        self._width = kw.get('width', 800)
        self._height = kw.get('height', 600)
        if (canvas != None):
            self._canvas = canvas
        else:
            self._canvas = vcs.init(
                geometry={'width': self._width, 'height':self._height}, bg=1)
            self._canvas.open()
            self._canvas.backend.renWin.AddObserver("ModifiedEvent", self.modifiedEvent)
        self._plot = PlotManager(self._canvas)
        self._plot.graphics_method = vcs.getisofill()              # default
        self._plot.template = vcs.elements['template']['default']  # default
        self._insideModifiedEvent = False

    def render(self, opts={}):
        self._width = opts.get('width', self._width)
        self._height = opts.get('height', self._height)

        if not self.getWindow():
            return
        self.getWindow().SetSize(self._width, self._height)
        self._canvas.backend.configureEvent(None, None)
        self._canvas.update()
        return True

    def modifiedEvent(self, obj, ev):
        if (not self._insideModifiedEvent):
            # seems that SetSize (800, 600)
            # sets the size to (814, 606) before settling on (800, 600)
            # this happens with OpenGL1. Probably should be fixed in VTK
            # if it happens with OpenGL2
            self._insideModifiedEvent = True
            newSize = self.getWindow().GetSize()
            if (newSize != (self._width, self._height)):
                self._canvas.backend.bgX = newSize[0]
                self._canvas.backend.bgY = newSize[1]
                self.render({'width': newSize[0], 'height': newSize[1]})
            self._insideModifiedEvent = False

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
            if gm[k] == 100000000000000000000:
                gm[k] = 1e20
            if gm[k] == -100000000000000000000:
                gm[k] = -1e20
            if isinstance(gm[k], list):
                conv = []
                for v in gm[k]:
                    if v == 100000000000000000000:
                        conv.append(1e20)
                    elif v == -100000000000000000000:
                        conv.append(-1e20)
                    else:
                        conv.append(v)
                gm[k] = conv
            if hasattr(my_gm, k):
                try:
                    setattr(my_gm, k, gm[k])
                except:
                    print "Could not set attribute %s on graphics method of type %s" % (k, t)
        if "ext_1" in gm:
            my_gm.ext_1 = gm["ext_1"]
        if "ext_2" in gm:
            my_gm.ext_2 = gm["ext_2"]
        self._plot.graphics_method = my_gm

    def setTemplate(self, template):
        if isinstance(template, dict):
            my_tmpl = vcs.createtemplate()
            for attr in template:
                if attr == "name":
                    continue
                if attr == "p_name":
                    continue
                for key in template[attr]:
                    if key == "member":
                        continue
                    tmpl_attr = getattr(my_tmpl, attr)
                    new_val = template[attr][key]
                    setattr(tmpl_attr, key, new_val)
        else:
            my_tmpl = vcs.gettemplate(str(template))
        self._plot.template = my_tmpl

    def loadVariable(self, var, opts={}):
        """Load a variable into the visualization.

        Returns success or failure.
        """
        self._plot.variables = var
        return True

    def getWindow(self):
        return self._canvas.backend.renWin

    def getCanvas(self):
        return self._canvas
