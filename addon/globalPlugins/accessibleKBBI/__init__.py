# -*- coding: utf-8 -*-
# Accessible KBBI for NVDA
# Copyright (C) 2026 Muhammad

import addonHandler
import globalPluginHandler
import scriptHandler
import gui
import wx
import api
import ui
import textInfos
import NVDAObjects.behaviors
import inputCore
from .interface import KBBIDialog

addonHandler.initTranslation()
_ = wx.GetTranslation


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Global plugin entry point for Accessible KBBI."""

	def __init__(self):
		super().__init__()
		self.dlg: KBBIDialog | None = None

	@scriptHandler.script(
		# Translators: Description for the command to open the Accessible KBBI dialog.
		description=_("Buka Accessible KBBI."),
		category=inputCore.SCRCAT_MISC,
		gesture="kb:NVDA+alt+k",
	)
	def script_showSearchDialog(self, gesture: inputCore.InputGesture):
		if self.dlg and not self.dlg.isClosing():
			self.dlg.Raise()
			self.dlg.SetFocus()
			# Translators: Message announced when the KBBI dialog is already open and focused.
			ui.message(_("Dialog Accessible KBBI sudah terbuka."))
			return

		self.dlg = KBBIDialog(gui.mainFrame)
		self.dlg.Show()
		self.dlg.Bind(wx.EVT_CLOSE, self.onClose)

	@scriptHandler.script(
		# Translators: Description for the command to search selected text in Accessible KBBI.
		description=_("Cari teks terpilih di Accessible KBBI."),
		category=inputCore.SCRCAT_MISC,
		gesture="kb:NVDA+shift+alt+k",
	)
	def script_searchSelection(self, gesture: inputCore.InputGesture):
		if self.dlg and not self.dlg.isClosing():
			self.dlg.Raise()
			self.dlg.SetFocus()
			# Translators: Message announced when the KBBI dialog is already open and focused.
			ui.message(_("Dialog Accessible KBBI sudah terbuka."))
			return

		text = self._getSelectedText()
		if not text:
			# Translators: Message announced when no text is selected for search.
			ui.message(_("Tidak ada teks yang dipilih."))
			return

		self.dlg = KBBIDialog(gui.mainFrame)
		self.dlg.Show()
		self.dlg.Bind(wx.EVT_CLOSE, self.onClose)

		self.dlg.searchBox.SetValue(text)
		self.dlg.onSearchClick(None)

	def _getSelectedText(self) -> str | None:
		"""
		Attempts to retrieve the currently selected text from various focus objects.

		:return: The selected text if found, otherwise None.
		"""
		focus_obj = api.getFocusObject()
		if not focus_obj:
			return None

		# 1. Tree Interceptor (e.g. Browser)
		if hasattr(focus_obj, "treeInterceptor") and focus_obj.treeInterceptor:
			try:
				info = focus_obj.treeInterceptor.makeTextInfo(
					textInfos.POSITION_SELECTION,
				)
				if info and info.text and not info.text.isspace():
					return info.text.strip()
			except Exception:
				pass

		# 2. Standard TextInfo (e.g. Word, Notepad)
		try:
			info = focus_obj.makeTextInfo(textInfos.POSITION_SELECTION)
			if info and info.text and not info.text.isspace():
				return info.text.strip()
		except Exception:
			pass

		# 3. Editable Text (Fallback for some edit fields)
		if isinstance(focus_obj, NVDAObjects.behaviors.EditableText):
			try:
				info = focus_obj.makeTextInfo(textInfos.POSITION_SELECTION)
				if info and info.text and not info.text.isspace():
					return info.text.strip()
			except Exception:
				pass

		# 4. Terminal
		if isinstance(focus_obj, NVDAObjects.behaviors.Terminal):
			try:
				info = focus_obj.makeTextInfo(textInfos.POSITION_SELECTION)
				if info and info.text and not info.text.isspace():
					return info.text.strip()
			except Exception:
				pass

		return None

	def _destroyDialog(self) -> None:
		dlg = self.dlg
		if not dlg:
			return
		self.dlg = None
		dlg.destroyDialog()

	def onClose(self, event: wx.Event):
		self._destroyDialog()

	def terminate(self):
		self._destroyDialog()
		super().terminate()
