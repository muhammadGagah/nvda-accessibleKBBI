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
from typing import Optional
from .interface import KBBIDialog

addonHandler.initTranslation()
_ = wx.GetTranslation


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.dlg: Optional[KBBIDialog] = None

	@scriptHandler.script(
		description=_("Buka Accessible KBBI."),
		gesture="kb:NVDA+alt+k",
	)
	def script_showSearchDialog(self, gesture: inputCore.InputGesture):
		if self.dlg:
			self.dlg.Raise()
			self.dlg.SetFocus()
			ui.message(_("Dialog Accessible KBBI sudah terbuka."))
			return

		self.dlg = KBBIDialog(gui.mainFrame)
		self.dlg.Show()
		self.dlg.Bind(wx.EVT_CLOSE, self._on_close)

	@scriptHandler.script(
		description=_("Cari teks terpilih di Accessible KBBI."),
		gesture="kb:NVDA+shift+alt+k",
	)
	def script_searchSelection(self, gesture: inputCore.InputGesture):
		if self.dlg:
			self.dlg.Raise()
			self.dlg.SetFocus()
			ui.message(_("Dialog Accessible KBBI sudah terbuka."))
			return

		text = self._get_selected_text()
		if not text:
			ui.message(_("Tidak ada teks yang dipilih."))
			return

		self.dlg = KBBIDialog(gui.mainFrame)
		self.dlg.Show()
		self.dlg.Bind(wx.EVT_CLOSE, self._on_close)

		self.dlg.search_box.SetValue(text)
		self.dlg.on_search_click(None)

	def _get_selected_text(self) -> Optional[str]:
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

	def _on_close(self, event):
		if self.dlg:
			wx.CallAfter(self.dlg.Destroy)
			self.dlg = None
