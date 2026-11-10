#!/usr/bin/env python3
"""Patch perbandingan BPS: jalankan SEKALI dari folder utama repository.
   python patch_bps.py
Mengubah (1) sel BPS di notebook dan (2) pemeriksaan BPS di tools/lengkapi.py."""
import json, re
from pathlib import Path

BASE = Path(__file__).resolve().parent
NB = BASE / "notebooks/akuisisi_akomodasi.ipynb"
LK = BASE / "tools/lengkapi.py"

NEW_CELL = '''# ===== PEMBANDING BPS (Podes 2025) =====
# Tabel 6.1.1 BPS = jumlah DESA yang memiliki sarana akomodasi, BUKAN jumlah usaha.
# Karena itu angkanya dipakai sebagai BATAS BAWAH (minimal 1 usaha per desa), bukan penyebut kelengkapan.
BPS_TAHUN = 2025
BPS_SUMBER = ("Kecamatan Kintamani Dalam Angka 2026, Tabel 6.1.1 hal. 71 (PDF hal. 95); "
              "sumber data BPS Podes 2025; angka = jumlah desa dengan sarana akomodasi")
BPS_DESA = {"Hotel": 4, "Penginapan": 12}
# Asumsi pemetaan jenis OSM -> kategori BPS (jelaskan di laporan):
PEMETAAN = {
    "Hotel": ["hotel"],
    "Penginapan": ["guest_house", "hostel", "motel", "apartment", "chalet"],
}
# =========================================

baris = []
for kat, jenis_osm in PEMETAAN.items():
    sub = akomodasi[akomodasi["jenis"].isin(jenis_osm)]
    batas = BPS_DESA[kat]
    baris.append({
        "kategori": kat, "jenis_osm": "+".join(jenis_osm),
        "jumlah_osm": len(sub), "desa_osm_terisi": int(sub["desa"].dropna().nunique()),
        "objek_osm_tanpa_desa": int(sub["desa"].isna().sum()),
        "bps_desa_dengan_sarana": batas,
        "rasio_osm_terhadap_batas_bawah_persen": round(len(sub) / batas * 100, 1),
        "uji_batas_bawah": "Lolos" if len(sub) >= batas else "TIDAK lolos",
    })
total_osm = sum(b["jumlah_osm"] for b in baris)
total_bps = sum(b["bps_desa_dengan_sarana"] for b in baris)
baris.append({
    "kategori": "TOTAL", "jenis_osm": "semua",
    "jumlah_osm": total_osm,
    "desa_osm_terisi": int(akomodasi["desa"].dropna().nunique()),
    "objek_osm_tanpa_desa": int(akomodasi["desa"].isna().sum()),
    "bps_desa_dengan_sarana": total_bps,
    "rasio_osm_terhadap_batas_bawah_persen": round(total_osm / total_bps * 100, 1),
    "uji_batas_bawah": "Lolos" if total_osm >= total_bps else "TIDAK lolos",
})
hasil_bps = pd.DataFrame(baris)
hasil_bps["tahun_bps"] = BPS_TAHUN
hasil_bps["sumber_bps"] = BPS_SUMBER
hasil_bps["tanggal_akses_osm"] = prov["waktu_akuisisi_utc"]
hasil_bps.to_csv(DOCS / "perbandingan_bps.csv", index=False, encoding="utf-8")

print("CATATAN: ini uji batas bawah, BUKAN persentase kelengkapan (BPS tidak memuat jumlah usaha).")
print("Rasio > 100% berarti OSM memuat lebih banyak objek daripada jumlah desa ber-akomodasi menurut BPS.")
hasil_bps.drop(columns=["sumber_bps", "tanggal_akses_osm"])
'''

NEW_CHECK = '''        tot = [x for x in r if x.get("kategori") == "TOTAL"]
        if tot:
            t = tot[0]
            bps_ok = all(t.get(k) for k in ["bps_desa_dengan_sarana", "rasio_osm_terhadap_batas_bawah_persen", "sumber_bps"])
        else:
            bps_ok = bool(r) and all(r[0].get(k) for k in ["jumlah_bps", "kelengkapan_persen", "sumber_bps"])
        ket = "pembanding BPS terisi (uji batas bawah, Podes 2025)" if bps_ok else "pembanding BPS belum terisi"
'''

# 1) notebook
nb = json.loads(NB.read_text(encoding="utf-8"))
ganti = 0
for c in nb["cells"]:
    if c["cell_type"] == "code" and "BPS_JUMLAH" in "".join(c["source"]):
        lines = NEW_CELL.rstrip("\n").split("\n")
        c["source"] = [l + "\n" for l in lines[:-1]] + [lines[-1]]
        c["outputs"], c["execution_count"] = [], None
        ganti += 1
assert ganti == 1, f"Sel BPS tidak ditemukan/ganda ({ganti}); patch dibatalkan"
NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("Notebook: sel BPS diganti")

# 2) tools/lengkapi.py
src = LK.read_text(encoding="utf-8")
pola = re.compile(r"        bps_ok = bool\(r\) and.*?(?=\n    cek\(\"bps\")", re.S)
assert pola.search(src), "Blok BPS di lengkapi.py tidak ditemukan; patch dibatalkan"
src = pola.sub(lambda m: NEW_CHECK.rstrip("\n"), src, count=1)
LK.write_text(src, encoding="utf-8")
print("tools/lengkapi.py: pemeriksaan BPS diganti")
print("\nSelanjutnya:\n  cd notebooks\n  jupyter nbconvert --to notebook --execute --inplace akuisisi_akomodasi.ipynb\n  cd ..\n  python tools/lengkapi.py periksa")
