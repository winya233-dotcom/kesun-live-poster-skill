# 科顺直播蓝色海报 Skill

一个面向 Codex 的科顺直播视觉物料生成 Skill。它内置已核准的蓝色系列 PSD、字体、品牌素材和排版规则，可根据每期直播信息自动生成 PNG 套图及局部可编辑 PPTX。

## 输出类型

### 企业微信直播套图

- 常规直播海报：1080×1920
- 企业微信直播封面：800×640
- 企业微信竖版封面：1080×2160
- 透明直播背景：1080×1920
- 除直播背景外，每项提供一份单页局部可编辑 PPTX

### 微信视频号直播套图

- 常规直播海报：1080×1920
- 预留出血位直播封面：1920×3415
- 透明直播背景：1080×1920
- 除直播背景外，每项提供一份单页局部可编辑 PPTX

## 主要能力

- Photoshop PSD 高保真自动化渲染
- BiRefNet/rembg 人像抠图
- MediaPipe + OpenCV 人脸、姿态和安全区分析
- 单人、双人、三人人像自动排版
- 姓名与职务标签动态尺寸和碰撞检测
- 主标题重点词放大、居中和模板效果继承
- 可选职业形象照生成工作流
- 人物、姓名/职务、时间、扫码文案和二维码局部可编辑 PPTX

## 环境要求

- Windows 10/11
- Adobe Photoshop
- Python 3.10 或 3.11
- Node.js 与 `@oai/artifact-tool`（生成 PPTX 时需要）

## 安装到 Codex

PSD、字体和模型已压缩为普通 Git 资产包，不依赖 Git LFS。将仓库直接克隆到 Codex Skills 目录：

```powershell
git clone https://github.com/winya233-dotcom/kesun-live-poster-skill.git "$env:USERPROFILE\.codex\skills\live-poster-generator"
```

最终目录应为：

```text
%USERPROFILE%\.codex\skills\live-poster-generator
```

重新打开 Codex 任务后，可显式输入：

```text
$live-poster-generator 输出企业微信直播套图……
```

也可以使用“输出企业微信直播套图”“输出微信视频号直播套图”等自然语言触发。

## 首次配置

```powershell
python scripts/install_bundled_assets.py
python -m pip install -r scripts/requirements.txt
powershell -ExecutionPolicy Bypass -File scripts/install_fonts.ps1
python scripts/check_environment.py
```

`check_environment.py` 和 `run_pipeline.py` 也会在发现素材未解包时自动执行恢复，因此通常无需手动运行第一条命令。

## 命令行执行

复制并填写 `assets/request.example.json`，然后执行：

```powershell
python scripts/run_pipeline.py path\to\request.json path\to\output
```

详细规则见 [SKILL.md](SKILL.md) 和 [references/usage.md](references/usage.md)。

## 重要说明

- 不需要使用者重新提供或拆解 PSD。
- Photoshop 是最终视觉效果的渲染权威。
- 二维码必须使用真实输入图片，禁止生成式重绘。
- 职业形象照生成依赖运行环境可用的图片生成能力，不随仓库分发。
- 模板、品牌素材和字体的授权范围见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 许可证

自动化代码和文档采用 [MIT License](LICENSE)。PSD、品牌素材、字体及其他第三方文件不自动包含在 MIT 授权范围内。
