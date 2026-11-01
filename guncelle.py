#!/usr/bin/env python3
"""AiPilot fiyat listesi üreticisi: şarj (sarjharitasi.tr) + akaryakıt (Opet) → fiyatlar.json.

GitHub Actions'ta günde bir çalışır (.github/workflows/fiyat-guncelle.yml). Uygulama bu dosyayı
doğrudan değil, yalnızca üretilen fiyatlar.json'u GitHub raw adresinden okur.

Kullanım:
  python guncelle.py              # fiyatlar.json üret
  python guncelle.py --iller 34 6 # yalnızca bu illeri çek (deneme)
"""
import argparse, datetime, html as _html, json, re, sys, time, urllib.request

UA = "AiPilot/1.0 (+https://github.com/hsynaltunta/aipilot-fiyatlar; price aggregator; once daily)"
SARJ_URL = "https://sarjharitasi.tr/guncel-sarj-ucretleri/"
OPET_URL = "https://api.opet.com.tr/api/fuelprices/prices?ProvinceCode={il}&IncludeAllProducts=true"
# Türkiye plaka kodları 1..81
ILLER = list(range(1, 82))


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _f(s):
    try:
        return round(float(s.replace(",", ".")), 2)
    except (ValueError, AttributeError):
        return None


def sarj_cek():
    """sarjharitasi.tr 'Güncel Şarj Ücretleri' tablosu → [{ad, ac, dc, kontrol}] (TL/kWh, KDV dahil)."""
    doc = _get(SARJ_URL)
    out = []
    for row in doc.split("<tr data-brand-name=")[1:]:
        m = re.search(r'class="price-brand">([^<]*)<', row)
        if not m:
            continue
        ad = _html.unescape(m.group(1).strip())
        if not ad:
            continue
        acm = re.search(r'class="price-ac">\s*([\d.,]+)', row)
        dcm = re.search(r'class="price-dc">\s*([\d.,]+)', row)
        chkm = re.search(r'data-last-check="([^"]*)"', row)
        ac = _f(acm.group(1)) if acm else None
        dc = _f(dcm.group(1)) if dcm else None
        chk = chkm.group(1) if chkm else ""
        if ac is None and dc is None:
            continue
        rec = {"ad": ad}
        if ac is not None:
            rec["ac"] = ac
        if dc is not None:
            rec["dc"] = dc
        rec["kontrol"] = chk
        out.append(rec)
    return out


def _medyan(v):
    v = sorted(v)
    return v[len(v) // 2] if v else None


def yakit_il(il):
    """Opet ilin ilçe fiyatları → (benzin, motorin) ortanca; bulunamazsa None."""
    try:
        data = json.loads(_get(OPET_URL.format(il=il)))
    except Exception:
        return None
    benzin, motorin = [], []
    for d in data:
        prices = d.get("prices") or []
        mot = None
        for p in prices:
            amt = p.get("amount") or 0
            if amt <= 0:
                continue
            if p.get("productCode") == "A100":
                benzin.append(amt)
            elif mot is None and str(p.get("productName", "")).startswith("Motorin"):
                mot = amt
        if mot:
            motorin.append(mot)
    b, m = _medyan(benzin), _medyan(motorin)
    return (round(b, 2), round(m, 2)) if b and m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iller", nargs="*", type=int, default=ILLER)
    ap.add_argument("--cikti", default="fiyatlar.json")
    args = ap.parse_args()

    sarj = sarj_cek()
    if len(sarj) < 20:
        print(f"HATA: şarj listesi beklenenden kısa ({len(sarj)}); dosya güncellenmedi", file=sys.stderr)
        sys.exit(1)

    yakit = {}
    for il in args.iller:
        r = yakit_il(il)
        if r:
            yakit[str(il)] = {"benzin": r[0], "motorin": r[1]}
        time.sleep(0.3)  # kibar: saniyede ~3 istek

    out = {
        "guncellendi": datetime.date.today().isoformat(),
        "kaynak": "AiPilot fiyat listesi",
        "not": "Otomatik üretildi. Şarj: sarjharitasi.tr güncel şarj ücretleri (işletmeci TL/kWh, KDV dahil). "
               "Yakıt: Opet il bazlı pompa fiyatı ortancası (TL/L).",
        "sarj": sarj,
        "yakit": yakit,
    }
    with open(args.cikti, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"fiyatlar.json yazıldı • {len(sarj)} işletmeci • {len(yakit)} il • {out['guncellendi']}")


if __name__ == "__main__":
    main()
