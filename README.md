# EnergyBot

Chatbot rule-based berbasis Flask untuk menghitung dan mengelola konsumsi energi listrik.

## Menjalankan

```powershell
cd "week 9"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Buka `http://127.0.0.1:5000`.

## Contoh pertanyaan

- `Hitung kipas 50 Watt selama 10 jam sehari`
- `Hitung biaya 100 kWh dengan tarif Rp1.500/kWh`
- `Hitung konsumsi AC saya` lalu jawab pertanyaan klarifikasi bot
- `Bagaimana cara menghemat listrik?`

Tarif default adalah Rp1.500/kWh. Nilai perhitungan bersifat estimasi; daya aktual perangkat dan komponen tagihan dapat berbeda.
