# Provider integration boundaries

Use current primary documentation and the installed package's actual interface.
Record component/repository, revision/version, license, model requirements,
resource estimates, network behavior, data destinations and local trial result.

- OpenHands: distinguish SDK, agent server, sandbox server, automation server and
  UI. Verify each requested component's own license. Normal project use does
  not authorize a new paid model/provider or remote workspace.
- OpenViking: context filesystem, summaries, sessions and compile capabilities
  depend on actual server/provider configuration. A file hierarchy replica is
  not OpenViking runtime acceptance. Hosted trials are separate from self-hosting.
- Cognee: test the actual installed local memory/graph path; do not assume the
  current default model, API calls, stores or graph schema from an old tutorial.
- GraphRAG: TextUnits, extraction, communities/summaries and Global/Local/DRIFT
  modes need separate source-bound acceptance. Existing graph traversal is not
  proof of GraphRAG integration or a complete graph-extraction run.
- LlamaIndex: configure explicit local LLM/embedding/storage behavior. Defaults
  may route to hosted providers. PropertyGraphIndex and its retrievers must be
  exercised with the selected actual backend.
- SCIP/Sourcegraph: distinguish the protocol, language indexer and hosting
  product; preserve symbol/occurrence IDs and confirm real exported index
  coverage. A same-named symbol or generic AST is not equivalent evidence.

Keep provider adapters separate from canonical source storage and accepted
indexes. Start with public/provider fixtures or small synthetic material; only
then use the authorized private corpus. Installation, configuration, connection,
successful request, source quality and accepted end-to-end result are different
states. Copy/sync only an explicit clean package, not profiles, secrets or raw
sessions. Cross-environment installation is not proven by source-copy hashes.
