import json
import os
from typing import Any

import globalVars
from logHandler import log

CONFIG_DIR_NAME = "accessibleKBBI"
CONFIG_FILE_NAME = "accessibleKBBI.json"


class ConfigManager:
	"""Manage search history and favorite words for Accessible KBBI."""

	def __init__(self):
		super().__init__()
		self.configDir = os.path.join(globalVars.appArgs.configPath, CONFIG_DIR_NAME)
		self.configPath = os.path.join(self.configDir, CONFIG_FILE_NAME)
		self.legacyConfigPath = os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)
		self.data = self._defaultData()
		self.load()

	@staticmethod
	def _defaultData() -> dict[str, list[str]]:
		return {"history": [], "favorites": []}

	def _loadJsonFile(self, path: str) -> dict[str, list[str]] | None:
		try:
			with open(path, "r", encoding="utf-8") as f:
				rawData = json.load(f)
		except FileNotFoundError:
			return None
		except json.JSONDecodeError:
			log.warning(f"Failed to decode Accessible KBBI config: {path}", exc_info=True)
			return None
		except OSError:
			log.warning(f"Failed to read Accessible KBBI config: {path}", exc_info=True)
			return None

		return self._validateData(rawData, path)

	def _validateData(self, data: Any, source: str) -> dict[str, list[str]] | None:
		if not isinstance(data, dict):
			log.warning(f"Accessible KBBI config is not a JSON object: {source}")
			return None

		validData = self._defaultData()
		for key in validData:
			items = data.get(key, [])
			if not isinstance(items, list):
				log.warning(f"Accessible KBBI config key {key!r} is not a list: {source}")
				continue
			validData[key] = [item for item in items if isinstance(item, str)]

		return validData

	def load(self) -> None:
		"""Load configuration, migrating legacy add-on-local data when needed."""
		currentConfigExists = os.path.exists(self.configPath)
		currentData = self._loadJsonFile(self.configPath) if currentConfigExists else None
		if currentData is not None:
			self.data = currentData
			return

		if currentConfigExists:
			return

		legacyData = self._loadJsonFile(self.legacyConfigPath)
		if legacyData is not None:
			self.data = legacyData
			self.save()

	def save(self) -> None:
		"""Save configuration to the NVDA user configuration directory."""
		try:
			os.makedirs(self.configDir, exist_ok=True)
			with open(self.configPath, "w", encoding="utf-8") as f:
				json.dump(self.data, f, ensure_ascii=False, indent=2)
		except OSError:
			log.error("Failed to save Accessible KBBI config", exc_info=True)

	def addHistory(self, lemma: str) -> None:
		"""Add a lemma to the top of search history."""
		if not lemma:
			return
		# Remove if exists to move to top
		if lemma in self.data["history"]:
			self.data["history"].remove(lemma)

		self.data["history"].insert(0, lemma)
		# Limit history to 50
		self.data["history"] = self.data["history"][:50]
		self.save()

	def removeHistory(self, lemma: str) -> None:
		"""Remove a lemma from search history."""
		if lemma in self.data["history"]:
			self.data["history"].remove(lemma)
			self.save()

	def getHistory(self) -> list[str]:
		"""Return saved search history."""
		return self.data["history"]

	def clearHistory(self) -> None:
		"""Clear search history."""
		self.data["history"] = []
		self.save()

	def addFavorite(self, lemma: str) -> None:
		"""Add a lemma to favorites."""
		if lemma and lemma not in self.data["favorites"]:
			self.data["favorites"].insert(0, lemma)
			self.save()

	def removeFavorite(self, lemma: str) -> None:
		"""Remove a lemma from favorites."""
		if lemma in self.data["favorites"]:
			self.data["favorites"].remove(lemma)
			self.save()

	def isFavorite(self, lemma: str) -> bool:
		"""Return whether a lemma is saved as a favorite."""
		return lemma in self.data["favorites"]

	def getFavorites(self) -> list[str]:
		"""Return saved favorite words."""
		return self.data["favorites"]
