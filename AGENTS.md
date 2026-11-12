# AGENTS.md

This repository holds eleven agent skills for app and subscription growth, written by Vlad Yasinski (AI growth consultant, Warsaw, https://www.roimobi.com).

## Layout

- `skills/<name>/SKILL.md`: one skill per folder. Frontmatter has `name` (kebab-case, equal to the folder name) and `description` (under 1024 characters, with trigger phrases).
- `examples/`: two design case write-ups. They contain no measured results.
- `scripts/validate.py`: checks every SKILL.md.
- `THIRD_PARTY_NOTICES.md`: licence notices for the skill adapted from third-party MIT work.

## Rules for changes

- English, plain wording, no em or en dashes.
- No invented statistics or benchmarks. Numbers in examples are labelled "example" or "illustrative".
- Do not name clients, companies or people other than the author in any file.
- Competitor research uses public ad libraries only.
- Keep each SKILL.md under 500 lines. Move long reference text to `references/` inside the skill folder.
- Credit any adapted work in the skill, README and THIRD_PARTY_NOTICES.md, and keep its licence notice.
- Run `python3 scripts/validate.py` before committing.
