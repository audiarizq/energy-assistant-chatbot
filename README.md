# EnergyBot

EnergyBot adalah chatbot rule-based berbahasa Indonesia untuk informasi dan edukasi penghematan energi listrik rumah tangga.

## Menjalankan

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
$env:ADMIN_KEY="admin123"
python app.py
```

Buka `http://127.0.0.1:5000` untuk langsung masuk ke chat EnergyBot. Dashboard admin tersedia di `http://127.0.0.1:5000/chat/energybot/admin`.

Pertanyaan pengguna yang dikenali maupun tidak dikenali disimpan ke SQLite untuk visualisasi dashboard. Riwayat lengkap percakapan, termasuk jawaban bot, disimpan di browser menggunakan `localStorage` agar tetap ada saat halaman dibuka kembali atau dashboard admin diakses. Tombol **Hapus riwayat** menghapus riwayat browser dan tampilan pengguna; data database tetap ada. Penghapusan database hanya tersedia dari tombol **Hapus seluruh data** di dashboard admin.

## Pengujian dan evaluasi

```powershell
pytest -v
python evaluate.py --tema energybot
python evaluate.py --tema energybot --sweep
python cli.py --debug
```

Engine menggunakan praproses bahasa Indonesia dan skor gabungan Jaccard 40%, fuzzy 30%, serta cakupan 30%, dengan threshold bawaan 0,45. Sistem tidak menghitung konsumsi kWh, biaya, atau tagihan listrik.
