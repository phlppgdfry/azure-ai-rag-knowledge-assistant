# Azure-modus

Dit stappenplan gebruikt bestaande services. Er worden geen betaalde resources automatisch aangemaakt. Live calls zijn nog niet uitgevoerd voor dit portfolio.

1. Gebruik een afzonderlijke testresource en synthetische data. Maak een Azure AI Search-service en Azure OpenAI-resource met een embeddingdeployment en een chatdeployment die JSON-object-output ondersteunt. Modelnamen zijn deploymentnamen in jouw resource.
2. Voeg onderstaande waarden toe aan de lokale `.env`. Keys/tokens blijven buiten Git. Gebruik voor de runtime een querykey of een beperkt dataleesrecht; gebruik uitsluitend tijdens indexadministratie een afzonderlijke admincredential. Een Azure Search-querykey kan de tenantfilters zelf niet afdwingen: clients mogen die key nooit ontvangen.

```dotenv
RAG_PROVIDER=azure
AZURE_SEARCH_ENDPOINT=https://YOUR-SERVICE.search.windows.net
AZURE_SEARCH_INDEX=synthetic-knowledge-v1
AZURE_SEARCH_API_VERSION=2026-04-01
AZURE_SEARCH_API_KEY=REPLACE_LOCALLY
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
AZURE_OPENAI_API_KEY=REPLACE_LOCALLY
AZURE_EMBEDDING_DEPLOYMENT=YOUR-EMBEDDING-DEPLOYMENT
AZURE_CHAT_DEPLOYMENT=YOUR-CHAT-DEPLOYMENT
```

3. Laad de waarden in je shell of via een private runner. De index-CLI leest omgevingsvariabelen, niet automatisch `.env`. Een veilige lokale Python-call is hieronder opgenomen. Het script doet een embeddingprobe, maakt/updatet het indexschema en uploadt de synthetische chunks. Een gedeeltelijk mislukte upload geeft een fout.

```bash
.venv/bin/python -c 'from dotenv import load_dotenv; load_dotenv(); from rag.index import main; main()' --tenant synthetic-firm --apply
```

4. Start de API met `uvicorn ... --env-file .env` zoals in de README. Gebruik dezelfde tenant als in `RAG_PRINCIPALS`. Test finance en HR afzonderlijk. Leg datum, indexschema, modeldeployment, corpusversie, latency, tokengebruik en menselijke beoordelingsresultaten vast. Zet daarna het resultaat pas op je cv als een geteste Azure-integratie.

5. Stop de app na de test; beslis zelf welke resources je behoudt of opruimt. Deze repo verwijdert geen resources.

Bearer-authenticatie kan via `AZURE_SEARCH_TOKEN` en `AZURE_OPENAI_TOKEN` in plaats van keys. Dit zijn tijdelijk aangeleverde tokens; automatische tokenvernieuwing/managed identity is niet geïmplementeerd. Verwijder de overeenkomstige API key-variabele om tokenauth te activeren. Voor enterprise-uitrol vervang je dit door server-side credentialbeheer met tokenvernieuwing, minimaal noodzakelijke RBAC, netwerkbeperking en een gevalideerde gebruikersidentiteit.

Documentatie opgevraagd via Context7 op 28 oktober 2026:

- [Azure Search security trimming](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search)
- [Hybride zoeken](https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query)
- [Vectorqueries](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-query)
- [Azure OpenAI API lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle)

De huidige REST-velden zijn contractgetest. Dat vervangt geen servicetest tegen jouw regio, permissies, quota en deployment.
