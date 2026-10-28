# Draaiboek

## Eerste controle

Voer de demo en tests uit; genereer daarna `.env`. Controleer dat `/ask` zonder key 401 geeft. Upload één bron via de adminsleutel en stel dezelfde vraag als finance, HR en een account zonder groepen. Doe dit ook na iedere wijziging aan rechten of indexschema.

## Storing

- **401:** key ontbreekt of staat niet in de serverconfiguratie. Deel de key niet in een issue. Herstart na een geautoriseerde configuratiewijziging.
- **403 bij ingest:** de principal heeft geen adminrecht. Verleen dat recht uitsluitend aan de ingestoperator.
- **Geen bronnen:** controleer tenant, groepen, corpusinhoud en vraagtermen. Lokaal zijn semantische synoniemen zonder woordoverlap niet gegarandeerd.
- **503 in Azure:** controleer resource-origin, credentials, tokenverval, deploymentnamen en indexschema. De server geeft opzettelijk geen providerresponse aan de client. Inspecteer Azure diagnostics binnen de bevoegde omgeving.
- **409 bij Azure-ingest/delete:** deze routes beheren alleen de lokale corpus. Gebruik de afzonderlijke Azure-indexadministratie.

## Backup en herstel

Stop writes en maak een SQLite-consistente backup met de Python `sqlite3.Connection.backup` API; kopieer geen actief bestand op goed geluk. Herstel in een aparte map, stel `RAG_DB` in en controleer tenants en aantallen voordat je de app weer openstelt. Verlies van auditgegevens is een te beoordelen incident, geen reden om fictieve events aan te vullen.

## Pilotvoorwaarden

De proceseigenaar accepteert bronactualiteit en antwoordcriteria; security valideert identiteit/egress; privacy beoordeelt gegevensgebruik; operations test restore/rollback. Gebruik een beperkte gebruikersgroep en meet mislukte zoekopdrachten, onjuiste antwoorden en onbeantwoorde vragen. Stop de pilot bij een toegangslek of herhaald foutief brongebruik. Rollback betekent Azure-modus uitzetten en gecontroleerd terugkeren naar een bekende corpusversie, niet stilzwijgend tijdens een request wisselen.
