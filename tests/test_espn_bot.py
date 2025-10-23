import importlib
import types


def _reload_espn_bot():
    module = importlib.import_module("gamedaybot.espn.espn_bot")
    return importlib.reload(module)


def _patch_common_dependencies(monkeypatch, espn_bot_module, discord_messages):
    class DummyLeague:
        def __init__(self, *args, **kwargs):
            self.scoringPeriodId = 1
            self.settings = types.SimpleNamespace(matchup_periods=[1])
            self.current_week = 2

    class GroupMeStub:
        def __init__(self, *_args, **_kwargs):
            pass

        def send_message(self, _message):
            return None

    class SlackStub(GroupMeStub):
        pass

    class DiscordStub:
        def __init__(self, webhook_url):
            self.webhook_url = webhook_url

        def send_message(self, message):
            discord_messages.append((self.webhook_url, message))

    monkeypatch.setattr(espn_bot_module, "GroupMe", GroupMeStub)
    monkeypatch.setattr(espn_bot_module, "Slack", SlackStub)
    monkeypatch.setattr(espn_bot_module, "Discord", DiscordStub)
    monkeypatch.setattr(espn_bot_module, "League", DummyLeague)
    monkeypatch.setattr(espn_bot_module.util, "str_limit_check", lambda text, _limit: [text])
    monkeypatch.setattr(espn_bot_module.espn, "get_close_scores", lambda _league: "close scores")


def test_espn_bot_uses_discord_override(monkeypatch):
    monkeypatch.setenv("LEAGUE_ID", "123")
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://default.example/webhook")
    monkeypatch.setenv("DISCORD_WEBHOOK_URL_CLOSE_SCORES", "https://override.example/webhook")

    espn_bot_module = _reload_espn_bot()
    discord_messages = []
    _patch_common_dependencies(monkeypatch, espn_bot_module, discord_messages)

    espn_bot_module.espn_bot("get_close_scores")

    assert discord_messages == [("https://override.example/webhook", "close scores")]


def test_espn_bot_uses_default_discord_webhook(monkeypatch):
    monkeypatch.setenv("LEAGUE_ID", "123")
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://default.example/webhook")

    espn_bot_module = _reload_espn_bot()
    discord_messages = []
    _patch_common_dependencies(monkeypatch, espn_bot_module, discord_messages)

    espn_bot_module.espn_bot("get_close_scores")

    assert discord_messages == [("https://default.example/webhook", "close scores")]
