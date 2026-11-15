# SpeicherPilot

Speicherplatz verstehen und gefahrlos freiräumen – lokale Windows-App (Python + Edge-App-Fenster, keine Installation nötig).

**Start:** Desktop-Verknüpfung „SpeicherPilot“ oder `SpeicherPilot starten.bat`.
Für Windows-Update-Reste & System-Temp: in der App „Als Administrator neu starten“.

## Bereiche
- **Übersicht** – Laufwerke, freiräumbares Potenzial, Top-Empfehlungen, größte Einzeldateien
- **Schnellreinigung** – Temp, Browser-/App-Caches, Shader-Cache, Miniaturansichten, Absturzberichte, Update-Reste, Entwickler-Caches, alte Installer, Papierkorb
- **Lange nicht benutzt** – Ordner nach Alter (Änderungsdatum) mit Erklärung, Inhaltsanalyse und Empfehlung
- **Riesige Dateien** – nach Größe hervorgehoben (GIGANTISCH ≥ 20 GB, RIESIG ≥ 5 GB, SEHR GROSS ≥ 1 GB)
- **Speicherkarte** – Treemap zum Hineinzoomen, Farbe = wie lange unverändert

## Sicherheit
- Analyse liest nur. Löschen nur nach Bestätigung, standardmäßig in den Papierkorb.
- Gesperrt: Windows, Programme (→ über Einstellungen › Apps deinstallieren), ProgramData, Store-Apps, Systemdateien, Sammelordner (Laufwerke, Benutzerordner, Desktop …), einzelne Spieldateien.
- Server lauscht nur auf 127.0.0.1, mit Zufallstoken und Host-Prüfung; beendet sich, wenn das Fenster geschlossen wird.
- Log: `%LOCALAPPDATA%\SpeicherPilot\log.txt`
