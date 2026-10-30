# Synthetic Evaluation Corpus: 6-Month Simulated Project

This dataset provides a pre-packaged, offline-accessible simulated repository containing 6 months of realistic engineering exhaust to evaluate ContinuumAI during hackathon judging.

### Contents:
- **45 Git Commits & Diffs:** Feature development, refactors, hotfixes, and staging configurations.
- **20 Pull Request Reviews:** Architectural debates, reviewer questions, and merged vs. abandoned solutions.
- **80 Slack / Discord Message Logs:** Design channel banter, incident triage, and informal agreements.
- **15 Jira / Linear Tasks:** Acceptance criteria, priority shifts, and closed tickets.

### Intentional Injected Edge Cases for Verification:
1. **Contradiction #1 (Database Architecture):** Slack debate proposes migrating cache to Memcached; Jira marks an exploratory spike; merged Git PR finalizes Redis Cluster. *(Tests TRE circuit breaker).*
2. **Contradiction #2 (Authentication Strategy):** PR discussion proposes custom Supabase wrapper; commit history reveals rollback to custom JWT auth due to enterprise cookie compliance.
3. **Knowledge Gap #3 (Undocumented Staging Secret):** Service deployment requires an undocumented environment variable `X_INTERNAL_SYNC_SALT` mentioned only once in a closed PR comment.
