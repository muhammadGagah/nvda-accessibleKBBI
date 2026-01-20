import gui
import wx


def onInstall():
	gui.messageBox(
		"Terima kasih telah menginstal Accessible KBBI! Semoga add-on ini membantu Anda belajar dan bekerja lebih produktif. Salam hangat dari Muhammad!",
		"Accessible KBBI",
		wx.OK | wx.ICON_INFORMATION,
	)
