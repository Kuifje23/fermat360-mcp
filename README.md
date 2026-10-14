# Fermat 360 MCP server

[![M8ven Score](https://m8ven.ai/badge/mcp/kuifje23-fermat360-mcp-g8xi2c?v=4457e37d00e29739914141db6a0e198a)](https://m8ven.ai/mcp/kuifje23-fermat360-mcp-g8xi2c?s=readme)

**Answers to questions of Dutch law from Dutch case law, legislation and EU law, with numbered citations. For law firms.**

[Fermat 360](https://fermat360.nl) is a legal research platform for Dutch law firms. Its remote MCP server lets Claude and ChatGPT put a legal question to Fermat 360 and get back an answer with numbered citations to the judgments and legislation it relies on.

## Connect

| | |
|---|---|
| **Endpoint** | `https://fermat360.nl/mcp` (streamable HTTP) |
| **Auth** | OAuth 2.1 with PKCE. Clients identify themselves with a Client ID Metadata Document; no API keys |
| **Supported clients** | Claude (claude.ai, Desktop, mobile), Claude Code, ChatGPT (developer mode), VS Code (GitHub Copilot) |
| **Registry** | [`nl.fermat360/fermat-360`](https://registry.modelcontextprotocol.io/v0/servers?search=nl.fermat360%2Ffermat-360) in the official MCP registry |
| **Documentation** (Dutch) | https://fermat360.nl/mcp-koppeling |
| **Pricing** | €200 per user per month excl. VAT; the one-week free trial does not include the connector. https://fermat360.nl/#prijzen |
| **Privacy policy** | https://fermat360.nl/privacy |
| **Terms** | https://fermat360.nl/gebruikersovereenkomst |
| **llms.txt** | https://fermat360.nl/llms.txt |

- **Claude:** Settings → Connectors → Add custom connector, paste `https://fermat360.nl/mcp`, choose Connect and click "Toestaan" (Allow) in Fermat 360.
- **Claude Code:** `claude mcp add --transport http fermat https://fermat360.nl/mcp`, then `/mcp` to sign in.
- **ChatGPT:** turn on developer mode for apps, create an app with `https://fermat360.nl/mcp` and click "Toestaan" in Fermat 360.
- **VS Code:** `code --add-mcp '{"name":"fermat","type":"http","url":"https://fermat360.nl/mcp"}'`. VS Code asks you to sign in the first time the server is used; click "Toestaan" in Fermat 360.

You sign in once with your Fermat 360 account and approve the connection. You can disconnect at any time under Instellingen → AI-koppelingen.

## What your assistant can do

- `vraag_fermat`: ask a question of Dutch law, or a follow-up question in the same conversation (`gesprek_id`). Fermat 360 searches its corpus and returns an answer with numbered citations and links to the source documents. An answer can take up to a minute. Optional `niveau`: `basis` (the default) or `extra`, which is more thorough and counts 10 units.
- `haal_antwoord`: fetch an answer that was still being prepared.

Answers are in Dutch. Each question counts toward the user's monthly allowance of 10,000 units, the same counter as the chat in Fermat 360: a question on Basis counts 1 unit, on Extra 10. Through the connector the default is Basis. Each question also appears in the user's chat history in Fermat 360.

## Sources

More than 1.6 million documents: Dutch case law (about 965,000 judgments and 48,000 disciplinary decisions), Dutch legislation (43,000 acts and regulations from the BWB and 280,000 local regulations from the CVDR), EU legislation (EUR-Lex) and judgments of the CJEU and the ECtHR. Dutch judgments are collected nightly from the official registers; legislation and European sources weekly or monthly.

## Trust properties

- Every answer carries numbered citations to the passages it relies on, each linking to the original document.
- ECLI numbers mentioned in an answer are checked automatically against the corpus.
- By default, only legislation currently in force is searched.
- A follow-up question always triggers a new search. This is enforced in code, not left to the model.
- Data is stored on European servers (EU region) and separated per firm. Documents and case files kept in Fermat 360 are not shared through the connector.
- Answers support legal research and are not legal advice. A qualified lawyer should review them before relying on them.

## About this repository

This is the public home of the hosted Fermat 360 MCP server: documentation and listing anchor only. The service itself is not developed in this repository.

Questions: fermat360@protonmail.com.
