import abc
import requests
import time
import base64
from typing import Optional, List, Dict, Any
from .config import APIConfig
from .utils import logger

class APIClient(abc.ABC):
    def __init__(self, config: APIConfig):
        self.config = config

    @abc.abstractmethod
    def generate_image(self, prompt: str, reference_images: List[Dict[str, str]], resolution: str = "4K") -> Optional[bytes]:
        pass

    @abc.abstractmethod
    def generate_text(self, prompt: str) -> Optional[str]:
        pass

    def _handle_image_response(self, response: requests.Response) -> Optional[bytes]:
        try:
            response.raise_for_status()
            data = response.json()
            if 'candidates' in data:
                for p in data['candidates'][0].get('content', {}).get('parts', []):
                    if 'inlineData' in p:
                        return base64.b64decode(p['inlineData'].get('data', ''))
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"API HTTP error: {e}")
            logger.error(f"Response content: {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Failed to parse API response: {e}")
            return None

    def _handle_text_response(self, response: requests.Response) -> Optional[str]:
        try:
            response.raise_for_status()
            data = response.json()
            if 'candidates' in data:
                parts = data['candidates'][0].get('content', {}).get('parts', [])
                if parts and 'text' in parts[0]:
                    return parts[0]['text']
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"API HTTP error: {e}")
            logger.error(f"Response content: {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API text request failed: {e}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Failed to parse API response: {e}")
            return None

class GoogleClient(APIClient):
    def _get_url(self):
        url = self.config.google_url
        key = self.config.google_key
        if not url or not key:
            return None
        if '?' not in url:
             return f"{url}?key={key}"
        return f"{url}&key={key}"

    def generate_image(self, prompt: str, reference_images: List[Dict[str, str]], resolution: str = "4K") -> Optional[bytes]:
        url = self._get_url()
        if not url:
            logger.error("Google API not configured")
            return None
        return self._make_image_request(url, prompt, reference_images, resolution)

    def generate_text(self, prompt: str) -> Optional[str]:
        url = self._get_url()
        if not url:
            logger.error("Google API not configured")
            return None
        return self._make_text_request(url, prompt)

    def _make_image_request(self, url: str, prompt: str, reference_images: List[Dict[str, str]], resolution: str) -> Optional[bytes]:
        parts = []
        for img in reference_images:
            parts.append({'inlineData': img})
        parts.append({'text': prompt})

        payload = {
            'contents': [{'parts': parts}],
            'generationConfig': {
                'responseModalities': ['IMAGE'],
                'imageConfig': {
                    'aspectRatio': '3:4',
                    'imageSize': resolution
                }
            }
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.config.timeout)
            return self._handle_image_response(response)
        except Exception as e:
             logger.error(f"Request exception: {e}")
             return None

    def _make_text_request(self, url: str, prompt: str) -> Optional[str]:
        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'responseModalities': ['TEXT']
            }
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.config.timeout)
            return self._handle_text_response(response)
        except Exception as e:
             logger.error(f"Request exception: {e}")
             return None

class NanoBananaClient(APIClient):
    def generate_image(self, prompt: str, reference_images: List[Dict[str, str]], resolution: str = "4K") -> Optional[bytes]:
        url = self.config.nanobanana_url
        key = self.config.nanobanana_key
        if not url or not key:
            logger.error("NanoBanana API not configured")
            return None
        return self._make_request(url, key, prompt, reference_images, is_image=True, resolution=resolution)

    def generate_text(self, prompt: str) -> Optional[str]:
        url = self.config.nanobanana_url
        key = self.config.nanobanana_key
        if not url or not key:
            logger.error("NanoBanana API not configured")
            return None
        # Note: Some providers might use different endpoints for text vs image,
        # but Gemini 3 Pro typically handles both on generateContent.
        # We assume NanoBanana mirrors this or user configured a compatible URL.
        return self._make_request(url, key, prompt, [], is_image=False)

    def _make_request(self, url: str, key: str, prompt: str, reference_images: List[Dict[str, str]], is_image: bool, resolution: str = "4K") -> Any:
        parts = []
        for img in reference_images:
            parts.append({'inlineData': img})
        parts.append({'text': prompt})

        payload = {
            'contents': [{'parts': parts}],
            'generationConfig': {
                'responseModalities': ['IMAGE'] if is_image else ['TEXT']
            }
        }

        if is_image:
             payload['generationConfig']['imageConfig'] = {
                'aspectRatio': '3:4',
                'imageSize': resolution
             }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {key}'
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.config.timeout)
            if is_image:
                return self._handle_image_response(response)
            else:
                return self._handle_text_response(response)
        except Exception as e:
             logger.error(f"Request exception: {e}")
             return None

def get_client(config: APIConfig) -> APIClient:
    """Factory function to create the appropriate API client."""
    if config.provider == 'google':
        return GoogleClient(config)
    elif config.provider == 'nanobanana':
        return NanoBananaClient(config)
    else:
        raise ValueError(f"Unknown API provider: '{config.provider}'. Valid options: 'google', 'nanobanana'")
