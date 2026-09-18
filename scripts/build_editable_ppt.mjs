import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

function arg(name, fallback = null) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

const requestPath = arg("request");
const layoutPath = arg("layout");
const jobPath = arg("job");
const outputDir = arg("output-dir");
const manifestPath = arg("manifest", path.join(path.dirname(path.dirname(new URL(import.meta.url).pathname)), "assets", "kesun-blue-manifest.json"));
if (!requestPath || !layoutPath || !jobPath || !outputDir) {
  throw new Error("Required: --request --layout --job --output-dir");
}

const runtimeModules = process.env.RUNTIME_NODE_MODULES;
let artifact;
if (runtimeModules) {
  const requireFromRuntime = createRequire(path.join(runtimeModules, "runtime-entry.js"));
  artifact = await import(pathToFileURL(requireFromRuntime.resolve("@oai/artifact-tool")).href);
} else {
  artifact = await import("@oai/artifact-tool");
}
const { Presentation, PresentationFile } = artifact;

const request = JSON.parse(await fs.readFile(requestPath, "utf8"));
const layoutData = JSON.parse(await fs.readFile(layoutPath, "utf8"));
const job = JSON.parse(await fs.readFile(jobPath, "utf8"));
const manifest = JSON.parse(await fs.readFile(manifestPath, "utf8"));
await fs.mkdir(outputDir, { recursive: true });

const FONT_TIME = "Alimama ShuHeiTi";
const FONT_LABEL = "方正兰亭特黑简体";

async function bytes(file) {
  return new Uint8Array(await fs.readFile(file));
}

function addImage(slide, blob, name, position, fit = "contain") {
  return slide.images.add({ blob, contentType: "image/png", alt: name, fit, position });
}

function addText(slide, text, name, position, fontSize, typeface = FONT_LABEL, color = "#FFFFFF") {
  const shape = slide.shapes.add({
    geometry: "textbox", name, position,
    fill: "none", line: { fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface, fontSize, color, alignment: "center", verticalAlignment: "middle",
    autoFit: "shrinkText", wrap: "none", insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return shape;
}

function addVerticalLabel(slide, label, style, scale) {
  const isName = label.kind === "name";
  const fill = isName ? style.name_fill : style.role_fill;
  const fontSize = (isName ? style.name_font_size : style.role_font_size) * scale;
  const shape = slide.shapes.add({
    geometry: "rect",
    name: `可编辑${isName ? "姓名" : "职位"}-${label.person_id}`,
    position: { left: label.left, top: label.top, width: label.width, height: label.height },
    fill,
    line: { fill: "none", width: 0 },
    shadow: `${7 * scale}px ${9 * scale}px ${7 * scale}px #003678/30`,
  });
  shape.text = Array.from(label.text).join("\n");
  shape.text.style = {
    typeface: FONT_LABEL, fontSize, color: style.text_color,
    alignment: "center", verticalAlignment: "middle", autoFit: "shrinkText", wrap: "none",
    insets: { top: 10 * scale, right: 2 * scale, bottom: 10 * scale, left: 2 * scale },
  };
}

function doc(id) {
  return job.documents.find(item => item.id === id);
}

async function makeEditable(templateId, filename) {
  const source = doc(templateId);
  const layout = layoutData.layouts[templateId];
  const spec = manifest.templates[templateId];
  const [width, height] = spec.canvas;
  const deck = Presentation.create({ slideSize: { width, height } });
  const slide = deck.slides.add();
  slide.background.fill = "#089CEB";

  const backplatePath = doc(`${templateId}_ppt_backplate`)?.output;
  const foregroundPath = doc(`${templateId}_ppt_foreground`)?.output;
  if (!backplatePath || !foregroundPath) throw new Error(`Missing PPT assets for ${templateId}`);
  addImage(slide, await bytes(backplatePath), "固定模板背景与主标题", { left: 0, top: 0, width, height }, "cover");

  for (const person of request.people) {
    const placement = layout.people[person.id];
    addImage(slide, await bytes(placement.asset), `可编辑人物-${person.name}`, {
      left: placement.left, top: placement.top, width: placement.width, height: placement.height,
    });
  }
  addImage(slide, await bytes(foregroundPath), "固定前景装饰", { left: 0, top: 0, width, height }, "cover");
  const scale = width / 1080;
  for (const label of layout.labels) addVerticalLabel(slide, label, manifest.label_style, scale);

  if (templateId === "poster") {
    if (request.qr_code_path) {
      const [left, top, qrWidth, qrHeight] = spec.qr_box;
      addImage(slide, await bytes(request.qr_code_path), "可替换二维码", { left, top, width: qrWidth, height: qrHeight }, "cover");
    }
    addText(slide, request.display_time, "可编辑时间", { left: 270, top: 1678, width: 470, height: 72 }, 62, FONT_TIME);
    const enterprise = request.suite_type === "enterprise_wechat";
    addText(slide, enterprise ? "企业微信" : "微信扫码", "可编辑平台文字", { left: 270, top: 1788, width: 175, height: 52 }, 40, FONT_LABEL, "#1565C0");
    addText(slide, request.cta || (enterprise ? "扫码 观看直播" : "开启直播"), "可编辑扫码提示", { left: 445, top: 1788, width: 300, height: 52 }, 40);
  } else if (templateId === "wechat_channels_cover") {
    addText(slide, request.display_time, "可编辑时间", { left: 520, top: 2870, width: 520, height: 110 }, 72, FONT_TIME);
  }
  slide.speakerNotes.textFrame.setText("人物可移动和缩放；姓名、职位、时间与扫码提示可编辑；二维码可替换；其他设计固定。 ");
  const output = path.join(outputDir, filename);
  await (await PresentationFile.exportPptx(deck)).save(output);
  console.log(output);
}

async function makeFixed(templateId, filename) {
  const spec = manifest.templates[templateId];
  const [width, height] = spec.canvas;
  const deck = Presentation.create({ slideSize: { width, height } });
  const slide = deck.slides.add();
  addImage(slide, await bytes(doc(templateId).output), "固定模板画面", { left: 0, top: 0, width, height }, "cover");
  const output = path.join(outputDir, filename);
  await (await PresentationFile.exportPptx(deck)).save(output);
  console.log(output);
}

await makeEditable("poster", "01-常规直播海报-局部可编辑.pptx");
if (request.suite_type === "enterprise_wechat") {
  await makeFixed("enterprise_cover_800", "02-企业微信直播封面-800x640.pptx");
  await makeEditable("enterprise_cover_1080", "03-企业微信直播封面-1080x2160-局部可编辑.pptx");
} else {
  await makeEditable("wechat_channels_cover", "02-微信视频号直播封面-预留出血位-局部可编辑.pptx");
}
