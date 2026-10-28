# Leren en demonstreren

## Begrippen in deze code

**Retrieval** selecteert fragmenten; **generatie** formuleert een antwoord. De lokale modus doet alleen selectie en extractie. **Embeddings** zetten tekst om in een vector waarmee semantische nabijheid wordt benaderd. **Hybride search** combineert die nabijheid met trefwoorden; dat is geen garantie op waarheid. **Chunking** beïnvloedt contextverlies, kosten en recall. **ACL** bepaalt of een document gelezen mag worden. **Abstention** betekent dat het systeem liever geen antwoord geeft wanneer bruikbare bronnen ontbreken.

## Oefeningen

1. Leg zonder hulpmiddel uit waarom filtering na antwoordgeneratie te laat is. Wijs in `core.py` en `azure.py` aan waar filtering plaatsvindt.
2. Voeg een synthetisch document toe dat beide afdelingen mogen lezen. Maak zelf vragen en verwachte bron-ID's; verifieer ook een gebruiker uit een andere tenant.
3. Verander chunkgrootte van 120 naar 60 woorden. Meet retrieval op tien eigen vragen en verklaar verschillen. Een hogere score van het algoritme is niet automatisch een beter antwoord.
4. Schrijf een test voor een groepswijziging en voor een lege groep. Toon dat de oude bron niet meer gevonden wordt.
5. Laat de gemockte Azure-generator een bestaand maar irrelevant bron-ID kiezen. De huidige citatiecheck kan dit accepteren. Ontwerp een menselijke of modelgebaseerde semantische beoordeling en beschrijf de kosten en fouten daarvan.
6. Diagnoseer een Azure 403 zonder keys te printen: onderscheid beheertoegang, datarechten, netwerktoegang en indexnaam.

## Demonstratie in twee minuten

0:00: toon dat dit een fictief kantoor en een lokale baseline is. 0:20: voer `python -m rag.demo` uit en toon antwoord plus bron. 0:50: toon de ACL-test met het verborgen bedrag. 1:20: leg de hybride Azure-query en prefilter uit. 1:45: vertel eerlijk dat cloudgedrag en antwoordkwaliteit nog een live pilot nodig hebben.

## Interview

Vraag: waarom geen vector-database lokaal? Antwoord dat je zelf moet kunnen verdedigen: een kleine, verklaarbare baseline maakt autorisatie en tests eenvoudig. Voor semantische dekking is de Azure-adapter beschikbaar. De juiste keuze hangt af van corpus, kosten, beheer, identiteit en meetbare retrievalkwaliteit.
