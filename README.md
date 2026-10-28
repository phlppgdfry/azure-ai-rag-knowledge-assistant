# Knowledge Assistant

Een kennisassistent voor een fictief accountancykantoor, met bronverwijzingen en toegangscontrole vóór retrieval. Een financieel medewerker mag het HR-document niet terugvinden, ook niet met een gerichte vraag naar een geheim bedrag.

**Status:** werkende lokale referentie en optionele Azure REST-adapter. De lokale modus gebruikt BM25-achtige trefwoordscores en extractieve antwoorden: geen semantische embeddings en geen LLM. De Azure-modus gebruikt echte embeddings, hybride Azure AI Search en Azure OpenAI-generatie wanneer je die services configureert. Azure-contracten zijn getest met geïnjecteerde HTTP-responses; er is geen live cloudkwaliteit gemeten. Alle meegeleverde inhoud is synthetisch.

## Starten

Python 3.13 is getest. Voer onderstaande commando's uit vanuit deze repo.

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m rag.demo
.venv/bin/python -m pytest -q
.venv/bin/python scripts/bootstrap.py
.venv/bin/uvicorn rag.api:app --env-file .env --host 127.0.0.1 --port 8084
```

Open `http://127.0.0.1:8084/docs`. De gegenereerde `.env` bevat aparte sleutels voor admin, finance en HR; lees deze alleen lokaal. Kies **Authorize**, gebruik de adminsleutel en voeg de documenten uit [fixtures](fixtures/documents.json) één voor één toe met `POST /documents`. Gebruik daarna de finance-sleutel en `POST /ask` met `{"question":"factuur goedkeuring","top":4}`. Een vraag naar `7312` moet voor finance zonder resultaat blijven en voor HR een bron geven.

`rag.demo` heeft een eigen tijdelijke database; het vult de API-database bewust niet. Bootstrap overschrijft geen bestaande `.env`.

## Mogelijkheden

| Onderdeel | Gedrag |
|---|---|
| Ingest | Documentvalidatie, overlappende chunks, inhoudshash, atomische upsert |
| Toegang | Serverconfiguratie bepaalt subject, tenant, groepen en schrijfrecht |
| Zoeken | Alleen toegankelijke documenten tellen mee voor lokale rangschikking |
| Antwoorden | Lokale bronextracten met stabiele chunk-ID's, of Azure JSON-antwoord met toegestane citaties |
| Levenscyclus | Upsert vervangt oude chunks; delete verwijdert document en chunks lokaal |
| Audit | Lokale ingest/delete/retrieval-events zonder vraagtekst of documentinhoud |
| Azure | Embeddings, hybride query met tenant-/groepsfilter en controle op zoekresultaten |

De API accepteert geen tenant of rol in vraagrequests. `RAG_PROVIDER=azure` schakelt de externe route in; elke fout geeft 503 en gebruikt geen lokaal vervangantwoord. In Azure-modus zijn de lokale ingest- en delete-endpoints geblokkeerd, zodat ze geen geslaagde cloudwijziging kunnen suggereren.

## Demo en bewijs

- [Architectuur en keuzes](docs/architecture.md)
- [Azure configureren en indexeren](docs/azure.md)
- [Beveiliging en beperkingen](docs/security.md)
- [Operationeel draaiboek](docs/runbook.md)
- [Leren en demonstreren](docs/learning.md)
- [OpenAPI](docs/openapi.json) en [testresultaat](evidence/tests.xml)

`docker compose up --build` draait dezelfde app met een leeg persistent volume; vul de documenten via de API. Lees de verificatiestatus in [evidence](evidence/README.md). Dockerbestanden zijn geen bewijs van een uitgevoerde containerbuild.

## Grenzen

Geen SharePoint-sync, Entra JWT-validatie, automatische bewaartermijnen, algemene PII-filtering of productiekwaliteitsclaim. Lokale API keys vervangen geen enterprise-identiteit. Azure-citatiecontrole bewijst dat de bron-ID bestaat; ze bewijst niet dat elke zin logisch uit de bron volgt. Zoekdrempels, meertaligheid en antwoordkwaliteit moeten op een representatieve en toegestane dataset worden gekalibreerd.

Met AI-ondersteuning gemaakt. Zelfstandig kunnen uitleggen, aanpassen en diagnosticeren is nodig voordat je dit als eigen vaardigheid presenteert.
