from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _

addon_info = AddonInfo(
	addon_name="accessibleKBBI",
	addon_summary=_("Accessible KBBI - Indonesian Dictionary Search"),
	addon_description=_("""Seamlessly search definitions in the Kamus Besar Bahasa Indonesia (KBBI), the official standard dictionary of the Indonesian language.
Features include looking up selected text effectively, Word of the Day, and favorite entries, all accessible directly from NVDA."""),
	addon_version="1.0",
	addon_changelog=_("""Initial Release."""),
	addon_author="Muhammad <muha.aku@gmail.com>",
	addon_url="https://github.com/muhammadGagah/nvda-accessibleKBBI/",
	addon_sourceURL="https://github.com/muhammadGagah/nvda-accessibleKBBI/",
	addon_docFileName="readme.html",
	addon_minimumNVDAVersion="2024.1",
	addon_lastTestedNVDAVersion="2025.3.2",
	addon_updateChannel=None,
	addon_license="GPL-2.0",
	addon_licenseURL="https://www.gnu.org/licenses/gpl-2.0.html",
)

pythonSources: list[str] = ["addon/globalPlugins/accessibleKBBI/*.py", "addon/installTasks.py"]

i18nSources: list[str] = pythonSources + ["buildVars.py"]

excludedFiles: list[str] = []

baseLanguage: str = "id"

markdownExtensions: list[str] = []

brailleTables: BrailleTables = {}

symbolDictionaries: SymbolDictionaries = {}
