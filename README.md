# Akuisisi Data Akomodasi di Kecamatan Kintamani

Tugas Praktik BIFP-243 Akuisisi dan Manajemen Data. Pengambil: **I Putu Wira Astina Rasmawan (2501010098)**.

## Tujuan
Mengakuisisi data akomodasi (hotel, guest house, hostel, motel, apartment, chalet) di Kecamatan Kintamani, Kabupaten Bangli, dari OpenStreetMap; membentuk dataset tabular yang terdokumentasi; dan menilai kelengkapannya terhadap angka resmi BPS.

## Sumber data
| Sumber | Pemakaian | Tanggal akses |
|---|---|---|
| OpenStreetMap via Overpass API (`https://overpass-api.de/api/interpreter`) | Data akomodasi + batas kecamatan | 2026-11-10 (lihat `docs/provenance.json`) |
| BPS Kabupaten Bangli (*Kecamatan Kintamani Dalam Angka* / *Bangli Dalam Angka*) | Pembanding jumlah | 2026-11-10 |

**Atribusi: © OpenStreetMap contributors.** Data OSM berlisensi Open Database License (ODbL): https://www.openstreetmap.org/copyright

## Metode akuisisi
1. Query Overpass QL (`docs/query_overpass.txt`) mengambil `nwr` dengan `tourism` ∈ {hotel, guest_house, hostel, motel, apartment, chalet} di area `Kintamani` (`admin_level=6`); `out center tags`.
2. Python `requests` (POST, timeout 120 s, retry 4x dengan exponential backoff, penanganan 429/504).
3. Respons mentah disimpan utuh di `data/raw/` dan dicatat hash MD5-nya di `docs/provenance.json`.
4. Diratakan menjadi `data/interim/akomodasi_kintamani.csv`; pemeriksaan kualitas dicatat di `docs/qc_log.csv`.

## Batasan etika
- Tidak ada scraping OTA/platform pemesanan atau Google Maps.
- Tidak mengambil nomor telepon, email, atau akun media sosial (minimisasi data).
- Pemakaian wajar: query dijalankan satu atau dua kali; berkas mentah dipakai ulang.
- Berkas `data/raw/` tidak diubah setelah disimpan.
- Data OSM diisi relawan dan tidak lengkap; lihat laporan.

## Cara menjalankan ulang
Cara cepat (Linux/macOS/Git Bash):
```bash
./run_all.sh "Nama Anda" NIM [BPS_JUMLAH BPS_TAHUN "BPS_SUMBER"]
```
Atau manual:
```bash
pip install -r requirements.txt
python tools/lengkapi.py identitas --nama "Nama Anda" --nim NIM
cd notebooks && jupyter nbconvert --to notebook --execute --inplace akuisisi_akomodasi.ipynb && cd ..
python tools/lengkapi.py periksa
```
Notebook memakai berkas mentah terbaru di `data/raw/` bila ada. Untuk mengambil ulang, set `REFETCH = True` pada sel konfigurasi (gunakan seperlunya).

## Struktur
Lihat bagian 7 lembar tugas. Dataset: `data/interim/akomodasi_kintamani.csv`; kamus data: `docs/data_dictionary.csv`.

© OpenStreetMap contributors
