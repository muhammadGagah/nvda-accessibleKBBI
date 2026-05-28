import wx
import threading
import addonHandler
import ui as nvdaUI
import api
import tones
import unicodedata
from collections.abc import Callable
from .client import KBBIClient
from .config import ConfigManager
from .models import KBBIResult

addonHandler.initTranslation()
_ = wx.GetTranslation


class SelectionDialog(wx.Dialog):
	"""Dialog for selecting, deleting, or clearing items from a list."""

	def __init__(
		self,
		parent: wx.Window,
		title: str,
		choices: list[str],
		callback: Callable[[str], None],
		deleteCallback: Callable[[str], None] | None = None,
		clearCallback: Callable[[], None] | None = None,
	):
		super(SelectionDialog, self).__init__(parent, title=title, size=(500, 450))
		self.callback = callback
		self.deleteCallback = deleteCallback
		self.clearCallback = clearCallback
		self.choices = list(choices)

		sizer = wx.BoxSizer(wx.VERTICAL)

		self.listBox = wx.ListBox(self, choices=self.choices)
		self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.onSelect)
		sizer.Add(self.listBox, 1, wx.EXPAND | wx.ALL, 10)

		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

		# Translators: Label for the 'Select' button.
		select_btn = wx.Button(self, label=_("Pilih"))
		select_btn.Bind(wx.EVT_BUTTON, self.onSelect)
		btn_sizer.Add(select_btn, 0, wx.RIGHT, 5)

		if self.deleteCallback:
			# Translators: Label for the 'Delete' button.
			del_btn = wx.Button(self, label=_("Hapus"))
			del_btn.Bind(wx.EVT_BUTTON, self.onDelete)
			btn_sizer.Add(del_btn, 0, wx.RIGHT, 5)

		if self.clearCallback:
			# Translators: Label for the 'Clear All' button.
			clear_btn = wx.Button(self, label=_("Bersihkan Semua"))
			clear_btn.Bind(wx.EVT_BUTTON, self.onClear)
			btn_sizer.Add(clear_btn, 0, wx.RIGHT, 5)

		# Translators: Label for the 'Close' button.
		close_btn = wx.Button(self, wx.ID_CANCEL, label=_("Tutup"))
		btn_sizer.Add(close_btn, 0)

		sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

		self.SetSizer(sizer)
		self.listBox.SetFocus()
		if self.choices:
			self.listBox.SetSelection(0)

	def onSelect(self, event: wx.Event):
		sel_idx = self.listBox.GetSelection()
		if sel_idx != wx.NOT_FOUND:
			selection = self.choices[sel_idx]
			self.callback(selection)
			self.Close()

	def onDelete(self, event: wx.Event):
		sel_idx = self.listBox.GetSelection()
		if sel_idx != wx.NOT_FOUND and self.deleteCallback:
			item = self.choices[sel_idx]
			self.deleteCallback(item)
			self.listBox.Delete(sel_idx)
			self.choices.pop(sel_idx)
			if self.listBox.GetCount() > 0:
				new_sel = min(sel_idx, self.listBox.GetCount() - 1)
				self.listBox.SetSelection(new_sel)

	def onClear(self, event: wx.Event):
		if self.choices and self.clearCallback:
			dlg = wx.MessageDialog(
				self,
				# Translators: Message asking if the user is sure to clear everything.
				_("Yakin ingin menghapus semua?"),
				# Translators: Title of the confirmation dialog.
				_("Konfirmasi"),
				wx.YES_NO | wx.ICON_QUESTION,
			)
			if dlg.ShowModal() == wx.ID_YES:
				self.clearCallback()
				self.listBox.Clear()
				self.choices = []
			dlg.Destroy()


class KBBIDialog(wx.Dialog):
	"""Main dialog for the Accessible KBBI add-on."""

	def __init__(self, parent: wx.Window):
		super(KBBIDialog, self).__init__(
			parent,
			# Translators: Title of the Accessible KBBI dialog.
			title=_("Accessible KBBI"),
			size=(700, 600),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)

		self.client = KBBIClient()
		self.config = ConfigManager()
		self.currentResult: KBBIResult | None = None
		self._isClosing = False
		self.Centers()

		self._initUi()
		# Ensure result area is clean on start
		self.resultArea.SetValue("")

	def _initUi(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		# Bind Escape key to close
		self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)
		self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroy)

		# --- Search Area ---
		input_sizer = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Label asking the user to search a word.
		input_label = wx.StaticText(self, label=_("Cari kata:"))
		input_sizer.Add(input_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

		self.searchBox = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.searchBox.Bind(wx.EVT_TEXT_ENTER, self.onSearchClick)
		input_sizer.Add(self.searchBox, 1, wx.EXPAND)

		# Translators: Label for the 'Search' button.
		self.searchBtn = wx.Button(self, label=_("Cari"))
		self.searchBtn.Bind(wx.EVT_BUTTON, self.onSearchClick)
		input_sizer.Add(self.searchBtn, 0, wx.LEFT, 5)

		main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 10)

		# --- Toolbar ---
		tool_sizer = wx.BoxSizer(wx.HORIZONTAL)

		# Translators: Label for the 'Word of the Day' button.
		self.wotdBtn = wx.Button(self, label=_("Kata Hari Ini"))
		self.wotdBtn.Bind(
			wx.EVT_BUTTON,
			self.onWotdClick,
		)
		tool_sizer.Add(self.wotdBtn, 1, wx.RIGHT, 5)

		# Translators: Label for the 'Random Word' button.
		self.randomBtn = wx.Button(self, label=_("Kata Acak"))
		self.randomBtn.Bind(
			wx.EVT_BUTTON,
			self.onRandomClick,
		)
		tool_sizer.Add(self.randomBtn, 1, wx.RIGHT, 5)

		# Translators: Label for the 'History' button.
		self.historyBtn = wx.Button(self, label=_("Riwayat"))
		self.historyBtn.Bind(wx.EVT_BUTTON, self.onHistory)
		tool_sizer.Add(self.historyBtn, 1, wx.RIGHT, 5)

		# Translators: Label for the 'Favorites' button.
		self.favListBtn = wx.Button(self, label=_("Ditandai"))
		self.favListBtn.Bind(wx.EVT_BUTTON, self.onFavorites)
		tool_sizer.Add(self.favListBtn, 1)

		main_sizer.Add(tool_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

		# --- Result Display ---
		# Translators: Label for the search result area.
		self.resultLabel = wx.StaticText(self, label=_("Hasil:"))
		main_sizer.Add(self.resultLabel, 0, wx.LEFT | wx.RIGHT, 10)

		self.resultArea = wx.TextCtrl(
			self,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
		)
		main_sizer.Add(self.resultArea, 1, wx.EXPAND | wx.ALL, 10)

		# --- Bottom Action Bar ---
		bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

		# Translators: Label for the 'Bookmark' / 'Mark' button.
		self.toggleFavBtn = wx.Button(self, label=_("Tandai"))
		self.toggleFavBtn.Bind(wx.EVT_BUTTON, self.onToggleFavorite)
		self.toggleFavBtn.Disable()
		bottom_sizer.Add(self.toggleFavBtn, 0, wx.RIGHT, 10)

		# Translators: Label for the 'Copy' button.
		self.copyBtn = wx.Button(self, label=_("Salin"))
		self.copyBtn.Bind(wx.EVT_BUTTON, self.onCopy)
		self.copyBtn.Disable()
		bottom_sizer.Add(self.copyBtn, 0, wx.RIGHT, 10)

		# Translators: Label for the 'Close' button.
		close_btn = wx.Button(self, wx.ID_CANCEL, label=_("Tutup"))
		close_btn.Bind(wx.EVT_BUTTON, self.onCloseButton)
		bottom_sizer.Add(close_btn, 0)

		main_sizer.Add(bottom_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

		self.SetSizer(main_sizer)
		self.searchBox.SetFocus()

	def Centers(self):
		self.CenterOnScreen()

	def isClosing(self) -> bool:
		return self._isClosing or self.IsBeingDeleted()

	def destroyDialog(self) -> None:
		if self.isClosing():
			return
		self._isClosing = True
		self.Destroy()

	def onDestroy(self, event: wx.Event):
		self._isClosing = True
		event.Skip()

	def onCloseButton(self, event: wx.CommandEvent):
		self.Close()

	def onCharHook(self, event: wx.KeyEvent):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
		else:
			event.Skip()

	def onCopy(self, event: wx.CommandEvent):
		text = self.resultArea.GetValue()
		if text:
			if api.copyToClip(text):
				# Translators: Message announced when text is copied to clipboard.
				nvdaUI.message(_("Disalin ke papan klip."))
			else:
				# Translators: Message announced when copying fails.
				nvdaUI.message(_("Gagal menyalin."))

	def onSearchClick(self, event: wx.CommandEvent | None):
		query = self.searchBox.GetValue().strip()
		if query:
			self.doApiCall(lambda: self.client.search(query))

	def onWotdClick(self, event: wx.CommandEvent):
		self.doApiCall(self.client.getWotd)

	def onRandomClick(self, event: wx.CommandEvent):
		self.doApiCall(self.client.getRandom)

	def onHistory(self, event: wx.CommandEvent):
		history = self.config.getHistory()
		if not history:
			# Translators: Message announced when history is empty.
			nvdaUI.message(_("Riwayat kosong."))
			return
		dlg = SelectionDialog(
			self,
			# Translators: Title of the History dialog.
			_("Riwayat Pencarian"),
			history,
			self.loadFromHistory,
			deleteCallback=self.deleteHistoryItem,
			clearCallback=self.clearAllHistory,
		)
		dlg.ShowModal()

	def deleteHistoryItem(self, lemma: str):
		self.config.removeHistory(lemma)

	def clearAllHistory(self):
		self.config.clearHistory()

	def onFavorites(self, event: wx.CommandEvent):
		favs = self.config.getFavorites()
		if not favs:
			# Translators: Message announced when favorites list is empty.
			nvdaUI.message(_("Belum ada kata yang ditandai."))
			return
		dlg = SelectionDialog(
			self,
			# Translators: Title of the Favorites dialog.
			_("Daftar Ditandai"),
			favs,
			self.loadFromHistory,
			deleteCallback=self.deleteFavoriteItem,
		)
		dlg.ShowModal()

	def deleteFavoriteItem(self, lemma: str):
		self.config.removeFavorite(lemma)
		if self.currentResult and self.currentResult.lemma == lemma:
			# Translators: Label for the 'Bookmark' / 'Mark' button.
			self.toggleFavBtn.SetLabel(_("Tandai"))

	def loadFromHistory(self, query: str):
		self.searchBox.SetValue(query)
		self.onSearchClick(None)

	def onToggleFavorite(self, event: wx.CommandEvent):
		if not self.currentResult:
			return

		lemma = self.currentResult.lemma
		if self.config.isFavorite(lemma):
			self.config.removeFavorite(lemma)
			# Translators: Message announced when a word is removed from favorites.
			nvdaUI.message(_("Dihapus dari tandai."))
			# Translators: Label for the 'Bookmark' / 'Mark' button.
			self.toggleFavBtn.SetLabel(_("Tandai"))
		else:
			self.config.addFavorite(lemma)
			# Translators: Message announced when a word is added to favorites.
			nvdaUI.message(_("Ditandai."))
			# Translators: Label for the 'Remove Bookmark' button.
			self.toggleFavBtn.SetLabel(_("Hapus Tanda"))

	def doApiCall(self, func: Callable[[], KBBIResult]):
		if self.isClosing():
			return

		self.searchBtn.Disable()
		self.wotdBtn.Disable()
		self.randomBtn.Disable()
		self.copyBtn.Disable()
		self.toggleFavBtn.Disable()
		# Translators: Text displayed when loading results.
		self.resultArea.SetValue(_("Memuat..."))

		threading.Thread(target=self._worker, args=(func,), daemon=True).start()

	def _worker(self, func: Callable[[], KBBIResult]):
		try:
			result = func()
			self._callAfterIfOpen(self._onSuccess, result)
		except Exception as e:
			self._callAfterIfOpen(self._onError, str(e))

	def _callAfterIfOpen(self, callback: Callable[..., None], *args: object) -> None:
		wx.CallAfter(self._runIfOpen, callback, *args)

	def _runIfOpen(self, callback: Callable[..., None], *args: object) -> None:
		if self.isClosing():
			return
		callback(*args)

	def _onSuccess(self, result: KBBIResult):
		if self.isClosing():
			return

		self._enableControls()
		self.currentResult = result

		# Update config/state
		self.config.addHistory(result.lemma)

		# Update UI
		text = self._formatResult(result)
		self.resultArea.SetValue(text)
		self.resultArea.SetInsertionPoint(0)
		self.resultArea.ShowPosition(0)

		# Set Focus to result for direct reading
		self.resultArea.SetFocus()

		if self.config.isFavorite(result.lemma):
			# Translators: Label for the 'Remove Bookmark' button.
			self.toggleFavBtn.SetLabel(_("Hapus Tanda"))
		else:
			# Translators: Label for the 'Bookmark' / 'Mark' button.
			self.toggleFavBtn.SetLabel(_("Tandai"))
		self.toggleFavBtn.Enable()
		self.copyBtn.Enable()

		# Translators: Message announced when data fetching completes successfully.
		nvdaUI.message(_("Selesai."))

	def _onError(self, error_msg: str):
		if self.isClosing():
			return

		self._enableControls()
		self.resultArea.SetValue(error_msg)
		tones.beep(150, 100)
		# Translators: Message announced when an error occurs during API call.
		nvdaUI.message(_("Error."))

	def _enableControls(self):
		self.searchBtn.Enable()
		self.wotdBtn.Enable()
		self.randomBtn.Enable()
		# Note: copy and fav are enabled only on success,
		# but we re-enable search controls here so user can try again.

	def _formatResult(self, res: KBBIResult) -> str:
		lines = []

		for idx, entry in enumerate(res.entries, 1):
			# Headword
			head = unicodedata.normalize("NFKC", entry.entry)
			if entry.pronunciation:
				head += f"  /{entry.pronunciation}/"
			lines.append(f"{head}")

			if entry.baseWord:
				lines.append(
					f"  Kata Dasar: {unicodedata.normalize('NFKC', entry.baseWord)}",
				)

			# Definitions
			if entry.definitions:
				lines.append("  Definisi:")
				for i, definition in enumerate(entry.definitions, 1):
					labels = ", ".join([lbl.code for lbl in definition.labels])
					label_part = f"[{labels}] " if labels else ""

					def_text = unicodedata.normalize("NFKC", definition.definition)
					lines.append(f"    {i}. {label_part}{def_text}")

					if definition.usageExamples:
						exs = "; ".join(
							[unicodedata.normalize("NFKC", ex) for ex in definition.usageExamples],
						)
						lines.append(f"       Contoh: {exs}")

			# Derived
			if entry.derivedWords:
				lines.append(
					"  Kata Turunan: "
					+ ", ".join(
						[unicodedata.normalize("NFKC", w) for w in entry.derivedWords],
					),
				)

			# Compound
			if entry.compoundWords:
				lines.append(
					"  Gabungan Kata: "
					+ ", ".join(
						[unicodedata.normalize("NFKC", w) for w in entry.compoundWords],
					),
				)

			# Proverbs
			if entry.proverbs:
				lines.append(
					"  Peribahasa: "
					+ ", ".join(
						[unicodedata.normalize("NFKC", w) for w in entry.proverbs],
					),
				)

			if idx < len(res.entries):
				lines.append("")

		return "\n".join(lines)
