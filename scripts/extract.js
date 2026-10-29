// Roda na página do produto aberta a partir do link de afiliado (meli.la ou link.amazon).
// Retorna os dados que o scripts/apply_check.py usa para atualizar o products.json.
(() => {
  if (/amazon\./.test(location.hostname)) {
    const q = s => document.querySelector(s);
    const img = q("#landingImage");
    return {
      kind: "amazon",
      title: q("#productTitle")?.textContent.trim() || "",
      price: q("#corePrice_feature_div .a-offscreen, #corePriceDisplay_desktop_feature_div .a-offscreen, .priceToPay .a-offscreen")?.textContent || "",
      old: q(".basisPrice .a-offscreen")?.textContent || "",
      image: img?.getAttribute("data-old-hires") || img?.src || "",
      avail: q("#availability")?.innerText.trim().slice(0, 200) || "",
      url: location.href.split("?")[0]
    };
  }
  const og = p => document.querySelector(`meta[property="og:${p}"]`)?.content || "";
  const main = (document.querySelector("main") || document.body).innerText || "";
  const head = main.split(/\n\s*Para você\s*\n/)[0].slice(0, 1500);
  return { kind: "ml", title: og("title"), image: og("image"), head, url: location.href.split("?")[0] };
})()
