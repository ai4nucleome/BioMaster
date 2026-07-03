# biomaster-resume

Purpose: Resume an interrupted run from run_states.

Usage: `/biomaster-resume <args>`

## Rule

Resume through `biomaster-intake` as the visible primary agent. Read `run_states.phase`, summarize the current phase to the user, then continue only through the next legal phase transition.

Do not jump directly to Plan/Execute/Check/Debug unless the run state proves all previous phases are complete.
