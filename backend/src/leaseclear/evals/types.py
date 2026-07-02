from __future__ import annotations

from dataclasses import dataclass

from leaseclear.types import ChunkBase, GenerationResult, ValidationResult


@dataclass(frozen=True)
class ClaimJudgment:
    text: str
    cited_ids: list[str]
    supported_by_citation: bool
    supported_by_context: bool


@dataclass(frozen=True)
class JudgeVerdict:
    claims: list[ClaimJudgment]

    @property
    def faithfulness(self) -> float | None:
        if not self.claims:
            return None
        return sum(c.supported_by_context for c in self.claims) / len(self.claims)

    @property
    def citation_precision(self) -> float | None:
        if not self.claims:
            return None
        return sum(c.supported_by_citation for c in self.claims) / len(self.claims)

    @property
    def hallucination_rate(self) -> float | None:
        if not self.claims:
            return None
        return sum(not c.supported_by_context for c in self.claims) / len(self.claims)


@dataclass
class CaseResult:
    item_id: str
    item_type: str
    question: str
    retrieved: list[ChunkBase]
    retrieval_hit: bool | None
    result: GenerationResult
    validation: ValidationResult
    refused: bool
    expected_refusal: bool
    correctly_refused: bool
    judge: JudgeVerdict | None
    ttft_s: float | None
    total_s: float
    input_tokens: int | None
    output_tokens: int | None
    error: str | None = None
