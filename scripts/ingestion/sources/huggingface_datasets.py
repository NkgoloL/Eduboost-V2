"""
HuggingFace Datasets Downloader
================================
Downloads open educational datasets from HuggingFace Hub using the
`datasets` library and emits RawContent records for each item.

No scraping involved — these are clean, structured datasets distributed
under permissive licenses (MIT, Apache 2, CC-BY variants).

Key datasets:
  - ARC (AI2 Reasoning Challenge) — grade-school science MCQs
  - GSM8K — grade-school math word problems with CoT solutions
  - MATH — competition math with step-by-step solutions
  - MMLU — HS/college level multi-subject MCQs
  - SciQ — science passage + MCQ
  - RACE — reading comprehension (middle + high school)
  - AfriQA — African QA (includes Zulu, Xhosa, Afrikaans)
"""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator

from scripts.ingestion.config import HF_DATASETS
from scripts.ingestion.models import RawContent
from scripts.ingestion.sources.base import BaseScraper

logger = logging.getLogger(__name__)


class HuggingFaceDatasetsScraper(BaseScraper):
    """
    Downloads datasets from HuggingFace Hub.

    Runs synchronously inside an async executor to avoid blocking
    the event loop during dataset downloads.
    """

    def __init__(
        self,
        dataset_ids: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        # HF doesn't need a real SourceConfig — use a dummy one
        from scripts.ingestion.config import SourceConfig
        cfg = SourceConfig(
            id             = "huggingface",
            name           = "HuggingFace Hub",
            base_url       = "https://huggingface.co",
            robots_txt_url = "https://huggingface.co/robots.txt",
            rate_limit_rps = 1.0,
            license        = "various",
        )
        super().__init__(config=cfg, **kwargs)
        self._dataset_ids = dataset_ids  # None = all

    async def scrape(self) -> AsyncIterator[RawContent]:
        try:
            import datasets as hf_datasets   # noqa: F401
        except ImportError:
            logger.error(
                "HuggingFace `datasets` not installed — "
                "run: pip install datasets --break-system-packages"
            )
            return

        catalogue = [
            d for d in HF_DATASETS
            if (self._dataset_ids is None or d["id"] in self._dataset_ids)
        ]
        self._total = len(catalogue)

        for i, ds_cfg in enumerate(catalogue):
            if self._at_limit():
                break
            self._emit(i, self._total, f"Dataset: {ds_cfg['id']}")
            async for item in self._load_dataset(ds_cfg):
                if self._at_limit():
                    return
                yield item

    async def _load_dataset(self, ds_cfg: dict[str, Any]) -> AsyncIterator[RawContent]:
        """Load a single HF dataset configuration and emit records."""
        import asyncio
        import functools
        from datasets import load_dataset  # type: ignore

        hf_id   = ds_cfg["hf_id"]
        subsets = ds_cfg.get("subsets") or [None]
        splits  = ds_cfg.get("splits", ["train"])
        license = ds_cfg.get("license", "unknown")

        for subset in subsets:
            for split in splits:
                try:
                    loader = functools.partial(
                        load_dataset,
                        hf_id,
                        subset,
                        split=split,
                    )
                    loop = asyncio.get_event_loop()
                    ds   = await loop.run_in_executor(None, loader)
                except Exception as exc:   # noqa: BLE001
                    logger.warning("[HF] Failed to load %s/%s/%s: %s",
                                   hf_id, subset, split, exc)
                    continue

                logger.info("[HF] Loaded %s/%s/%s — %d rows",
                            hf_id, subset or "", split, len(ds))

                for row in ds:
                    if self._at_limit():
                        return
                    item = self._row_to_raw(row, ds_cfg, subset, split, license)
                    if item:
                        self._done += 1
                        yield item

    @staticmethod
    def _row_to_raw(
        row: dict[str, Any],
        ds_cfg: dict[str, Any],
        subset: str | None,
        split: str,
        license: str,
    ) -> RawContent | None:
        """Convert a HF row to a RawContent record using per-dataset field heuristics."""
        ds_id  = ds_cfg["id"]
        grades = ds_cfg.get("grade_range", (1, 12))
        ds_cfg.get("subjects", [])

        # ── ARC ─────────────────────────────────────────────────────────────
        if ds_id == "arc":
            q       = row.get("question", "")
            choices = row.get("choices", {})
            labels  = choices.get("label", [])
            texts   = choices.get("text",  [])
            ans_key = row.get("answerKey", "")
            answer  = ""
            if ans_key and labels and texts:
                try:
                    idx    = labels.index(ans_key)
                    answer = texts[idx]
                except (ValueError, IndexError):
                    answer = ans_key
            options = texts if texts else []
            option_block = "\n".join(f"{lbl}. {txt}" for lbl, txt in zip(labels, texts))
            raw_text = f"{q}\n\n{option_block}" if option_block else q
            return RawContent(
                source_id  = "huggingface",
                source_internal_id = f"arc_{subset}_{row.get('id', '')}",
                raw_text   = raw_text,
                raw_json   = {"question": q, "options": options, "answer": answer,
                              "subset": subset, "split": split},
                metadata   = {
                    "kind":     "assessment_item",
                    "dataset":  ds_id,
                    "subset":   subset,
                    "subject":  "natural_sciences",
                    "grades":   list(range(*grades)),
                },
                license=license, language="en",
            )

        # ── GSM8K ────────────────────────────────────────────────────────────
        if ds_id == "gsm8k":
            q   = row.get("question", "")
            ans = row.get("answer", "")
            return RawContent(
                source_id  = "huggingface",
                source_internal_id = f"gsm8k_{split}_{hash(q)}",
                raw_text   = q,
                raw_json   = {"question": q, "answer": ans, "split": split},
                metadata   = {
                    "kind":    "worked_example",
                    "dataset": ds_id,
                    "subject": "mathematics",
                    "grades":  list(range(*grades)),
                },
                license=license, language="en",
            )

        # ── MATH (lighteval/MATH) ─────────────────────────────────────────
        if ds_id == "math":
            q    = row.get("problem", "")
            sol  = row.get("solution", "")
            ans  = row.get("answer", "")
            lvl  = row.get("level", "")
            typ  = row.get("type", subset or "")
            return RawContent(
                source_id  = "huggingface",
                source_internal_id = f"math_{typ}_{hash(q)}",
                raw_text   = q,
                raw_json   = {"question": q, "solution": sol, "answer": ans,
                              "level": lvl, "type": typ},
                metadata   = {
                    "kind":       "worked_example",
                    "dataset":    ds_id,
                    "subject":    "mathematics",
                    "topic":      typ,
                    "difficulty": lvl,
                    "grades":     list(range(*grades)),
                },
                license=license, language="en",
            )

        # ── MMLU ─────────────────────────────────────────────────────────────
        if ds_id == "mmlu":
            q       = row.get("question", "")
            options = row.get("choices", [])
            ans_idx = row.get("answer", -1)
            answer  = options[ans_idx] if isinstance(ans_idx, int) and options else str(ans_idx)
            subj    = (subset or "").replace("_", " ")
            option_block = "\n".join(f"{chr(65+i)}. {o}" for i, o in enumerate(options))
            raw_text = f"{q}\n\n{option_block}" if option_block else q
            return RawContent(
                source_id  = "huggingface",
                source_internal_id = f"mmlu_{subset}_{hash(q)}",
                raw_text   = raw_text,
                raw_json   = {"question": q, "options": options,
                              "answer": answer, "subject_label": subj},
                metadata   = {
                    "kind":    "assessment_item",
                    "dataset": ds_id,
                    "subset":  subset,
                    "subject": subj,
                    "grades":  list(range(*grades)),
                },
                license=license, language="en",
            )

        # ── SciQ ─────────────────────────────────────────────────────────────
        if ds_id == "sciq":
            q           = row.get("question", "")
            support     = row.get("support", "")
            correct     = row.get("correct_answer", "")
            distractors = [row.get(f"distractor{i}", "") for i in range(1, 4)]
            options     = [correct] + [d for d in distractors if d]
            return RawContent(
                source_id  = "huggingface",
                source_internal_id = f"sciq_{hash(q)}",
                raw_text   = f"{support}\n\n{q}",
                raw_json   = {"question": q, "support": support,
                              "options": options, "answer": correct},
                metadata   = {
                    "kind":    "assessment_item",
                    "dataset": ds_id,
                    "subject": "natural_sciences",
                    "grades":  list(range(*grades)),
                },
                license=license, language="en",
            )

        # ── RACE ─────────────────────────────────────────────────────────────
        if ds_id == "race":
            passage = row.get("article", "")
            q       = row.get("question", "")
            options = row.get("options", [])
            ans_key = row.get("answer", "")
            ans_map = {"A": 0, "B": 1, "C": 2, "D": 3}
            answer  = options[ans_map[ans_key]] if ans_key in ans_map and options else ans_key
            level   = subset or ""
            grade_map = {"middle": [6, 7, 8], "high": [9, 10, 11, 12]}
            return RawContent(
                source_id  = "huggingface",
                source_internal_id = f"race_{level}_{hash(q)}",
                raw_text   = f"PASSAGE:\n{passage}\n\nQUESTION:\n{q}",
                raw_json   = {"passage": passage, "question": q,
                              "options": options, "answer": answer},
                metadata   = {
                    "kind":    "assessment_item",
                    "dataset": ds_id,
                    "subject": "english_home_language",
                    "subset":  level,
                    "grades":  grade_map.get(level, list(range(*grades))),
                },
                license=license, language="en",
            )

        # ── AfriQA (SA languages) ─────────────────────────────────────────
        if ds_id == "afriqa":
            q    = row.get("question", "")
            ans  = row.get("answer", {}).get("text", [""])[0] if isinstance(
                       row.get("answer"), dict) else row.get("answer", "")
            lang_map = {"zul": "zu", "xho": "xh", "afr": "af"}
            lang = lang_map.get(subset or "", "en")
            return RawContent(
                source_id  = "huggingface",
                source_internal_id = f"afriqa_{subset}_{hash(q)}",
                raw_text   = q,
                raw_json   = {"question": q, "answer": ans, "lang": lang},
                metadata   = {
                    "kind":         "assessment_item",
                    "dataset":      ds_id,
                    "language":     lang,
                    "jurisdiction": "za",
                    "grades":       list(range(*grades)),
                },
                license=license, language=lang,
            )

        # ── Generic fallback ─────────────────────────────────────────────────
        text = (
            row.get("question") or row.get("text") or
            row.get("input") or row.get("premise") or
            json.dumps(row)
        )
        return RawContent(
            source_id  = "huggingface",
            source_internal_id = f"{ds_id}_{hash(text)}",
            raw_text   = str(text),
            raw_json   = dict(row),
            metadata   = {
                "kind":    "unknown",
                "dataset": ds_id,
                "subset":  subset,
                "grades":  list(range(*grades)),
            },
            license=license, language="en",
        )
