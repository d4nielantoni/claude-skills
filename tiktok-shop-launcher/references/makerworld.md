# Getting product data from MakerWorld (and Printables)

Goal per link: title, creator, license, photos, plate weight / print time, and the **real size** of the profile the user linked.

## MakerWorld

`curl` gets a Cloudflare "Just a moment…" page. Read everything from the user's logged-in Chrome tab instead.

The user's link usually ends in `#profileId-<n>`: that is the **instance/print profile** the user picked. Profiles of the same design can be different sizes (e.g. a statue had a 200 mm and a 100 mm profile), so measure that profile, not the default one.

### 1. Design data (on the design page)

```js
const d = window.__NEXT_DATA__.props.pageProps.design;
JSON.stringify({
  id: d.id, title: d.title, creator: d.designCreator?.name, license: d.license,
  pics: (d.designExtension?.design_pictures || []).map(p => p.url.split('/makerworld/model/')[1]),
  inst: (d.instances || []).map(i => i.id + ':' + i.title + ':' +
    (i.extention?.modelInfo?.plates || []).map(p => p.weight + 'g/' + Math.round(p.prediction / 60) + 'min').join(','))
})
```

Tool output is truncated around 1–2 k characters — return compact strings and split into several calls if needed.

From any MakerWorld page you can fetch other designs without navigating:

```js
const j = await (await fetch('/api/v1/design-service/design/<designId>', {credentials: 'include'})).json();
```

The summary (`d.summary`) is HTML in the creator's language; strip tags if you want hints (LED type, assembly).

### 2. Photos

Picture URLs are `https://makerworld.bblmw.com/makerworld/model/<path>`; the CDN downloads fine with `curl`. Save them to a work folder, make a contact sheet (`scripts/contact_sheet.py --dir WORK/ref`) and pick the base photo per product:

- the product alone or clearly dominant, real photo preferred over render;
- no logos, crests, franchise items, other products, printer beds with brand text — or crop them out (PIL) and tell Flow in `{O_QUE_E}` what to leave out;
- lit products: a photo with the light on.

Save it as `NOVOS/<nXX-code - Nome>/base_<nXX-code>.jpg`.

### 3. Real size from the 3MF

The 3D preview loads a signed 3MF. Ask the API for it inside the page and return only the query string, base64-encoded (otherwise the tool redacts the `key=` parameter):

```js
const j = await (await fetch('/api/v1/design-service/instance/<profileId>/f3mf?type=preview&devModelName=N2S', {credentials: 'include'})).json();
j.name + ' | ' + j.url.split('?')[0].split('/makerworld/model/')[1] + ' | Q:' + btoa(j.url.split('?')[1])
```

Download within ~5 minutes (the signature expires) and measure:

```bash
B=https://makerworld.bblmw.com/makerworld/model
curl -s -o WORK/<code>.3mf "$B/<path>?$(echo '<Q>' | base64 -d)"
python3 scripts/bbox3mf.py WORK/<code>.3mf
```

Read the output with judgment:
- one line per object on the plate; **Z is the printed height**;
- several objects = separate parts (glasses frame + 2 temples, a lamp body + an LED holder); describe the assembled product (frame 12.7 × 6.3 cm, temples 14 cm);
- a design may be printed lying down — use the orientation the product is displayed in;
- keychains: report the size without the ring.

Plate weight (g) and print time are in `instances[].extention.modelInfo.plates[]` (`weight`, `prediction` in seconds) — use them for shipping weight and pricing.

### 4. License

Sending a link means the user already holds the license to sell prints of that model — it is implied, they don't have to say it. Never ask, never block, and don't put license warnings in the report. Reading `license` is only useful for the credit line in the listing (e.g. CC BY on Printables requires attribution).

## Printables

Earlier batches came from Printables. The user's script `~/Downloads/Produtos 3D - Datas Comemorativas/baixar_modelos.py` uses the public GraphQL API (`https://api.printables.com/graphql/`, images from `https://media.printables.com/`) and already filters models whose license allows selling prints. Model files there are usually STL; `scripts/bbox3mf.py` measures `.stl` too (binary and ASCII). Earlier measurements live in `medidas_cm.json` in the same folder.

Credit line in listings: `Modelo 3D por <creator> (Printables), licença <CC …>.` — CC BY/BY-SA require attribution.
