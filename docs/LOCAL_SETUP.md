# Lokale setup uBiblio

## Doel
Deze setup draait uBiblio lokaal via Docker Compose met persistente data voor:
- SQLite database
- geheime sleutels
- exports/backups
- coverafbeeldingen
- e-bookbestanden

## Aannames
- Repository is gecloned in deze map.
- Docker Desktop of een compatibele Docker daemon draait lokaal.
- De Linux container engine is beschikbaar.
- Je gebruikt de development compose file als basis voor lokaal testen.

## Snelle start
1. Kopieer het environment-bestand:

```powershell
Copy-Item .env.example .env
```

2. Pas minimaal deze waarden aan in `.env`:
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- optioneel `GB_API` voor betere ISBN metadata uit Google Books
- optioneel `LANGUAGE=FR`
- voor lokale ontwikkeling mag `DEV=true`, voor stabiel lokaal gebruik liever `DEV=false`

3. Start Docker Desktop en controleer dat de daemon draait:

```powershell
docker info
```

De `Server` sectie moet beschikbaar zijn. In deze sessie was de Docker CLI aanwezig, maar de daemon draaide nog niet.

4. Start de app:

```powershell
docker compose -f docker-compose.dev.yml up --build -d
```

5. Open daarna:

```text
http://localhost:8000
```

6. Maak de eerste admin aan door eenmalig deze URL te bezoeken:

```text
http://localhost:8000/user-setup
```

Daarna kun je inloggen met de waarden uit `.env`.

## Compose-opzet
De lokale compose-config gebruikt deze persistente mounts:

- `./data/config:/app/config`
- `./data/export:/app/export`
- `./data/bookImages:/app/static/bookImages`
- `./data/eBooks:/app/static/eBooks`

Daardoor blijven database, sleutels, uploads en exports behouden als de container opnieuw wordt gebouwd of verwijderd.

## Belangrijke bestanden en data-opslag
- database: `/app/config/sql_app.db`
- session secret: `/app/config/secret_key.txt`
- federation signing key: `/app/config/sign_key.txt`
- federation verify key: `/app/config/verify_key.txt`
- exports/backups: `/app/export`
- cover images: `/app/static/bookImages`
- e-books: `/app/static/eBooks`

## Stoppen en opnieuw starten
Stoppen:

```powershell
docker compose -f docker-compose.dev.yml down
```

Opnieuw starten:

```powershell
docker compose -f docker-compose.dev.yml up -d
```

Logs bekijken:

```powershell
docker compose -f docker-compose.dev.yml logs -f
```

## Basis backup-instructies
### Optie 1: via de app
Admin > backups ondersteunt:
- SQL export
- CSV export van boeken
- ZIP backup van bestanden
- restore van SQL en file backups

### Optie 2: handmatig vanaf host
Backup de volledige persistente map:

```powershell
Compress-Archive -Path .\data\* -DestinationPath .\backup-data.zip
```

### Optie 3: alleen database
Als SQLite consistent moet worden gekopieerd, stop kort de app of gebruik de ingebouwde exportfunctie. Simpele host-kopie:

```powershell
Copy-Item .\data\config\sql_app.db .\backup-sql_app.db
```

## Restore
### Volledige restore vanaf host
1. Stop de containers.
2. Zet de inhoud van `data/` terug.
3. Start de containers opnieuw.

### Restore via de app
Gebruik de backup-pagina voor:
- SQL restore
- file restore uit ZIP

Let op: restore overschrijft bestaande inhoud.

## Tests
Lokale tests zijn buiten Docker uitgevoerd in een Python virtualenv.

Uitgevoerde commandos:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-test.txt
```

Test-run:

```powershell
$env:USE_REDIS='false'
$env:SECRET_KEY='test-secret'
$env:SIGNING_KEY='7f12a9c6f72a9f12c7750f3180a4e812e425af6ce74625a7f35ad268053db0c1'
$env:VERIFY_KEY='659f08516edfd015aa8ee8debf47d7f194ca40db2f74bf0bb8a3fb1c36091a1a828b67b01a218ba9d0f91ec3fcd133b13bfc818336b7cc17a26ee535d3862175'
.\.venv\Scripts\pytest -q
```

Resultaat:
- `22 passed`
- 8 warnings
- belangrijkste warnings:
  - FastAPI `@app.on_event("startup")` is deprecated
  - `datetime.utcnow()` deprecation uit dependency `python_jose`

## Problemen die tijdens setup zijn gevonden
1. Docker daemon draaide niet in deze omgeving.
   - `docker compose` kon niet verbinden met `dockerDesktopLinuxEngine`.
   - Daardoor kon de container niet echt worden opgebouwd of gestart in deze sessie.

2. De bestaande `docker-compose.dev.yml` gebruikte alleen een bind mount van de repo.
   - Daardoor waren config, uploads en exports niet expliciet persistent afgescheiden.
   - Dit is aangepast met aparte `data/` mounts.

3. Zonder `.env` geeft Compose waarschuwingen voor ontbrekende admin-variabelen.
   - Daarom is `.env.example` toegevoegd.

4. Tests falen op Windows zonder expliciete secrets.
   - `ubiblio/vars.py` verwacht standaard `openssl` op PATH voor keygeneratie.
   - In Docker is dat aanwezig, lokaal op Windows niet altijd.

## Aanbevolen lokale werkwijze
Voor dagelijks gebruik:
- `DEV=false`
- Docker Compose gebruiken
- regelmatig `data/` backuppen

Voor codewerk:
- `DEV=true`
- logs volgen met `docker compose ... logs -f`
- tests lokaal draaien in `.venv`

## Lokale start in één blok
```powershell
Copy-Item .env.example .env
# bewerk .env
# start Docker Desktop

docker compose -f docker-compose.dev.yml up --build -d
Start-Process http://localhost:8000
```
