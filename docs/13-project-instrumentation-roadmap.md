# Project Instrumentation Roadmap

This is the meta-workstream: the system that keeps everything measurable and reviewable.

## Phase P0: boot

- repo skeleton exists
- policies + templates exist
- issue forms exist

## Phase P1: rubrics v1

- descriptor rubrics for core deliverables
- writing quality rubric included on every memo

## Phase P2: validators

- time cap validator
- reference format validator
- submission packet completeness validator

## Phase P3: dashboard MVP

- Streamlit reads GitHub metadata (Issues/PRs/CI), logs, reviews
- Review Console writes review YAML

## Phase P4: static dashboard + report PRs

- scheduled build writes dashboard markdown and opens a PR (no direct pushes)

## Phase P5: tighten

- auto-open revision issues
- richer Workflows ecosystem linkage reporting