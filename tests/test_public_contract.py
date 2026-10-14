"""Contract tests for the hosted Fermat 360 MCP server.

They check what anyone can check without a Fermat 360 account: that the
endpoint refuses unauthenticated calls and points to its OAuth metadata, that
the metadata matches what the README documents, and that the README,
.mcp.json and the official MCP registry agree on the endpoint.

Run with: python3 -m unittest discover tests
"""

import json
import pathlib
import re
import unittest
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://fermat360.nl/mcp"
ISSUER = "https://fermat360.nl"
REGISTRY_NAME = "nl.fermat360/fermat-360"
REPOSITORY = "https://github.com/Kuifje23/fermat360-mcp"
TOOLS = ("vraag_fermat", "haal_antwoord")

ROOT = pathlib.Path(__file__).resolve().parent.parent
TIMEOUT = 20


def fetch(url, data=None, headers=None):
    """Return (status, headers, body) without raising on 4xx/5xx."""
    request = urllib.request.Request(url, data=data, headers=headers or {})
    request.add_header("User-Agent", "fermat360-mcp-contract-tests")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        with error:
            return error.code, error.headers, error.read()


def fetch_json(url):
    status, _, body = fetch(url, headers={"Accept": "application/json"})
    if status != 200:
        raise AssertionError(f"{url} returned {status}")
    return json.loads(body)


class EndpointTest(unittest.TestCase):
    def test_unauthenticated_call_is_refused_with_resource_metadata(self):
        initialize = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "contract-tests", "version": "1"},
            },
        }
        status, headers, _ = fetch(
            ENDPOINT,
            data=json.dumps(initialize).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )
        self.assertEqual(status, 401)
        challenge = headers.get("WWW-Authenticate", "")
        self.assertTrue(challenge.startswith("Bearer "), challenge)
        match = re.search(r'resource_metadata="([^"]+)"', challenge)
        self.assertIsNotNone(match, challenge)

        metadata = fetch_json(match.group(1))
        self.assertEqual(metadata["resource"], ENDPOINT)
        self.assertIn(ISSUER, metadata["authorization_servers"])


class AuthorizationServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = fetch_json(f"{ISSUER}/.well-known/oauth-authorization-server")

    def test_issuer(self):
        self.assertEqual(self.metadata["issuer"], ISSUER)

    def test_pkce_with_s256(self):
        self.assertIn("S256", self.metadata["code_challenge_methods_supported"])

    def test_clients_identify_with_a_metadata_document_not_an_api_key(self):
        self.assertTrue(self.metadata.get("client_id_metadata_document_supported"))
        self.assertEqual(self.metadata["token_endpoint_auth_methods_supported"], ["none"])
        self.assertNotIn("registration_endpoint", self.metadata)

    def test_authorization_code_with_refresh(self):
        self.assertEqual(self.metadata["response_types_supported"], ["code"])
        self.assertEqual(
            sorted(self.metadata["grant_types_supported"]),
            ["authorization_code", "refresh_token"],
        )

    def test_endpoints_are_https_on_the_issuer(self):
        for key in ("authorization_endpoint", "token_endpoint", "revocation_endpoint"):
            with self.subTest(key=key):
                self.assertTrue(self.metadata[key].startswith(f"{ISSUER}/"), self.metadata[key])


class DocumentationTest(unittest.TestCase):
    def test_mcp_json_points_to_the_endpoint(self):
        config = json.loads((ROOT / ".mcp.json").read_text())
        urls = [server["url"] for server in config["mcpServers"].values()]
        self.assertEqual(urls, [ENDPOINT])

    def test_readme_documents_the_endpoint_and_every_tool(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn(ENDPOINT, readme)
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self.assertIn(f"`{tool}`", readme)

    def test_registry_lists_this_endpoint_and_repository(self):
        query = urllib.parse.urlencode({"search": REGISTRY_NAME})
        listing = fetch_json(f"https://registry.modelcontextprotocol.io/v0/servers?{query}")
        latest = [
            entry["server"]
            for entry in listing["servers"]
            if entry["server"]["name"] == REGISTRY_NAME
            and entry["_meta"]["io.modelcontextprotocol.registry/official"]["isLatest"]
        ]
        self.assertEqual(len(latest), 1)
        self.assertEqual([remote["url"] for remote in latest[0]["remotes"]], [ENDPOINT])
        self.assertEqual(latest[0]["repository"]["url"], REPOSITORY)


if __name__ == "__main__":
    unittest.main()
