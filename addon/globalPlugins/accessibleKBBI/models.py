from dataclasses import dataclass, field


@dataclass
class Label:
	"""Label or tag associated with a dictionary definition."""

	code: str
	name: str
	kind: str


@dataclass
class Definition:
	"""Single definition of a dictionary entry."""

	definition: str
	referencedLemma: str = ""
	labels: list[Label] = field(default_factory=list)
	usageExamples: list[str] = field(default_factory=list)


@dataclass
class Entry:
	"""Dictionary entry including forms and definitions."""

	entry: str
	baseWord: str
	pronunciation: str
	definitions: list[Definition] = field(default_factory=list)
	derivedWords: list[str] = field(default_factory=list)
	compoundWords: list[str] = field(default_factory=list)
	metaphors: list[str] = field(default_factory=list)
	proverbs: list[str] = field(default_factory=list)
	# Bentuk tidak baku, e.g. "apotik" for "apotek".
	nonStandardWords: list[str] = field(default_factory=list)
	# Varian that have their own dictionary entry, e.g. "udeh" for "ude".
	variants: list[str] = field(default_factory=list)
	# Other ways to refer to the entry, which may have no entry of their own.
	entryVariants: list[str] = field(default_factory=list)
	# Prakategorial: no meaning on its own until affixed; has no definitions.
	isPrecategorical: bool = False


@dataclass
class KBBIResult:
	"""Result returned from a KBBI API search."""

	lemma: str
	entries: list[Entry] = field(default_factory=list)
