# Addendum: Erweiterte Systemarchitektur der SleepApnea-Monitor App (v0.1.8+)

Die ursprüngliche Konzeptstudie („Schlafapnoe-Erkennung per Android-App.md“) definierte die fundamentalen Anforderungen an ein lokales Edge-KI-System zur Überwachung von Atemgeräuschen. Die aktuelle Implementierung der App übertrifft diese Spezifikationen in mehreren kritischen Bereichen signifikant und entwickelt das System von einem reinen Monitor zu einem **autonomen, selbst-optimierenden Gesundheits-Assistenten**.

Dieses Addendum dokumentiert die technologischen Durchbrüche und Architektur-Upgrades, die über den initialen Entwurf hinausgehen.

## 1. Storage-Effizienz: Entkopplung von ML-Inferenz und Langzeit-Logging
Während die Konzeptstudie primär auf die Extraktion von WAV-Daten (PCM) für das Modell fokussierte, stieß dies in der Realität auf massive Speicherprobleme (ca. 4 GB pro Nacht bei unkomprimiertem Audio).
Die App nutzt nun eine gespaltene Audio-Architektur:
- **In-Memory PCM für KI:** Ein zyklischer Ringpuffer fängt kontinuierlich 16-kHz-PCM-Daten ab, die exklusiv für das YAMNet-Modell (und den RMS-Gatekeeper) im RAM gehalten werden. Es entstehen keine Festplatten-Latenzen oder Abnutzungserscheinungen.
- **AAC/M4A für Langzeit-Logging:** Parallel läuft ein MediaRecorder, der die Nacht hocheffizient als AAC (`.m4a`) aufzeichnet. Dies reduziert die Dateigrößen von Gigabytes auf wenige Megabytes (ca. 90% Ersparnis), ermöglicht aber dennoch eine spätere manuelle Überprüfung der akustischen Ereignisse durch den Nutzer.

## 2. Das "Mechanistische Gehirn": Autonome Selbst-Optimierung
Der revolutionärste Aspekt der neuesten Version ist das autonome "Recommendation Brain". Das System analysiert am Morgen nicht nur die rohen CSV-Daten, sondern korreliert sie mit den historischen Metadaten (den Einstellungen, die *zum Zeitpunkt* der Aufnahme aktiv waren).
- **Relativ-Optimierung:** Die App erkennt Fehlkonfigurationen (z. B. 0 Alarme trotz hoher KI-Konfidenz, oder 30 Alarme durch Überempfindlichkeit) und bietet per One-Click-Button eine direkte Anpassung an. Die Korrektur-Vektoren beziehen sich nicht auf statische Default-Werte, sondern auf die im Header des Nacht-Logs gespeicherten Parameter.
- **Protection of ML-Integrity:** Spezielle Testläufe ("E2E-Tests") werden automatisch als solche im Log markiert (`test=true`), sodass sie das Gehirn nicht mit künstlichen Fehlalarmen "vergiften".
- **Akkumulierte Gewichtung (In Planung/Implementierung):** Die App lernt über mehrere Nächte hinweg die individuellen Schwellenwerte (z.B. Snore-Score) anzupassen und verschiebt die Empfindlichkeit des TFLite-Modells dynamisch.

## 3. Dynamische Label-Gewichtung und Interaktives Onboarding (Morning Questionnaire)
Während das Basis-YAMNet-Modell statisch ist, wird die *Interpretation* der Ausgabesignale dynamisch. 
- Das System integriert eine "Guten Morgen"-Befragung (getriggert durch die ersten signifikanten Smartphone-Bewegungen des Tages per Akzelerometer).
- Ein logarithmischer Fragebogen erfasst die subjektive Qualität der Nacht (Wurden Sie zu oft geweckt? War der Ton zu laut?).
- Die ML-Klassifikations-Schwellen (z.B. "Apnoe-Konfidenz muss > 0.40 sein") werden daraufhin algorithmisch modifiziert. Meldet der Nutzer "Oft grundlos geweckt", wird das Gewicht der Apnoe-Erkennungsschwelle angehoben.

## 4. Adaptive User Experience und i18n
Die Konzeptstudie fokussierte rein auf die akustische Auslösung. Die App verfügt nun über:
- **Material Deep Night Themes:** Automatische System-Theme-Anpassung zur Schonung der Augen im Schlafzimmer.
- **Micro-Controls:** Frei wählbare Alarm-Dauer und noch präzisere Lautstärken-Kontrolle über Slider.
- **Internationalization (i18n):** Vollständige Mehrsprachigkeit (Deutsch/Englisch), um eine breitere klinische Testgruppe zu erreichen.

## 5. DND-Override und Ausfallsicherheit
Zusätzlich zu den vorgeschlagenen `AudioAttributes` (USAGE_ALARM) nutzt die App nun vollumfängliche Berechtigungseskalationen, inklusive tiefgreifendem `ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS`-Handling. Damit umgeht die App selbst modifizierte Custom-ROMs (z. B. MIUI oder ColorOS), die herkömmliche Wecker im DND-Modus blockieren würden.
