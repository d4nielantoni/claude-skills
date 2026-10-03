# Google Flow — how to drive it

Flow lives at `https://flow.google.com/` (old `labs.google/fx/…/tools/flow` links redirect). Each project has a media grid and, on the right, an **agent chat panel** ("Sessão sem título" + prompt box). Generation is asked for in that chat.

## Isolation rule (user requirement)

- **One Flow project per product.** On the home page click **Novo projeto** (`find` "Novo projeto button"). Save the project URL in the product folder as `flow_projeto.txt`. Every 1024 px image in that project then belongs to that product, which makes downloads unambiguous.
- **One chat session per request.** Before each request (the 7 photos, each redo, each video) click the **new-session icon** in the chat panel header (pencil/square icon between the session title and the X; hint ≈ (1503, 80) at 1568 px width). Never ask for two products, or for photos and a video, in the same session.

## Per-project settings (set them in every new project)

Click the sliders icon next to the prompt box → "Configurações do agente":

| Setting | Value | Why |
|---|---|---|
| Confirmar antes de gerar | **Nunca** | No pauses; failures are not charged |
| Padrão da geração de imagens | **1:1**, **x1**, **Nano Banana 2** | Nano Banana 2 cost 0 credits; one "7 fotos" prompt returns 7 separate images |
| Padrão para geração de vídeo | **9:16**, **x1**, **Veo 3.1 - Lite** | 10 credits per video (Omni 1.1 Flash = 15) |

Click **Salvar**. A click on a dropdown option sometimes swallows the next click — take a screenshot and re-click what didn't stick.

Global gear menu (top bar): **Retornar vídeos sem áudio = ON**.

Credits: avatar menu → "N créditos do Google Flow". About **50 per day, reset at 20:04** (local). Plan **at most 5 Veo Lite videos per day**; photos are free. If credits run out, finish the photos and posting texts, and tell the user which videos remain for after 20:04.

## Upload a file into the project

The chat "+" opens a media picker with **Enviar mídia**, which normally opens the native file dialog (unusable). Patch the page so the file input stays in the DOM, then use `file_upload`:

```js
// 1. once per page load
if (!window.__origClick) {
  window.__origClick = HTMLInputElement.prototype.click;
  HTMLInputElement.prototype.click = function () {
    if (this.type === 'file') {
      this.style.display = 'block';
      if (!this.isConnected) document.body.appendChild(this);
      window.__lastFileInput = this;
      return;                       // do NOT open the native dialog
    }
    return window.__origClick.call(this);
  };
}
'ok'
```

```js
// 2. after clicking the chat panel "+" (bottom-left of the prompt box)
window.__lastFileInput = null;
const b = [...document.querySelectorAll('button')].find(x => x.textContent.trim().endsWith('Enviar mídia'));
b.click(); await new Promise(r => setTimeout(r, 800));
window.__lastFileInput ? 'found input' : 'no input'
```

3. `find` "file input (type=file) element" → `file_upload` with absolute paths (several files at once is fine; total < 10 MB). Files must live under the user's folders (e.g. the product folder), not in /tmp.

Use the chat panel "+" — the top-bar "+" → "Enviar" path did not go through the patch.

## Ask for the photos

1. New session → chat "+" → type the file name in the picker search (e.g. `base_n24`) → the matching asset is preselected → **Incluir no comando**.
2. Click the prompt box (a contenteditable; the only `<textarea>` on the page is reCAPTCHA — never script into it) and `type` the prompt from `prompts.md`.
3. Click the send arrow. 7 photos take ~1–2 min; the grid shows a % per image. If it sits at 99% for a long time, wait 30 s more; a reload shows the finished images.

## Download images

Grid thumbnails are 512 px (`/asb/…` URLs). Open any generated image (edit view): its filmstrip holds the full 1024 px images (`/image/…` URLs). Download them as files named by you:

```js
window.__done = window.__done || new Set();
window.__dl = async (urls, prefix) => {
  let n = 0;
  for (const [k, u] of urls.entries()) {
    const b = await (await fetch(u)).blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(b); a.download = `${prefix}_${k}.jpeg`;
    document.body.appendChild(a); a.click(); a.remove(); n++;
    await new Promise(r => setTimeout(r, 700));
  }
  return n;
};
window.__grab = async (prefix) => {
  const seen = new Set();
  const news = [...document.querySelectorAll('img')]
    .filter(i => i.naturalWidth === 1024 && i.naturalHeight === 1024).map(i => i.src)
    .filter(u => { const p = new URL(u).pathname; if (seen.has(p) || window.__done.has(p)) return false; seen.add(p); return true; });
  news.forEach(u => window.__done.add(new URL(u).pathname));
  return await window.__dl(news, prefix);
};
await window.__grab('flow_n24')      // later redos: await window.__grab('flow_n24_r')
```

- Never return full image URLs from `javascript_tool` (the output is blocked for query-string data). Return counts or pathnames only.
- Files land in `~/Downloads`. Collect and review: `scripts/contact_sheet.py --dir WORK/n24 --collect "~/Downloads/flow_n24_*.jpeg"`, then `Read` the sheet.
- DOM order is not generation order. Assign slots by looking at the sheet, not by index.
- If the base photo you uploaded is exactly 1024×1024 it will be grabbed too — ignore it on the sheet.
- One specific image: open it and download the largest displayed `<img>` (sort by `getBoundingClientRect().width`).

## Review checklist (photos)

Reject and redo (new session, `prompts.md` §2) when a photo has:
- invented text or branding ("MY BRAND", "3D PRINTED…", book titles, labels, logos, crests);
- a changed product (different shape/colour, extra or missing parts, a lens where there is none, a different castle);
- extra copies of the product, or a second product from the base photo;
- the wrong slot (e.g. a desk scene where photo 2 asked for white background 3/4);
- a scale that contradicts the measurements (a 20 cm statue should be about twice a mug's height).

Minor issues (photo 2 almost frontal, a gift photo that isn't strictly flat-lay) can stay; say so in the report.

## Videos

1. Put the start frame in the product folder as `vbase_<code>.jpg` (copy of `06 - foto6_escala.jpg` or `04 - foto4_ambiente.jpg`), upload it into **the same product's project**, new session, include it, send the video prompt (`prompts.md` §3).
2. 1–3 min. The chat may say the video "foi agendada e está na fila devido à alta demanda" — that is normal; watch the grid.
3. Failures show as a card "Falha":
   - **"…políticas de fornecedores de conteúdo terceirizados…"** → the product looks like a protected character/brand. **Do not rephrase to get around it.** Make a photo-only posting video and tell the user.
   - **"Falha ao gerar áudio"** → click **Tentar de novo** on the card (not charged).
4. Download: open the video → download icon → **720p (Tamanho original)**. The file lands in `~/Downloads` with an automatic name (e.g. `Mão_segurando_óculos_redondos_<timestamp>.mp4`); pick it with `ls -t ~/Downloads/*.mp4 | head -1` and move it to `Videos para postar/Flow - mao mostrando/NN - Nome (mao|camera).mp4`.
5. Check fidelity frame by frame before using it:
   ```bash
   for t in 0.5 2 3.5 5 6.5 7.8; do ffmpeg -v error -y -ss $t -i clip.mp4 -frames:v 1 -vf scale=200:-1 f_$t.jpg; done
   ```
   Join the frames into one strip with PIL and `Read` it. If the product morphs after N seconds (the snow globe grew a glass dome while rotating), either redo with the gentle-tilt prompt (if credits allow) or keep only the faithful part with `"video_ate": N` in `montar_video.py`.

## Parallel work

Two Chrome tabs can drive two products at once (each tab on its own product's project). Patch functions (`__origClick`, `__grab`, `__done`) live per tab — run the snippets in each tab. A tab only sees media created elsewhere after a reload.

## Leaving pages

If a navigation is blocked by a "Leave site?" dialog, call `navigate` with `force: true` — never trigger or click browser dialogs.
