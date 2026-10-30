# Verificação diária da NLG Store

O site (nlgstore.com) é publicado pela Netlify a partir deste repositório. Toda alteração enviada para a branch `main` vai para o ar em cerca de 1 minuto.

Os produtos ficam em `products.json`. Cada produto tem um `id` (código do produto na loja) e um `link`, que é o link de afiliado.

## Passo a passo da verificação

1. Abra o navegador integrado do Claude no computador do dono do canal (as ferramentas `Claude_Browser`). Os sites `meli.la`, `mercadolivre.com.br`, `link.amazon`, `amazon.com.br`, `s.click.aliexpress.com`, `pt.aliexpress.com`, `s.shopee.com.br` e `shopee.com.br` já estão liberados.
   Se o navegador não responder, o computador está desligado: pare, não altere nada e avise no resumo que a verificação de hoje não rodou.
2. Para cada produto de `products.json` com `"store"` igual a `"ml"`, `"amazon"`, `"ali"` ou `"shopee"`, em lotes de até 12 produtos por `browser_batch`:
   - `navigate` para o `link` do produto
   - `javascript_tool` com o conteúdo de `scripts/extract.js`
3. Junte as respostas em um arquivo JSON no formato `{"<id>": <resposta>, ...}`. Se um link der erro, use `null` para esse id.
4. Rode `python3 scripts/apply_check.py <arquivo>`. O script atualiza preços, preço antigo, foto e disponibilidade, e imprime um resumo.
5. Faça commit e push para `main` com a mensagem `Verificação diária AAAA-MM-DD`.
6. Mande o resumo impresso pelo script para o dono do canal, em português.

Produtos esgotados ou com anúncio pausado ficam com `"available": false` e somem do site. Eles voltam sozinhos quando ficarem disponíveis de novo. Não apague produtos do `products.json`.

## Adicionar produtos

Acrescente um objeto em `products` com: `id`, `name`, `cat`, `store`, `price`, `img`, `link`, `available: true`, e, se quiser, `oldPrice`, `coupon` e `tag`.
Os departamentos válidos para `cat` estão em `CATEGORIES` no `index.html`.

O campo `"featured": true` marca o produto que aparece em "Destaques de cada categoria". Se ele esgotar, o site mostra outro produto da mesma categoria automaticamente.

Links do AliExpress (`s.click.aliexpress.com/e/...`) são gerados no AliExpress Portals com o ID de rastreamento `nlgstore` e envio para o Brasil. Não monte esses links à mão.

Links da Shopee (`s.shopee.com.br/...`) são gerados em affiliate.shopee.com.br, em Oferta → Link personalizado, com Sub_id 1 = `nlgstore`. Não monte esses links à mão.
