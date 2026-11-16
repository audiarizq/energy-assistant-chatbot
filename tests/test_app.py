import pytest

from app import BASE_DIR, create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "energybot.db"),
        "ADMIN_KEY": "rahasia",
    })
    return app.test_client()


def test_halaman_utama(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.location.endswith("/chat/energybot")


def test_halaman_chat(client):
    assert client.get("/chat/energybot").status_code == 200


def test_database_default_mengarah_ke_folder_energybot():
    app = create_app({"TESTING": True})
    assert app.config["DATABASE"] == str(BASE_DIR / "chat_history.db")


def test_api_chat_berhasil(client):
    response = client.post("/api/chat", json={"theme": "energybot", "message": "cara menghemat listrik"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["intent"] == "energy_saving_tips"


def test_api_menolak_pesan_kosong(client):
    response = client.post("/api/chat", json={"theme": "energybot", "message": ""})
    assert response.status_code == 400


def test_api_menolak_tema_salah(client):
    response = client.post("/api/chat", json={"theme": "kampus", "message": "halo"})
    assert response.status_code == 400


def test_riwayat_dan_hapus(client):
    client.post("/api/chat", json={"theme": "energybot", "message": "halo"})
    rows = client.get("/api/history/energybot").get_json()
    assert len(rows) == 1
    assert rows[0]["sender"] == "user"
    assert client.delete("/api/history/energybot").get_json()["database_unchanged"] is True
    assert len(client.get("/api/history/energybot").get_json()) == 1


def test_dashboard_admin_tanpa_kunci(client):
    assert client.get("/chat/energybot/admin").status_code == 200
    assert client.get("/admin/energybot").status_code == 302


def test_api_stats_tanpa_kunci(client):
    assert client.get("/api/stats/energybot").status_code == 200


def test_hapus_seluruh_data_admin(client):
    client.post("/api/chat", json={"theme": "energybot", "message": "halo"})
    assert client.delete("/api/admin/history/energybot").get_json()["database_unchanged"] is False
    assert client.get("/api/stats/energybot").get_json() == []


def test_pesan_tetap_tersimpan_setelah_hapus_tampilan(client):
    client.post("/api/chat", json={"theme": "energybot", "message": "pertanyaan yang tidak dikenali"})
    client.delete("/api/history/energybot")
    rows = client.get("/api/history/energybot").get_json()
    assert len(rows) == 1
    assert rows[0]["text"] == "pertanyaan yang tidak dikenali"
