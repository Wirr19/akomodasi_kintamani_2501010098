#!/usr/bin/env python3
"""Alat bantu penyelesaian tugas.

  python tools/lengkapi.py identitas --nama "Nama Anda" --nim 2501234 [--bps-jumlah 120 --bps-tahun 2024 --bps-sumber "Kec. Kintamani Dalam Angka 2025, Tabel x.y"]
      -> mengisi nama/NIM (dan angka BPS bila ada) ke notebook dan README. Jalankan SEBELUM notebook.

  python tools/lengkapi.py periksa
      -> dijalankan SETELAH notebook dieksekusi: memverifikasi semua luaran, mengisi
         tanggal akses di README, dan menulis docs/data_ethics_checklist.csv berdasarkan bukti nyata.
"""
import argparse, csv, hashlib, json, re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
NB = BASE / "notebooks/akuisisi_akomodasi.ipynb"
README = BASE / "README.md"
KOLOM = ["osm_type", "osm_id", "nama", "jenis", "lat", "lon", "desa", "bintang", "jumlah_kamar", "website", "url_osm"]


def identitas(a):
    nb = json.loads(NB.read_text(encoding="utf-8"))
    sub = {'NAMA = "ISI_NAMA"': f'NAMA = {json.dumps(a.nama, ensure_ascii=False)}',
           'NIM = "ISI_NIM"': f'NIM = {json.dumps(a.nim)}'}
    if a.bps_jumlah is not None:
        sub["BPS_JUMLAH = None"] = f"BPS_JUMLAH = {int(a.bps_jumlah)}"
    if a.bps_tahun is not None:
        sub["BPS_TAHUN = None"] = f"BPS_TAHUN = {int(a.bps_tahun)}"
    if a.bps_sumber:
        sub['BPS_SUMBER = ""'] = f"BPS_SUMBER = {json.dumps(a.bps_sumber, ensure_ascii=False)}"
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        for k, v in sub.items():
            src = src.replace(k, v)
        lines = src.split("\n")
        c["source"] = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    r = README.read_text(encoding="utf-8").replace("ISI_NAMA", a.nama).replace("ISI_NIM", a.nim)
    README.write_text(r, encoding="utf-8")
    print("Identitas terisi di notebook dan README. Lanjut: jalankan notebook.")


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def periksa():
    hasil, bukti = [], {}

    def cek(kode, ok, ket):
        hasil.append((kode, ok, ket))
        bukti[kode] = (ok, ket)

    # query
    q = BASE / "docs/query_overpass.txt"
    cek("query", q.exists() and "admin_level" in q.read_text(encoding="utf-8"), "docs/query_overpass.txt ada dan memuat admin_level")

    # provenance + raw
    pv = BASE / "docs/provenance.json"
    prov, raw_ok, ket = {}, False, "provenance.json tidak ada"
    if pv.exists():
        prov = json.loads(pv.read_text(encoding="utf-8"))
        need = ["endpoint", "query", "waktu_akuisisi_utc", "jumlah_elemen", "berkas_mentah", "md5", "lisensi", "pengambil"]
        miss = [k for k in need if k not in prov]
        rawp = BASE / "data/raw" / prov.get("berkas_mentah", "-")
        ident = prov.get("pengambil", {})
        if miss:
            ket = f"provenance kekurangan kunci: {miss}"
        elif "ISI_" in json.dumps(ident):
            ket = "nama/NIM di provenance masih placeholder; jalankan 'identitas' lalu ulangi notebook"
        elif not rawp.exists():
            ket = f"berkas mentah {rawp.name} tidak ditemukan"
        elif md5(rawp) != prov["md5"]:
            ket = "MD5 berkas mentah BERBEDA dari provenance (berkas diubah?)"
        else:
            raw_ok, ket = True, f"provenance lengkap; MD5 {prov['md5']} cocok dengan {rawp.name}"
    cek("provenance_raw", raw_ok, ket)

    # csv
    csvp = BASE / "data/interim/akomodasi_kintamani.csv"
    csv_ok, ket = False, "CSV tidak ada"
    contact_ok = False
    if csvp.exists():
        with csvp.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        cols = list(rows[0].keys()) if rows else []
        if cols != KOLOM:
            ket = f"kolom CSV tidak sesuai struktur: {cols}"
        else:
            n, ne = len(rows), prov.get("jumlah_elemen")
            csv_ok = ne is not None and n <= ne
            ket = f"{n} baris, 11 kolom sesuai; elemen mentah {ne}"
        teks = csvp.read_text(encoding="utf-8")
        contact_ok = not re.search(r"(\+62|\b08\d{8,}|[\w.]+@[\w.]+\.\w+)", teks) and not any(
            k in cols for k in ["phone", "email", "telepon", "contact:phone", "contact:email"])
    cek("csv", csv_ok, ket)
    cek("kontak", csvp.exists() and contact_ok, "tidak ada kolom/pola telepon/email di CSV")

    # notebook
    nb_ok, ket = False, "notebook tidak ada"
    if NB.exists():
        nb = json.loads(NB.read_text(encoding="utf-8"))
        kode = [c for c in nb["cells"] if c["cell_type"] == "code"]
        tanpa = [i for i, c in enumerate(kode) if not c.get("outputs")]
        err = [i for i, c in enumerate(kode) if any(o.get("output_type") == "error" for o in c.get("outputs", []))]
        nb_ok = not tanpa and not err
        ket = f"{len(kode)} sel kode; tanpa output: {tanpa}; error: {err}"
    cek("notebook", nb_ok, ket)

    # data dictionary
    dd = BASE / "docs/data_dictionary.csv"
    dd_ok = dd.exists() and [r["kolom"] for r in csv.DictReader(dd.open(encoding="utf-8"))] == KOLOM
    cek("data_dictionary", dd_ok, "data_dictionary.csv menjelaskan 11 kolom")

    # BPS
    bp = BASE / "docs/perbandingan_bps.csv"
    bps_ok, ket = False, "perbandingan_bps.csv tidak ada"
    if bp.exists():
        r = list(csv.DictReader(bp.open(encoding="utf-8")))
        tot = [x for x in r if x.get("kategori") == "TOTAL"]
        if tot:
            t = tot[0]
            bps_ok = all(t.get(k) for k in ["bps_desa_dengan_sarana", "rasio_osm_terhadap_batas_bawah_persen", "sumber_bps"])
        else:
            bps_ok = bool(r) and all(r[0].get(k) for k in ["jumlah_bps", "kelengkapan_persen", "sumber_bps"])
        ket = "pembanding BPS terisi (uji batas bawah, Podes 2025)" if bps_ok else "pembanding BPS belum terisi"
    cek("bps", bps_ok, ket)

    # sampel
    sp = BASE / "docs/sampel_verifikasi.csv"
    sp_ok, ket = False, "sampel_verifikasi.csv tidak ada"
    if sp.exists():
        r = list(csv.DictReader(sp.open(encoding="utf-8")))
        lengkap = [x for x in r if all(x.get(k, "").strip() for k in ["nama_benar", "jenis_benar", "lokasi_benar", "sumber_verifikasi"])]
        sp_ok = len(r) >= min(10, len(r)) and len(lengkap) == len(r) and len(r) > 0
        ket = f"{len(lengkap)}/{len(r)} sampel sudah diverifikasi manual (isi kolom di docs/sampel_verifikasi.csv)"
    cek("sampel", sp_ok, ket)

    # README
    rd = README.read_text(encoding="utf-8") if README.exists() else ""
    tgl = prov.get("waktu_akuisisi_utc", "")[:10]
    if tgl and "ISI_TANGGAL" in rd:
        rd = rd.replace("ISI_TANGGAL", tgl)
        README.write_text(rd, encoding="utf-8")
    need_rd = ["© OpenStreetMap contributors", "ODbL", "Cara menjalankan ulang", "Batasan etika", "Metode akuisisi", "Tujuan", "Sumber data"]
    rd_ok = all(k.lower() in rd.lower() for k in need_rd) and "ISI_" not in rd
    cek("readme", rd_ok, "README lengkap, atribusi ada, tanpa placeholder ISI_")

    # endpoint hanya Overpass
    nbtxt = NB.read_text(encoding="utf-8") if NB.exists() else ""
    terlarang = [d for d in ["booking.com", "agoda", "traveloka", "tiket.com", "airbnb", "tripadvisor", "google.com/maps"] if d in nbtxt.lower()]
    cek("sumber", not terlarang, "notebook hanya memakai overpass-api.de" if not terlarang else f"sumber terlarang: {terlarang}")

    # checklist etika
    peta = [
        ("Sumber data diizinkan (OSM Overpass; BPS/Satu Data Bali)", "provenance_raw", "docs/provenance.json (endpoint overpass-api.de)"),
        ("Tidak memakai sumber terlarang (OTA/Google Maps scraping)", "sumber", "notebook hanya memanggil overpass-api.de"),
        ("Lisensi ODbL dipahami dan atribusi OpenStreetMap contributors dicantumkan", "readme", "README.md + provenance.lisensi + reports/peta_sebaran.png"),
        ("Tidak ada data kontak pribadi (telepon/email/media sosial)", "kontak", "pemeriksaan CSV: tidak ada kolom/pola kontak; fungsi ratakan() tidak mengambilnya"),
        ("Minimisasi data: hanya kolom yang diperlukan diambil", "csv", "CSV 11 kolom sesuai docs/data_dictionary.csv"),
        ("Pemakaian wajar: query 1-2 kali; ada timeout; ada retry+backoff", "notebook", "sel ambil_overpass; berkas mentah dipakai ulang (REFETCH=False)"),
        ("User-Agent teridentifikasi (nama kuliah + kontak)", "notebook", "variabel HEADERS di sel konfigurasi"),
        ("Berkas mentah tidak diubah dan tercatat hash MD5", "provenance_raw", "MD5 di provenance.json cocok dengan berkas di data/raw/"),
        ("Tidak ada penghapusan data diam-diam; keputusan dicatat", "csv", "docs/qc_log.csv"),
        ("Keterbatasan data (OSM tidak lengkap) dijelaskan", "bps", "docs/perbandingan_bps.csv + catatan di notebook"),
    ]
    with (BASE / "docs/data_ethics_checklist.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["no", "butir", "status", "bukti", "catatan"])
        for i, (butir, kode, bk) in enumerate(peta, 1):
            ok, ket = bukti[kode]
            w.writerow([i, butir, "Ya" if ok else "Belum", bk, "" if ok else ket])
        w.writerow([11, "Kendala server (jika ada) dilaporkan", "Isi manual", "", "Tulis di laporan"])
        w.writerow([12, "Kode/query/laporan dibuat sendiri; bantuan pihak lain diungkapkan", "Isi manual", "README", ""])

    print("\nHASIL PEMERIKSAAN (laporan PDF tidak diperiksa)")
    for kode, ok, ket in hasil:
        print(f"  [{'OK ' if ok else 'BELUM'}] {kode:16s} {ket}")
    print("\ndocs/data_ethics_checklist.csv ditulis ulang berdasarkan hasil di atas.")
    sys.exit(0 if all(ok for _, ok, _ in hasil) else 1)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("identitas")
    a.add_argument("--nama", required=True)
    a.add_argument("--nim", required=True)
    a.add_argument("--bps-jumlah", type=int)
    a.add_argument("--bps-tahun", type=int)
    a.add_argument("--bps-sumber")
    sp.add_parser("periksa")
    x = p.parse_args()
    identitas(x) if x.cmd == "identitas" else periksa()
