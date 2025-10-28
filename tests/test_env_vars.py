import importlib
import os


def test_get_env_vars_discord_overrides(monkeypatch):
    monkeypatch.setenv("LEAGUE_ID", "123")
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://default.example/webhook")
    monkeypatch.setenv("DISCORD_WEBHOOK_URL_SCOREBOARD", "https://scoreboard.example/webhook")
    monkeypatch.setenv("DISCORD_WEBHOOK_URL_GET_TROPHIES", "https://trophies.example/webhook")

    env_vars = importlib.import_module("gamedaybot.espn.env_vars")
    importlib.reload(env_vars)

    data = env_vars.get_env_vars()

    overrides = data.get("discord_webhook_overrides", {})
    assert overrides["get_scoreboard_short"] == "https://scoreboard.example/webhook"
    assert overrides["get_trophies"] == "https://trophies.example/webhook"
    assert "get_close_scores" not in overrides


def test_get_env_vars_discord_overrides_absent(monkeypatch):
    for key in list(os.environ.keys()):
        if key.startswith("DISCORD_WEBHOOK_URL") or key in {"LEAGUE_ID"}:
            monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("LEAGUE_ID", "123")

    env_vars = importlib.import_module("gamedaybot.espn.env_vars")
    importlib.reload(env_vars)

    data = env_vars.get_env_vars()

    assert "discord_webhook_overrides" not in data
