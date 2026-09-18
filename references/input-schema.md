# Weekly Input Schema

Use structured input for weekly generation. If the user provides a screenshot, document, chat message, or unstructured text, extract these fields first and show unresolved fields before rendering.

## Minimal Payload

```json
{
  "template_id": "kesun-blue-v1",
  "suite_type": "enterprise_wechat",
  "title": "斩获大湾区百亿工程，科安顺助力广州机场建设",
  "display_time": "09月21日 16:00",
  "cta": "企业微信扫码 观看直播",
  "program": "顺道聊聊",
  "people": [
    {
      "id": "guest",
      "name": "席浩岩",
      "role": "科安顺减隔震事业部业务总监",
      "portrait_path": "inputs/speaker-1.jpg"
    },
    {
      "id": "host",
      "name": "李文秀",
      "role": "主持人",
      "portrait_path": "inputs/speaker-2.jpg"
    }
  ],
  "qr_code_path": "inputs/qr.png"
}
```

## Optional Fields

```json
{
  "subtitle": "可选副标题",
  "title_emphasis": "斩获大湾区百亿工程",
  "portrait_mode": "retouch_source",
  "show_once_waterproof_slogan": false,
  "notes": "用户本次明确提出的特殊要求"
}
```

For suite generation, also normalize:

- `suite_type`: `enterprise_wechat` or `wechat_channels`.
- `title_emphasis`: an exact phrase that the user asked to enlarge or emphasize.
- `portrait_mode`: `use_source`, `retouch_source`, or `generate_professional_portrait`，可设为全局值或写入单个人物对象。
- `show_once_waterproof_slogan`: default `true`; set `false` when the user explicitly says it is not needed.

## Validation

Before rendering:

- Confirm all required manifest slots have matching input values or default values.
- Confirm local asset paths exist and formats are usable.
- Confirm the QR code image is not too small, blurry, cropped, or generated from a model.
- Confirm portrait resolution is sufficient for the target image slot.
- Normalize dates and times into the format required by the template.
- Reject unsupported changes that would alter locked design layers unless the user explicitly asks to edit the template.

## Missing Data Response

If required data is missing, ask for the smallest concrete set of missing fields. Do not invent guest names, dates, QR codes, event links, job titles, platform names, or sponsor information.
