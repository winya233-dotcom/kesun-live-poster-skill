# Special Prompt Intents

Apply these intent rules before composing the poster.

## Generate A Professional Portrait

Trigger when the user says `根据附件图片生成人物形象照`, `基于图片生成职业照`, or equivalent wording.

1. Use the supplied image as the identity reference and generate a high-resolution professional studio portrait before poster composition.
2. Preserve recognizable identity, approximate age, facial structure, skin tone, glasses, and other defining features.
3. Prefer a natural standing or upper-body business pose suitable for poster cropping. Avoid exposing the lower body in the final poster unless the template requires it.
4. Apply professional studio lighting, restrained skin retouching and whitening, natural color correction, and sufficient sharpness. If the source is visibly soft or undersized, enhance resolution before or during portrait generation.
5. Remove the generated background with the approved high-quality cutout route, preferably BiRefNet, then clean hair, shoulders, arms, and underarm gaps before layout.
6. Run the normal MediaPipe and OpenCV placement checks before final composition.

Do not silently generate a new face when the user only asks to use, retouch, or cut out the original portrait.

## Emphasize Part Of The Main Title

Trigger when the user says `主标题中“XXXXX”内容重点展示`, `重点突出主标题“XXXXX”`, or equivalent wording.

1. Extract the exact emphasized phrase and preserve all title wording exactly.
2. Give that phrase the dominant type size or line allocation within the approved title region. Reduce or reflow the remaining title only as needed.
3. Keep the complete title block optically centered, including after rotation or skew. Preserve the approved left-low/right-high tilt, gradient, blue dimensional shadow, glow, and yellow ribbon relationship.
4. Recalculate line spacing after resizing. Lines must read as one compact title group without touching or drifting too far apart.
5. Maintain the title-to-portrait head clearance and all bleed-safe boundaries. If emphasis cannot fit within the approved size range, choose a different line break before shrinking the emphasized phrase.
