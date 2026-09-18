# 运行依赖

## 必需环境

- Windows 10/11。
- Adobe Photoshop，支持 ExtendScript 和 COM 自动化。
- Python 3.10 或 3.11。
- Python 包：`Pillow`、`numpy`、`opencv-python`、`mediapipe`、`rembg`、`onnxruntime`。
- Codex 桌面版内置演示文稿运行时，或能提供 `@oai/artifact-tool` 的 Node.js 环境，用于局部可编辑 PPTX。

安装 Python 依赖：

```powershell
python -m pip install -r scripts/requirements.txt
```

首次使用 rembg 的 BiRefNet 模型时可能需要联网下载模型。模型缓存不放入发布包。

## 字体

字体文件已放在 `assets/fonts/`。在 Windows 上执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_fonts.ps1
```

Photoshop 中应能解析以下字体名：

- `AlimamaShuHeiTi-Bold`
- `FZLTTHJW--GB1-0`
- `FZLTHJW--GB1-0`

## 环境检查

```powershell
python scripts/check_environment.py
```

检查结果会区分错误与警告。缺少 Photoshop、模板、关键字体或 Python 包时，不要继续正式渲染。

## 外部能力

当用户明确要求根据附件生成职业形象照时，调用当前环境可用的图片生成 Skill。生成完成后再进入本 Skill 的抠图、排版和 Photoshop 渲染流程。图片生成服务本身不随此目录分发。
