from dataclasses import dataclass, field


def doc_id(family: str, name: str) -> str:
    return f"{family}-{name}"


@dataclass
class DocMeta:
    name: str
    title: str
    tags: list[str]
    eval_targets: list[str] = field(default_factory=list)

    def id_for(self, family: str) -> str:
        return doc_id(family, self.name)
