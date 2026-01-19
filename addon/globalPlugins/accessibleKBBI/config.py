import os
import json


class ConfigManager:
	def __init__(self):
		self.config_path = os.path.join(
			os.path.dirname(__file__), "accessibleKBBI.json"
		)
		self.data = {"history": [], "favorites": []}
		self.load()

	def load(self):
		try:
			if os.path.exists(self.config_path):
				with open(self.config_path, "r", encoding="utf-8") as f:
					self.data = json.load(f)
		except Exception:
			# If fails, use default
			pass

	def save(self):
		try:
			with open(self.config_path, "w", encoding="utf-8") as f:
				json.dump(self.data, f, ensure_ascii=False, indent=2)
		except Exception:
			pass

	def add_history(self, lemma: str):
		if not lemma:
			return
		# Remove if exists to move to top
		if lemma in self.data["history"]:
			self.data["history"].remove(lemma)

		self.data["history"].insert(0, lemma)
		# Limit history to 50
		self.data["history"] = self.data["history"][:50]
		self.save()

	def remove_history(self, lemma: str):
		if lemma in self.data["history"]:
			self.data["history"].remove(lemma)
			self.save()

	def get_history(self) -> list[str]:
		return self.data["history"]

	def clear_history(self):
		self.data["history"] = []
		self.save()

	def add_favorite(self, lemma: str):
		if lemma and lemma not in self.data["favorites"]:
			self.data["favorites"].insert(0, lemma)
			self.save()

	def remove_favorite(self, lemma: str):
		if lemma in self.data["favorites"]:
			self.data["favorites"].remove(lemma)
			self.save()

	def is_favorite(self, lemma: str) -> bool:
		return lemma in self.data["favorites"]

	def get_favorites(self) -> list[str]:
		return self.data["favorites"]
