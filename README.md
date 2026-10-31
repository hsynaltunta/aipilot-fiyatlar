# AiPilot fiyat listesi

AiPilot uygulaması şarj ve akaryakıt fiyatlarını **doğrudan işletmeci/dağıtıcı sitelerinden
çekmez**; yalnızca bu depodaki tek dosyayı okur:

```
https://raw.githubusercontent.com/hsynaltunta/aipilot-fiyatlar/main/fiyatlar.json
```

Uygulama bu dosyayı **günde en çok bir kez** indirir, telefonda saklar; indiremezse son
kopyayı (yoksa kullanıcının Ayarlar'da elle girdiği fiyatları) kullanır.

## Biçim (`fiyatlar.json`)

| Alan | Açıklama |
|---|---|
| `guncellendi` | gg/aaaa-aa-gg, dosyanın son güncellenme tarihi |
| `sarj[]` | `{ad, ac, dc, dcHigh?, kontrol}` — işletmeci adı ve TL/kWh (KDV dahil). `dcHigh`: 100 kW üstü DC için ayrı fiyat (ops.) |
| `yakit{}` | `"<il plaka kodu>": {benzin, motorin}` — TL/L |

- `sarj` içindeki `ad`, istasyonun EPDK marka adıyla eşleştirilir (küçük harf, Türkçe harfler sadeleşir).
  Eşleşmeyen işletmeciler listedeki fiyatların ortancasıyla "(tahmini)" hesaplanır.
- Kullanıcının Ayarlar'da girdiği fiyat her zaman bu listenin önüne geçer.

## Güncelleme

Günde bir kez `fiyatlar.json` güncellenip bu depoya push edilir. Değerlerin kaynağı temiz
tutulmalı: elle girilmiş ya da izinli/halka açık resmi veri. Dosya elle düzenlenebilir;
`tools/fiyatlar.py` (ana uygulama deposunda) biçimi doğrular.
