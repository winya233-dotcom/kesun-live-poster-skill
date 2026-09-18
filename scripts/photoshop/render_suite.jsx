#target photoshop

(function () {
  app.displayDialogs = DialogModes.NO;
  app.preferences.rulerUnits = Units.PIXELS;

  if (typeof LIVE_POSTER_JOB_PATH === "undefined") throw new Error("LIVE_POSTER_JOB_PATH is not defined");

  function readJson(path) {
    var file = new File(path);
    file.encoding = "UTF8";
    if (!file.open("r")) throw new Error("Cannot open job: " + path);
    var content = file.read();
    file.close();
    // Older ExtendScript builds do not expose JSON.parse. The job is generated
    // locally by this skill, so evaluating the JSON object literal is safe here.
    return eval("(" + content + ")");
  }

  var job = readJson(LIVE_POSTER_JOB_PATH);

  function ensureParent(path) {
    var file = new File(path);
    if (!file.parent.exists) file.parent.create();
  }

  function log(message) {
    ensureParent(job.log);
    var file = new File(job.log);
    file.encoding = "UTF8";
    file.open("a");
    file.writeln(new Date().toString() + " " + message);
    file.close();
  }

  function getLayer(container, names) {
    var node = container;
    for (var i = 0; i < names.length; i++) node = node.layers.getByName(names[i]);
    return node;
  }

  function px(value) { return value.as("px"); }
  function bounds(layer) {
    var value = layer.bounds;
    return [px(value[0]), px(value[1]), px(value[2]), px(value[3])];
  }
  function width(layer) { var value = bounds(layer); return value[2] - value[0]; }
  function height(layer) { var value = bounds(layer); return value[3] - value[1]; }
  function moveCenter(layer, x, y) {
    var value = bounds(layer);
    layer.translate(x - (value[0] + value[2]) / 2, y - (value[1] + value[3]) / 2);
  }
  function fitWidthRange(layer, minWidth, maxWidth) {
    var current = width(layer);
    if (current <= 0) return;
    var target = current;
    if (minWidth > 0 && current < minWidth) target = minWidth;
    if (maxWidth > 0 && current > maxWidth) target = maxWidth;
    if (Math.abs(target - current) > 1) layer.resize(target / current * 100, target / current * 100, AnchorPosition.MIDDLECENTER);
  }
  function resizeToHeight(layer, targetHeight) {
    var current = height(layer);
    if (current > 0) layer.resize(targetHeight / current * 100, targetHeight / current * 100, AnchorPosition.MIDDLECENTER);
  }
  function placeFile(path) {
    var descriptor = new ActionDescriptor();
    descriptor.putPath(charIDToTypeID("null"), new File(path));
    descriptor.putEnumerated(charIDToTypeID("FTcs"), charIDToTypeID("QCSt"), charIDToTypeID("Qcsa"));
    executeAction(charIDToTypeID("Plc "), descriptor, DialogModes.NO);
    return app.activeDocument.activeLayer;
  }
  function fitInBox(layer, box) {
    var scale = Math.min(box[2] / width(layer), box[3] / height(layer));
    layer.resize(scale * 100, scale * 100, AnchorPosition.MIDDLECENTER);
    moveCenter(layer, box[0] + box[2] / 2, box[1] + box[3] / 2);
  }
  function exportPng(doc, path, transparency) {
    ensureParent(path);
    var options = new ExportOptionsSaveForWeb();
    options.format = SaveDocumentType.PNG;
    options.PNG8 = false;
    options.transparency = !!transparency;
    options.interlaced = false;
    options.quality = 100;
    doc.exportDocument(new File(path), ExportType.SAVEFORWEB, options);
  }

  function perform(doc, operation) {
    try {
      if (operation.type === "visible") {
        getLayer(doc, operation.path).visible = operation.value;
      } else if (operation.type === "hide_all_top_level") {
        for (var i = 0; i < doc.layers.length; i++) doc.layers[i].visible = false;
      } else if (operation.type === "text") {
        var textLayer = getLayer(doc, operation.path);
        textLayer.textItem.contents = operation.value;
        if (operation.font) textLayer.textItem.font = operation.font;
        fitWidthRange(textLayer, operation.min_width || 0, operation.max_width || 0);
        if (operation.center) moveCenter(textLayer, operation.center[0], operation.center[1]);
      } else if (operation.type === "place") {
        var placed = placeFile(operation.file);
        placed.name = operation.name || "placed-image";
        resizeToHeight(placed, operation.height);
        moveCenter(placed, operation.center[0], operation.center[1]);
        if (operation.parent) placed.move(getLayer(doc, operation.parent), ElementPlacement.INSIDE);
      } else if (operation.type === "place_box") {
        var boxLayer = placeFile(operation.file);
        boxLayer.name = operation.name || "placed-box-image";
        fitInBox(boxLayer, operation.box);
      } else if (operation.type === "place_canvas") {
        var canvasLayer = placeFile(operation.file);
        canvasLayer.name = operation.name || "placed-canvas-image";
        // The overlay PNG already matches the PSD canvas. Photoshop reports
        // only the non-transparent layer bounds, so resizing from layer bounds
        // would magnify labels and destroy their absolute coordinates.
      } else {
        throw new Error("Unknown operation: " + operation.type);
      }
    } catch (error) {
      if (operation.optional) {
        log("optional operation skipped: " + operation.type + " " + error);
      } else {
        throw error;
      }
    }
  }

  for (var d = 0; d < job.documents.length; d++) {
    var item = job.documents[d];
    log("start " + item.id);
    var doc = app.open(new File(item.psd));
    try {
      for (var o = 0; o < item.operations.length; o++) perform(doc, item.operations[o]);
      exportPng(doc, item.output, item.transparent);
      log("exported " + item.output);
    } finally {
      doc.close(SaveOptions.DONOTSAVECHANGES);
    }
  }
  log("all documents complete");
})();
