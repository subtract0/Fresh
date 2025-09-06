import requests
from typing import Dict, Any

class OpenAIUsageTracker:
    """
    Class to track the usage of OpenAI API.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.usage_url = "https://api.openai.com/v1/usage"

    def get_usage(self) -> Dict[str, Any]:
        """
        Get the usage of OpenAI API.
        """
        try:
            response = requests.get(self.usage_url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

    def _get_headers(self) -> Dict[str, str]:
        """
        Get the headers for OpenAI API request.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }