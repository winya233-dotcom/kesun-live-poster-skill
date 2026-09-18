---
name: live-poster-generator
description: Generate Kesun blue-template livestream poster suites for Enterprise WeChat or WeChat Channels, including PSD-faithful PNGs, portrait preprocessing, layout QA, and limited-editable PPTX files. Use when a request mentions 科顺直播海报、企业微信直播套图、微信视频号直播套图、微信扫码开启直播、企业微信扫码开启直播，或要求基于人物图片制作职业照并应用到直播物料。
metadata:
  short-description: Generate Kesun blue livestream asset suites
---

# 科顺直播蓝色海报

使用 Skill 内置的已核准 PSD、字体和品牌素材生成直播套图。不要要求用户重新上传模板，也不要每次重新推断 PSD 图层。

## 执行入口

1. 从用户消息、图片、表格或文档中提取结构化输入，遵循 [references/input-schema.md](references/input-schema.md)。
2. 按 [references/platform-output-rules.md](references/platform-output-rules.md) 判定企业微信或微信视频号套图。
3. 遇到“生成职业形象照”或“重点突出主标题”时，先执行 [references/prompt-intents.md](references/prompt-intents.md)。职业照生成使用可用的图片生成 Skill；没有明确生成指令时只做修图和抠图，不改变身份。
4. 首次运行或环境变化后执行 `python scripts/check_environment.py`。缺少依赖时按 [references/dependencies.md](references/dependencies.md) 处理。
5. 对人物执行 `scripts/remove_background.py` 和 `scripts/analyze_portraits.py`，然后执行 [references/rendering-qa.md](references/rendering-qa.md) 的碰撞与安全区检查。
6. 用 `scripts/build_photoshop_job.py` 生成任务，再通过 `scripts/run_photoshop.ps1` 调用 Photoshop。PSD 图层、字号、光效、渐变、阴影和装饰以模板为准，禁止用生成式图片重绘整张海报。
7. 用 `scripts/build_editable_ppt.mjs` 输出每张非背景物料对应的单页 PPTX。仅人物、姓名/职务、时间/扫码小字和二维码可编辑，其余保持固定。
8. 对所有 PNG 和 PPTX 进行可视化复核，通过后再交付。

完整命令和交付目录见 [references/usage.md](references/usage.md)。

## 固定资产

- `assets/templates/`：已核准的科顺蓝色 PSD 模板，不重新拆解。
- `assets/fonts/`：模板所需字体。运行前如未安装，使用 `scripts/install_fonts.ps1` 安装。
- `assets/brand/`：可选品牌素材。
- `assets/kesun-blue-manifest.json`：唯一有效的模板图层和几何规则。

## 不可破坏的规则

- 主标题使用 Alimama 字体并继承 PSD 原有效果；方向为左低右高，整体居中。
- 人名和职务使用方正兰亭特黑简体，姓名靠近人物，职务位于外侧，色块高度按文字长度计算。
- 双人默认脸部中心距离约为画布宽度的 34%，两侧保留约 60–65 px，人物组整体居中。
- 人像以上半身为主体，头顶与主标题保留安全距离；标签不得进入扩展后的人脸安全区。
- 二维码只能替换为原始图片，不能由图片生成模型重绘。
- “不需要一次防水一次就好”必须关闭右上角口号；未出现该指令时按模板默认显示。
- 直播背景直接修改内置 PSD 并保留透明通道，不重新设计。
- 任何自动检查失败都要修正后重渲染，不能带着碰撞、缺字或错误尺寸交付。

## 发布边界

此 Skill 已自带模板和字体，不要求使用者提供 PSD。Photoshop 是高保真渲染依赖；BiRefNet/rembg、MediaPipe、OpenCV 和 PPT 运行时属于软件依赖，见 [references/dependencies.md](references/dependencies.md)。
