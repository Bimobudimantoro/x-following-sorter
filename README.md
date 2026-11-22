# X Following Sorter

**Sortir otomatis daftar following X/Twitter ke dalam 14 kategori.**

Auto-detect dari username, nama, dan bio. Hasil: HTML + CSV per kategori. Dilengkapi tool review manual untuk akun yang tidak terdeteksi.

---

## Kategori

| Kategori | Keyword Utama |
|---|---|
| 🪙 Crypto / Web3 | bitcoin, ethereum, defi, onchain, layer2, dex, web3 |
| 🎭 Memecoin / Caller | pepe, doge, memecoin, alpha call, 100x |
| 🪂 Airdrop / Hunter | airdrop, farming, zksync, starknet, retrodrop |
| 🔞 NSFW / Porn | onlyfans, pasutri, swing, alter, bokep, vcs |
| 🎨 NFT | nft, opensea, punk, azuki, blur |
| 💻 Dev / Tech | developer, engineer, open source, AI |
| 📰 News / Media | journalist, breaking, coindesk |
| 🤖 Bot | bot, automated, auto-follow |
| 🎮 Gaming | gamer, esports, valorant, steam |
| 📈 Trading / Finance | trader, invest, stock, perps, technical analysis |
| 🎵 Music / Entertainment | musician, singer, spotify, actor |
| 🏛️ Government / Politics | president, politician, government |
| 🏀 Sports | football, basketball, nba, ufc |
| 📚 Education / Science | professor, researcher, phd |

---

## Usage

### 1. Export following list

Gunakan [X Following Scraper](https://github.com/Bimobudimantoro/x-following-scraper) untuk export CSV dari X.

### 2. Auto-sort

```bash
python3 sorter.py following_xxx_FINAL.csv
```

Output:
- `following_xxx_FINAL_sorted.html` — tabel per kategori (buka di browser, dark mode)
- `following_xxx_FINAL_sorted/` — satu CSV per kategori

### 3. Manual review (opsional)

Untuk akun yang belum terdeteksi:

```bash
python3 manual.py following_xxx_FINAL_sorted/Uncategorized.csv
```

Pilih kategori dengan keyboard (`1`-`9`, `a`-`z`), `s` untuk skip, `u` untuk undo, `q` untuk simpan.

Hasil tersimpan di `following_xxx_FINAL_sorted/manual_reviewed/`.

---

## Custom Kategori

Edit `categories.toml` untuk menambah/mengubah keyword. Format:

```toml
[[categories]]
label = "🎯 Kategori Baru"
color = "#ff0000"
keywords = [
    "(?i)keyword1|keyword2",
    "(?i)\\bkata\\b.*penting",
]
```

Regex otomatis case-insensitive. Dicocokkan ke `screen_name + name + bio`.

---

## Requirements

- Python 3.11+ (pakai `tomllib` bawaan)
- Atau Python 3.10 dengan `pip install tomli`

---

## Sample Output

Dari 5,174 akun following — hasil auto-sort:

```
🪙 Crypto / Web3         1,754  ████████████████████████████████
📈 Trading / Finance       665  ███████████████
💻 Dev / Tech              232  ██████
🏛️ Government / Politics  207  █████
🎭 Memecoin / Caller       188  █████
🪂 Airdrop / Hunter        188  █████
🔞 NSFW / Porn             184  █████
🎨 NFT                     182  █████
📰 News / Media            142  ████
🏀 Sports                  103  ███
📚 Education / Science      97  ███
🎮 Gaming                   96  ███
🎵 Music / Entertainment    70  ██
🤖 Bot / Automated          34  █

🏁 4,142 classified, 2,435 uncategorized (80% coverage)
```

2,435 uncategorized mayoritas bio kosong atau sangat pendek — bisa di-review dengan `manual.py`.

---

## License

MIT — pakai, fork, tambahin kategori sendiri. Stars ⭐ appreciated.

---

**Dibuat untuk menemani [X Following Scraper](https://github.com/Bimobudimantoro/x-following-scraper).**