import json
from typing import Any
from urllib import error, parse, request

from logHandler import log

from .models import Definition, Entry, KBBIResult, Label

API_BASE_URL = "https://kbbi.raf555.dev/api/v1"
# The API accepts up to 100 suggestions per request.
MAX_SUGGESTIONS = 100
# Shortest prefix used when trimming a misspelled word to find suggestions.
MIN_SUGGESTION_PREFIX = 3
USER_AGENT = (
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
	"(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AccessibleKBBI/1.4.0"
)


class EntryNotFoundError(ValueError):
	"""The requested lemma is not in KBBI. `suggestions` lists lemmas with a similar prefix."""

	def __init__(self, message: str, suggestions: list[str] | None = None):
		super().__init__(message)
		self.suggestions = suggestions or []


def _words(values: Any) -> list[str]:
	"""Keep only non-empty strings from an API list field."""
	return [value for value in values or [] if isinstance(value, str) and value]


def _parseLabel(data: dict[str, Any]) -> Label:
	"""Build a Label from known fields only, so new or missing API fields cannot break parsing."""
	return Label(
		code=str(data.get("code", "")),
		name=str(data.get("name", "")),
		kind=str(data.get("kind", "")),
	)


class KBBIClient:
	"""Client for fetching definitions from the KBBI API."""

	def __init__(self):
		super().__init__()
		self.timeout = 15

	def _fetch(self, url: str) -> dict[str, Any] | None:
		"""
		Makes an HTTP GET request to the given URL and parses the JSON response.

		:param url: The API endpoint URL to fetch.
		:return: A dictionary containing the JSON response, or None if the request fails.
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
			log.warning(f"KBBI API HTTP Error: {e.code} for {url}")
			if e.code == 404:
				raise EntryNotFoundError("Entri tidak ditemukan.") from None
			raise ConnectionError(f"Gagal menghubungi server: {e.code}")
		except Exception as e:
			log.exception("KBBI API Error")
			raise ConnectionError(f"Terjadi kesalahan: {e!s}")
		return None

	def _parseResponse(self, data: dict[str, Any] | None) -> KBBIResult:
		"""
		Parses the raw JSON response from the API into a KBBIResult object.

		:param data: The parsed JSON dictionary from the API.
		:return: A KBBIResult object containing the parsed lemma and entries.
		:raises ValueError: If the data format is invalid.
		"""
		if not data or "entries" not in data:
			raise ValueError("Format data tidak valid.")

		lemma = str(data.get("lemma", ""))
		entries_list = []

		for e_data in data.get("entries", []):
			defs = []
			for d_data in e_data.get("definitions", []):
				labels = [_parseLabel(lbl_data) for lbl_data in d_data.get("labels", [])]
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
					derivedWords=_words(e_data.get("derivedWords")),
					compoundWords=_words(e_data.get("compoundWords")),
					metaphors=_words(e_data.get("metaphors")),
					proverbs=_words(e_data.get("proverbs")),
					nonStandardWords=_words(e_data.get("nonStandardWords")),
					variants=_words(e_data.get("variants")),
					entryVariants=_words(e_data.get("entryVariants")),
					isPrecategorical=e_data.get("isPrecategorical") is True,
				),
			)

		return KBBIResult(lemma=lemma, entries=entries_list)

	def search(self, query: str) -> KBBIResult:
		"""Search for a specific word in KBBI.

		:raises EntryNotFoundError: If the word is not found; suggestions are attached when available.
		"""
		# safe="" also encodes "/", which would otherwise change the API path.
		safe_query = parse.quote(query, safe="")
		url = f"{API_BASE_URL}/entry/{safe_query}"
		try:
			data = self._fetch(url)
		except EntryNotFoundError as notFound:
			notFound.suggestions = self.suggestForMissingWord(query)
			raise
		return self._parseResponse(data)

	def suggest(self, prefix: str, limit: int = MAX_SUGGESTIONS) -> list[str]:
		"""Return KBBI lemmas that start with prefix, as the KBBI application suggests them."""
		prefix = prefix.strip()
		if not prefix:
			return []
		query = parse.urlencode({"entry": prefix, "limit": max(1, min(limit, MAX_SUGGESTIONS))})
		data = self._fetch(f"{API_BASE_URL}/entry/_search?{query}")
		if not isinstance(data, dict):
			raise ValueError("Format data tidak valid.")
		return _words(data.get("lemmas"))

	def suggestForMissingWord(self, query: str) -> list[str]:
		"""Suggest lemmas for a word that was not found, trimming a few final letters if needed.

		Suggestions are prefix-based, so a typo near the end (e.g. "rumh") still finds "rumah".
		Failures return an empty list so the original "not found" message is still shown.
		"""
		query = query.strip()
		prefixes = [query]
		for trim in (1, 2):
			if len(query) - trim >= MIN_SUGGESTION_PREFIX:
				prefixes.append(query[:-trim])
		for prefix in prefixes:
			try:
				suggestions = self.suggest(prefix, limit=10)
			except (ConnectionError, ValueError):
				return []
			suggestions = [word for word in suggestions if word != query]
			if suggestions:
				return suggestions
		return []

	def getWotd(self) -> KBBIResult:
		"""Fetch the Word of the Day from KBBI."""
		url = f"{API_BASE_URL}/entry/_wotd"
		data = self._fetch(url)
		return self._parseResponse(data)

	def getRandom(self) -> KBBIResult:
		"""Fetch a random word from KBBI."""
		url = f"{API_BASE_URL}/entry/_random"
		data = self._fetch(url)
		return self._parseResponse(data)
