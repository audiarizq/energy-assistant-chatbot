"""Mesin khusus EnergyBot: rule-based, ekstraksi angka, dan perhitungan energi."""
import re

from .engine import ChatbotEngine

DEFAULT_TARIFF = 1500


def _number(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def rupiah(value: float) -> str:
    return "Rp" + f"{round(value):,}".replace(",", ".")


class EnergyBotEngine(ChatbotEngine):
    """Chatbot rule-based dengan fungsi hitung yang deterministik."""

    def extract(self, message: str) -> dict:
        text = message.lower()
        result = {}
        watt = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:watt|wat|w)\b", text)
        hours = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:jam|hour|hours)\b", text)
        days = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:hari|days)\b", text)
        kwh = re.search(r"(\d+(?:[.,]\d+)?)\s*kwh\b", text)
        tariff = re.search(r"(?:rp\s*|tarif\s*(?:listrik)?\s*(?:rp)?\s*)(\d+(?:[.,]\d+)?)", text)
        percent = re.search(r"(\d+(?:[.,]\d+)?)\s*%", text)
        if watt: result["watt"] = _number(watt.group(1))
        if hours: result["hours"] = _number(hours.group(1))
        if days: result["days"] = _number(days.group(1))
        if kwh: result["kwh"] = _number(kwh.group(1))
        if tariff: result["tariff"] = _number(tariff.group(1))
        if percent: result["target"] = _number(percent.group(1))
        for device in ("ac", "kipas", "lampu", "kulkas", "televisi", "tv", "mesin cuci", "setrika", "komputer"):
            if device in text:
                result["device"] = device
                break
        return result

    def _consumption(self, data: dict) -> str:
        daily = data["watt"] * data["hours"] / 1000
        days = data.get("days", 30)
        monthly = daily * days
        device = data.get("device", "perangkat")
        return (f"{device.title()} menggunakan sekitar {daily:.2f} kWh per hari. "
                f"Dengan asumsi {days:g} hari, konsumsi bulanannya sekitar {monthly:.2f} kWh.")

    def _cost(self, data: dict) -> str:
        tariff = data.get("tariff", DEFAULT_TARIFF)
        cost = data["kwh"] * tariff
        return (f"Estimasi biaya energi = {data['kwh']:.2f} kWh x {rupiah(tariff)}/kWh "
                f"= {rupiah(cost)}. Nilai ini adalah estimasi biaya energi, bukan jaminan tagihan akhir.")

    def reply(self, message: str, context: dict | None = None) -> dict:
        context = context if context is not None else {}
        data = self.extract(message)

        # Menyelesaikan permintaan yang sebelumnya menunggu data tambahan.
        if context.get("pending"):
            pending = context["pending"]
            merged = {**context.get("data", {}), **data}
            needed = {"consumption": ("watt", "hours"), "cost": ("kwh",), "comparison": ()}.get(pending, ())
            missing = [key for key in needed if key not in merged]
            if not missing:
                context.clear()
                if pending == "consumption":
                    return {"reply": self._consumption(merged), "intent": "energy_consumption", "score": 1.0}
                if pending == "cost":
                    return {"reply": self._cost(merged), "intent": "electricity_cost", "score": 1.0}
            context["data"] = merged

        tag, score = self.classify(message)
        lower = message.lower()
        # Angka dan satuan merupakan sinyal kuat meskipun kalimatnya tidak
        # sama persis dengan training phrase di JSON.
        if "watt" in data and "hours" in data and any(word in lower for word in ("hitung", "konsumsi", "listrik")):
            tag, score = "energy_consumption", 1.0
        elif "kwh" in data and any(word in lower for word in ("biaya", "tarif", "hitung")):
            tag, score = "electricity_cost", 1.0
        if tag == "energy_consumption":
            if "watt" not in data or "hours" not in data:
                context.update(pending="consumption", data=data)
                return {"reply": "Saya membutuhkan daya perangkat dalam Watt dan lama penggunaan dalam jam per hari.", "intent": "clarification", "score": 1.0}
            context.clear()
            return {"reply": self._consumption(data), "intent": tag, "score": score}

        if tag == "electricity_cost":
            if "kwh" not in data:
                context.update(pending="cost", data=data)
                return {"reply": "Masukkan konsumsi energi dalam kWh. Tarif default saya adalah Rp1.500/kWh dan dapat diubah.", "intent": "clarification", "score": 1.0}
            context.clear()
            return {"reply": self._cost(data), "intent": tag, "score": score}

        if tag == "energy_comparison" and len(re.findall(r"\d+(?:[.,]\d+)?\s*(?:watt|w)\b", message.lower())) >= 2:
            values = re.findall(r"(\d+(?:[.,]\d+)?)\s*(?:watt|w)\b[^\d]{0,35}(\d+(?:[.,]\d+)?)\s*(?:jam|hour)", message.lower())
            if len(values) >= 2:
                rows = []
                for index, (watt, hours) in enumerate(values[:2], 1):
                    rows.append((index, _number(watt) * _number(hours) / 1000))
                rows.sort(key=lambda item: item[1], reverse=True)
                return {"reply": f"Perbandingan konsumsi: Perangkat 1 {rows[0][1]:.2f} kWh/hari dan perangkat 2 {rows[1][1]:.2f} kWh/hari. Perangkat {rows[0][0]} lebih boros berdasarkan data yang diberikan.", "intent": tag, "score": score}

        if tag in {"energy_analysis", "saving_recommendation"}:
            return {"reply": "Untuk analisis, kirim daftar perangkat beserta daya (Watt) dan durasi penggunaan per hari. Saya akan menghitung total, kontribusi, dan perangkat paling boros.", "intent": tag, "score": score}

        result = super().reply(message)
        return result
