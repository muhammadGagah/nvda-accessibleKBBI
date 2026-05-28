import json
import logging
from urllib import request, error, parse
from typing import Any
from .models import KBBIResult, Entry, Definition, Label

API_BASE_URL = "https://kbbi.raf555.dev/api/v1"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AccessibleKBBI/1.0"


class KBBIClient:
	"""
	Client for fetching definitions from the KBBI API.
	"""

	def __init__(self):
		"""
		Initializes the KBBIClient.
		"""
		super().__init__()
		self.timeout = 15

	def _fetch(self, url: str) -> dict[str, Any] | None:
		"""
		Makes an HTTP GET request to the given URL and parses the JSON response.

		:param url: The API endpoint URL to fetch.
		:type url: str
		:return: A dictionary containing the JSON response, or None if the request fails.
		:rtype: dict[str, Any] | None
		:raises ValueError: If the API returns a 404 (Not Found).
		:raises ConnectionError: If there's a network or server error.
		"""
		req = request.Request(url)
		req.add_header("User-Agent", USER_AGENT)
		try:
			with request.urlopen(req, timeout=self.timeout) as response:
				if response.getcode() == 200:
					return json.loads(response.read().decode("utf-8"))
		except error.HTTPError as e:
			logging.warning(f"KBBI API HTTP Error: {e.code} for {url}")
			if e.code == 404:
				raise ValueError("Entri tidak ditemukan.")
			raise ConnectionError(f"Gagal menghubungi server: {e.code}")
		except Exception as e:
			logging.error(f"KBBI API Error: {str(e)}")
			raise ConnectionError(f"Terjadi kesalahan: {str(e)}")
		return None

	def _parseResponse(self, data: dict[str, Any] | None) -> KBBIResult:
		"""
		Parses the raw JSON response from the API into a KBBIResult object.

		:param data: The parsed JSON dictionary from the API.
		:type data: dict[str, Any] | None
		:return: A KBBIResult object containing the parsed lemma and entries.
		:rtype: KBBIResult
		:raises ValueError: If the data format is invalid.
		"""
		if not data or "entries" not in data:
			raise ValueError("Format data tidak valid.")

		lemma = str(data.get("lemma", ""))
		entries_list = []

		for e_data in data.get("entries", []):
			defs = []
			for d_data in e_data.get("definitions", []):
				labels = [Label(**lbl_data) for lbl_data in d_data.get("labels", [])]
				defs.append(
					Definition(
						definition=d_data.get("definition", ""),
						referencedLemma=d_data.get("referencedLemma", ""),
						labels=labels,
						usageExamples=d_data.get("usageExamples", []),
					),
				)

			entries_list.append(
				Entry(
					entry=e_data.get("entry", ""),
					baseWord=e_data.get("baseWord", ""),
					pronunciation=e_data.get("pronunciation", ""),
					definitions=defs,
					derivedWords=[w for w in e_data.get("derivedWords", []) if w],
					compoundWords=[w for w in e_data.get("compoundWords", []) if w],
					metaphors=[w for w in e_data.get("metaphors", []) if w],
					proverbs=[w for w in e_data.get("proverbs", []) if w],
				),
			)

		return KBBIResult(lemma=lemma, entries=entries_list)

	def search(self, query: str) -> KBBIResult:
		"""
		Searches for a specific word in the KBBI.

		:param query: The word to search for.
		:type query: str
		:return: The search result containing definitions.
		:rtype: KBBIResult
		"""
		safe_query = parse.quote(query)
		url = f"{API_BASE_URL}/entry/{safe_query}"
		data = self._fetch(url)
		return self._parseResponse(data)

	def getWotd(self) -> KBBIResult:
		"""
		Fetches the Word of the Day from KBBI.

		:return: The Word of the Day result.
		:rtype: KBBIResult
		"""
		url = f"{API_BASE_URL}/entry/_wotd"
		data = self._fetch(url)
		return self._parseResponse(data)

	def getRandom(self) -> KBBIResult:
		"""
		Fetches a random word from KBBI.

		:return: A random word result.
		:rtype: KBBIResult
		"""
		url = f"{API_BASE_URL}/entry/_random"
		data = self._fetch(url)
		return self._parseResponse(data)
