import wx
import threading
import addonHandler
import ui as nvdaUI
import api
import tones
import unicodedata
from typing import Optional, Callable
from .client import KBBIClient
from .config import ConfigManager
from .models import KBBIResult

addonHandler.initTranslation()
_ = wx.GetTranslation


class SelectionDialog(wx.Dialog):
	def __init__(
		self,
		parent: wx.Window,
		title: str,
		choices: list[str],
		callback: Callable[[str], None],
		delete_callback: Optional[Callable[[str], None]] = None,
		clear_callback: Optional[Callable[[], None]] = None,
	):
		super(SelectionDialog, self).__init__(parent, title=title, size=(500, 450))
		self.callback = callback
		self.delete_callback = delete_callback
		self.clear_callback = clear_callback
		self.choices = list(choices)

		sizer = wx.BoxSizer(wx.VERTICAL)

		self.list_box = wx.ListBox(self, choices=self.choices)
		self.list_box.Bind(wx.EVT_LISTBOX_DCLICK, self.on_select)
		sizer.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 10)

		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

		select_btn = wx.Button(self, label=_("Pilih"))
		select_btn.Bind(wx.EVT_BUTTON, self.on_select)
		btn_sizer.Add(select_btn, 0, wx.RIGHT, 5)

		if self.delete_callback:
			del_btn = wx.Button(self, label=_("Hapus"))
			del_btn.Bind(wx.EVT_BUTTON, self.on_delete)
			btn_sizer.Add(del_btn, 0, wx.RIGHT, 5)

		if self.clear_callback:
			clear_btn = wx.Button(self, label=_("Bersihkan Semua"))
			clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
			btn_sizer.Add(clear_btn, 0, wx.RIGHT, 5)

		close_btn = wx.Button(self, wx.ID_CANCEL, label=_("Tutup"))
		btn_sizer.Add(close_btn, 0)

		sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

		self.SetSizer(sizer)
		self.list_box.SetFocus()
		if self.choices:
			self.list_box.SetSelection(0)

	def on_select(self, event: wx.Event):
		sel_idx = self.list_box.GetSelection()
		if sel_idx != wx.NOT_FOUND:
			selection = self.choices[sel_idx]
			self.callback(selection)
			self.Close()

	def on_delete(self, event: wx.Event):
		sel_idx = self.list_box.GetSelection()
		if sel_idx != wx.NOT_FOUND:
			item = self.choices[sel_idx]
			self.delete_callback(item)
			self.list_box.Delete(sel_idx)
			self.choices.pop(sel_idx)
			if self.list_box.GetCount() > 0:
				new_sel = min(sel_idx, self.list_box.GetCount() - 1)
				self.list_box.SetSelection(new_sel)

	def on_clear(self, event: wx.Event):
		if self.choices:
			dlg = wx.MessageDialog(
				self,
				_("Yakin ingin menghapus semua?"),
				_("Konfirmasi"),
				wx.YES_NO | wx.ICON_QUESTION,
			)
			if dlg.ShowModal() == wx.ID_YES:
				self.clear_callback()
				self.list_box.Clear()
				self.choices = []
			dlg.Destroy()


class KBBIDialog(wx.Dialog):
	def __init__(self, parent: wx.Window):
		super(KBBIDialog, self).__init__(
			parent,
			title=_("Accessible KBBI"),
			size=(700, 600),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)

		self.client = KBBIClient()
		self.config = ConfigManager()
		self.current_result: Optional[KBBIResult] = None
		self.Centers()

		self._init_ui()
		# Ensure result area is clean on start
		self.result_area.SetValue("")

	def _init_ui(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		# Bind Escape key to close
		self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

		# --- Search Area ---
		input_sizer = wx.BoxSizer(wx.HORIZONTAL)
		input_label = wx.StaticText(self, label=_("Cari kata:"))
		input_sizer.Add(input_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

		self.search_box = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.search_box.Bind(wx.EVT_TEXT_ENTER, self.on_search_click)
		input_sizer.Add(self.search_box, 1, wx.EXPAND)

		self.search_btn = wx.Button(self, label=_("Cari"))
		self.search_btn.Bind(wx.EVT_BUTTON, self.on_search_click)
		input_sizer.Add(self.search_btn, 0, wx.LEFT, 5)

		main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 10)

		# --- Toolbar ---
		tool_sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.wotd_btn = wx.Button(self, label=_("Kata Hari Ini"))
		self.wotd_btn.Bind(
			wx.EVT_BUTTON,
			lambda e: self.do_api_call(self.client.get_wotd),
		)
		tool_sizer.Add(self.wotd_btn, 1, wx.RIGHT, 5)

		self.random_btn = wx.Button(self, label=_("Kata Acak"))
		self.random_btn.Bind(
			wx.EVT_BUTTON,
			lambda e: self.do_api_call(self.client.get_random),
		)
		tool_sizer.Add(self.random_btn, 1, wx.RIGHT, 5)

		self.history_btn = wx.Button(self, label=_("Riwayat"))
		self.history_btn.Bind(wx.EVT_BUTTON, self.on_history)
		tool_sizer.Add(self.history_btn, 1, wx.RIGHT, 5)

		self.fav_list_btn = wx.Button(self, label=_("Ditandai"))
		self.fav_list_btn.Bind(wx.EVT_BUTTON, self.on_favorites)
		tool_sizer.Add(self.fav_list_btn, 1)

		main_sizer.Add(tool_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

		# --- Result Display ---
		self.result_label = wx.StaticText(self, label=_("Hasil:"))
		main_sizer.Add(self.result_label, 0, wx.LEFT | wx.RIGHT, 10)

		self.result_area = wx.TextCtrl(
			self,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
		)
		main_sizer.Add(self.result_area, 1, wx.EXPAND | wx.ALL, 10)

		# --- Bottom Action Bar ---
		bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

		self.toggle_fav_btn = wx.Button(self, label=_("Tandai"))
		self.toggle_fav_btn.Bind(wx.EVT_BUTTON, self.on_toggle_favorite)
		self.toggle_fav_btn.Disable()
		bottom_sizer.Add(self.toggle_fav_btn, 0, wx.RIGHT, 10)

		self.copy_btn = wx.Button(self, label=_("Salin"))
		self.copy_btn.Bind(wx.EVT_BUTTON, self.on_copy)
		self.copy_btn.Disable()
		bottom_sizer.Add(self.copy_btn, 0, wx.RIGHT, 10)

		close_btn = wx.Button(self, wx.ID_CANCEL, label=_("Tutup"))
		close_btn.Bind(wx.EVT_BUTTON, self.on_close_button)
		bottom_sizer.Add(close_btn, 0)

		main_sizer.Add(bottom_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

		self.SetSizer(main_sizer)
		self.search_box.SetFocus()

	def Centers(self):
		self.CenterOnScreen()

	def on_close_button(self, event: wx.CommandEvent):
		self.Close()

	def on_char_hook(self, event: wx.KeyEvent):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
		else:
			event.Skip()

	def on_copy(self, event: wx.CommandEvent):
		text = self.result_area.GetValue()
		if text:
			if api.copyToClip(text):
				nvdaUI.message(_("Disalin ke papan klip."))
			else:
				nvdaUI.message(_("Gagal menyalin."))

	def on_search_click(self, event: Optional[wx.CommandEvent]):
		query = self.search_box.GetValue().strip()
		if query:
			self.do_api_call(lambda: self.client.search(query))

	def on_history(self, event: wx.CommandEvent):
		history = self.config.get_history()
		if not history:
			nvdaUI.message(_("Riwayat kosong."))
			return
		dlg = SelectionDialog(
			self,
			_("Riwayat Pencarian"),
			history,
			self.load_from_history,
			delete_callback=self.delete_history_item,
			clear_callback=self.clear_all_history,
		)
		dlg.ShowModal()

	def delete_history_item(self, lemma: str):
		self.config.remove_history(lemma)

	def clear_all_history(self):
		self.config.clear_history()

	def on_favorites(self, event: wx.CommandEvent):
		favs = self.config.get_favorites()
		if not favs:
			nvdaUI.message(_("Belum ada kata yang ditandai."))
			return
		dlg = SelectionDialog(
			self,
			_("Daftar Ditandai"),
			favs,
			self.load_from_history,
			delete_callback=self.delete_favorite_item,
		)
		dlg.ShowModal()

	def delete_favorite_item(self, lemma: str):
		self.config.remove_favorite(lemma)
		if self.current_result and self.current_result.lemma == lemma:
			self.toggle_fav_btn.SetLabel(_("Tandai"))

	def load_from_history(self, query: str):
		self.search_box.SetValue(query)
		self.on_search_click(None)

	def on_toggle_favorite(self, event: wx.CommandEvent):
		if not self.current_result:
			return

		lemma = self.current_result.lemma
		if self.config.is_favorite(lemma):
			self.config.remove_favorite(lemma)
			nvdaUI.message(_("Dihapus dari tandai."))
			self.toggle_fav_btn.SetLabel(_("Tandai"))
		else:
			self.config.add_favorite(lemma)
			nvdaUI.message(_("Ditandai."))
			self.toggle_fav_btn.SetLabel(_("Hapus Tanda"))

	def do_api_call(self, func: Callable[[], KBBIResult]):
		self.search_btn.Disable()
		self.wotd_btn.Disable()
		self.random_btn.Disable()
		self.copy_btn.Disable()
		self.toggle_fav_btn.Disable()
		self.result_area.SetValue(_("Memuat..."))

		threading.Thread(target=self._worker, args=(func,), daemon=True).start()

	def _worker(self, func: Callable[[], KBBIResult]):
		try:
			result = func()
			wx.CallAfter(self._on_success, result)
		except Exception as e:
			wx.CallAfter(self._on_error, str(e))

	def _on_success(self, result: KBBIResult):
		self._enable_controls()
		self.current_result = result

		# Update config/state
		self.config.add_history(result.lemma)

		# Update UI
		text = self._format_result(result)
		self.result_area.SetValue(text)
		self.result_area.SetInsertionPoint(0)
		self.result_area.ShowPosition(0)

		# Set Focus to result for direct reading
		self.result_area.SetFocus()

		if self.config.is_favorite(result.lemma):
			self.toggle_fav_btn.SetLabel(_("Hapus Tanda"))
		else:
			self.toggle_fav_btn.SetLabel(_("Tandai"))
		self.toggle_fav_btn.Enable()
		self.copy_btn.Enable()

		nvdaUI.message(_("Selesai."))

	def _on_error(self, error_msg: str):
		self._enable_controls()
		self.result_area.SetValue(error_msg)
		tones.beep(150, 100)
		nvdaUI.message(_("Error."))

	def _enable_controls(self):
		self.search_btn.Enable()
		self.wotd_btn.Enable()
		self.random_btn.Enable()
		# Note: copy and fav are enabled only on success,
		# but we re-enable search controls here so user can try again.

	def _format_result(self, res: KBBIResult) -> str:
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
