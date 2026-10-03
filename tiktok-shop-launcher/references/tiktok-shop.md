# TikTok Shop — listing texts and the Seller Center form

> **SETTING — print wording in listing text: `KEEP` (current shop convention)**
> The user asked to keep "impresso em 3D" **out of image and video prompts** (always). Listing text still uses the shop's existing wording: title suffix `– Impressão 3D`, the bullet `• Material: plástico PLA impresso em 3D`, the made-to-order footer and the `#impressao3d` / `#feitoem3d` hashtags.
> To switch to `DROP`: remove the title suffix, write `• Material: plástico PLA` (or `plástico rígido`), edit `RODAPE` in `scripts/gerar_textos.py` (e.g. "Peça produzida sob encomenda, com acabamento artesanal…"), and drop those two hashtags. Keep the "menores de 3 anos" warning either way.

**Publishing:** "Enviar para análise" publishes the product to buyers once approved (approval took only minutes). The user's request to run this skill on a batch is the go-ahead to submit that batch. Never submit anything outside the batch, never edit or delete existing products unless asked.

## 1. Text conventions (Be Nice shop)

**Title** (≤ 255 characters, Portuguese): `<O que é> [tamanho] – <uso/benefício> – Impressão 3D[ – Presente]`
Examples: `Chaveiro Chapéu de Bruxo Falante – Chaveiro Geek para Mochila – Impressão 3D – Presente` · `Estátua Espectro Sombrio Encapuzado 20 cm – Decoração Geek e Halloween – Impressão 3D`.
Never put franchise/character/brand names in titles, descriptions or hashtags (no Harry Potter, Hogwarts, Pokémon, Disney…). Describe instead ("chapéu de bruxo falante", "castelo de várias torres").

**Description:**
```
<1–2 sentences: what it is, what it's for>

• Medidas: <a> x <b> cm[; extra]
• Material: plástico PLA impresso em 3D
• Cor: <cor>  (or "Cores: x ou y")
• <inclui / não inclui (vela/luz de LED não inclusa…)>

Peça produzida sob encomenda em impressora 3D: pequenas marcas de camada fazem parte do processo. Não indicado para menores de 3 anos (contém partes pequenas).

Modelo 3D por <creator> (MakerWorld), licença comercial.
```
Seller Center strips non-Latin characters; for such creator names use `Modelo 3D de designer da MakerWorld, com licença comercial.` (`gerar_textos.py` does this automatically).

**Posting caption:** hook + emoji, one sentence with the key size/feature, CTA `Toque na sacola laranja e garanta o seu!` (or `a sua`).
**Hashtags:** 5 suggested (`#<categoria> #<nicho> #<tema> #presentegeek #impressao3d`) + extras (`#tiktokshop #achadinhosdotiktok #tiktokmefezcomprar #feitoem3d #presentecriativo` + 2–3 niche tags).
**Nome curto** for the post's product name field: ≤ 30 characters.

## 2. Generating the text files

Write a `produtos.json` for the batch and run `scripts/gerar_textos.py` (writes `anuncio.txt` in each product folder and `<NN> - <Nome>.txt` next to the final video):

```json
[{
  "code": "n24-gato", "pasta": "n24-gato - Gato articulado", "num": "15", "video": "Gato articulado",
  "titulo": "Gato Articulado Flexi – Brinquedo Fidget e Decoração – Impressão 3D – Presente",
  "nome_curto": "Gato Articulado Flexi",
  "desc": "Gatinho articulado que mexe todo o corpo…\n\n• Medidas: 15 cm de comprimento\n• Material: plástico PLA impresso em 3D\n• Cor: laranja",
  "criador": "Jacek Maryniowski", "site": "Printables",
  "preco": 29.90, "peso": 100, "cx": [16, 10, 5],
  "legenda": "Ele mexe tudo 😻 Gatinho articulado de 15 cm… Toque na sacola laranja e garanta o seu!",
  "tags": "#gato #fidget #brinquedo #presentegeek #impressao3d",
  "extras": "#gatos #articulado #tiktokshop #achadinhosdotiktok #tiktokmefezcomprar #feitoem3d #presentecriativo",
  "atencao": ""
}]
```
`num` = next free number in `Videos para postar/Para postar - versao final/` (look at existing `NN - …` files). `cx` = [comprimento, largura, altura].

## 3. Category map (used and accepted)

| Product type | Category path in the form |
|---|---|
| Keychain | Acessórios de moda > Bijuterias e acessórios > Chaveiros |
| Costume accessory (glasses, masks, hats to wear) | Artigos para casa > Produtos para festas e comemorações > Chapéus, máscaras e acessórios de festa — **not** "Óculos > Armações e óculos" (that is real eyewear) |
| Statue, figure, décor object; lamp shade sold **without** electrics | Artigos para casa > Decoração de casa > Estátuas e estatuetas (lighting categories ask for voltage/wattage) |
| Seasonal / Christmas décor, LED-tealight village or globe | Artigos para casa > Produtos para festas e comemorações > Decorações festivas |
| Tealight holder (Halloween pumpkin…) | Artigos para casa > Decoração de casa > Castiçais |
| Desk organiser, pencil holder | Organizadores domésticos > Caixas e recipientes de armazenamento |
| Hanging ornament | Decoração de casa > Decoração suspensa |

A yellow "Esta categoria pode não ser a ideal…" notice is advisory; red "Problemas críticos" block submission.

## 4. Price and shipping (suggestions — always report them as suggestions)

| Reference product | Price |
|---|---|
| Keychain (small, < 10 g) | R$ 24,90 |
| Small flexi/fidget, costume glasses | R$ 29,90 – 34,90 |
| Small LED-tealight décor | R$ 29,90 |
| Snow globe / 11 cm LED décor | R$ 69,90 |
| LED village 15 cm | R$ 89,90 |
| 16–20 cm figure or statue (~200 g, ~9 h) | R$ 119,90 |
| Large lamp shade 22 cm (~280 g, ~14 h) | R$ 149,90 |

Scale with print grams and hours. Stock: 50 (made to order). Package weight = print grams + packaging (~70 g small, ~150–250 g medium, ~400 g large). Box = measured size + 2–4 cm per side.

## 5. Seller Center single-product form

URL: `https://seller-br.tiktok.com/product/create?shop_region=BR` (or Gerenciar produtos → Adicionar produto; after a submit, the success page has an **Adicionar produto** button). One product at a time:

1. **Images:** `find` "image file input near 'Carregar imagem principal'" → `file_upload` the 7 files `_upload_central_midia/<code>_01.jpg … _07.jpg` in one call. Order is kept; 01 becomes the main image. Wait ~6 s.
2. **Nome do produto:** click the field, `type` the title.
3. **Categoria:** click the field → a "Sugestão" list with **Aplicar** buttons. Apply the one matching §3; otherwise click the category field and type in its search box (e.g. "Estátuas", "lumin"), then pick. Changing category later shows "Alterar categoria do produto?" → Continuar (attributes are reset).
4. **Marca:** open the dropdown → `find` 'Selecione "Sem marca"' → click.
5. **Atributos (Principais):** Material → type "Plás" → tick **Plástico** → Escape. Fill obvious ones (Feriado = Natal, Tipo = Adereço…); leave the rest.
6. **Descrição:** click inside the rich editor and `type` the description with `\n` line breaks. Verify:
   ```js
   [...document.querySelectorAll('[contenteditable=true]')].map(e => e.innerText.length + ': ' + e.innerText.slice(0, 60) + ' … ' + e.innerText.trim().slice(-60)).join(' ## ')
   ```
   Fix a line by selecting all (`cmd+a`) and retyping the whole description. **Never use shift+Home on macOS** — it selects the whole text and the next keystroke replaces everything.
7. **Vídeo:** skip (automated video upload hangs).
8. **Variações** (only when the product has options, e.g. 2 colours): toggle **Adicionar variações** → Nome da variação → **Cor** → first option field → type → **Adicionar opção** → second option. Each row gets an image: `find` "input type=file in the '<option>' variation row" → `file_upload` a square crop of that colour (crop it from the main photo with PIL). Fill each row: Estoque, Preço, Peso do pacote (g, per row here), SKU `<code>-<cor>`.
9. **Preço e estoque** (no variations): Estoque `50`, SKU `<code>`, then the price.
   **Price quirk:** the first entry into an empty price field is often dropped, and a dot is read as thousands (`24.90` → R$ 2.490,00). Click the price field, `type` the integer part (`149`), then `type` `,90` separately; click elsewhere; `zoom` the row to confirm `R$ 149,90`. If empty or wrong: click, `cmd+a`, `Delete`, retype the same way.
10. **Conformidade (INMETRO):** optional fields — leave empty.
11. **Envio:** Peso do pacote (g) and Dimensões: **Altura**, **Largura**, **Comprimento** (cm). The "Taxa de envio estimada" appears when valid.
12. Check there is no "Problemas críticos" block:
    ```js
    const t = document.body.innerText, i = t.indexOf('Problemas cr'); i >= 0 ? t.slice(i, i + 200) : 'sem problemas'
    ```
13. **Enviar para análise** (top right). Success page: "Produto enviado". Close any rating pop-up with its X.

Scroll with the mouse over the right margin (≈ x 1400) — over the description editor the wheel scrolls the editor, not the page. Coordinates in this file are hints from a 1568 px-wide viewport; prefer `find`/refs and screenshots.

If a navigation away from an edit page is blocked by "Leave site?", use `navigate` with `force: true` (only when you made no changes you need).

## 6. Verify and record

Gerenciar produtos (`/product/manage?shop_region=BR`) → tabs **Ativo** / **Em análise** / **Precisa de atenção**; search by name (`&search_content=<word>` in the URL) and read with `get_page_text`. Append to each product's `anuncio.txt`:

```
TIKTOK SHOP
ID do produto: <id>
Categoria: <path>
Status em <dd/mm/aaaa>: Ativo | Em análise
```

## 7. Posting videos (hand-off — the user does this)

Automated uploads of videos to Seller Center/TikTok hang at 1%, so the user posts them. Point them to `Videos para postar/Para postar - versao final/` and `00 - LEIA PRIMEIRO - como postar.txt`: choose the video → paste LEGENDA into Descrição → 3–5 hashtags → Adicionar produto (the title in the .txt) → Nome do produto = NOME CURTO → turn on **Conteúdo gerado por IA** → Publicar. Best 18h–21h, 1–2 per day. Videos must be > 15 s for the Start-Up mission.

## 8. Final report to the user

Plain PT-BR, non-technical (no file paths, framework or code names unless asked). Include:
- a table: produto | preço | status (Ativo / Em análise / bloqueado);
- decisions you took on your own (prices, categories, LED included or not, removed credits…), each with how to change it;
- anything blocked or skipped (policy refusal → photo-only video, credits exhausted → videos pending after 20:04, photos you could not fix);
- (no license notes: sending the link already means the user can sell it);
- what the user still has to do (post the videos).
