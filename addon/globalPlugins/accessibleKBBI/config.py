import os
import json


class ConfigManager:
	"""
	Manages the configuration, search history, and favorite words for Accessible KBBI.
	"""

	def __init__(self):
		"""
		Initializes the ConfigManager and loads existing data if available.
		"""
		super().__init__()
		self.configPath = os.path.join(
			os.path.dirname(__file__),
			"accessibleKBBI.json",
		)
		self.data = {"history": [], "favorites": []}
		self.load()

	def load(self):
		"""
		Loads the configuration data from the JSON file.
		"""
		try:
			if os.path.exists(self.configPath):
				with open(self.configPath, "r", encoding="utf-8") as f:
					self.data = json.load(f)
		except Exception:
			# If fails, use default
			pass

	def save(self):
		"""
		Saves the configuration data to the JSON file.
		"""
		try:
			with open(self.configPath, "w", encoding="utf-8") as f:
				json.dump(self.data, f, ensure_ascii=False, indent=2)
		except Exception:
			pass

	def addHistory(self, lemma: str):
		"""
		Adds a lemma to the search history.
		Moves it to the top if it already exists, and limits the history to 50 items.

		:param lemma: The word to add.
		:type lemma: str
		"""
		if not lemma:
			return
		# Remove if exists to move to top
		if lemma in self.data["history"]:
			self.data["history"].remove(lemma)

		self.data["history"].insert(0, lemma)
		# Limit history to 50
		self.data["history"] = self.data["history"][:50]
		self.save()

	def removeHistory(self, lemma: str):
		"""
		Removes a lemma from the search history.

		:param lemma: The word to remove.
		:type lemma: str
		"""
		if lemma in self.data["history"]:
			self.data["history"].remove(lemma)
			self.save()

	def getHistory(self) -> list[str]:
		"""
		Retrieves the list of search history.

		:return: List of past searches.
		:rtype: list[str]
		"""
		return self.data["history"]

	def clearHistory(self):
		"""
		Clears the search history.
		"""
		self.data["history"] = []
		self.save()

	def addFavorite(self, lemma: str):
		"""
		Adds a lemma to the list of favorites.

		:param lemma: The word to add.
		:type lemma: str
		"""
		if lemma and lemma not in self.data["favorites"]:
			self.data["favorites"].insert(0, lemma)
			self.save()

	def removeFavorite(self, lemma: str):
		"""
		Removes a lemma from the list of favorites.

		:param lemma: The word to remove.
		:type lemma: str
		"""
		if lemma in self.data["favorites"]:
			self.data["favorites"].remove(lemma)
			self.save()

	def isFavorite(self, lemma: str) -> bool:
		"""
		Checks if a lemma is in the list of favorites.

		:param lemma: The word to check.
		:type lemma: str
		:return: True if favorited, False otherwise.
		:rtype: bool
		"""
		return lemma in self.data["favorites"]

	def getFavorites(self) -> list[str]:
		"""
		Retrieves the list of favorite words.

		:return: List of favorited words.
		:rtype: list[str]
		"""
		return self.data["favorites"]
