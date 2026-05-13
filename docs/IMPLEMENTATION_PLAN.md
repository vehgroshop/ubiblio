# Implementation plan

## Doel
uBiblio stapsgewijs uitbreiden voor een persoonlijke bibliotheek-app, met minimale verstoring van de bestaande architectuur en met prioriteit op stabiliteit, backups en dagelijks gebruik op mobiel.

## Werkprincipes
- Werk in kleine, reviewbare stappen.
- Houd SQLite en bestaande FastAPI/Jinja-structuur intact.
- Pas bestaande velden alleen slim aan als dat migraties simpeler maakt.
- Voeg tests toe voor nieuwe datamodellen, CRUD en kritieke routes.
- Gebruik veilige defaults en documenteer alle nieuwe environment variables.

---

## Fase 0 — Basis op orde

### Taak 0.1 — Lokale Docker Compose setup afronden
**Prioriteit:** Must-have  
**Complexiteit:** Laag

- Verifiëren dat Docker daemon draait op doelmachine
- `.env` maken vanaf `.env.example`
- app lokaal opstarten
- eerste admin aanmaken
- smoke test van login, boek toevoegen, export

**Output:** werkende lokale app op `http://localhost:8000`

### Taak 0.2 — Persistente data en backup valideren
**Prioriteit:** Must-have  
**Complexiteit:** Laag

- valideren dat database in `data/config/` blijft bestaan
- valideren dat uploads in `data/bookImages/` en `data/eBooks/` blijven bestaan
- SQL export en file export uitvoeren
- korte restore-test op kopieomgeving

**Output:** bewezen backup/restore basis

### Taak 0.3 — Setup issues harden
**Prioriteit:** Must-have  
**Complexiteit:** Laag/middel

- controleren of app ook zonder Linux `openssl` op host testbaar blijft
- indien nodig veilige fallback voor secret/key generatie toevoegen in Python
- deprecation warnings inventariseren, maar alleen direct fixen als risico laag is

**Output:** stabielere setup en testbaarheid

---

## Fase 1 — Datamodel voor persoonlijke bibliotheek

### Taak 1.1 — Bestaande locatievelden mappen op gewenste fysieke locatie
**Prioriteit:** Must-have  
**Complexiteit:** Laag/middel

**Voorkeursaanpak:** hergebruik bestaande velden om snelle waarde te leveren
- `library` -> kamer
- `collection` -> kast
- `shelf` -> plank/locatie
- extra vrije notitie toevoegen als nieuw veld `locationNote`

Alternatief:
- expliciete nieuwe velden `room`, `bookcase`, `shelf`, `location_note`

**Aanbeveling:** eerst bestaande velden herlabelen in UI en alleen `locationNote` toevoegen als extra veld.

### Taak 1.2 — Persoonlijke leesgegevens modelleren
**Prioriteit:** Must-have  
**Complexiteit:** Middel

Nieuwe tabel voorstellen, bijvoorbeeld `userbookstate`:
- `id`
- `user_id`
- `book_id`
- `status`
- `rating`
- `personal_notes`
- `date_started`
- `date_finished`
- `progress_value`
- `progress_unit`

Waarom:
- multi-user compatibel
- ratings en notities worden persoonsgebonden
- reading list kan hierin opgaan

### Taak 1.3 — Quotes model toevoegen
**Prioriteit:** Must-have  
**Complexiteit:** Middel

Nieuwe tabel `bookquotes`:
- `id`
- `book_id`
- `user_id`
- `quote_text`
- `page_reference`
- `created_at`

### Taak 1.4 — Uitleenbeheer uitbreiden
**Prioriteit:** Should-have  
**Complexiteit:** Middel

Nieuwe tabel `loans`:
- `book_id`
- `lent_to`
- `loaned_at`
- `due_at`
- `returned_at`
- `status`

Bestaande `withdrawn` en `withdrawnBy` voorlopig behouden voor backward compatibility, later afbouwen.

---

## Fase 2 — UI en gebruikersflow

### Taak 2.1 — Boekformulier aanpassen voor persoonlijke bibliotheek
**Prioriteit:** Must-have  
**Complexiteit:** Middel

- labels aanpassen naar kamer/kast/plank
- veld voor locatie-notitie toevoegen
- notitiesplitsing maken tussen algemene boeknotitie en persoonlijke notitie indien gekozen datamodel dit ondersteunt
- defaults duidelijker maken voor fysiek boek vs e-book

### Taak 2.2 — Detailpagina uitbreiden
**Prioriteit:** Must-have  
**Complexiteit:** Middel

Toevoegen aan boekdetail:
- rating
- persoonlijke notities
- quotes overzicht + toevoegen/verwijderen
- leesstatus
- leesdatums
- voortgang
- duidelijkere uitleenstatus

### Taak 2.3 — Mobiele scanflow verbeteren
**Prioriteit:** Must-have  
**Complexiteit:** Middel

- compact mobiel scanformulier
- scan-resultaat direct tonen in kort bevestigingsscherm
- camera-keuze beter onthouden
- betere foutmeldingen bij mislukte scans
- grotere knoppen en minder scroll voor mobiel gebruik

### Taak 2.4 — Mobiel dashboard / snelle acties
**Prioriteit:** Nice-to-have  
**Complexiteit:** Middel

- snelle knoppen voor:
  - scan boek
  - voeg wishlist-item toe
  - leen uit
  - markeer als aan het lezen

---

## Fase 3 — Leesstatus en persoonlijke workflow

### Taak 3.1 — Reading status uitbreiden
**Prioriteit:** Should-have  
**Complexiteit:** Middel

Ondersteunde statussen:
- bezit ik
- wishlist
- wil ik lezen
- aan het lezen
- gelezen
- gestopt / did not finish

**Opmerking:** `bezit ik` is conceptueel deels al `owned`; beslissen of dat apart in UI blijft of onderdeel van één state machine wordt.

### Taak 3.2 — Start- en einddatum lezen
**Prioriteit:** Should-have  
**Complexiteit:** Laag/middel

- opslaan in `userbookstate`
- tonen op detailpagina
- eventueel filter “recent gelezen” later toevoegen

### Taak 3.3 — Voortgang/pagina
**Prioriteit:** Should-have  
**Complexiteit:** Laag/middel

- numerieke voortgang plus eenheid (`page`, `%`, `location`) 
- belangrijk voor zowel fysieke boeken als Kindle-notatie

---

## Fase 4 — Duplicaten en exports

### Taak 4.1 — Duplicatenoverzicht
**Prioriteit:** Should-have  
**Complexiteit:** Middel

Eerste versie:
- exact ISBN match
- titel + auteur normalized match
- overzichtspagina met vermoedelijke duplicaten

Tweede versie later:
- fuzzy matching
- merge suggesties

### Taak 4.2 — JSON export
**Prioriteit:** Should-have  
**Complexiteit:** Laag

- admin endpoint voor JSON export
- export van boeken, user states, quotes, loans en config

### Taak 4.3 — CSV export uitbreiden
**Prioriteit:** Should-have  
**Complexiteit:** Laag/middel

- huidige CSV export exporteert alleen de `books` tabel
- uitbreiden met duidelijke headers
- eventueel extra exportbestanden voor quotes en leesstatus

---

## Fase 5 — Import workflows

### Taak 5.1 — Goodreads CSV import
**Prioriteit:** Nice-to-have  
**Complexiteit:** Middel

- importer met mapping preview
- velden koppelen naar titel, auteur, status, rating, dates, notes

### Taak 5.2 — Generieke eigen CSV import
**Prioriteit:** Nice-to-have  
**Complexiteit:** Middel

- template CSV ondersteunen
- validatie + preview
- duplicate warning voor import

### Taak 5.3 — Kindle metadata-workflow documenteren
**Prioriteit:** Nice-to-have  
**Complexiteit:** Laag

- geen accountintegratie
- alleen handmatige of legale exportgestuurde workflow

---

## Fase 6 — Deployment en hardening

### Taak 6.1 — Productie compose-profiel
**Prioriteit:** Must-have voor online deployment  
**Complexiteit:** Laag/middel

- aparte `docker-compose.yml` voor niet-dev gebruik
- `DEV=false`
- geen source bind mount nodig
- alleen persistente volumes

### Taak 6.2 — Cloudflare Tunnel voorbeeldconfiguratie
**Prioriteit:** Nice-to-have  
**Complexiteit:** Laag

- documentatie met tunnel-config
- uitleg domeinbinding en private origin

### Taak 6.3 — VPS deploymentrichtlijn
**Prioriteit:** Should-have  
**Complexiteit:** Laag

- firewall
- reverse proxy of tunnel
- automatische backups
- updateproces

### Taak 6.4 — Backup automation
**Prioriteit:** Must-have voor productie  
**Complexiteit:** Laag/middel

- periodieke backup van hele `data/`
- retention policy
- restore-instructies testen

---

## Aanbevolen bouwvolgorde

### Sprint 1
1. Lokale Docker setup echt werkend maken
2. Backup/restore valideren
3. Setup/documentatie afronden

### Sprint 2
4. Locatievelden verbeteren
5. Rating + persoonlijke notities modelleren
6. Boekdetailpagina uitbreiden

### Sprint 3
7. Quotes toevoegen
8. Reading status uitbreiden
9. Start/einddatum en voortgang toevoegen

### Sprint 4
10. Mobiele scanflow verbeteren
11. Duplicatenoverzicht bouwen
12. JSON export toevoegen

### Sprint 5
13. Goodreads/eigen CSV import
14. Snelle uitleenflow
15. Mooier mobiel dashboard en dark mode

---

## Teststrategie per fase
- **Model tests:** nieuwe tabellen, defaults, migratiepaden
- **CRUD tests:** create/update/delete voor user state, quotes, loans
- **Route tests:** boekdetail, scanflow, exports, imports
- **UI smoke tests:** mobiel relevante pagina’s handmatig testen
- **Backup tests:** export en restore op sample data

---

## Eerste concrete bouwtaak
**Aanbevolen eerstvolgende taak:**

### Taak 1 — Productieklare lokale runtime afronden
- Docker daemon starten en compose-run verifiëren
- admin account aanmaken
- één fysiek boek toevoegen
- één e-bookrecord toevoegen
- backup/export scherm doorlopen
- eventuele runtime issues minimaal fixen

Dit is de juiste eerste taak omdat alle functionele uitbreidingen pas zinvol zijn als de basis lokaal betrouwbaar draait.