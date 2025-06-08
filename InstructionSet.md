You are an AI development agent. Your goal is to build a fully generic, example-driven Documentation Management CLI tool (“DocMan”) that users can drop into any monorepo—and immediately try it out on their own codebase (e.g. DynaFlow). Your prompt to yourself should drive a step-by-step implementation, with concrete example data modeled on DynaFlow as a demonstration.

Phase 1 – MVP (complete)

Implement a CLI under tools/docman/ that, when pointed at any repo root, will:

1.	Scaffold the project
	•	Create tools/docman/ containing:
	•	cli.py entry script
	•	src/ modules (validators/, indexer.py, reporter.py, utils/)
	•	tests/ with empty test stubs
	•	Makefile (install, check-syntax, run, run-fix, run-verbose, run-report, validate, test, lint, format, type-check, clean, quick-check)
	•	Top-level README.md that includes:
	•	How to install & run
	•	Example invocation on a sample “DynaFlow”-style repo
	•	Sample output snippets
	•	Seed the repo with a small example directory tree (in examples/dynaflow/) that mirrors:
    
    examples/dynaflow/
├── apps/llm/phi4/README.md         ← with correct metadata block  
├── libs/config_utils/README.md  
├── tools/documentation_maintenance/README.md  
└── core/legacy_module/README.md    ← should be ignored  

2.	README Presence Validation
	•	Recursively walk all folders, ignoring (.git/, node_modules/, venv/, __pycache__/, core/).
	•	Require a README.md in each; report missing as 🚧 Missing README: path/to/dir.
	•	Example: on examples/dynaflow/libs/phi4_monitoring/, if no README exists, show it.

3.	Metadata Format Enforcement
	•	In each README.md, parse a block:
            **Status**: ✅ Production Ready  
            **Version**: 1.2.3  
            **Last Updated**: 2025-06-08
	•	Violation → 🚧 Bad metadata in examples/dynaflow/apps/llm/phi4/README.md: missing “Version”.

4.	Link & Date Integrity
	•	Scan each README.md for [text](other/file.md) (skip /core/).
	•	For each link, verify file exists; broken → 🚧 Broken link in ….
	•	If a child’s “Last Updated” > parent’s, update only the parent metadata date to match.
	•	Example: apps/llm/phi4/README.md has date 2025-06-08, but apps/llm/README.md is 2025-05-01; bump parent to 2025-06-08.

5.	Index Management
	•	Open or create DOCUMENTATION_INDEX.md at repo root.
	•	Collect all .md (excluding ignores), detect those not listed in the index.
	•	Append missing entries under headings:

            ## Project Root
            - [README.md](README.md) – ✅ Production Ready – 2025-06-08

            ## Applications
            - [apps/llm/phi4/README.md](apps/llm/phi4/README.md) – 🚧 Draft – 2025-05-10

	•	Example: show a snippet of how examples/dynaflow/DOCUMENTATION_INDEX.md is extended.

6.	Reporting & Exit Codes
	•	Print terminal summary sections with emojis:
	1.	🚧 Missing READMEs (n)
	2.	🚧 Metadata violations (n)
	3.	🚧 Broken links (n)
	4.	🚧 Parent-date bumps applied (n)
	5.	✅ New index entries (n)
	•	Exit 0 if all counts zero; else 1.
	
7.	Tests & README
	•	Write unit tests for each validator and the indexer in tests/.
	•	Flesh out README.md with:
	•	Quick start on the example DynaFlow tree.
	•	Sample Makefile commands.
	•	Expected output screenshots or snippets.

Phase 2 – VS Code Extension (Ausblick)
	•	Scaffold a vscode-docman extension that:
	•	Runs DocMan on file save and via Command Palette.
	•	Shows diagnostics (metadata errors, broken links).
	•	Offers “Fix Index” in the editor.
	•	Respects .docmanrc ignore patterns.

⸻

Phase 3 – Web-UI Dashboard (Ausblick)
	•	Build an Express/Electron app that:
	•	Displays a navigable file tree of .md files.
	•	Lets users validate single files or whole branches.
	•	Shows metadata and link statuses in a sidebar.
	•	Configurable via .docmanrc.

⸻

Phase 4 – MkDocs + Docker Navigation (Ausblick)
	1.	4.1 Setup MkDocs Structure
	•	Create mkdocs.yml
	•	Use Material theme, corporate colors
	•	Define nav: from repo hierarchy
	•	Enable German localization
	2.	4.2 Docker Integration
	•	Write a Dockerfile for MkDocs
	•	Provide docker-compose.yml (dev/prod)
	•	Scripts to build & serve docs
	3.	4.3 Navigation & Features
	•	Advanced section/subsection nav
	•	Full-text search
	•	Automatic cross-references
	•	Corporate branding injection
	4.	4.4 Automation & Integration
	•	Hook mkdocs build into the CLI/Makefile
	•	Auto-regenerate nav on doc changes
	•	Live-reload dev server
	•	Deployment recipes (GitHub Pages, S3)

⸻

Phase 5 – Out-of-the-Box Scaffolding
	•	Provide a Cookiecutter or npm init docman-template:
	•	Generates the full tools/docman/ CLI scaffold
	•	Includes example tree (examples/dynaflow/)
	•	Supplies sample DOCUMENTATION_INDEX.md, README.md, Makefile

⸻

Phase 6 – Release & Community Docs
	•	Adopt SemVer: start at v0.1.0, follow major/minor/patch.
	•	Include CONTRIBUTING.md & CODE_OF_CONDUCT.md.
	•	Write a 1-Minute Quick-Start Guide in the README.
	•	Add GitHub Badges (Build status, Coverage, PyPI).
	•	Maintain CHANGELOG.md with each release.