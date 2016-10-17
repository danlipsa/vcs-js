import RemoteRenderer from 'ParaViewWeb/NativeUI/Canvas/RemoteRenderer';
import { onSizeChange, startListening } from 'ParaViewWeb/Common/Misc/SizeHelper';
import SmartConnect from 'ParaViewWeb/IO/WebSocket/SmartConnect';
import { createClient } from 'ParaViewWeb/IO/WebSocket/ParaViewWebClient';


const backend = {
  connect: (url) => {
    const smartConnect = new SmartConnect({
      sessionURL: url,
    });

    const connectionPromise = new Promise((resolve, reject) => {
      smartConnect.onConnectionReady(resolve);
      smartConnect.onConnectionError(reject);
      smartConnect.onConnectionClose(reject);
    });

    // create a pvw client object after the session is ready
    const pvw = connectionPromise.then((connection) => {
      const handlers = ['MouseHandler', 'ViewPort', 'ViewPortImageDelivery', 'FileListing'];
      return {
        pvw: createClient(connection, handlers),
        close: (canvas) => {
          if (canvas.windowId !== undefined) {
            this.pvw.session.call('cdat.view.close', [canvas.windowId]);
          }
        },
      };
    });
    smartConnect.connect();
    return pvw;
  },
  plot: (canvas, dataSpec, template, method) => {
    return canvas.clients.vtkweb.then((client) => {
      // dataSpec is either one or more variable objects (if more, they're in an array)
      let spec = [];

      if (!Array.isArray(dataSpec)) {
        spec.push(dataSpec);
      } else {
        spec = dataSpec;
      }
      client.pvw.session.call(
        'cdat.view.create',
        [spec, template, method]).then((windowId) => {
          canvas.windowId = windowId;
          const renderer = new RemoteRenderer(client.pvw, canvas.el, windowId);
          onSizeChange(() => {
            renderer.resize();
          });
          startListening();
        });
    });
  },
};

export { backend as default };