# Prompt templates (PT-BR)

These are the user's own templates from the session that created this skill, extended to the 7-photo set used for new products. Keep the wording. Fill only the `{…}` slots.

Hard rules for every generation prompt (photos, redos and videos):

- **Never write "impresso em 3D", "impressão 3D", "impressora 3D" or "PLA" in a prompt** (and don't mention layers anywhere except the negative anti-defect line). Those words make the image model draw layer lines, stringing and rough print texture. Describe the material neutrally: `plástico rígido fosco` (or `plástico rígido brilhante`, `plástico translúcido` when it is).
- **Always include the anti-defect line** (`{ACABAMENTO}` below).
- Describe the product by what it looks like, never by a franchise or character name (no "Harry Potter", "Hogwarts", "Pokémon", "Stitch"…). Writing the name can also trigger Flow/Veo refusals.
- If the product has text that is part of the design (e.g. a flag saying "Vibe Coder", a plaque on a base), say it must stay exactly as in the original photo, and add it as the only exception to the no-text rule.

```text
{ACABAMENTO} = Acabamento perfeito: superfícies lisas e limpas, sem rebarbas, sem fiapos, sem linhas de camada aparentes, sem bolhas, sem marcas de suporte e sem imperfeições.
```

## 1. Photo prompt — 7 photos (one Flow session, one product)

```text
Você é um fotógrafo profissional de produtos para e-commerce. Use SOMENTE a imagem que enviei como referência. Vou enviar a foto de uma peça que eu vendo no TikTok Shop. Crie 7 novas fotos desse MESMO produto para o meu anúncio, cada foto como uma imagem separada. Sobre o produto: - O que é: {O_QUE_E} - Medidas reais: {MEDIDAS} - Material e acabamento: {MATERIAL}, acabamento liso e uniforme. Regras obrigatórias para TODAS as fotos: - O produto deve ser idêntico ao da foto original: mesmo formato, proporções, detalhes, textura e cor{TEXTO_DO_PRODUTO}. Não invente partes, não mude o design, não "melhore" a peça. - {ACABAMENTO} - Formato quadrado (1:1), alta resolução, iluminação suave de estúdio, foco nítido. - Sem marca d'água, sem logotipos, sem marcas ou personagens de terceiros. - Sem texto na imagem (nem em livros, etiquetas, caixas ou objetos do cenário), exceto os números da foto 5{EXCECAO_TEXTO}. - Aparência realista de fotografia, não de ilustração ou 3D renderizado. As 7 fotos: 1. Foto principal: produto de frente, centralizado, fundo branco puro (#FFFFFF), sombra suave embaixo, ocupando cerca de 80% do quadro. 2. Mesmo fundo branco, produto em ângulo de 3/4, mostrando profundidade e volume. 3. Close de detalhe: textura e acabamento da superfície, mostrando o acabamento liso e caprichado da peça, em fundo neutro claro. 4. Produto em uso num ambiente real e aconchegante [ex: {AMBIENTE}], com luz natural, com o produto como destaque. 5. Foto de medidas: produto em fundo branco com linhas de cota indicando [{COTAS}], com números legíveis e fonte simples. 6. Foto de escala: {ESCALA}, para mostrar o tamanho real. 7. Foto de presente: produto sobre uma mesa clara ao lado de uma caixa de presente e papel de seda, em estilo flat lay, sem etiquetas escritas, transmitindo "ótima ideia de presente".
```

Slots:

| Slot | How to fill |
|---|---|
| `{O_QUE_E}` | Visual description: shape, colours, distinctive details, what is NOT in the product. If the base photo shows extra items (a second model, a scarf with a crest, a bottle, cables, a printer bed), say "Mostre apenas …, sem …". If the product comes in colours shown together, say which photos show both colours and which show one. |
| `{MEDIDAS}` | From the 3MF/STL measurement, e.g. `4,4 cm de largura x 3,3 cm de altura (sem contar a argola)`. |
| `{MATERIAL}` | `plástico rígido fosco` by default. |
| `{TEXTO_DO_PRODUTO}` | Empty, or e.g. `, e a bandeira sempre com o texto "Vibe Coder"` / `, e a placa em relevo da base exatamente igual à da foto original`. |
| `{EXCECAO_TEXTO}` | Empty, or ` e o texto que já existe no produto`. |
| `{AMBIENTE}` | A real scene for the product's use. Add "livros de lombada lisa" whenever books appear (Flow invents titles otherwise). Lit products: "à noite, com a luz acesa". |
| `{COTAS}` | e.g. `altura 18 cm, largura 22 cm`. |
| `{ESCALA}` | Small items (< ~12 cm): `uma mão segurando UMA unidade do produto` (keychains: `pela argola`). Large items: `o produto sobre uma mesa ao lado de uma caneca comum`. |

## 2. Redo prompt (follow-up in a NEW session of the same product's project)

Attach the same base photo again, then:

```text
Use SOMENTE a imagem que enviei como referência. Refaça só esta(s) foto(s) do mesmo produto, idêntico ao da foto original (mesmo formato, proporções, detalhes e cor), formato quadrado 1:1, aparência realista de fotografia. {ACABAMENTO} Foto {N}: {DESCRICAO_DA_FOTO}. {CORRECAO} Nenhum texto, palavra ou letra na imagem{EXCETO_COTAS}.
```

`{CORRECAO}` names what went wrong, e.g. `Sem mesa, sem notebook, sem nenhum texto.` / `Livros de capa lisa SEM títulos e SEM nenhuma letra nas lombadas.` / `Mostre o produto de 3/4, não de frente.`

## 3. Video prompt (one Flow session per video)

The user's template, with model and anti-defect added. Pick the motion by product size.

**Small items (hand rotation)** — start frame: `06 - foto6_escala.jpg` (a hand already holds the product):

```text
Gere 1 vídeo vertical 9:16 a partir desta imagem (use a imagem como primeiro quadro), com o modelo Veo 3.1 Lite. A mão segura {PRODUTO_CURTO} e mostra para a câmera, girando o pulso devagar para mostrar os lados {DO_PRODUTO} e depois voltando para a frente. Movimento natural e suave, câmera parada estilo vídeo de celular, luz suave. O produto deve continuar idêntico ao da imagem ({TRACOS_CHAVE}). {ACABAMENTO} Nenhum texto na tela, sem legenda.
```

**Large or intricate items (camera move)** — start frame: `04 - foto4_ambiente.jpg`:

```text
Gere 1 vídeo vertical 9:16 a partir desta imagem (use a imagem como primeiro quadro), com o modelo Veo 3.1 Lite. A câmera de celular faz uma aproximação lenta e um leve giro ao redor {DO_PRODUTO} {ONDE}; {DETALHE_DE_CENA}. O produto fica parado e deve continuar idêntico ao da imagem ({TRACOS_CHAVE}). Movimento natural e suave. {ACABAMENTO} Nenhum texto na tela, sem legenda.
```

**Products whose back/sides the model would have to invent** (domes, open backs, flat reliefs) — gentle tilt instead of rotation:

```text
… A mão segura {PRODUTO_CURTO} e o aproxima devagar da câmera, inclinando só um pouquinho para a esquerda e para a direita (no máximo 15 graus), sempre mostrando a frente. Não gire o produto, não mostre a parte de trás. {O_QUE_NAO_TEM, ex: O produto não tem vidro: é uma cúpula aberta de plástico branco fosco.} O produto deve continuar idêntico ao da imagem durante todo o vídeo. Movimento natural e suave, câmera parada estilo vídeo de celular, luz suave. {ACABAMENTO} Nenhum texto na tela, sem legenda.
```
(The first part is the same as the small-items template: "Gere 1 vídeo vertical 9:16 a partir desta imagem (use a imagem como primeiro quadro), com o modelo Veo 3.1 Lite.")

`{TRACOS_CHAVE}`: colour, shape, proportion and the one or two details the model must not change (e.g. `mesma cor, formato, proporção e o raio em cima da lente`). `{DETALHE_DE_CENA}`: `as chamas das velas tremulam suavemente`, `a luz amarela dos olhos e da boca pulsa suavemente`.

## 4. Filled examples (from the first batch — already without print words)

**Keychain (two colours)**
- O que é: `Chaveiro de chapéu de bruxo falante: chapéu pontudo e amassado com um rosto formado pelas dobras (olhos e boca), com argola e corrente de chaveiro prateada. Disponível em 2 cores: bege claro e marrom escuro, como na foto. Mostre as duas cores juntas nas fotos 1, 2 e 7; nas outras, só o bege claro. Não inclua nenhum outro chaveiro, medalha ou logotipo`
- Ambiente: `mochila escolar ou chaves de casa sobre uma mesa de madeira, com o chaveiro pendurado` · Escala: `uma mão segurando UM chaveiro pela argola`

**Costume accessory**
- O que é: `Óculos de bruxo para fantasia e cosplay: armação redonda bem fina, preta fosca, com um pequeno raio em zigue-zague em cima da lente esquerda; sem lentes (só a armação), com hastes de encaixe`
- Ambiente: `sobre uma pilha de livros antigos de lombada lisa, ao lado de uma vela e de uma pena, numa escrivaninha de madeira`

**Statue (20 cm)**
- O que é: `Estátua decorativa de espectro sombrio encapuzado, flutuando com o manto rasgado e esvoaçante e mãos esqueléticas estendidas, sobre uma base com fumaça; toda preta fosca, como na foto`
- Ambiente: `estante de colecionador com livros antigos de lombada lisa e velas, luz baixa e clima misterioso` · Escala: `o produto sobre uma mesa ao lado de uma caneca comum`
- Video (camera move): `…ao redor da estátua preta do espectro encapuzado sobre a estante; as chamas das velas tremulam suavemente e a luz baixa cria um clima misterioso…`

**Lamp shade / lit décor**
- O que é: `Luminária em forma de chapéu de bruxo falante grande: chapéu pontudo e amassado, cor marrom claro, com um rosto nas dobras; com a luz de LED acesa por dentro, os olhos e a boca brilham em luz amarela quente. Mostre apenas a luminária grande, sem o chapeuzinho pequeno, sem cachecol, sem garrafas, sem fio aparente e sem logotipos da foto original`
- Ambiente: `criado-mudo de um quarto à noite, com livros de lombada lisa, a luminária acesa iluminando o ambiente`
- Video: `Quarto à noite: a câmera de celular se aproxima devagar da luminária…; a luz amarela quente dos olhos e da boca pulsa suavemente e ilumina o ambiente. O chapéu não se mexe…`

**LED tealight décor (globe)**
- O que é: `Globo de neve decorativo: castelo de várias torres dentro de uma cúpula aberta, sobre base redonda com encaixe para vela de LED, tudo em plástico branco fosco; com a vela acesa, uma luz amarela quente ilumina o castelo por trás. A placa em relevo na frente da base deve ficar exatamente igual à da foto original`
- Ambiente: `mesa de sala à noite decorada para o Natal, com a vela de LED acesa dentro`
- Video: use the **gentle tilt** variant (a free rotation made the model invent a glass dome).
