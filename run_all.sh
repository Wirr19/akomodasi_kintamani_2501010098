#!/usr/bin/env bash
# Pemakaian: ./run_all.sh "Nama Anda" NIM [BPS_JUMLAH BPS_TAHUN "BPS_SUMBER"]
set -e
cd "$(dirname "$0")"
[ -n "$2" ] || { echo "Pemakaian: ./run_all.sh \"Nama\" NIM [BPS_JUMLAH BPS_TAHUN \"BPS_SUMBER\"]"; exit 1; }
EXTRA=()
[ -n "$3" ] && EXTRA=(--bps-jumlah "$3" --bps-tahun "$4" --bps-sumber "$5")
pip install -q -r requirements.txt
python tools/lengkapi.py identitas --nama "$1" --nim "$2" "${EXTRA[@]}"
(cd notebooks && jupyter nbconvert --to notebook --execute --inplace akuisisi_akomodasi.ipynb)
python tools/lengkapi.py periksa || true
echo "Selanjutnya: isi docs/sampel_verifikasi.csv (10 sampel), jalankan ulang './run_all.sh' hanya jika perlu, lalu ganti nama folder dan push."
