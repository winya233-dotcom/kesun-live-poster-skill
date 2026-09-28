# 使用与交付

## 1. 准备环境

```powershell
python scripts/install_bundled_assets.py
python -m pip install -r scripts/requirements.txt
powershell -ExecutionPolicy Bypass -File scripts/install_fonts.ps1
python scripts/check_environment.py
```

也可以在 Skill 根目录运行 `powershell -ExecutionPolicy Bypass -File .\setup.ps1` 一次完成。安装后看不到 PSD 时，先执行资源恢复命令；不要把尚未解压误判为仓库缺文件。

高保真 PNG 需要 Windows 版 Adobe Photoshop。PPT 输出需要 Node.js 和 `@oai/artifact-tool`；在 Codex 桌面版中优先使用工作区自带运行时。

## 2. 准备请求

复制 `assets/request.example.json` 到 Skill 目录外，填写人物与二维码路径。不要修改内置 PSD。

`suite_type` 可选：

- `enterprise_wechat`：海报、800×640 封面、1080×2160 封面、透明直播背景、三份单页可编辑 PPTX。
- `wechat_channels`：海报、1920×3415 预留出血位封面、透明直播背景、两份单页可编辑 PPTX。

## 3. 执行

```powershell
python scripts/run_pipeline.py path\to\request.json path\to\output
```

默认执行抠图、人物分析、碰撞检查、Photoshop 渲染和 PPT 生成。调试规则时可加 `--dry-run`，只生成中间任务和布局报告。

## 4. 交付结构

```text
output/
  png/
  pptx/
  .work/
```

只交付 `png/` 和 `pptx/`。`.work/` 是可删除的中间文件。

## 5. 验收

- PNG 尺寸与平台模板一致。
- 直播背景为 RGBA 真透明，Alpha 同时包含 0 和 255。
- 人物头顶、画布边缘、主标题和人物标签之间保留安全距离。
- 姓名靠近人物，职务位于外侧，色块长度随文字变化。
- PPT 页面比例与对应 PNG 一致；人物可移动和缩放，姓名/职务、时间、扫码文案可编辑，二维码可替换。
- 二维码必须来自输入文件，不允许生成式重绘。
