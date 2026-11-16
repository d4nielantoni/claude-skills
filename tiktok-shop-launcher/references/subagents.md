# Pipeline with subagents (photos → publishing)

Use this for any batch of 2 or more products. The main agent is the **orchestrator**: it does the work every product needs before photos can start, then runs a conveyor belt. **Photographer** subagents make the Flow photos, one product each. As soon as a product's photos are saved, a **publisher** subagent puts that product on TikTok Shop while the next products are still being photographed.

```
orchestrator: Phase 1 (all products) → Phase 5 texts (all) → start belt
  photographer n50 ─┐   photographer n51 ─┐   photographer n52 …
                    └→ publisher n50       └→ publisher n51 …
orchestrator: verify Seller Center list → videos (optional) → final report
```

## Why it is shaped this way

- The **photographer needs only** `base_<code>.jpg` + `prompt_flow.txt`. The **publisher needs only** the 7 files in `_upload_central_midia/` + `anuncio.txt` + a short spec. So the orchestrator writes all of that up front, and the subagents never need the chat history.
- **No polling.** Background agents re-invoke the orchestrator when they finish. Each finished photographer notification is the trigger to start that product's publisher and the next photographer. Never write `sleep` loops or waiting scripts.
- **Concurrency limits:**
  - At most **2 photographers** at a time: Flow gets slow, and each one needs its own tab.
  - At most **1 publisher** at a time. Seller Center misbehaves with several create forms open: dropped prices, swallowed clicks. If a publisher is still running when more photos are ready, queue those products and start the next publisher when its notification arrives.
- **One product per subagent.** A failure then stays contained, and the report says exactly which product needs attention.

## Orchestrator steps

1. **Phase 1 for all products** (SKILL.md), done by the orchestrator itself:
   - Create the folders.
   - Save `base_<code>.jpg`.
   - Measure, estimate cost, pick prices and categories.
   - Write `prompt_flow.txt`, filled from `prompts.md` §1.
2. **Phase 5 for all products:**
   - Write `produtos.json`.
   - Run `scripts/gerar_textos.py`, so every `anuncio.txt` exists before any publisher starts.
   - Write one **publish spec** per product to `WORK/spec_<code>.json`, with these fields:
     `{code, pasta, titulo, desc (full text incl. footer + credit), categoria ("lamp"|"festive"|path), atributos (e.g. {"Tensão de entrada (V)":"5","Potência (W)":"3"} or {"Material":"Plástico","Feriado/Ocasiões especiais":"Natal"}), preco, estoque, sku, peso, cx [altura, largura, comprimento], variacoes (optional: [{nome, preco, sku, foto}]), nfe: "off"}`.
3. **Check the board:** run `python3 scripts/fila.py --novos "<…/NOVOS>" n50-code n51-code …`. It shows, per product, whether it has a base photo, a prompt, texts, the 7 photos and a TikTok ID.
4. **Start the belt:**
   - Launch photographers for the first 2 products: Agent tool, `subagent_type: "general-purpose"`, `run_in_background: true`, prompt from the template below.
   - Tell the user in one line that the belt is running.
5. **On each photographer notification:**
   - Run `fila.py` to confirm the 7 photos exist.
   - Look at the photographer's contact sheet yourself (rule 6, verify before claiming).
   - If the photos are OK and no publisher is running, start a publisher for that product. Otherwise queue it.
   - Start the next photographer, if any product is still waiting for photos.
6. **On each publisher notification:**
   - Confirm the ID was appended to `anuncio.txt` (`fila.py`).
   - Start the next queued publisher.
7. **After the last publisher:**
   - Open Gerenciar produtos once and read the status of every product in the batch.
   - Then do videos if the user asked for them; Flow credits are shared, so do them sequentially.
   - Write the final report.

A subagent may report a failure: a policy refusal, a photo that could not be fixed, a form that would not save. In that case, record it and skip that product. Do not retry blindly. Never let a subagent's failure stop the other products.

## Rules every subagent prompt must carry

Subagents start with no context. Paste these points into every prompt, adapted to the role:

- **Browser:**
  - Load the Chrome tools in ONE ToolSearch call (core set + `javascript_tool`, `find`, `file_upload`, `get_page_text`, `browser_batch`).
  - Call `tabs_context_mcp`, then **create your own new tab** with `tabs_create_mcp`.
  - **Use only that tab ID.** Never touch, navigate or close other tabs: other agents are working in them. Close your tab at the end.
- **No clipboard.** Never use `pbcopy`/`cmd+v`. The user and the other agents share the clipboard. Type text with the `type` action, and read long text from files.
- **Downloads:** Flow downloads land in `~/Downloads`. Always use a product-specific prefix (`flow_<code>_…`) and collect only your own prefix.
- **Wording:**
  - Never write "impressão 3D" / "impresso em 3D" / "impressora 3D" / "PLA" in a prompt, and never write franchise names.
  - Content-policy refusals are final.
- **Read the reference sections the prompt points to:** `references/google-flow.md` for the photographer, `references/tiktok-shop.md` §5 for the publisher. They hold the UI quirks.
- **Report:** finish with a short report of facts only. What was done, file paths, the product ID, anything that failed. No questions to the user.

## Photographer prompt template

```
You are the PHOTOGRAPHER for one product of the Be Nice TikTok Shop batch. Do only this product.

Product: <code> — <nome>
Folder: ~/Downloads/Fotos Anuncios TikTok/NOVOS/<pasta>/
Inputs already there: base_<code>.jpg (reference photo) and prompt_flow.txt (the exact 7-photo prompt).
Work folder for downloads/sheets: <WORK>/<code>

Read first: ~/.claude/skills/tiktok-shop-launcher/references/google-flow.md (whole file) and references/prompts.md §2 (redo prompt).

Steps:
1. <browser rules: own tab only, one ToolSearch, close tab at end>
2. Flow home → "Novo projeto" (use find, not coordinates) → save the project URL to <pasta>/flow_projeto.txt.
3. Agent settings: Confirmar antes de gerar = Nunca; images 1:1, x1, default Nano Banana model; video 9:16, x1, Veo 3.1 - Lite. Salvar. Zoom to verify.
4. Patch the file input (google-flow.md), chat "+" → "Fazer upload de mídia" → file_upload base_<code>.jpg → select it → "Incluir no comando".
5. Click the prompt box and TYPE the contents of prompt_flow.txt (no clipboard). Send.
6. When the 7 images are done: open one image, location.reload(), run __grab('flow_<code>'). If results are stacked as versions, click each history thumbnail to load the 1024 px image before grabbing.
7. scripts/contact_sheet.py --dir <WORK>/<code> --collect "$HOME/Downloads/flow_<code>_*.jpeg" and Read the sheet.
8. Review with the checklist in google-flow.md (invented text/logos, changed product, extra objects, wrong slot, wrong scale). Text burned into a photo (e.g. "Photo 6: …") → crop it out with PIL if the product stays whole; otherwise redo that photo in a NEW chat session of the same project (prompts.md §2), grab with prefix flow_<code>_r.
9. Map slots and save: scripts/save_photos.py --src <WORK>/<code> --product "<folder>" --picks <7 names in slot order> --code <code> --upload "~/Downloads/Fotos Anuncios TikTok/NOVOS/_upload_central_midia"
<if variations: 10. Crop one square image per variation from the main photo into <folder>/3 - variacoes/var_<opção>.jpg and check them visually.>

Never generate photos for any other product. Do not make videos. Do not publish anything.
Report: Flow project URL, slot mapping (which file went to which slot), any photo you fixed/cropped and why, the contact-sheet path, and anything that failed.
```

## Publisher prompt template

```
You are the PUBLISHER for one product of the Be Nice TikTok Shop batch. Submit only this product.

Product: <code> — spec in <WORK>/spec_<code>.json (title, description, category, attributes, price, stock, SKU, weight, box, variations).
Photos: ~/Downloads/Fotos Anuncios TikTok/NOVOS/_upload_central_midia/<code>_01.jpg … _07.jpg (01 = main image).
Listing text file to append the result to: NOVOS/<pasta>/anuncio.txt

Read first: ~/.claude/skills/tiktok-shop-launcher/references/tiktok-shop.md §3, §5 and §6.
The user's request to run this batch is the go-ahead to click "Enviar para análise" for THIS product. Do not touch any other product.

Steps:
1. <browser rules: own tab only, one ToolSearch, close tab at end>
2. Open https://seller-br.tiktok.com/product/create?shop_region=BR in your tab.
3. Images: upload 01–04 to the main image input, wait ~7 s, then 05–07 to the "Carregar imagem" input (7 at once can leave one stuck on "Carregando"). Confirm 7 thumbnails and no "Carregando" in the page text.
4. Title: click the name field and TYPE it; verify with JS that an input holds the full title.
5. Category: open the suggestions and click "Aplicar" on the row whose text matches the spec — do it via JS (the list reorders): find the button whose row text includes the target path and .click() it; then read the Categoria text back. If wrong, open "N sugestões" and fix (confirm "Alterar categoria").
6. Marca → "Sem marca". Attributes from the spec (lamps: Tensão/Potência are type-then-"Adicionar"; festive: Material = Plástico, Feriado = Natal).
7. Description: click inside the editor and TYPE the spec text (never paste). Verify length/first/last words with JS.
8. Price & stock (or variations: toggle "Adicionar variações" → "Adicionar nova" name → options one by one, clicking the page margin before each field → per-row stock/price/SKU → per-row image via file inputs tagged with aria-label by JS). Price: type the integer, then ",90"; zoom to confirm.
9. Envio: weight (g) and Altura/Largura/Comprimento from the spec. Turn OFF the NF-e switch (spec nfe = "off").
10. Check there is no "Problemas críticos" (JS on page text), then "Enviar para análise". Expect "Produto enviado".
11. Gerenciar produtos with &search_content=<a word of the title> → read ID and status (Ativo / Em análise).
12. Append to anuncio.txt:
    TIKTOK SHOP
    ID do produto: <id>
    Categoria: <path>
    Status em <dd/mm/aaaa>: <status>

Report: product ID, status, category, price(s) as shown, number of photos, anything you could not fill or that failed.
```

## Resuming

If the session stops halfway, run `fila.py` with the batch codes:
- Products with 7 photos but no ID go to publishers.
- Products without photos go to photographers.

Nothing is redone that is already done.
