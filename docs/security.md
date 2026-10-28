# Vertrouwensgrenzen en gegevensbescherming

| Bedreiging | Controle | Restrisico |
|---|---|---|
| Gebruiker vraagt andere tenant | Tenant uit serverprincipal; queries met tenantfilter | Foute serverconfiguratie blijft mogelijk |
| HR-inhoud opvragen als finance | Groepen vóór ranking, opnieuw gecontroleerd in Azure | Extern gedeelde eerdere antwoorden kun je niet intrekken |
| Vraag probeert rol te wijzigen | Extra requestvelden verboden; tekst heeft geen autorisatiefunctie | Een model kan wel ongewenste tekst genereren |
| Bron bevat instructies | Bron als onbetrouwbare data in modelprompt; geen tools beschikbaar | Promptinstructies zijn geen bewijs van injectionbestendigheid |
| Model verzint bron-ID | Alleen retrieval-ID's toegestaan | Een echte bron kan onjuist worden geïnterpreteerd |
| Document veranderd of verwijderd | Atomische lokale vervanging/delete | Azure lifecycle vereist afzonderlijke administratie |
| API key of broninhoud in log | Audit bevat actie, subject en aantal, geen vraaginhoud | Infrastructuur- en proxylogs moeten apart worden gecontroleerd |

Gebruik uitsluitend synthetische data in de demo. Voor klantdata zijn doel, grondslag, contracten, bewaartermijnen, toegang, doorgiften en de noodzaak van een DPIA door de bevoegde privacy/securitypersonen te beoordelen. Dit project geeft geen juridisch oordeel en is geen GDPR-certificering.

Publieke routes zijn health en API-documentatie. Zet de app achter een TLS-gateway, limieten voor requestgrootte/rate, geverifieerde Entra-identiteit en een egressbeleid voordat andere gebruikers toegang krijgen. De app heeft geen malware-scanner, back-upencryptie of fraudedetectie. SQLite-bestanden en API keys zijn leesbaar voor een bevoegde hostbeheerder.

Er is geen gedeelde antwoordcache. Een later toegevoegde cache moet minimaal tenant, groepen, corpusversie en autorisatieversie in de sleutel opnemen en een geteste rechtenintrekking hebben.
