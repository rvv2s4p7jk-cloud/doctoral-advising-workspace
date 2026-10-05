# Security and deployment scope

Ship this release as source code and a localhost demo. Do not deploy it publicly with the demo accounts or enter real student information.

Implemented: PBKDF2 password hashing with unique salts; random, expiring server-side sessions; HTTP-only SameSite=Strict cookies; workspace assignment checks; server-side role authorization; parameterized SQL; transaction rollback; stale-write guards; escaped HTML rendering; CSV formula-prefix neutralization.

Remaining production work: provisioning and invitation approvals, TLS and Secure cookies, institutional identity integration, login throttling, recovery/rotation procedures, encrypted storage and backups, audit retention and tamper resistance, document permissions, retention policy, and institutional review. Shared projects deliberately grant all fictional accounts access. Role selection is a login convenience, not an authorization mechanism.

Academic decisions are explicit human records. The AI notice is proposed wording and does not authorize AI use. No LLM, originality score or AI-authorship detection is included. Defense outcomes are recorded by the chair rather than inferred from ratings.
