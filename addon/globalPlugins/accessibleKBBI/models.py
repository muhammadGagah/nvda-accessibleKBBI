from dataclasses import dataclass, field


@dataclass
class Label:
	"""
	Represents a label or tag associated with a dictionary definition.

	:param code: The short code for the label (e.g., 'n', 'v', 'ki').
	:type code: str
	:param name: The full name of the label (e.g., 'Nomina', 'Verba').
	:type name: str
	:param kind: The category of the label (e.g., 'Kelas Kata', 'Ragam').
	:type kind: str
	"""
	code: str
	name: str
	kind: str


@dataclass
class Definition:
	"""
	Represents a single definition of an entry.

	:param definition: The text of the definition.
	:type definition: str
	:param referencedLemma: A lemma referenced by this definition, if any.
	:type referencedLemma: str
	:param labels: A list of labels categorizing this definition.
	:type labels: list[Label]
	:param usageExamples: A list of examples showing how the word is used.
	:type usageExamples: list[str]
	"""
	definition: str
	referencedLemma: str = ""
	labels: list[Label] = field(default_factory=list)
	usageExamples: list[str] = field(default_factory=list)


@dataclass
class Entry:
	"""
	Represents a dictionary entry including its forms and definitions.

	:param entry: The headword of the entry.
	:type entry: str
	:param baseWord: The base word (kata dasar) if this is a derived word.
	:type baseWord: str
	:param pronunciation: The pronunciation guide.
	:type pronunciation: str
	:param definitions: A list of definitions for this entry.
	:type definitions: list[Definition]
	:param derivedWords: A list of derived words (kata turunan).
	:type derivedWords: list[str]
	:param compoundWords: A list of compound words (gabungan kata).
	:type compoundWords: list[str]
	:param metaphors: A list of metaphors (kiasan).
	:type metaphors: list[str]
	:param proverbs: A list of proverbs (peribahasa).
	:type proverbs: list[str]
	"""
	entry: str
	baseWord: str
	pronunciation: str
	definitions: list[Definition] = field(default_factory=list)
	derivedWords: list[str] = field(default_factory=list)
	compoundWords: list[str] = field(default_factory=list)
	metaphors: list[str] = field(default_factory=list)
	proverbs: list[str] = field(default_factory=list)


@dataclass
class KBBIResult:
	"""
	Represents the result returned from a KBBI API search.

	:param lemma: The original query or lemma searched.
	:type lemma: str
	:param entries: A list of dictionary entries found for the lemma.
	:type entries: list[Entry]
	"""
	lemma: str
	entries: list[Entry] = field(default_factory=list)
