# Platform Output Rules

Use these rules when the user requests a complete livestream asset suite or when the supplied brief contains platform-specific scan-to-watch wording.

## Platform Detection

Select `enterprise_wechat` when either condition is true:

- The user says `输出企业微信直播套图` or equivalent wording.
- The supplied material contains `企业微信扫码开启直播`, `企业微信扫码观看直播`, or an unambiguous equivalent.

Select `wechat_channels` when either condition is true:

- The user says `输出微信视频号直播套图` or equivalent wording.
- The supplied material contains `微信扫码开启直播`, `微信扫码观看直播`, or an unambiguous equivalent without the enterprise-WeChat qualifier.

Use longest, most specific matching: `企业微信` takes precedence over the generic substring `微信`. An explicit suite request takes precedence over wording inferred from attachments. If both platforms are explicitly requested, generate both suites. If they conflict without a clear explicit request, ask which platform should control the output.

## Enterprise WeChat Suite

Generate four PNG assets:

1. Standard livestream poster at the approved poster template size, normally 1080 x 1920.
2. Enterprise WeChat landscape cover at 800 x 640.
3. Enterprise WeChat vertical cover at 1080 x 2160.
4. Livestream background from its approved PSD, preserving transparency where the template requires a transparent background.

Also generate three separate one-page PPTX files, one for each non-background asset. Each PPT page must match its PNG's aspect ratio and intended output dimensions. Do not combine the three assets into one deck.

## WeChat Channels Suite

Generate three PNG assets:

1. Standard livestream poster at the approved poster template size.
2. WeChat Channels livestream cover using the approved `预留出血位版本` PSD and its native canvas size. Preserve the bleed-safe composition.
3. Livestream background from its approved PSD, preserving transparency where required.

Also generate two separate one-page PPTX files, one for the poster and one for the bleed-reserved cover. Do not create a PPTX for the livestream background.

## Editable PPT Contract

Keep the approved design, main title treatment, program badge, brand art, decorative effects, and fixed frame flattened or locked. Only expose fields that exist on that output:

- Portraits are separate transparent image objects and can be moved or resized.
- Person names, roles, date/time, and scan-to-watch wording remain editable text.
- The QR code remains a replaceable image object.
- Keep text-box fills and other required label backgrounds; editing the text must not remove the color block.
- Preserve the exact visual placement from the approved PNG at the time of export.

Deliver the PNG files and the separate PPTX files in clearly named folders, plus the layout QA report when portrait detection was used.
