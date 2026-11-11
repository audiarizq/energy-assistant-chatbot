import re

from chatbot.energy_engine import EnergyBotEngine
from chatbot.engine import load_themes


def engine():
    theme = load_themes("themes")["energybot"]
    return EnergyBotEngine(theme)


def test_consumption_tc01():
    result = engine().reply("Hitung lampu 15 W selama 12 jam sehari")
    assert result["intent"] == "energy_consumption"
    assert "0.18 kWh" in result["reply"]
    assert "5.40 kWh" in result["reply"]


def test_cost_tc02():
    result = engine().reply("Hitung biaya 100 kWh dengan tarif Rp1.500/kWh")
    assert result["intent"] == "electricity_cost"
    assert "Rp150.000" in result["reply"]


def test_clarification_tc03():
    result = engine().reply("Hitung konsumsi AC saya")
    assert result["intent"] == "clarification"
    assert "Watt" in result["reply"]


def test_follow_up_calculation():
    bot = engine()
    context = {}
    bot.reply("Hitung konsumsi AC saya", context)
    result = bot.reply("500 Watt selama 8 jam sehari", context)
    assert result["intent"] == "energy_consumption"
    assert "4.00 kWh" in result["reply"]
