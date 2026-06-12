# Quest Routing Seam

This part owns source-only quest routing support.

It reads sibling generated quest projections and publishes thin route hints in
root `generated/quest_dispatch_hints.min.json`.

The seam does not parse live quest YAML from source repos and does not rewrite
quest meaning.
