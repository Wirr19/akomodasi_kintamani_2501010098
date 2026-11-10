# Laporan Akuisisi Data Akomodasi di Kecamatan Kintamani
Nama / NIM: I Putu Wira Astina Rasmawan / 2501010098 · Tanggal akses OSM: ISI · Data © OpenStreetMap contributors

## 1. Ringkasan dataset
- Total akomodasi: N (cap waktu basis OSM: ...)
- Tabel jumlah per jenis (dari sel "Per jenis") dan per desa (dari sel "Per desa").
- Catatan jenis yang dimasukkan dan alasannya: hotel, guest_house, hostel, motel, apartment, chalet. Villa di OSM umumnya bertag guest_house/chalet/apartment, sehingga villa tidak dapat dipisahkan dari jenis lain.
- Catatan: berapa % baris tanpa `desa`?

## 2. Peta sebaran
Sisipkan `reports/peta_sebaran.png` + tangkapan layar overpass-turbo. Atribusi: © OpenStreetMap contributors.

## 3. Uji kelengkapan
- Angka BPS: ISI (tahun, publikasi, tabel, halaman). Jika angka per kecamatan tidak ditemukan, jelaskan upaya pencarian (BPS Bangli, Satu Data Bali) dan pembanding alternatif.
- Kelengkapan = OSM ÷ BPS × 100% = ISI %.
- Perhatikan perbedaan definisi: BPS menghitung usaha akomodasi (termasuk homestay/pondok wisata/losmen), OSM menghitung objek bertag.
- Verifikasi 10 sampel (tabel dari docs/sampel_verifikasi.csv): benar/salah nama, jenis, lokasi; akurasi = x/10.

## 4. Masalah kualitas dan keputusan
Ringkas docs/qc_log.csv: duplikat, tanpa nama, koordinat di luar wilayah, kolom kosong. Tulis keputusan dan alasannya.

## 5. Refleksi (150–200 kata)
Mengapa OSM tidak boleh dianggap lengkap (kontributor relawan, bias area wisata/aksesibilitas, tag tidak seragam, tidak ada kewajiban pembaruan, definisi berbeda dari BPS) dan sumber tambahan untuk riset lanjutan (data perizinan OSS/DPMPTSP, Dinas Pariwisata Bangli, PHRI, survei lapangan, Google Places API dengan billing sendiri).

## Kendala
Catat jika ada kendala server Overpass (status 429/504) dan cara menanganinya.
