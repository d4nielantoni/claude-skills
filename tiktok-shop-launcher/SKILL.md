---
name: tiktok-shop-launcher
description: "Turns 3D-model links (MakerWorld or Printables) for products the user prints and sells into finished TikTok Shop launches: measures the real size from the model file, generates 7 ad photos and a showcase video per product in Google Flow (one isolated Flow project per product), builds 1080x1920 posting videos with captions, writes titles, descriptions, captions and hashtags, and submits each product through TikTok Seller Center's single-product form. Use when the user sends model links and asks to create ads, photos or videos, 'subir no TikTok Shop', 'cadastrar os produtos', 'gerar anúncios', or to run the full product-launch flow for their 3D-print shop."
---

# TikTok Shop launcher (MakerWorld → Flow → TikTok Shop)

Built from a real session for the user's shop **Be Nice** (TikTok Shop Brasil). Everything the buyer sees is in Brazilian Portuguese; this file is in English.

The user wants this to run **end to end without pausing for questions**. Decide, act, and list your decisions in the final report. Stop only for things that truly need the user: a login, a payment, or a content-policy refusal you must not work around.

**Sale license is implied.** If the user sends a model link, they already hold the license to sell prints of it. They don't need to say so in the message. Never ask about it, never make it a condition to proceed, and don't add license warnings to the report.

## Non-negotiable rules

1. **Isolation in Google Flow.** One **new Flow project per product**, and a **new chat session for every request** (the 7 photos, each redo, each video). Never generate two products, or photos and a video, in the same session. This stops one product's look from leaking into another and makes downloads unambiguous.
2. **Prompts:** use the user's templates in [references/prompts.md](references/prompts.md). **Never write "impresso em 3D", "impressão 3D", "impressora 3D" or "PLA" in an image or video prompt**, and always include the anti-defect line ("…sem rebarbas, sem fiapos, sem linhas de camada aparentes…").
3. **No franchise names** (Harry Potter, Hogwarts, Pokémon, Disney…) in prompts, titles, descriptions or hashtags. Describe what the object looks like.
4. **Content-policy refusals are final.** If Flow/Veo refuses ("políticas de fornecedores de conteúdo terceirizados"), do not rephrase to get around it: make a photo-only video and tell the user.
5. **Publishing:** "Enviar para análise" publishes to buyers once approved. The user's request to run this skill on a batch is the go-ahead for that batch only. Never edit, delete or re-price existing products unless asked.
6. **Verify before claiming.** Look at every photo (contact sheet) and at video frames before using them; read the Seller Center list before saying a product is live.
7. Don't commit, push, or change settings/config files outside the shop folders.

## Tools and folders

- Chrome: `mcp__claude-in-chrome__*` (load the core set + `javascript_tool`, `find`, `file_upload`, `get_page_text`, `browser_batch` in one ToolSearch). The user is logged in to MakerWorld, Google Flow and TikTok Seller Center in Chrome. Work in your own tab group and close your tabs at the end.
- Shell: `python3` with Pillow + numpy, `ffmpeg`/`ffprobe`. Scripts are in `scripts/` next to this file.
- A scratch work folder for downloads, sheets and 3MFs (`WORK` below; use the session scratchpad).

Shop folders (keep these names exactly — earlier batches use them):

```
~/Downloads/Fotos Anuncios TikTok/
  NOVOS/
    nXX-code - Nome/                 # e.g. "n24-gato - Gato articulado"
      base_nXX-code.jpg              # reference photo uploaded to Flow
      prompt_flow.txt                # the exact photo prompt used
      flow_projeto.txt               # URL of this product's Flow project
      vbase_nXX-code.jpg             # video start frame
      anuncio.txt                    # listing text + TikTok ID/status
      2 - fotos para o anuncio/01 - foto1_principal.jpg … 07 - foto7_presente.jpg
    _upload_central_midia/nXX-code_01.jpg … _07.jpg
  Videos para postar/
    Flow - mao mostrando/NN - Nome (mao|camera).mp4     # raw Flow clips
    Para postar - versao final/NN - Nome.mp4 + NN - Nome.txt
    00 - LEIA PRIMEIRO - como postar.txt
```

Next product code: one above the highest existing `nXX` in `NOVOS/`. Next video number: one above the highest `NN` in `Para postar - versao final/`. Codes are short ASCII slugs (`n24-gato`).

## Phase 1 — Model data and real size

For each link, follow [references/makerworld.md](references/makerworld.md):

1. Read title, creator, license, photo URLs, plate weight and print time from the page (`__NEXT_DATA__`).
2. Download the photos (CDN works with curl), build a contact sheet, pick the base photo, save it as `base_<code>.jpg` (crop out logos/other items if needed).
3. Download the linked profile's 3MF via the signed API URL and run `scripts/bbox3mf.py`. Turn the boxes into human measurements (e.g. "22 cm de diâmetro x 18 cm de altura"; glasses = frame + temples; keychain without the ring).

Write down per product: name idea, what it looks like, measurements, colours, grams, hours, creator, license, small vs large (≈ 12 cm threshold), and which category it will go in ([references/tiktok-shop.md](references/tiktok-shop.md) §3).

## Phase 2 — Ad photos in Google Flow (per product)

Follow [references/google-flow.md](references/google-flow.md).

1. Flow home → **Novo projeto** → save the URL to `flow_projeto.txt`.
2. Set the project's agent settings: Confirmar antes de gerar = **Nunca**; images **1:1, x1, Nano Banana 2** (free); video **9:16, x1, Veo 3.1 - Lite**. Global gear: "Retornar vídeos sem áudio" ON.
3. Upload `base_<code>.jpg` (file-input patch + `file_upload`).
4. **New session** → include the base photo → type the 7-photo prompt (filled from `prompts.md` §1; save it as `prompt_flow.txt`) → send.
5. When done, open one image, `__grab('flow_<code>')`, collect with `scripts/contact_sheet.py --dir WORK/<code> --collect "~/Downloads/flow_<code>_*.jpeg"`, and `Read` the sheet.
6. Review with the checklist (invented text/brands, changed product, extra objects, wrong slot, wrong scale). For each bad photo: **new session** → base photo → redo prompt (`prompts.md` §2) → grab with prefix `flow_<code>_r`.
7. Map images to slots and save:
   ```bash
   python3 scripts/save_photos.py --src WORK/<code> --product "<…/NOVOS/nXX-code - Nome>" \
     --picks <p1> <p2> <p3> <p4> <p5> <p6> <p7> --code <code> --upload "<…/NOVOS/_upload_central_midia>"
   ```

Two products can run in parallel in two tabs (each tab on its own product's project). Photos cost no credits.

## Phase 3 — Showcase video in Flow (per product)

Credits: ~50/day, reset at 20:04; Veo 3.1 Lite = 10 → **max 5 videos per day**. Check the balance (avatar menu) before starting. If there are more products than credits, do the ones with the best video potential and list the rest as pending.

1. Start frame: small products → `06 - foto6_escala.jpg` (hand rotation); large or intricate → `04 - foto4_ambiente.jpg` (slow camera push-in/orbit); products whose back the model would invent (domes, open backs) → hand photo + gentle tilt. Copy it to `vbase_<code>.jpg` and upload it into **that product's project**.
2. **New session** → include `vbase_<code>` → video prompt from `prompts.md` §3 → send.
3. On "Falha": content-policy → stop, photo-only video for this product; "Falha ao gerar áudio" → **Tentar de novo** on the card (free).
4. Download 720p, move it to `Flow - mao mostrando/NN - Nome (mao|camera).mp4`.
5. Extract 5–6 frames and check the product never changes. If it drifts after N seconds, either redo with a tighter prompt (credits permitting) or use only the first N seconds (`video_ate`). Delete clips you replaced.

## Phase 4 — Final posting videos

`scripts/montar_video.py config.json` → 1080×1920, 30 fps, no audio, blurred-background fill, captions in white boxes (one dark box). Target 16–22 s (TikTok's Start-Up mission needs > 15 s).

Standard structure:

| Part | Content | Caption |
|---|---|---|
| Hook | Flow clip (≈ 8 s) — or `06 escala` photo 3.5 s when photo-only | hook from the posting caption ("Os olhos acendem de verdade") |
| Benefit | `01 principal` 3 s | size/benefit ("Luminária geek de 22 cm") |
| Detail | `03 detalhe` / `04 ambiente` / `05 medidas` / `06 escala` 2.5 s each | none |
| Gift | `07 presente` 3 s | "Presente geek certeiro" (dark box) |
| CTA | `02 ângulo` 3 s | "Toque na sacola laranja e garanta o seu" |

See the docstring in `scripts/montar_video.py` for the JSON format. Check the output with `ffprobe` (1080×1920, duration) and look at 2–4 frames.

## Phase 5 — Listing texts

Build `produtos.json` (format in `tiktok-shop.md` §2) following the shop's conventions (title pattern, bullets, footer, credit line, caption with "Toque na sacola laranja", 5 + extra hashtags), then:

```bash
python3 scripts/gerar_textos.py produtos.json --novos "<…/NOVOS>" --videos "<…/Para postar - versao final>"
```

Pick prices and shipping from `tiktok-shop.md` §4 (they are suggestions — say so in the report). The print-wording setting for listing text is at the top of `tiktok-shop.md`.

## Phase 6 — Publish on TikTok Shop

For each product, fill the single-product form exactly as in `tiktok-shop.md` §5: 7 images → title → category → "Sem marca" → Material = Plástico → description (verify text) → colour variations if any → stock 50, SKU, price (integer then ",90", zoom to verify) → weight and box → no "Problemas críticos" → **Enviar para análise**.

Then open Gerenciar produtos, confirm each product is **Ativo** or **Em análise**, and append the product ID, category and status to its `anuncio.txt`.

Do not try to upload videos to TikTok (it hangs at 1%): the user posts them.

## Phase 7 — Report to the user

Plain PT-BR, non-technical, short (format in `tiktok-shop.md` §8): table of products with price and status, what was decided on their behalf and how to change it, what was blocked (policy refusals, credits), and the next step for them (posting the videos with the ready captions). Update the auto-memory file about the shop if you learned a new quirk.

## Known pitfalls (from the first run)

- MakerWorld blocks curl on pages — use the browser; tool output that contains signed URLs is redacted, so return base64 or pathnames.
- Flow's prompt box is a contenteditable; the `<textarea>` on the page is reCAPTCHA.
- Flow invents text on props (book titles, "MY BRAND" on a desk) — the prompt's no-text rule now names props, but still check every image.
- Rotating a product makes Veo invent the unseen side (a globe grew a glass dome) — prefer tilt/push-in for such shapes.
- Seller Center: first price entry is often dropped; "24.90" becomes R$ 2.490,00; shift+Home selects the whole description on macOS; non-Latin characters are stripped.
- Large lamp-like products: lighting categories require voltage/wattage; sold without electrics they go to "Estátuas e estatuetas".
