# Mining Resource Frequency Mapping

Dit document bevat alleen de frequenties per resource op basis van de door jou aangeleverde tekst.

## Wat betekenen E-Type, Q-Type, M-Type, enz.

Dit zijn community-benamingen voor asteroid- of rock-klassen in Star Citizen mining. Ze worden vaak gecombineerd met scan-signatures zoals `1660`, `1700`, `1750`, `1850`, `1870`, `1900`, `5250`, `5550` en `5700`.

Belangrijk:

- de letter (`C-Type`, `E-Type`, `Q-Type`, enz.) beschrijft de rock-klasse
- de numerieke waarde is een scan-return die miners gebruiken om een rock of cluster snel te herkennen
- een hogere waarde is vaak een veelvoud van een basis-return en wijst dus vaak op een cluster, niet op een andere klasse
- de klasse alleen bepaalt niet of je hem kunt breken; massa, resistance, instability en je laser-setup bepalen dat in de praktijk

## Rock type referentie

Op basis van de huidige Star Citizen Wiki en community mining-referenties:

- `C-Type`
  Lage resistance, lage instability. Vaak Quartz, Copper, Tungsten en Iron. Kleine kansen op Quantanium en Stileron.
- `E-Type`
  Medium tot hoge resistance, medium instability. Vaak Silicon, Iron, Tungsten en Corundum. Kleine kansen op Quantanium en Laranite.
- `I-Type`
  Ice-klasse. Volgens de wiki momenteel alleen in Pyro. Lage resistance, medium instability.
- `M-Type`
  Hoge resistance, hoge instability. Vaak Quartz, Copper, Silicon en Titanium. Kleine kansen op Quantanium, Riccite en Stileron.
- `P-Type`
  Hoge resistance, hoge instability. Vaak Quartz, Copper, Iron en Titanium. Kleine kansen op Quantanium, Riccite en Stileron.
- `Q-Type`
  Lage resistance, medium instability. Vaak Quartz, Copper, Iron en Titanium. Kleine kansen op Quantanium en Stileron.
- `S-Type`
  Lage resistance, medium instability. Vaak Titanium, Quartz, Iron en Tungsten. Kleine kansen op Quantanium en Riccite.

## Welk mining tool, voertuig of ship kan dit meestal breken

Er is geen perfecte 1-op-1 regel per lettertype. In de praktijk is dit de bruikbare indeling:

- `Hand mining`
  Gebruik `Pyro RYT Multi-tool` + `OreBit Mining Attachment`.
  Bedoeld voor FPS / cave / hand-minable nodes.
  Niet bedoeld voor ROC- of ship-sized deposits.

- `ROC mining`
  Gebruik de `Greycat ROC`.
  Bedoeld voor crystalline mineral nodes die te groot zijn voor hand mining maar te klein of onpraktisch zijn voor Prospector/MOLE extractie.
  Praktisch: als een node te zwaar is voor de handtool maar nog duidelijk een gem/crystal node is, dan is dat ROC-territory.

- `Ship mining solo`
  Gebruik een `MISC Prospector` met een size-1 mining head.
  Beste inzet voor solo mining van grotere asteroid- en surface rocks.
  `Q-Type`, `C-Type` en veel `S-Type` rocks zijn vaak de makkelijkste kandidaten.
  `E-Type`, `M-Type` en `P-Type` worden sneller lastig als de massa groot is of de rock ongunstige resistance/instability heeft.

- `Ship mining multicrew`
  Gebruik een `ARGO MOLE` met size-2 mining heads.
  Praktisch beter voor grotere, lastigere en instabielere rocks.
  Vooral nuttig wanneer `E-Type`, `M-Type` en `P-Type` rocks te zwaar of te wild zijn voor een Prospector.

- `Grote mining platforms`
  `Arrastra` en later `Orion` vallen in de heavy multicrew categorie.
  Die horen conceptueel bij de grootste en lastigste targets, maar zijn niet relevant als snelle baseline voor de huidige dagelijkse mining-documentatie.

## Praktische vuistregels per type

- `Q-Type`
  Goede kandidaat om met een Prospector te checken. Community-wise vaak interessant voor high-value content.
- `E-Type`
  Vaak de moeite waard, maar door resistance/instability vaker iets waarvoor setup en ervaring belangrijk zijn.
- `M-Type` en `P-Type`
  Praktisch zwaardere kandidaten. Regelmatig beter geschikt voor sterkere ship lasers, modules of MOLE-support.
- `S-Type` en `C-Type`
  Vaak prettiger voor solo ship mining.
- `I-Type`
  Ice-specifiek. Niet behandelen als gewone ore-heuristiek.

## Laser-opmerking

Welke laser exact nodig is hangt niet alleen af van het type, maar vooral van:

- massa
- resistance
- instability
- gewenste optimal charge window
- modules en consumables

Voor de basisplatforms geldt:

- hand mining gebruikt de `OreBit Mining Attachment`
- ROC gebruikt de geïntegreerde ROC mining laser
- Prospector gebruikt een `Size 1` mining laser
- MOLE gebruikt `Size 2` mining lasers

Daarom is de juiste manier om dit document te lezen:

- type + scan-signature geeft je een snelle verwachting
- de uiteindelijke haalbaarheid wordt bevestigd door de detailed scan van de rock

## Voorbereidingsloadouts

Gebruik deze als praktische baseline wanneer iemand een resource-route plant en vooraf wil bepalen wat hij moet meenemen.

- `Starter / Drake Golem`
  Neem de `Pitman Mining Laser` als stock-startpunt mee en behandel de Golem als entry-level ship miner.
  Radar: `Surveyor-Lite` industrial radar.
  Gebruik `Okunis` of `WaveShift` gadgets wanneer de charge window lastig wordt.
  Praktisch doel: makkelijke rocks scouten, detailed scans leren lezen en slechte rocks overslaan.

- `Solo / MISC Prospector`
  Beste solo-baseline: `Helix I Mining Laser`.
  Modules: `Rieger-C3 Module` en `Focus III Module`.
  Actieve swap-ins: `Surge` en `Stampede` wanneer extra push nodig is.
  Gadgets: `WaveShift`, `BoreMax`, `Okunis`.
  Radar: `Surveyor-Lite` industrial radar.
  Dit is de standaard solo-aanbeveling voor serieuze ore mining.

- `Crew / ARGO MOLE`
  Beste crew-baseline: gemixte turretrollen in plaats van drie identieke beams.
  Hoofdsetup: `Arbor MH2` als stabiele baseline en `Lancet MH2` als support / extra power.
  Modules: `Focus III Module`, `Rieger-C3 Module`, met `Surge` en `Stampede` als situational actives.
  Gadgets: `BoreMax`, `WaveShift`, `Okunis`.
  Radar: `Surveyor` industrial radar.
  Dit is de veiligste keuze voor zwaardere of instabielere rocks.

- `Vehicle / ROC`
  Gebruik de `Greycat ROC` met de ingebouwde `Arbor MHV` laser.
  Beste voor surface gem nodes en niet voor klassieke ship-mining ore rocks.
  Zoek eerst met een support ship, land vervolgens dichtbij en werk de gem field met de ROC af.

- `FPS / Hand mining`
  Gebruik `Pyro RYT Multi-tool` + `OreBit Mining Attachment`.
  Nodig voor cave nodes en hand-minable deposits.
  Neem een backpack mee zodat je opbrengst niet direct capped raakt.

## Radar voor mining en scanning

Mining-prep moet ook radar meenemen, omdat de mining ships hun scan loop daarmee starten.

- `Prospector`
  Stock en aanbevolen: `Surveyor-Lite` industrial radar.
- `MOLE`
  Stock en aanbevolen: `Surveyor` industrial radar.
- `ROC`
  Stock en aanbevolen: `Surveyor-Go` industrial radar.
- `Grotere industrial/scanning platforms`
  Gebruik bij voorkeur een size-matching `Surveyor` of `FullSpec` industrial radar.

Huidige kooplocaties die online bevestigd zijn:

- `Surveyor`
  UEX toont verkoop bij `Omega Pro - New Babbage`.
- `Fullspec-Max`
  UEX toont verkoop bij `Omega Pro - New Babbage`.

Voor `Surveyor-Go`, `Surveyor-Lite` en sommige andere radarvarianten is online niet altijd een actuele winkelverkoop bevestigd. Praktisch betekent dat meestal: stock fitted houden tenzij een nieuwe in-game listing is bevestigd.

## Hoe scannen in de praktijk

- `Ship mining`
  Begin met brede ping sweeps.
  Vertraag zodra een contact zich oplost in een cluster.
  Ga pas committen nadat de detailed scan resistance, instability en massa heeft bevestigd.
  Een mooie resource is niet automatisch een goede rock als de massa slecht uitvalt.

- `ROC mining`
  Zoek laag en langzaam over oppervlaktes.
  Gebruik je ship om de field te vinden en stap daarna over op de ROC.

- `Hand mining`
  Zoek vooral caves, enclosed POI's en hand-minable pockets.
  Dit is geen wide-area ping gameplay zoals ship mining.

## Bronnen en betrouwbaarheid

De resourceverdelingen en scan-heuristieken zijn grotendeels community intelligence. Dat is belangrijk, want veel mining-distributiedata is in recentere patches meer server-side of dynamisch geworden.

Gebruikte bronnen:

- Star Citizen Wiki, `Asteroid`
  https://starcitizen.tools/Asteroid
- Star Citizen Wiki, `Mining`
  https://starcitizen.tools/Mining
- Star Citizen Wiki, `Mining laser`
  https://starcitizen.tools/Mining_laser
- Star Citizen Wiki, `Prospector`
  https://starcitizen.tools/Prospector
- Star Citizen Wiki, `MOLE`
  https://starcitizen.tools/MOLE
- Star Citizen Wiki, `Golem`
  https://starcitizen.tools/Golem
- Star Citizen Wiki, `ROC`
  https://starcitizen.tools/ROC
- Star Citizen Wiki, `OreBit Mining Attachment`
  https://starcitizen.tools/OreBit_Mining_Attachment
- Star Citizen Wiki, `Radar`
  https://starcitizen.tools/Radar
- Star Citizen Wiki, `Surveyor-Lite`
  https://starcitizen.tools/Surveyor-Lite
- Star Citizen Wiki, `Surveyor`
  https://starcitizen.tools/Surveyor
- Star Citizen Wiki, `Lancet MH2 Mining Laser`
  https://starcitizen.tools/Lancet_MH2_Mining_Laser
- Star Citizen Wiki, `Focus II Module`
  https://starcitizen.tools/Focus_II_Module
- Star Citizen Wiki, `Surge Module`
  https://starcitizen.tools/Surge_Module
- Star Citizen Wiki, `Mining gadget`
  https://starcitizen.tools/Mining_gadget
- Regolith Survey Corps rock type reference
  https://regolith.rocks/
- Red Monster SC, `Best Mining Loadouts in Star Citizen 4.1.1 - Golem, Prospector, and Mole`
  https://www.youtube.com/live/l-J-V9txQ1E
- Community observations about signal values and ice returns
  https://www.reddit.com/r/starcitizen/comments/1j6b5om/
- Community note that some rocks are hand-minable only up to very small mass and that larger small-node crystals become ROC territory
  https://www.reddit.com/r/starcitizen/comments/14fa8uq/
- UEX item listing, `Surveyor`
  https://uexcorp.space/items/info?is_kiosk=0&name=surveyor
- UEX item listing, `Fullspec-Max`
  https://uexcorp.space/items/info?name=fullspec-max

## Resource -> Frequenties

- 1850 M-Type -> Silicon
- 1850 M-Type -> Copper
- 1850 M-Type -> Tungsten
- 1850 M-Type -> Iron
- 5550 M-Type -> Quartz
- 1870 E-Type -> Bexalite
- 1720 S-Type -> Iron
- 5700 E-Type -> Taranite, Tungsten
- 1750 P-Type -> Copper
- 1870 E-Type -> Aluminium
- 1750 P-Type -> onbekend
- 1750 P-Type -> Bexalite
- 1850 M-Type -> Agricium
- 1850 M-Type -> Gold
- 1900 E-Type
- 5250 P-Type -> Laranite, Taranite
- 1750 P-Type -> Taranite
- 1850 P-Type
- 1850 M-Type -> Copper
- 1870 Q-Type -> Titanium
- 5700 E-Type -> Silicon
- 1660 I-Type -> Raw Ice
- 1850 C-Type -> Titanium
- 3400 C-Type -> Quartz
- 1700 C-Type -> Quantanium
- 1720 S-Type -> Beryl
- 1850 M-Type -> Agricium
- 1720 S-Type -> Titanium
- 1870 Q-Type -> Tungsten
- 5250 P-Type -> Taranite, Copper
- 1700 C-Type -> Iron
- 1700 C-Type -> Taranite
- 3400 C-Type -> Hephaestanite
- 5550 M-Type -> Agricium
- 1660 I-Type -> Hephaestanite
- 1850 M-Type -> Agricium
- 5700 E-Type -> Gold
- 1870 Q-Type -> Tin
- 1700 C-Type -> Quartz
- 1750 P-Type -> Corundum
- 5250 P-Type -> Laranite, Copper
- 5700 E-Type -> Beryl, Tungsten
- 1870 Q-Type -> Stileron
- 1900 E-Type
- 1720 S-Type -> Laranite
- 1850 C-Type -> Hephaestanite
- 1870 Q-Type -> Gold
- 1850 M-Type -> Agricium
- 1870 Q-Type -> Laranite
- 5700 E-Type -> Beryl, Taranite
- 10000 -> salvage panels
