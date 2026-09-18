# Rendering And QA

Use this before delivering the final poster.

## Rendering Rules

- Render text with the approved font, color, tracking, line height, alignment, and bounding box from the manifest.
- Fit long text by applying manifest rules in order: preferred line breaks, smaller font size within range, alternate compact slot, then stop for user approval.
- Place portraits inside the approved image slot and mask. Do not cover important text or brand elements.
- Keep QR codes as original raster/vector assets. Resize with high-quality deterministic scaling and preserve quiet zones.
- Export to the requested size and color profile.

## Portrait Preprocessing

AI portrait work is allowed only before final composition and only for the portrait slot.

Acceptable operations:

- Background removal.
- Subtle professional retouching.
- Lighting and color correction to match the template.
- Edge cleanup around hair and shoulders.
- Background extension when the slot needs more safe area.

Avoid:

- Changing identity, age, body shape, skin tone, clothing style, or expression unless requested.
- Generating text, QR codes, logos, or title areas.
- Replacing the template's visual language with a new style.

## Portrait Geometry And Collision Rules

- Trim transparent margins with OpenCV before measuring or placing a portrait.
- Use MediaPipe Face Detector and Pose Landmarker for face bounds, eye line, shoulders, elbows, and hips.
- Never normalize people by source image or PNG canvas height. Normalize two-person layouts by detected face height.
- Keep two detected face heights within 5 percent and eye-line positions within 2 percent of canvas height unless the approved reference intentionally uses depth hierarchy.
- For a 1080-pixel two-person poster, target about 60 to 65 pixels of visible breathing room at both outer edges. Scale this margin proportionally for other canvas widths.
- Keep the combined visible portrait span at or below 89 percent of canvas width. Do not let shoulders, arms, or clothing touch both canvas edges at the same time.
- For a balanced two-person composition, target a face-center gap of 32 to 36 percent of canvas width; use about 34 percent by default. This should create a natural shoulder overlap without making the faces feel crowded.
- Keep left and right portrait groups visually centered as one unit after tightening the gap. Do not tighten by moving only one person.
- Apply the outer-edge rule to the OpenCV alpha mask, not the rectangular image frame.
- Prefer an upper-body crop. Let the fixed foreground hide the lower body instead of showing legs by default.
- Expand each detected face box by 14 percent to form a text exclusion zone.
- Put the name closest to its person and the role farther toward the outer canvas edge.
- Apply the same outer safe margin to name and role blocks as to portraits. On a 1080-pixel canvas, keep label blocks about 60 to 65 pixels from the left or right edge unless the approved PSD uses a stricter inset.
- Size each vertical label block from character count, font size, tracking, and top/bottom padding. Do not reuse a fixed height for short and long names or roles.
- Run OpenCV rectangle or mask intersection checks before export. A name, role, title, QR, or bleed-unsafe region must not intersect the expanded face exclusion zone.
- For multi-person layouts, reject the candidate when face-size balance, eye-line balance, or collision checks fail, then recompute positions before rendering.

## QA Checklist

Before final delivery, verify:

- Canvas size matches the manifest or requested export size.
- All required text fields are present and exactly match the input.
- No text overflows, overlaps, or becomes unreadably small.
- QR code is present, unredrawn, uncropped, and has a quiet zone.
- Portrait subject is not distorted and edges look clean.
- Multi-person face heights and eye lines are visually balanced.
- Person labels do not intersect face, hair, or neck exclusion zones.
- Locked brand elements remain unchanged.
- Output filename includes template id and date or another traceable run id.

If any check fails, fix and rerender. If the failure cannot be fixed without changing the template or losing accuracy, report the blocker clearly.
