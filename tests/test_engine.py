from chatbot import ChatbotEngine, load_themes


THEME = load_themes("themes")["energybot"]
BOT = ChatbotEngine(THEME, 0.45)


def test_normalisasi_kata_tidak_baku():
    assert "bagaimana" in BOT.explain("gmn cara hemat listrik")[0]["pattern"] or BOT.classify("gmn cara hemat listrik")[0]


def test_greeting():
    assert BOT.classify("Halo EnergyBot")[0] == "greeting"


def test_ac_spesifik_mengalahkan_tips_umum():
    assert BOT.classify("bagaimana cara menghemat listrik AC")[0] == "ac_saving_tips"


def test_perangkat():
    assert BOT.classify("televisi menggunakan banyak listrik?")[0] == "appliance_information"


def test_perbandingan():
    assert BOT.classify("mana lebih hemat kipas angin atau AC")[0] == "energy_comparison"


def test_salah_ketik_masih_dikenali():
    assert BOT.classify("bagaimna menghemat listrk")[0] == "energy_saving_tips"


def test_fallback_di_luar_domain():
    tag, score = BOT.classify("ceritakan tentang sepak bola")
    assert tag is None
    assert score < 0.45


def test_reply_memiliki_data_lengkap():
    result = BOT.reply("apa itu watt dan kwh")
    assert result["intent"] == "electricity_information"
    assert result["reply"]
    assert 0 <= result["score"] <= 1


def test_semua_intent_memiliki_pola_dan_respons():
    assert len(THEME["intents"]) == 14
    assert all(i["patterns"] and i["responses"] for i in THEME["intents"])
