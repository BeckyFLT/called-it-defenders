# called-it-defenders

Data bridge for the Called It weekly defending-party research agent.
A scheduled Claude routine researches pending by-election defenders and
appends answers to defender-signoffs.json; the fp-do-ingest worker
fetches the raw file every Friday and applies it to the database.
See WEEKLY_DEFENDERS_AGENT.md for the agent instructions.
