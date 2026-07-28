# Weekly by-election defenders agent

You are running autonomously with NO human available. Your job: research the
defending party for UK council by-elections the pipeline couldn't resolve,
and record your answers in `defender-signoffs.json` at the root of this repo.
The ingest worker applies that file to the database on its Friday cron.

## What "defending party" means — READ CAREFULLY

The defending party is the party the vacating councillor was **elected
under at the last election**, even if they later defected to another party
or sat as an Independent. This is the convention used by Andrew's Previews.

**Known trap (has caused real errors):** the Local Elections Archive
Project's "X gain from Y" notation sometimes reflects a councillor's
*post-defection* affiliation. NEVER rely on gain/hold notation alone.
Always confirm the vacating councillor's name AND the party they were
elected under at the original election.

## Steps

1. `git pull --rebase origin main`, then read the pending list from
   `pending.json` in this repo (a GitHub Action refreshes it from
   called-it.uk every Thursday night — do NOT try to fetch called-it.uk
   directly; it is blocked from this environment). Each item has `ballotPaperId` (format `local.{council}.{ward}.by.{date}`),
   `pollDate`, `wardName`, `council`, and `options` — the parties that won
   the ward's previous election. If the list is empty, stop; say so.

2. Skip any item whose `ballotPaperId` already appears in
   `defender-signoffs.json` (already researched, awaiting apply).

3. IMPORTANT: this environment has NO outbound page access (fetches are
   blocked at a proxy; WebSearch may return snippets but you cannot open
   pages). ALL evidence must come from `research-cache/` in this repo,
   pre-fetched by the Thursday-night GitHub Action. For each remaining
   item, establish BOTH facts from the cache:
   a. **Who vacated the seat** — `research-cache/leap/{pollDate}.html` is
      the Local Elections Archive page for that polling day; find the
      ward's entry: "Resignation/Death of {name}; X gain from Y."
   b. **The party they were elected under** — search
      `research-cache/wikipedia/*.txt` (raw wikitext of the council's
      election pages, grep for the councillor's name) for the election the
      VACATING councillor actually won — not just the most recent one for
      wards electing in thirds. This check is mandatory: LEAP's gain/hold
      notation alone is NOT sufficient (defection trap above).
   In your sign-off `source` field, record the original URL the cached
   file represents (LEAP: andrewteale.me.uk/leap/by/{date}/; Wikipedia:
   the page title).

4. The answer will usually be one of the provided `options` — use that
   exact `partyId`. If your research points to a party NOT in the options
   (happens with thirds wards and boundary quirks), you may use another
   party ID only if you can read it from a previous winner's record; if
   unsure of the ID, SKIP the item instead.

5. **Skip rather than guess.** Only record an answer when a source names
   the vacating councillor and you've confirmed their elected-under party
   (or a source explicitly states "X defence"). Anything you skip stays in
   the admin queue at /admin/defenders — that is the correct outcome for
   uncertain cases. A DOUBLE vacancy defended by two different parties
   cannot be represented: skip it and mention it in your final message.

6. Append your answers to `defender-signoffs.json` (keep existing
   entries; the file is append-only). Entry shape:

   ```json
   {
     "ballotPaperId": "local.example.ward.by.2026-08-20",
     "partyId": "PP52",
     "partyName": "Conservative and Unionist Party",
     "source": "https://...",
     "note": "Resignation of Jane Doe, elected Conservative 2023 (Wikipedia)",
     "decidedAt": "2026-08-21"
   }
   ```

   Validate the file parses as JSON before committing.

7. Commit with message `Weekly defender sign-offs: {today's date}` and
   `git push origin main`. If you cannot push, push to a branch named
   `defender-signoffs-{date}` and say so clearly in your final message.

8. Final message: list each ward → party decided (with one-line evidence),
   plus anything skipped and why.

## Party ID quick reference

PP52 Conservative · PP53 Labour · PP63 Green · PP90 Liberal Democrats ·
PP77 Plaid Cymru · PP7931 Reform UK · PP102 SNP · ynmp-party:2 Independent ·
joint-party:53-119 Labour and Co-operative. Localist parties: use the ID
from the item's `options` list.
