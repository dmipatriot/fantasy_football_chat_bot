import requests
import json
import logging


def _normalize_report_name(report_name):
    if report_name is None:
        return ""
    return str(report_name).strip().lower()


def get_webhook_for_report(report_name, default_webhook, report_webhooks=None):
    """Return the webhook URL configured for a specific report type.

    Parameters
    ----------
    report_name : str
        The identifier for the report being sent (for example, a function name
        like ``"get_power_rankings"``).
    default_webhook : str
        The default webhook URL to use when a specific report override is not
        configured.
    report_webhooks : Dict[str, str], optional
        A dictionary mapping report identifiers to webhook URLs. Keys are
        compared in a case-insensitive manner.

    Returns
    -------
    str
        The webhook URL that should receive the report. If no report-specific
        webhook is configured, the ``default_webhook`` value is returned.
    """

    if not report_webhooks:
        return default_webhook

    normalized_report = _normalize_report_name(report_name)

    for name, url in report_webhooks.items():
        if _normalize_report_name(name) == normalized_report:
            return url

    # Allow for a catch-all channel via the key "default"
    if "default" in report_webhooks:
        return report_webhooks["default"]

    return default_webhook

logger = logging.getLogger(__name__)


class DiscordException(Exception):
    pass


class Discord(object):
    """
    A class used to send messages to a Discord channel through a webhook.

    Parameters
    ----------
    webhook_url : str
        The URL of the Discord webhook to send messages to.

    Attributes
    ----------
    webhook_url : str
        The URL of the Discord webhook to send messages to.

    Methods
    -------
    send_message(text: str)
        Sends a message to the Discord channel.
    """

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def __repr__(self):
        return "Discord Webhook Url(%s)" % self.webhook_url

    def send_message(self, text):
        """
        Sends a message to the Discord channel.

        Parameters
        ----------
        text : str
            The message to be sent to the Discord channel.

        Returns
        -------
        r : requests.Response
            The response object of the POST request.

        Raises
        ------
        DiscordException
            If there is an error with the POST request.
        """

        message = "```{0}```".format(text)
        template = {
            "content": message  # limit 3000 chars
        }

        headers = {'content-type': 'application/json'}

        if self.webhook_url not in (1, "1", ''):
            r = requests.post(self.webhook_url,
                              data=json.dumps(template), headers=headers)

            if r.status_code != 204:
                print(r.content)
                logger.error(r.content)
                raise DiscordException(r.content)

            return r
