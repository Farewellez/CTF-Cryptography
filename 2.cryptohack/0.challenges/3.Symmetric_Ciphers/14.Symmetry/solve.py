import requests

URL = "https://aes.cryptohack.org/symmetry"

class Remote:
    def __init__(self, choice):
        self.choice = choice
        self.base_url = URL
        self.session = requests.Session()

    def _getJson(self, endpoint):
        url = f"{self.base_url}/"