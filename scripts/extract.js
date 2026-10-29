// Roda na página do Mercado Livre aberta a partir de um link meli.la.
// Retorna os dados que o scripts/apply_check.py usa para atualizar o products.json.
(() => {
  const og = p => document.querySelector(`meta[property="og:${p}"]`)?.content || "";
  const main = (document.querySelector("main") || document.body).innerText || "";
  const head = main.split(/\n\s*Para você\s*\n/)[0].slice(0, 1500);
  return { title: og("title"), image: og("image"), head, url: location.href.split("?")[0] };
})()
