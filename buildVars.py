from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries, SpeechDictionaries
from site_scons.site_tools.NVDATool.utils import _

addon_info = AddonInfo(
	addon_name="accessibleKBBI",
	addon_summary=_("Accessible KBBI - Indonesian Dictionary Search"),
	addon_description=_("""Seamlessly search definitions in the Kamus Besar Bahasa Indonesia (KBBI), the official standard dictionary of the Indonesian language.
Features include looking up selected text effectively, Word of the Day, and favorite entries, all accessible directly from NVDA."""),
	addon_version="1.4.0",
	addon_changelog=_("""Tested with NVDA 2026.3.
New Suggestions button lists KBBI words that start with the typed text.
When a word is not found, similar words are suggested.
New Related words button opens base, derived, compound, and variant words directly.
Results now show non-standard forms, variants, and precategorical entries.
New option to show full label names, such as Nomina instead of n.
Results now include metaphors (kiasan), which were previously hidden.
History and favorites lists no longer hide their Close button on scaled displays.
Searching for text that contains a slash now looks up the right entry.
Results no longer fail when the KBBI service adds new label information.
History and favorites are saved safely, so an interrupted save cannot erase them.
The add-on now uses its own translation catalog."""),
	addon_author="Muhammad <muha.aku@gmail.com>",
	addon_url="https://github.com/muhammadGagah/nvda-accessibleKBBI/",
	addon_sourceURL="https://github.com/muhammadGagah/nvda-accessibleKBBI/",
	addon_docFileName="readme.html",
	addon_minimumNVDAVersion="2024.1",
	addon_lastTestedNVDAVersion="2026.3",
	addon_updateChannel=None,
	addon_license="GPL-2.0",
	addon_licenseURL="https://www.gnu.org/licenses/gpl-2.0.html",
)

pythonSources: list[str] = ["addon/globalPlugins/accessibleKBBI/*.py", "addon/installTasks.py"]

i18nSources: list[str] = pythonSources + ["buildVars.py"]

excludedFiles: list[str] = [
	"__pycache__/*",
	"**/__pycache__/*",
	"*.pyc",
	"*.pyo",
	"globalPlugins/accessibleKBBI/accessibleKBBI.json",
]

baseLanguage: str = "id"

markdownExtensions: list[str] = []

brailleTables: BrailleTables = {}

symbolDictionaries: SymbolDictionaries = {}

speechDictionaries: SpeechDictionaries = {}
