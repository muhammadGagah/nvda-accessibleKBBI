import addonHandler
import gui
import wx

addonHandler.initTranslation()
_ = wx.GetTranslation


def onInstall():
	# Translators: Message shown after Accessible KBBI is installed.
	message = _(
		"Terima kasih telah menginstal Accessible KBBI! "
		"Semoga add-on ini membantu Anda belajar dan bekerja lebih produktif. "
		"Salam hangat dari Muhammad!",
	)
	# Translators: Title of the Accessible KBBI install confirmation dialog.
	title = _("Accessible KBBI")
	gui.messageBox(
		message,
		title,
		wx.OK | wx.ICON_INFORMATION,
	)
