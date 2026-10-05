# Architecture

FastAPI serves a same-origin HTML/CSS/JavaScript dashboard. SQLite stores users, assignments, expiring sessions, and JSON workspace records. Workflow rules are centralized in backend/domain.py; the frontend presents available actions, and the server independently checks permissions and prerequisites.

A mutation obtains a write transaction, checks record revision, validates the action, appends an actor/time/revision audit event, and commits. Failure rolls back the complete record. Report versions are retained; topic requests do not replace approved topics until accepted. Workspace template changes retain prior versions and affect only that workspace.

Authorization uses both an assigned workspace and the authenticated role. Personal Advisor records are not assigned to other accounts. Committee members verify their own corrections; the chair may consolidate verification. Local audit history is not tamper-proof against database owners.

The initial database is seeded once. Dates are ISO calendar dates. add_months handles month-end and leap-year dates. Completion target revisions never change the institutional deadline. Automatic forecasting and institutional exception workflows are future features.

Extension path: normalized PostgreSQL tables, invitations and institutional SSO, committee assignments, versioned program templates, upload storage with access checks, DOCX/PDF rendering, authorized messaging and institutional integrations.
