# Product fit analyse uBiblio

## Samenvatting
uBiblio is een bruikbare basis voor een privacy-first persoonlijke bibliotheek-app, vooral voor zelfhosting, fysieke boeken, e-books, ISBN-toevoeging, eenvoudige uitleenregistratie en basis backups. Het project is klein, overzichtelijk en relatief makkelijk uit te breiden.

Voor de gewenste use-case van een persoonlijke bibliotheek voor je vriendin is de fit goed als basis, maar niet compleet. De kern voor collectiebeheer is aanwezig, terwijl persoonlijke leesdata, uitgebreidere statusflows, fijnmazige locatievelden, quotes, duplicate-detectie en rijkere export/import nog gebouwd moeten worden.

## Bestaande functies

| Functie | Standaard aanwezig | Opmerkingen | Relevante bestanden/modules |
|---|---|---|---|
| Fysieke boeken beheren | Ja | CRUD aanwezig met titel, auteur, samenvatting, genre, library, shelf, collection, ISBN, notes | `ubiblio/models.py`, `ubiblio/crud.py`, `ubiblio/routers/books/api.py`, `templates/newBook.html` |
| E-books beheren | Ja | Boek kan `ebook=True` zijn, upload/download/delete van bestanden aanwezig | `ubiblio/models.py`, `ubiblio/routers/files.py`, `templates/ebookDetails.html` |
| Zoeken op titel/auteur | Ja | Zoek-UI en endpoints aanwezig | `templates/booksearch.html`, `ubiblio/routers/books/api.py`, `ubiblio/routers/books/service.py` |
| Toevoegen via ISBN | Ja | Metadata lookup via meerdere bronnen | `ubiblio/routers/books/api.py`, `ubiblio/routers/books/book_metadata_client.py` |
| Barcode/ISBN scannen met camera | Ja | Browsergebaseerd via QuaggaJS, lokaal asset meegeleverd | `templates/scanIsbn.html`, `static/assets/js/quagga.min.js` |
| Coverafbeeldingen | Ja, optioneel | Tot 16 afbeeldingen per boek, thumbnails ondersteund | `ubiblio/models.py`, `ubiblio/routers/files.py`, `templates/bookDetails.html` |
| Wishlist | Ja | Wordt gemodelleerd als `owned=False` | `README.md`, `ubiblio/crud.py`, `templates/wishlist.html` |
| Reading list | Ja | Per gebruiker, maar geen rijke reading status | `ubiblio/models.py`, `ubiblio/routers/reading_lists.py` |
| Uitleen / withdrawn | Gedeeltelijk | Alleen `withdrawn` boolean en `withdrawnBy` username, geen leen- of retourdatum | `ubiblio/models.py`, `ubiblio/routers/reading_lists.py`, `templates/withdrawn.html` |
| Multi-user | Ja | Admin en gewone gebruikers, invite links | `ubiblio/models.py`, `ubiblio/routers/admin.py`, `ubiblio/routers/auth.py` |
| Browse by genre | Ja | Eenvoudige genre-navigatie | `ubiblio/crud.py`, `ubiblio/routers/books/api.py` |
| CSV export | Ja | Exporteert `books` tabel naar CSV | `ubiblio/routers/admin.py` |
| SQL/database backup | Ja | SQL dump via sqlite iterdump | `ubiblio/routers/admin.py`, `daily_backup.sh` |
| Bestandsbackup | Ja | ZIP van `static` map | `ubiblio/routers/admin.py` |
| Restore | Ja | SQL restore en file restore aanwezig | `ubiblio/routers/admin.py` |
| Federated search | Ja | Niet nodig voor deze use-case, maar aanwezig | `ubiblio/routers/federation.py`, `README.md` |
| Mobiele bruikbaarheid | Gedeeltelijk | Simpele UI werkt op telefoons, maar forms en scanflow zijn basic | `README.md`, templates |
| Privacy-first / self-hosted | Ja | Geen tracking, geen verplichte cloud | `README.md` |

## Missende functies

| Gewenste functie | Prioriteit | Geschatte complexiteit | Voorgestelde implementatie |
|---|---|---|---|
| Stabiele lokale Docker Compose setup | Must-have | Laag | Compose met persistente volumes, `.env.example`, duidelijke docs |
| Duidelijke backup/restore procedure | Must-have | Laag | Docs uitbreiden en liefst restore-procedure testen met data-volumes |
| Locatievelden: kamer / kast / plank / vrije notitie | Must-have | Middel | Bestaande `library`, `shelf`, `collection` hernoemen/hergebruiken of nieuwe kolommen toevoegen plus vrije locatie-notitie |
| Rating per boek | Must-have | Laag | Nieuwe kolom op boek of gebruikersspecifieke leestabel, afhankelijk van single-user vs multi-user strategie |
| Persoonlijke notities per boek | Must-have | Middel | Bestaande `notes` bestaat al, maar is globaal op boekniveau; voor nette uitbreiding liever personal notes model per user/book |
| Quotes per boek | Must-have | Middel | Nieuwe tabel `book_quotes` met boek, gebruiker, quote, pagina/locatie optioneel |
| Verbeterde mobiele scan/invoerflow | Must-have | Middel | Scanresultaat direct naar compact mobiel formulier, autofocus, camera-voorkeur en betere foutafhandeling |
| Reading status: wishlist / wil lezen / aan het lezen / gelezen / DNF | Should-have | Middel | Nieuw statusveld in user-book relatie; huidige reading list is te beperkt |
| Startdatum/einddatum lezen | Should-have | Middel | Toevoegen aan user-book relationeel model |
| Duplicatenoverzicht | Should-have | Middel | Query op ISBN en fuzzy fallback op titel+auteur, aparte admin/view pagina |
| Export naar JSON | Should-have | Laag | Endpoint en admin actie naast SQL/CSV |
| CSV/Goodreads/legale importflow | Nice-to-have | Middel | Mapping importservice met preview en handmatige bevestiging |
| Mooier mobiel dashboard | Nice-to-have | Middel | Responsieve template-aanpassingen, snellere actieknoppen |
| Dark mode | Nice-to-have | Laag/middel | CSS theme toggle |
| Snelle uitleenknop met meer metadata | Nice-to-have | Middel | Klein modal/form voor lener + data |
| Cloudflare Tunnel voorbeeldconfiguratie | Nice-to-have | Laag | Documentatiebestand met voorbeeld compose/snippet |

## Datamodel
### Bestaande modellen/tables
Uit `ubiblio/models.py`:

- `users`
  - `username`, `passhash`, `isAdmin`
- `books`
  - `title`, `author`, `summary`, `genre`, `library`, `shelf`, `collection`, `ISBN`, `notes`, `owned`, `withdrawn`, `withdrawnBy`, `customField1`, `customField2`, `ebook`
- `readinglistitems`
  - koppelt `book` aan `user_id`
- `bookImages`
  - meerdere cover/boekafbeeldingen per boek
- `ebooks`
  - bestandsnaam per boek
- `config`
  - versie, cover images, custom field names, genres
- `userEmails`
  - nu feitelijk niet belangrijk
- `links`
  - invite links
- `vkeys`
  - federation keys per remote instance

### Observaties
- `books` is nu het centrale model voor bijna alles.
- `notes` zit direct op boekniveau en is dus niet per gebruiker.
- `readinglistitems` is te beperkt voor rijke leesstatus en leeshistorie.
- uitleenbeheer is ook te simpel: alleen boolean + username.

### Aanbevolen uitbreidingen
1. **UserBookState** of vergelijkbaar model
   - `user_id`
   - `book_id`
   - `status`
   - `rating`
   - `personal_notes`
   - `date_started`
   - `date_finished`
   - `progress_value`
   - `progress_unit`

2. **BookQuote**
   - `id`
   - `book_id`
   - `user_id`
   - `quote_text`
   - `page_reference` of `location_reference`
   - `created_at`

3. **Loan**
   - `id`
   - `book_id`
   - `lent_to`
   - `loaned_at`
   - `due_at`
   - `returned_at`
   - `status`

4. **Location normalisatie**
   Twee opties:
   - snel: hergebruik `library`, `shelf`, `collection`, plus nieuwe `location_note`
   - netter: expliciet `room`, `bookcase`, `shelf`, `position_note`

5. **Duplicate detection hoeft niet direct extra tabel te krijgen**
   - kan eerst als query/view worden gebouwd

## Mobiele scanflow
### Huidige situatie
- Er is een aparte pagina `/scan_isbn`.
- De pagina gebruikt QuaggaJS lokaal vanuit `static/assets/js/quagga.min.js`.
- De browser vraagt cameratoegang.
- De gebruiker kan een camera selecteren.
- Een gescande barcode opent direct `/isbn/{isbn}/scan`.
- Daarna komt een vooraf ingevuld formulier voor goedkeuring.

### Beoordeling
Positief:
- geen externe barcode-SaaS nodig
- werkt in de browser
- lokaal meegeleverde JS, dus privacyvriendelijk
- conceptueel bruikbaar op telefoon

Beperkingen:
- UX is basaal
- camera-keuze met cookie op indexbasis is fragiel
- geen expliciete mobiele optimalisatie van knoppen/form layout
- geen fallback-flow voor moeilijke scans behalve handmatige entry
- alleen admin kan toevoegen/scannen

### Conclusie
De scanflow is bruikbaar als eerste versie, maar voor dagelijks telefoongebruik waarschijnlijk niet prettig genoeg zonder kleine UX-verbeteringen.

## Kindle/e-book workflow
### Hoe e-books nu worden toegevoegd
- Bij aanmaken van een boek kan `ebook=True` worden gezet.
- Op de ebook detailpagina kan een admin één of meer bestanden uploaden.
- Bestanden worden opgeslagen in `static/eBooks/`.
- Gebruikers kunnen bestanden downloaden via de app.

### Wat ontbreekt
- geen Kindle-accountintegratie
- geen import van Kindle bibliotheekmetadata
- geen legale sync met Amazon
- geen bulk-import voor e-books in de huidige UI

### Praktische en legale workflow
1. **Handmatig toevoegen van Kindle-boeken**
   - maak een boekrecord aan via titel/auteur of ISBN
   - zet `ebook=True`
   - vul taal, ISBN, notities en tags in
   - upload alleen het e-bookbestand als de gebruiker dat bestand zelf bezit en mag bewaren

2. **Handmatige registratie zonder bestand**
   - voor Kindle-aankopen waarbij geen exporteerbaar bestand beschikbaar is
   - voeg het boek toe als metadata-only item
   - noteer in notities dat het in Kindle staat

3. **CSV import later**
   - nuttig als er een legale exportbron is
   - bijvoorbeeld eigen spreadsheet, Goodreads-export of andere niet-DRM metadata-export

4. **Goodreads-export als latere optie**
   - kan nuttig zijn voor gelezen/wil-lezen status en ratings
   - vereist mapping naar uBiblio velden

5. **Geen onveilige/illegale Kindle-integratie bouwen**
   - geen scraping van Amazon account
   - geen DRM-omzeiling
   - geen browser-automation tegen Kindle account als productfeature

## Deploymentadvies
### Lokaal Docker
Aanbevolen als eerste stap.
- draai met Docker Compose
- persistente volumes voor config/db/uploads/exports
- `DEV=false` voor stabiel gebruik
- alleen lokaal of LAN beschikbaar

### Thuisserver met Cloudflare Tunnel
Geschikt als tweede stap.
- uBiblio alleen lokaal binden achter Docker
- Cloudflare Tunnel publiceert HTTPS endpoint
- geen poortforwarding nodig
- combineer met sterke wachtwoorden en liefst extra toegangsbescherming
- let op dat Cloudflare een externe partij blijft voor transportlaag/public endpoint

### VPS met Docker Compose
Geschikt later als je externe bereikbaarheid en uptime wilt.
- Docker Compose met persistente volumes
- reverse proxy of tunnel
- automatische backups naar tweede locatie
- liefst OS hardening, firewall en updatebeleid

### Backups
Minimaal:
- SQLite database backup
- uploads/export map backup
- config/key files backup

Aanbevolen:
- hele `data/` map periodiek backuppen
- 3-2-1 backupstrategie op termijn
- periodiek restore-testen

### HTTPS
- lokaal niet noodzakelijk
- extern altijd HTTPS
- bij thuisserver: Cloudflare Tunnel of reverse proxy met TLS
- bij VPS: reverse proxy met Let’s Encrypt of tunnel

### Authenticatie
- sterke unieke admin credentials
- eventueel tweede gewone gebruiker voor dagelijks gebruik
- geen publieke registratie
- invite-link flow alleen als multi-user echt nodig is

### Updates
- eerst backups maken
- release notes/changelog controleren
- image of repo updaten
- database migratiegedrag vooraf testen op kopie van DB
- omdat het project SQLite en handmatige upgradepaden gebruikt, updates voorzichtig uitvoeren

## Licentie
uBiblio gebruikt **GNU GPL v3**.

Praktische betekenis voor dit project:
- persoonlijk gebruik en lokaal aanpassen is toegestaan
- forken en intern draaien is toegestaan
- code wijzigen is toegestaan
- als je de aangepaste software distribueert of publiek doorgeeft, moet je onder GPLv3 aan de copyleft-verplichtingen voldoen
- voor puur privégebruik in huis is dat meestal geen probleem

## Data-opslag en backupmogelijkheden
### Database
- SQLite via `DB_LOCATION`
- standaard repo-pad of in Docker beter `/app/config/sql_app.db`
- SQLAlchemy gebruikt SQLite engine

### Uploads en bestanden
- e-books in `static/eBooks/`
- coverafbeeldingen in `static/bookImages/`
- exports/backups in `export/`
- secrets en signing keys in config-bestanden

### Backupmogelijkheden in huidige app
- SQL dump export
- CSV export van boeken
- ZIP file backup van `static`
- restore van SQL backup
- restore van ZIP file backup
- shellscript `daily_backup.sh` voor sqlite backup

## Eindconclusie
uBiblio is geschikt als startpunt voor deze persoonlijke bibliotheek-app, vooral omdat het al self-hosted, privacy-first, klein en uitbreidbaar is. Voor collectiebeheer, ISBN-toevoeging, e-books en eenvoudige uitleenregistratie is er genoeg basis aanwezig.

De grootste gaten zitten in persoonlijke leesdata, uitgebreid statusbeheer, betere fysieke locatie-structuur, quotes, duplicates en mobiele UX. Dat zijn realistische incrementele uitbreidingen zonder volledige rewrite.