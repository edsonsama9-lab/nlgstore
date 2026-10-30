#!/usr/bin/env python3
"""Aplica o resultado da verificação diária ao products.json.

Uso:  python3 scripts/apply_check.py resultados.json
O arquivo de resultados é um objeto {"<id do link meli.la>": <retorno do extract.js>, ...}.
Um id que falhou ao abrir pode vir com o valor null: o produto fica como está.
Imprime um resumo em português do que mudou.
"""
import json, re, sys
from datetime import datetime, timezone, timedelta

ROOT = __file__.rsplit("/scripts/", 1)[0]
PRODUCTS = f"{ROOT}/products.json"
UNAVAILABLE = re.compile(r"pausad|indispon|esgotad|sem estoque|finalizad|não está disponível", re.I)


def money(txt):
    """'1.234,56' ou '229' -> float"""
    return float(txt.replace(".", "").replace(",", "."))


def parse_amazon(res):
    if not res.get("title"):
        return None
    if not res.get("price") or re.search(r"não disponível|indisponível", res.get("avail") or "", re.I):
        return (False, None, None, None)
    num = lambda t: money(re.sub(r"[^\d.,]", "", t))
    price = num(res["price"])
    old = num(res["old"]) if res.get("old") else None
    if old and old <= price * 1.01:
        old = None
    img = res.get("image") or None
    if img:
        img = re.sub(r"\._[^/]*_\.(jpg|png)$", r"._AC_SL500_.\1", img)
    return (True, price, old, img)


def parse_ali(res):
    if not res.get("title"):
        return None
    if res.get("soldout") or not res.get("price"):
        return (False, None, None, None)
    num = lambda t: money(re.sub(r"[^\d.,]", "", t))
    price = num(res["price"])
    old = num(res["old"]) if res.get("old") else None
    if old and old <= price * 1.01:
        old = None
    img = res.get("image") or None
    if img:
        ext = img.rsplit(".", 1)[-1]
        img = f"{img}_480x480.{ext}"
    return (True, price, old, img)


def parse(res):
    """Devolve (disponível, preço, preço_antigo, imagem) ou None se não deu para ler."""
    if not res:
        return None
    if res.get("kind") == "amazon":
        return parse_amazon(res)
    if res.get("kind") == "ali":
        return parse_ali(res)
    if res.get("kind") == "shopee":
        r = parse_ali({**res, "image": None})  # mesmo formato de preço; mantém a foto atual
        return r
    title = res.get("title") or ""
    head = re.sub(r"\s+", " ", res.get("head") or "")
    if UNAVAILABLE.search(head) or (not title and "R$" not in head):
        return (False, None, None, None)
    m = re.search(r"- R\$ ([\d.]+(?:,\d{2})?)\s*$", title)
    if not m:
        return None
    price = money(m.group(1))
    old = None
    if re.search(r"\d+% OFF", head):
        amounts = [money(a + ("," + c if c else "")) for a, c in
                   re.findall(r"R\$ ?([\d.]+)(?: ?, ?(\d{2}))?", head)]
        bigger = [a for a in amounts[:3] if a > price * 1.01]
        if bigger:
            old = bigger[0]
    img = res.get("image") or None
    if img:
        img = re.sub(r"-[A-Z]\.webp$", "-O.webp", img)
    return (True, price, old, img)


def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    results = json.load(open(sys.argv[1], encoding="utf-8"))
    data = json.load(open(PRODUCTS, encoding="utf-8"))
    changes, gone, back, failed = [], [], [], []
    for p in data["products"]:
        if p["id"] not in results:
            continue
        r = parse(results[p["id"]])
        if r is None:
            failed.append(p["name"])
            continue
        ok, price, old, img = r
        if not ok:
            if p.get("available", True):
                gone.append(p["name"])
            p["available"] = False
            continue
        if not p.get("available", True):
            back.append(p["name"])
        p["available"] = True
        if abs(price - p["price"]) >= 0.01:
            changes.append(f"{p['name']}: {brl(p['price'])} → {brl(price)}")
            p["price"] = price
        if old:
            p["oldPrice"] = old
        elif "oldPrice" in p and p["oldPrice"] <= price:
            p.pop("oldPrice")
        if img:
            p["img"] = img
    data["updatedAt"] = datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec="minutes")
    json.dump(data, open(PRODUCTS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    total = sum(1 for p in data["products"] if p.get("available", True))
    print(f"Produtos à venda no site: {total} de {len(data['products'])}")
    print(f"Preços alterados: {len(changes)}")
    for c in changes:
        print(f"  - {c}")
    if gone:
        print(f"Esgotados ou pausados (escondidos do site): {len(gone)}")
        for n in gone:
            print(f"  - {n}")
    if back:
        print(f"Voltaram ao estoque: {len(back)}")
        for n in back:
            print(f"  - {n}")
    if failed:
        print(f"Não foi possível ler (mantidos como estavam): {len(failed)}")
        for n in failed:
            print(f"  - {n}")


if __name__ == "__main__":
    main()
