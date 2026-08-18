# Security

## Reporting a vulnerability

Open a [private security advisory](https://github.com/DoctorYanmar/books/security/advisories/new)
on this repository. Please do not open a public issue for anything exploitable.

There is no service and no server here: the pipeline is a set of local scripts run by hand, so the
realistic surface is small. Reports about the following are still welcome:

- **Path handling in `scripts/extract.py`.** It reads archives (EPUB is a ZIP) and writes files
  under a directory you name. A crafted archive that escapes that directory would be a real bug.
- **Anything in the scripts that executes content from a book file** rather than treating it as
  text.
- **Generated pages.** `page.html` is opened in a browser and inlines text taken from a book. A
  path from book content to script execution in the page would be a real bug; `page_lint.py`
  checks that the page loads nothing but Google Fonts, but it does not sanitise content.

## What is not a vulnerability here

- The pipeline reads books you supply. It does not fetch, unlock or redistribute them, and it
  handles no credentials, no accounts and no network services of its own.
- Study packs contain long verbatim quotes from copyrighted books. That is the point of the tool
  and the reason `input/` and `library/` are gitignored in full. Committing a pack is a mistake to
  fix, not a vulnerability to report.

## If you accidentally commit book content

Remove it from history before pushing — once pushed, it stays reachable by commit SHA even after a
force-push, which is [GitHub's documented
behaviour](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
Use `git filter-repo` (v2.47+) to purge it, and treat any clone or fork made in the meantime as
still holding the old history.
