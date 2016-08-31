import requests
import json

from decimal import Decimal as D
from typing import Iterable, Any, Dict

from django.core.exceptions import ValidationError
from django.core.validators import validate_email, validate_ipv46_address

IPINTEL_URL = 'https://check.getipintel.net/check.php'
VALID_FLAGS = ['m', 'b', 'f', None]
PROBABILITY = D(0.99)
TIMEOUT = 5.00


class IPIntelException(ValueError):
    """Raised error when a GetIPIntel query responds with an error."""

    def __init__(self, message: str, *args: Iterable[Any]):
        self.message = message
        super().__init__(message, *args)


class IPIntel:
    def __init__(self, email: str, ip: str, flag: str = None):
        """Params:
        :param email: A valid email address to contact
        :param ip: A valid IPv4 or IPv6 IP Address to query.
        :param flag: A valid flag to url. Options: m, b, f or None
        """
        self.email = email
        self.ip = ip
        self.flag = flag
        self.format = 'json'

    def lookup(self) -> bool:
        """Attempts to determine if the given address is a possible proxy

        :return: True if the given address is a bad address, or exceeds
        the given probability
        """
        self._check_params()
        params = self._build_params()
        url = self._build_url(params)
        return self._send_request(url)

    def _send_request(self, url: str) -> bool:
        try:
            response = requests.get(url, timeout=TIMEOUT)
        except (requests.HTTPError, requests.Timeout):
            raise IPIntelException('Server don\'t response')

        if response.status_code != requests.codes.ok:
            msg = 'Server response {} code'.format(response.status_code)
            raise IPIntelException(msg)

        if response.status_code == 429:
            msg = 'Your exceed max query limit'
            raise IPIntelException(msg)

        content = json.loads(response.text)

        if content.get('status') == 'success':
            if self.flag == 'm':
                return bool(content.get('result'))
            else:
                return D(content.get('result')) < PROBABILITY
        elif content.get('status') == 'error':
            raise IPIntelException(content.get('message'))

        raise IPIntelException('Unknown response', content)

    def _build_params(self) -> Dict[str, str]:
        return {'ip': self.ip, 'email': self.email, 'format': self.format,
                'flag': self.flag}

    def _build_url(self, params: Dict[str, str]) -> str:
        url = '{}?ip={ip}&contact={email}&format={format}'
        url = url.format(IPINTEL_URL, **params)

        if self.flag:
            url += '&flag={}'.format(params.get('flag', 'b'))

        return url

    def _check_params(self):
        self._check_email()
        self._check_ip()
        self._check_flag()

    def _check_email(self):
        validate_email(self.email)

    def _check_flag(self):
        if self.flag not in VALID_FLAGS:
            raise ValidationError('Flag is not valid')

    def _check_ip(self):
        validate_ipv46_address(self.ip)
