# Werkelijk verificatiebewijs

Uitgevoerd op 28 oktober 2026, Python 3.13:

- 12 pytest-tests geslaagd; zie `tests.xml` en `pytest.txt`.
- Lokale extractieve demo uitgevoerd met tijdelijke database; zie `demo.json`.
- Azure hybride query, tenantfilters, response-scope en citaties contractgetest met HTTP MockTransport. Geen live Azure-call.
- Dependencycontrole geslaagd; zie `dependencies.txt`.
- Docker-image werkelijk gebouwd; verpakte app met TestClient gecontroleerd; standaard Uvicorn-CMD geïsoleerd gestart en `/health` gaf 200. Zie `container-smoke.txt` en `container-runtime.txt`.
- OpenAPI uit de app gegenereerd en op verschil gecontroleerd.

De upstream Starlette/httpx TestClient-combinatie meldt één deprecationwarning; de tests slagen. Deze resultaten bewijzen geen modelkwaliteit, productielast of juridische conformiteit. Eventuele remote CI-resultaten staan bij GitHub Actions; deze lokale bewijsbestanden zijn geen verzonnen Actions-uitvoer.
