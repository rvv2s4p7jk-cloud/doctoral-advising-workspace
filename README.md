# Scholar · Doctoral Research & Advising Workspace

A working local portfolio application connecting topic approvals, chapter milestones, structured progress reports, and defense corrections.

**Release: v1.0 demo. Fictional accounts and institution. Intended for local review, not production student records.**

## Start in five minutes

Requires Python 3.11 or newer. Open a terminal inside the extracted project folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

Open **http://127.0.0.1:8001**. Port 8001 leaves the escalation-intelligence project on port 8000. On Windows, activate using `.venv\Scripts\activate`.

Docker alternative: `docker compose up --build`. Docker configuration is supplied but its image build was not validated in the creation environment.

## Demo accounts

Every account uses password **demo-research**. Sign out to switch roles.

| Login | Role | Demonstrates |
|---|---|---|
| candidate | Doctoral researcher | Submit topic and chapters, check-ins, responses, corrections |
| advisor | Advisor | Endorse topics, accept chapters, issue reports, confirm readiness |
| university | University office | Final topic approval, notification acknowledgment, scheduling, submission |
| chair | Committee chair | Official defense outcome and final correction clearance |
| member | Committee member | Individual feedback and correction verification |

The shared record starts with a draft topic. The Advisor also has a separate own-research workspace, invisible to other accounts. Own-research topic acceptance is recorded by the Advisor; it does not imply university approval. New shared workspaces are automatically assigned to all fictional demo accounts. This behavior must be replaced by explicit invitations before real deployment.

## End-to-end walkthrough

1. **Candidate:** Topic & chapters → Submit topic.
2. **Advisor:** Endorse for university.
3. **University:** Approve topic with a decision reference.
4. **Candidate:** Start Chapter 1, then submit it.
5. **Advisor:** Move to Advisor review, request revisions or accept. Repeat for Chapters 2–5. Earlier chapters must be accepted first.
6. **Candidate:** Prepare a check-in under Meetings & reports.
7. **Advisor:** Issue a progress report, including separate ratings for research quality, professionalism and timeline. Add follow-up actions under Tasks & alignment.
8. **Candidate:** Acknowledge and respond. Amended reports retain prior versions.
9. **Advisor:** Record proposal, research execution and full-manuscript gates; confirm defense readiness. Prepare the notification draft, then record that it was actually sent externally.
10. **University:** Acknowledge receipt and record official defense arrangements.
11. **Chair/member:** Record feedback; chair records the official outcome.
12. **Candidate:** Submit correction responses. Assigned member or chair verifies them.
13. **Chair:** Confirm final clearance; required corrections must be accepted.
14. **University:** Record final submission confirmation.

The application records external decisions and communications; it does not send email or approve work autonomously.

## Included capabilities

- Role-authorized actions and authenticated local demo sessions.
- Topic approval and versioned topic changes; approved topic stays active during review.
- Five chapter milestones with editable due dates and validated transitions.
- Original/current completion targets, duration, weekly availability and institutional deadline warning.
- Multiple department/program labels on workspaces and versioned local program settings.
- Check-ins, report amendments, red/yellow/green assessments, improvement plans and responses.
- Action register, optional-hypothesis research alignment matrix, and AI-use documentation.
- Separate readiness, notification, scheduling, outcome, corrections and final-submission records.
- Print/save PDF of the complete research record, CSV timeline, ICS calendar and JSON backup.
- SQLite persistence and transactional revision guards preventing stale overwrites.

## Validation

```bash
python -m pytest -q
node --check frontend/app.js
```

DOM-based smoke checks also passed for all five role logins, all six dashboard sections, and the topic submission form. To reproduce, start the server on port 8001, then run `npm install` and `npm run test:ui` with Node 22 or newer. These checks do not replace a visual browser review.

See tests for topic authority, approval gates, chapter sequence, topic preservation, report versions, notification prerequisites, committee corrections, authentication, private-record isolation, stale-write rejection, persistence, exports and month-end scheduling.

## Honest release boundaries

This is a demonstrable application, not a university information system. Default accounts are public; binding must stay on localhost. University policy examples are illustrative. No actual university policy compliance is claimed.

Not implemented: account provisioning/invitations, SSO, centrally administered university/department hierarchies, configurable committee rosters and sign-off authority, document uploads, DOCX export, automated email, automatic forecast/capacity modeling, committee-comment reconciliation, formal leave/extension adjudication, or AI generation/detection. Program labels and a limited versioned settings editor are implemented; complete institutional template administration remains future work. Chapter gates use the five-chapter praxis/dissertation demonstration structure.

PDF export uses the browser's Print → Save as PDF. No native PDF generation or visual browser QA was completed in this environment. CSV and calendar export and full JSON records are server-generated.

See [architecture](docs/architecture.md), [security and deployment](docs/security.md), and [requirements coverage](docs/coverage.md).

Independent project: no confidential institutional data, proprietary procedures or real student records. MIT licensed.
