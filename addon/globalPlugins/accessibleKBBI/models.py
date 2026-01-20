from dataclasses import dataclass, field


@dataclass
class Label:
	code: str
	name: str
	kind: str


@dataclass
class Definition:
	definition: str
	referencedLemma: str = ""
	labels: list[Label] = field(default_factory=list)
	usageExamples: list[str] = field(default_factory=list)


@dataclass
class Entry:
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
	lemma: str
	entries: list[Entry] = field(default_factory=list)
