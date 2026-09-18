from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = SKILL_DIR / "assets" / "kesun-blue-manifest.json"


def resolve_asset(relative: str) -> str:
    return str((SKILL_DIR / "assets" / relative).resolve()).replace("\\", "/")


def split_title(title: str, emphasis: str | None, supplied: list[str] | None) -> list[str]:
    if supplied:
        return [str(item) for item in supplied[:2]]
    title = title.strip()
    if emphasis and emphasis in title:
        remainder = title.replace(emphasis, "", 1).strip(" ，,。；;：:")
        return [emphasis, remainder] if remainder else [emphasis, ""]
    parts = [part.strip() for part in re.split(r"[，,；;。]", title) if part.strip()]
    if len(parts) >= 2:
        return [parts[0], "，".join(parts[1:])]
    midpoint = max(1, len(title) // 2)
    return [title[:midpoint], title[midpoint:]]


def visible(path: list[str], value: bool, optional: bool = True) -> dict[str, object]:
    return {"type": "visible", "path": path, "value": value, "optional": optional}


def text_op(path: list[str], value: str, geometry: dict[str, object], font: str, optional: bool = False) -> dict[str, object]:
    return {
        "type": "text", "path": path, "value": value, "font": font,
        "center": geometry.get("center"), "min_width": geometry.get("min_width", 0),
        "max_width": geometry.get("max_width", 0), "optional": optional,
    }


def place_op(asset: str, placement: dict[str, object], parent: list[str] | None, name: str, optional: bool = False) -> dict[str, object]:
    return {
        "type": "place", "file": asset.replace("\\", "/"), "name": name,
        "center": [placement["center_x"], placement["center_y"]],
        "height": placement["height"], "parent": parent, "optional": optional,
    }


def common_program_ops(manifest: dict[str, object], program: str) -> list[dict[str, object]]:
    return [visible([layer], label == program) for label, layer in manifest["program_layers"].items()]


def document_job(
    template_id: str,
    spec: dict[str, object],
    output_path: Path,
    lines: list[str],
    request: dict[str, object],
    layout: dict[str, object] | None,
    label_path: Path | None,
    manifest: dict[str, object],
) -> dict[str, object]:
    title_font = manifest["fonts"]["title"]["postscript_name"]
    label_font = manifest["fonts"]["label_bold"]["postscript_name"]
    operations: list[dict[str, object]] = []

    if template_id in {"poster", "enterprise_cover_1080", "wechat_channels_cover"}:
        operations += common_program_ops(manifest, request["program"])
    if spec.get("slogan_layer"):
        operations.append(visible(spec["slogan_layer"], bool(request.get("show_once_waterproof_slogan", True))))

    for path in spec.get("template_portraits", []):
        operations.append(visible(path, False))
    for path in spec.get("template_labels", []):
        operations.append(visible(path, False))
    operations.append(visible(["主题", "标题", "组 2"], False))
    operations.append(visible(["主题", "标题", "防水老兵解析未来10年的市场机遇"], False))
    operations.append(visible(["主题", "标题", "圆角矩形 1"], False))

    for index, path in enumerate(spec.get("title_layers", [])):
        value = lines[index] if index < len(lines) else ""
        operations.append(text_op(path, value, spec["title_geometry"][index], title_font))

    if spec.get("time_layer") and request.get("display_time"):
        operations.append(text_op(spec["time_layer"], request["display_time"], {"center": spec.get("time_center"), "min_width": 0, "max_width": 0}, title_font))

    if template_id == "poster":
        if request["suite_type"] == "enterprise_wechat":
            platform_text, cta_text = "企业微信", request.get("cta", "扫码 观看直播")
        else:
            platform_text, cta_text = "微信扫码", request.get("cta", "开启直播")
        operations.append(text_op(spec["platform_layer"], platform_text, {"center": spec["platform_center"], "min_width": 0, "max_width": 190}, label_font))
        operations.append(text_op(spec["cta_layer"], cta_text, {"center": spec["cta_center"], "min_width": 0, "max_width": 300}, label_font))
        if request.get("qr_code_path"):
            operations.append(visible(spec["qr_layer"], False))
            x, y, width, height = spec["qr_box"]
            operations.append({
                "type": "place_box", "file": str(Path(request["qr_code_path"]).resolve()).replace("\\", "/"),
                "name": "可替换二维码", "box": [x, y, width, height], "optional": False,
            })

    if layout:
        people_by_id = {item["id"]: item for item in request["people"]}
        for person_id, placement in layout["people"].items():
            operations.append(place_op(placement["asset"], placement, spec.get("portrait_parent"), f"人物-{people_by_id[person_id]['name']}"))
        if label_path:
            operations.append({
                "type": "place_canvas", "file": str(label_path.resolve()).replace("\\", "/"),
                "name": "人物姓名职位标签", "optional": False,
            })

    return {
        "id": template_id,
        "psd": resolve_asset(spec["file"]),
        "output": str(output_path.resolve()).replace("\\", "/"),
        "transparent": bool(spec.get("transparent", False)),
        "operations": operations,
    }


def ppt_variants(documents: list[dict[str, object]], request: dict[str, object], work_dir: Path) -> list[dict[str, object]]:
    variants: list[dict[str, object]] = []
    for document in documents:
        if document["id"] not in {"poster", "enterprise_cover_1080", "wechat_channels_cover"}:
            continue
        backplate = deepcopy(document)
        backplate["id"] += "_ppt_backplate"
        backplate["output"] = str((work_dir / "ppt-assets" / f"{document['id']}-backplate.png").resolve()).replace("\\", "/")
        backplate["operations"] = [op for op in backplate["operations"] if op["type"] not in {"place", "place_canvas", "place_box"}]
        backplate["operations"] += [
            visible(["相框主体"], False),
            visible(["底部背景", "09月14日 20:00"], False),
            visible(["底部背景", "08月27日 20:00"], False),
            visible(["底部背景", "LIVE BROADCAST TIME"], False),
            visible(["底部背景", "企业微信"], False),
            visible(["底部背景", "扫码 开启直播"], False),
            visible(["底部背景", "企业微信截图_17833324779516"], False),
        ]
        variants.append(backplate)

        foreground = {
            "id": document["id"] + "_ppt_foreground",
            "psd": document["psd"],
            "output": str((work_dir / "ppt-assets" / f"{document['id']}-foreground.png").resolve()).replace("\\", "/"),
            "transparent": True,
            "operations": [
                {"type": "hide_all_top_level"},
                visible(["底部背景"], True),
                visible(["底部"], True),
                visible(["顺道聊聊-蓝"], request["program"] == "顺道聊聊"),
                visible(["玩转产品"], request["program"] == "玩转产品"),
                visible(["AI工作坊"], request["program"] == "AI工作坊"),
                visible(["底部背景", "09月14日 20:00"], False),
                visible(["底部背景", "08月27日 20:00"], False),
                visible(["底部背景", "LIVE BROADCAST TIME"], False),
                visible(["底部背景", "企业微信"], False),
                visible(["底部背景", "扫码 开启直播"], False),
                visible(["底部背景", "企业微信截图_17833324779516"], False),
            ],
        }
        variants.append(foreground)
    return variants


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Photoshop execution job from a livestream request")
    parser.add_argument("request", type=Path)
    parser.add_argument("layout", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--include-ppt-assets", action="store_true")
    args = parser.parse_args()

    request = json.loads(args.request.read_text(encoding="utf-8"))
    layout_data = json.loads(args.layout.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    lines = split_title(request["title"], request.get("title_emphasis"), request.get("title_lines"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    work_dir = args.output_dir / ".work"
    work_dir.mkdir(parents=True, exist_ok=True)

    if request["suite_type"] == "enterprise_wechat":
        template_ids = ["poster", "enterprise_cover_800", "enterprise_cover_1080", "live_background"]
        background_name = "04-直播背景-透明底.png"
    else:
        template_ids = ["poster", "wechat_channels_cover", "live_background"]
        background_name = "03-直播背景-透明底.png"

    documents = []
    for template_id in template_ids:
        spec = manifest["templates"][template_id]
        output_name = background_name if template_id == "live_background" else spec["export"]
        layout = layout_data["layouts"].get(template_id)
        label_path = work_dir / "labels" / f"labels-{template_id}.png"
        documents.append(document_job(template_id, spec, args.output_dir / "png" / output_name, lines, request, layout, label_path if layout else None, manifest))

    if args.include_ppt_assets:
        documents += ppt_variants(documents, request, work_dir)

    job = {
        "version": 1,
        "output_dir": str(args.output_dir.resolve()).replace("\\", "/"),
        "log": str((work_dir / "photoshop-render.log").resolve()).replace("\\", "/"),
        "request": request,
        "documents": documents,
    }
    output = work_dir / "photoshop-job.json"
    output.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output.resolve())


if __name__ == "__main__":
    main()
