# s7tools: Übungsprojekt für CI/CD mit GitHub Actions

Ein kleines, echtes Python-Paket mit Tests und einer vollständigen Pipeline. Es ist zum Ausprobieren auf GitHub
gedacht: hochladen, zusehen, wie die Pipeline läuft, absichtlich Fehler einbauen und lesen, was rot wird.

Was drin ist:

| Datei | Inhalt |
|---|---|
| `src/s7tools/tpkt.py` | TPKT-Rahmen bauen und prüfen (wie Übung 02) |
| `src/s7tools/address.py` | S7-Adressen parsen (wie Übung 08) |
| `src/s7tools/client.py` | TCP-Client: einen TPKT-Rahmen senden und genau einen zurücklesen |
| `tests/` | Unit-Tests, dazu Integrationstests gegen eine simulierte SPS (`conftest.py`) |
| `pyproject.toml` | Paketdefinition, pytest- und ruff-Einstellungen |
| `.github/workflows/ci.yml` | die Pipeline: Lint, Unit-Tests als Matrix, Integrationstests, Paket, Release |

Die Pipeline (Details im Schnellkurs, Teil 3):

```
Lint (ruff) ──> Unit-Tests: Ubuntu + Windows × Python 3.10 + 3.13 (4 Jobs parallel) ──> Integrationstests ──> Paket
                                                                                                         └─> Release (nur bei Tag v*)
```

## 1. Lokal ausprobieren (optional, 5 Minuten)

Im Ordner `demo-project` (venv wie in `python-practice/SETUP.md`, Abschnitt 3):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
ruff check .                           # Lint
pytest -m "not integration"            # Unit-Tests
pytest -m integration                  # Integrationstests gegen die simulierte SPS
pytest --cov=s7tools                   # alle Tests mit Testabdeckung
```

Genau diese Befehle führt die Pipeline auch aus, nur auf GitHubs Rechnern. Das ist der Kern von CI: Was lokal
läuft, läuft bei jedem Push automatisch und für alle gleich.

## 2. Auf GitHub bringen

Wichtig: GitHub führt Workflows nur aus `.github/workflows/` **im Wurzelordner** eines Repos aus. Darum läuft die
Pipeline im Lebenslauf-Repo nicht, und das Projekt braucht ein eigenes Repo.

1. Auf github.com oben rechts **+ > New repository**. Name z. B. `s7tools-ci-demo`, **Public** (dann sind die
   Actions-Minuten unbegrenzt kostenlos; privat gibt es ein Monatskontingent, und Windows-Minuten zählen doppelt).
   **Kein** README, keine .gitignore anhaken: das Repo muss leer sein.
2. Den Ordner `demo-project` irgendwohin kopieren, wo noch kein Git-Repo ist (z. B. `C:\Users\<du>\code\s7tools-ci-demo`),
   dort ein Terminal öffnen und:

   ```powershell
   git init -b main
   git add .
   git commit -m "Erste Version"
   git remote add origin https://github.com/<dein-name>/s7tools-ci-demo.git
   git push -u origin main
   ```

   Beim ersten Push öffnet sich ein Browserfenster zur Anmeldung bei GitHub.
   Ohne Git geht es auch im Browser: *Add file > Upload files* und alle Dateien hineinziehen. Der versteckte Ordner
   `.github` wird dabei leicht vergessen; dann im Repo *Add file > Create new file*, als Name
   `.github/workflows/ci.yml` eintippen und den Inhalt der Datei hineinkopieren.
3. Im Repo den Tab **Actions** öffnen. Der Lauf „CI" startet von selbst. Ein Klick darauf zeigt den Graphen der Jobs;
   ein Klick auf einen Job zeigt jeden Schritt mit seinem Log.

## 3. Übungen (je 5 bis 10 Minuten)

Jede Übung: ändern, `git add . ; git commit -m "..." ; git push`, im Actions-Tab zusehen, dann zurückändern.

1. **Alles grün:** Lies im Lauf nach, welche Jobs parallel liefen und welche aufeinander gewartet haben (`needs`).
   Lade unten unter *Artifacts* einen JUnit-Bericht und das Paket `dist` herunter und sieh hinein.
2. **Ein Test wird rot:** in `src/s7tools/tpkt.py` aus `len(payload) + HEADER` den Ausdruck `len(payload) + 3` machen.
   Welche Jobs werden rot, welche laufen gar nicht mehr? Finde im Log den Test und die Zeile.
3. **Lint wird rot:** oben in `client.py` eine unbenutzte Zeile `import os` einfügen. Was passiert mit den Tests?
   (Sie starten gar nicht, weil sie `needs: lint` haben: schnelle Prüfungen zuerst, das spart Zeit.)
4. **Nur ein Betriebssystem bricht:** in `address.py` ganz oben `import os` ergänzen (über `import re`) und in
   `size_bytes` vor dem `return` diese zwei Zeilen einfügen (mit 4 und 8 Leerzeichen eingerückt):

   ```python
       if os.name == "nt":
           return 0
   ```

   Nur die Windows-Jobs werden rot; `fail-fast: false` lässt die Linux-Jobs trotzdem zu Ende laufen. Genau dafür gibt
   es die Matrix: Fehler, die nur auf einer Plattform auftreten.
5. **Pull Request mit Sperre:** *Settings > Branches > Add branch ruleset* (oder *Add rule*) für `main`:
   *Require a pull request before merging* und *Require status checks to pass*, als Checks die Unit-Test-Jobs
   wählen. Dann einen Branch anlegen (`git switch -c kaputt`), den Fehler aus Übung 2 pushen und auf GitHub einen
   Pull Request öffnen: Der Merge-Knopf ist gesperrt, solange die Pipeline rot ist. So schützt CI den Hauptzweig.
6. **Matrix erweitern:** in `ci.yml` bei `os:` noch `macos-latest` ergänzen. Wie viele Unit-Test-Jobs gibt es jetzt?
7. **Von Hand und nachts:** im Actions-Tab links „CI" wählen, rechts *Run workflow*. Der nächtliche Lauf (`schedule`)
   kommt von allein um 02:00 UTC.
8. **Release (das „CD"):** `git tag v0.1.0` und `git push origin v0.1.0`. Der Job „Paket" legt unter *Releases* ein
   Release mit dem Wheel an.

Danach kannst du im Gespräch ehrlich sagen: „Zur Vorbereitung habe ich mir eine Pipeline mit GitHub Actions
gebaut: Lint, Unit-Tests als Matrix über Windows und Linux, Integrationstests gegen eine simulierte SPS, Paket und
Release, und ich habe ausprobiert, wie ein roter Test den Merge sperrt."
