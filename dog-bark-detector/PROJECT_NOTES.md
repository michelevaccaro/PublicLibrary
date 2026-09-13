# Dog Bark Detector — contesto di progetto

Questo file esiste per far ripartire una nuova sessione Claude Code (es. in
locale, con accesso al filesystem dell'utente) senza perdere il contesto
accumulato in una sessione precedente molto lunga. Leggilo tutto prima di
agire: contiene decisioni, misurazioni reali e vicoli ciechi già esplorati
che non vanno rifatti da capo.

**Non è un CLAUDE.md**: nome scelto di proposito per non caricarsi in
automatico all'apertura di una sessione in questa cartella — l'utente
lavora su più progetti/repository/account e vuole decidere lui, di volta
in volta, quando questo contesto va letto. Leggilo solo se l'utente lo
chiede esplicitamente o ti indirizza su questo progetto.

## Come riprendere il progetto

- Repository: `michelevaccaro/PublicLibrary` (repo storicamente un sito
  statico non correlato — il progetto vive nella sottocartella
  `dog-bark-detector/`, per scelta esplicita dell'utente invece di un
  repository dedicato).
- Branch: `claude/dog-bark-detection-audio-f9trr8`.
- Clone: `git clone -b claude/dog-bark-detection-audio-f9trr8 https://github.com/michelevaccaro/PublicLibrary.git`,
  poi `cd PublicLibrary/dog-bark-detector`.
- Setup: `python -m venv .venv && .venv\Scripts\activate` (Windows) o
  `source .venv/bin/activate` (Linux/Mac), poi `pip install -r requirements.txt`.
  Tensorflow (`--use-yamnet`) e OneDrive sono extra separati, vedi sotto.
- Avvio web app: `python webapp/app.py`, poi `http://127.0.0.1:5000`.
- L'utente lavora su Windows, con un PC potente (32GB RAM, CPU forte, GPU) —
  gira tutto in locale, non ha senso proporre hosting cloud con risorse
  limitate (già tentato e scartato, vedi sezione OneDrive più sotto).

## Chi è l'utente e obiettivo del progetto

Michele (michele.vaccaro@gmail.com) vuole documentare in modo oggettivo gli
abbai eccessivi del cane di un vicino (Chihuahua), registrando con un
TASCAM DR-44WL (mic esterni, alimentazione phantom 48V) da circa 60 metri
di distanza (balcone). Serve uno strumento che analizzi le registrazioni
(anche di ore), isoli solo i tratti con abbai, e produca un unico file
"montaggio" utile a documentare il disturbo — l'output deve suonare il più
vicino possibile a come l'abbaio si sente davvero a distanza ravvicinata
(più "pieno"/fastidioso di quanto risulti nella registrazione grezza).

Progetto futuro pianificato (non ancora iniziato): un filtro analogo per
il parlato umano, quasi certamente basato su DeepFilterNet (vedi sotto
perché è stato scartato per gli abbai ma è probabilmente ottimo per la voce).

## Struttura repository

Il progetto vive in `dog-bark-detector/` dentro il repo
`michelevaccaro/PublicLibrary` (repo storicamente un sito statico non
correlato — si è deciso di usare una sottocartella invece di un repo
nuovo). Branch di lavoro: `claude/dog-bark-detection-audio-f9trr8`.

```
dog-bark-detector/
  detect_barks.py          CLI (uso avanzato, tutti i parametri esposti)
  requirements.txt          dipendenze base (numpy, scipy, librosa,
                             soundfile, noisereduce, flask)
  requirements-yamnet.txt   extra opzionali per --use-yamnet (tensorflow)
  requirements-onedrive.txt extra per l'integrazione OneDrive (parcheggiata,
                             vedi sotto)
  src/
    filters.py              bandpass Butterworth
    detection.py            rilevamento candidati (energia+spettro) +
                             versione streaming a blocchi
    postprocess.py          merge_and_pad: sequenze + padding
    segments.py             taglio/concatenazione/report, denoise/enhance
    enhance.py               EQ (enhance_bark_presence) + denoise (noisereduce)
    yamnet_confirm.py        conferma opzionale via YAMNet
    pipeline.py              orchestrazione usata dalla web app (locale)
    onedrive_auth.py         login MSAL — scritto ma NON collegato alla
                             web app attiva (vedi sezione OneDrive)
  webapp/
    app.py                  Flask, versione LOCALE (folder-based) — è la
                             versione attiva
    templates/index.html, static/app.js, static/style.css
  tests_audio/               file di test reali dell'utente (gitignored)
```

## Come funziona il rilevamento (src/detection.py)

**Niente ML/YAMNet di default.** Primo tentativo con YAMNet (TensorFlow):
non riconosceva mai l'abbaio acuto di un Chihuahua come classe dominante,
nemmeno a soglie di confidenza bassissime — è tarato su cani di taglia
medio-grande. Analisi spettrale sui file reali dell'utente ha mostrato che
il rumore di fondo domina sotto i 500Hz (233-250Hz) mentre l'abbaio si
concentra nettamente in banda 1000-4000Hz (dominante tipica 1350-2050Hz).

Pipeline (nessun modello, solo DSP):
1. **Bandpass 1000-4000Hz** sul segnale.
2. **Energia RMS** sul segnale filtrato vs **soglia adattiva** (percentile
   mobile del rumore di fondo locale). Default: `floor_window_s=3.0`,
   `floor_percentile=20`, `threshold_factor=3.0`.
3. **Conferma di forma spettrale** per ogni candidato:
   - `dominant_freq_hz`: calcolata sul segnale **filtrato**, non grezzo —
     bug trovato e corretto: sul segnale grezzo il rumore a bassa frequenza
     domina anche in finestre brevi, dando sempre ~0Hz. Range accettato:
     700-3500Hz.
   - `band_energy_ratio`: energia in banda 1-4kHz / energia totale, sul
     segnale **grezzo**. Soglia minima 0.35. Scarta rumore a banda larga
     (treni, traffico).
   - `peak_concentration`: energia entro ±150Hz dalla frequenza dominante /
     energia totale filtrata. Soglia minima 0.35. **Aggiunta dopo aver
     trovato falsi positivi da rumore di passi/ciabatte** che avevano
     energia e ratio sufficienti ma dispersa su tutta la banda invece che
     in un picco armonico stretto. Sui dati reali: abbai veri 0.41-0.81,
     rumori di passi 0.20-0.33.
4. **Lettura a blocchi** (`detect_candidates_streaming`): mai tutto il file
   in RAM, blocchi da 600s con 10s di overlap (per non perdere candidati a
   cavallo di un confine). Necessario per file di ore / oltre 1GB.

Tutti i parametri sono esposti come flag CLI in `detect_barks.py`.

## Post-processing (src/postprocess.py)

`merge_and_pad`: i candidati grezzi vengono raggruppati in "sequenze" se il
gap tra un abbaio e il successivo è < `gap_threshold_s` (default 5.0s), poi
ogni sequenza viene "paddata" di `padding_s` (default 3.0s) prima/dopo.
`Sequence` porta `bark_windows` (lista di tuple start/end assolute nel file
sorgente), da cui si derivano `bark_count` e `bark_starts`.

## Output ed elaborazione audio (src/segments.py, src/enhance.py)

- Taglio efficiente: legge solo i byte range richiesti dal file sorgente
  (mai l'intero file), anche per l'estrazione finale.
- **Normalizzazione**: picco finale a -1dBFS di default. Necessaria perché
  le registrazioni originali erano molto silenziose (headroom eccessivo in
  registrazione, vedi sezione TASCAM sotto) — senza normalizzazione l'output
  era quasi inudibile.
- Output scritto esplicitamente in **PCM_16** (non float32) per massima
  compatibilità di riproduzione.
- **`--enhance`** (`enhance_bark_presence`): highpass a 400Hz (taglia il
  rumore sotto la frequenza dell'abbaio) + boost parallelo sulla banda
  1200-2500Hz (+6dB) sommato al segnale filtrato-alto, invece di isolare
  l'abbaio con un passa-banda stretto (suonerebbe innaturale/sottile).
- **`--denoise`** (`denoise_background`, libreria `noisereduce`, modalità
  non stazionaria, `prop_decrease=0.9`): riduzione del rumore continua e
  per-frequenza. Scelta dopo un tentativo precedente con un **gate nel
  tempo** (abbassare di ~-18/-20dB tutto ciò che non è dentro una finestra
  di abbaio nota, con smoothing Hann) che è stato **costruito, testato e
  poi rimosso**: l'utente lo ha bocciato perché introduceva cambi di volume
  troppo bruschi e a tratti "cancellava" parzialmente abbai più deboli —
  suonava innaturale. **Non riproporre il gate nel tempo.**
- **`--denoise --enhance` insieme** (denoise poi EQ) è risultata la
  combinazione migliore secondo l'utente finora ("il risultato migliore").
  È il default nella web app.

### DeepFilterNet — provato e scartato per gli abbai

Rete neurale di noise suppression, buona reputazione specifica per rumore
non stazionario (treni/traffico). L'utente ha scaricato manualmente il
checkpoint (`models/DeepFilterNet3.zip` dal repo GitHub Rikorose/DeepFilterNet
— **non serve tutto il repo da 99MB**, solo questo file da ~8MB con dentro
`config.ini` + `checkpoints/model_120.ckpt.best`) e caricato in chat; è stato
estratto in `~/.cache/DeepFilterNet/DeepFilterNet3/` e testato con successo
dal punto di vista tecnico. **Risultato: cancella l'abbaio quasi del tutto
insieme al rumore** (picco ridotto di ~50dB) perché è addestrata
specificamente sulla voce umana — un abbaio acuto di Chihuahua è troppo
diverso dal parlato per essere riconosciuto come segnale da preservare.
Stesso identico problema di YAMNet. **Scartato per il progetto abbai.**
**Da riprendere per il futuro progetto voce umana**, dove probabilmente è
la scelta giusta.

### YAMNet — conferma opzionale, non testabile in sandbox cloud

`--use-yamnet` (`src/yamnet_confirm.py`) scarica il modello da tfhub.dev a
runtime: **bloccato dalla policy di rete di ambienti sandbox Claude Code
cloud** (403). Funziona normalmente su un PC con internet libero. Mai
verificato empiricamente se aiuta davvero a distinguere i casi ambigui
(vedi "Limite noto" sotto) — da testare in locale se si vuole riprendere.

## Risultati di taratura sui file reali (cronologia)

Tutti i default attuali sono tarati su questi file. Non ripartire da zero:

1. **File 1** (`000101_0024S3.wav`, 172.9s, mono, 48kHz/24bit, picco -26dBFS):
   4 abbai noti dall'utente (47.1/53.1/55.0/56.7s). Il rilevatore, dopo il
   fix del bug frequenza-dominante, trova 47.12/53.06/56.19/56.73/62.43/
   64.01s (6 abbai — i due extra confermati veri). Il bark a 55.0s è troppo
   debole per essere rilevato da solo ma rientra comunque nella sequenza
   fusa. Due falsi positivi iniziali (33.6s, 120.2s) erano rumore di
   ciabatte — origine del filtro `peak_concentration`.
2. **File 2** (`000101_0024S12.wav`, 72.5s, stereo, 48kHz/16bit, picco
   -4dBFS): timestamp quasi identici al file 1 (47.10/51.71/53.06/56.20/
   56.72/62.42/64.02s) — forte sospetto di **sovrapposizione/stessa sessione
   di registrazione** (canale diverso?), mai risolto. L'utente ha poi
   abbandonato questo file per uno nuovo.
3. **File 3** (`000101_0026S3_1215.wav`, 180s): soglie di default trovano 2
   sequenze reali (70.5/71.0/71.3s e 149.7s, confermate). Soglie allentate
   fanno emergere altri 2 candidati (157.2s, 171.6s) **confermati falsi
   positivi dall'utente** — buona validazione che i default (ratio 0.35,
   concentration 0.35) sono tarati bene senza bisogno di allentarli.
4. **File 4** (`0026S3_02.wav`, 120s): 4 sequenze trovate. Nell'ultima
   (85.2s + 91.2s) l'utente ha confermato che **solo 91.2s è vero**, 85.2s
   è falso positivo — ma è quasi indistinguibile su base spettrale pura
   (concentration 0.43 vs il range vero 0.41-0.81). **Limite noto e non
   risolto** dell'approccio spettrale puro: caso candidato per una futura
   conferma YAMNet, mai testata per il blocco di rete.
5. **File 5** (`0026S3_811.wav`, 180s): 7 sequenze trovate e inviate
   all'utente per conferma — **risposta non ancora arrivata**, la
   conversazione è stata interrotta da altri argomenti (web app, OneDrive).

## TASCAM: livelli di registrazione — stato aperto, da riprendere

- Prima registrazioni: headroom molto ampio (~-19dB secondo l'utente, o
  gain "0dB" sul device che dava picco -47dBFS in condizioni normali senza
  grossi rumori — terminologia mai riconciliata del tutto, trattare ogni
  numero come approssimativo finché non misurato direttamente da un file).
  Consigliato: puntare a picchi -12/-6dB con limiter attivo se disponibile.
- L'utente ha alzato il gain sul device da **0dB a +15dB** e fatto una
  nuova registrazione di test: **`260721_0046S3.wav`**. Non ancora
  misurata (blocco di trasferimento file, vedi sotto) — **primo passo da
  fare in una nuova sessione con accesso al filesystem locale**: leggere
  questo file (probabilmente nella cartella OneDrive locale
  dell'utente) e riportare picco/RMS effettivi in dBFS, confrontare con i
  target consigliati.
- Richiesta dell'utente non ancora implementata: aggiungere alla web app
  la visualizzazione di picco/dBFS per ogni file analizzato, così l'utente
  può auto-verificare i livelli senza dover mandare file a Claude.

## Web app (webapp/, Flask, solo locale)

Decisione finale (dopo un giro su hosting cloud, vedi sotto): gira **solo
in locale** sul PC dell'utente (`python webapp/app.py`,
`http://127.0.0.1:5000`). Ha 32GB RAM/CPU forte/GPU in locale — nessun
motivo di usare hosting cloud con risorse limitate.

Flusso (`src/pipeline.py: run_folder_pipeline`):
1. Utente sceglie tipo suono (solo "Abbaiare di Cani" attivo; "Parlato
   delle persone" presente nel menu ma disabilitato, riservato al progetto
   futuro) e inserisce il percorso della cartella sorgente (tipicamente la
   cartella OneDrive locale, es. `C:\Users\miche\OneDrive\...`).
2. Analizza tutti i `.wav` trovati direttamente nella cartella (esclude
   automaticamente output di run precedenti tramite pattern sul nome file,
   vedi `_is_previous_output` in pipeline.py — altrimenti un output
   verrebbe ri-analizzato come se fosse un nuovo file sorgente).
3. Se trova sequenze, crea un unico file combinato
   `abbai_AAAAMMGG_HHMMSS.wav` nella cartella sorgente stessa, con
   `--denoise` ed `--enhance` **sempre attivi** (combinazione migliore
   trovata finora).
4. Sposta tutti i file WAV analizzati (+ i report) in una sottocartella
   `FileAnalizzati/` della cartella sorgente. Alla fine la cartella
   sorgente contiene solo il/i file di output.

Testato end-to-end in sandbox con file reali dell'utente (validazione
cartella, multi-file, spostamento, esclusione output precedenti, casi
limite cartella vuota/non trovata/tipo suono non disponibile).

### OneDrive / hosting cloud — tentato e parcheggiato

Sequenza di eventi (per capire cosa NON rifare): richiesta iniziale web app
locale → poi l'utente, frustrato dall'installazione locale, ha chiesto
hosting online legato al repo GitHub → costruita integrazione OneDrive
completa (OAuth via MSAL, Microsoft Graph API) pensata per hosting su
Render.com → **arrivati al piano gratuito Render (512MB RAM / 0.1 CPU)
palesemente insufficiente** per il carico di lavoro (audio/numpy/scipy) →
l'utente ha 32GB RAM in locale, nessun senso usare quel piano → **tornati
alla versione locale** (ripristinata da un commit precedente).

Codice OneDrive rimasto nel repo ma **non collegato alla webapp attiva**
(verificato riga per riga dopo un reset del checkout, sono completi):
- `src/onedrive_auth.py`: login MSAL, cache token su file locale.
- `src/onedrive_client.py`: client Graph API (list/download/upload con
  upload session per file grandi/move via PATCH parentReference).
- `src/pipeline_onedrive.py`: `run_onedrive_pipeline`, equivalente di
  `run_folder_pipeline` ma sorgente/destinazione OneDrive — scarica i wav
  in una cartella temporanea, riusa **la stessa identica pipeline di
  rilevamento** (nessuna differenza di algoritmo dalla versione locale),
  poi carica l'output e sposta gli originali via Graph API.

Codice scritto con cura ma **mai testato end-to-end** (nessun modo di
ottenere un access token reale in sandbox cloud per provarlo). Se si
riprende questa strada, va innanzitutto validato con un vero login.
Dipendenze isolate in `requirements-onedrive.txt` (msal, requests,
gunicorn) per non appesantire l'installazione locale normale.

Nota tecnica sul perché l'accesso diretto a OneDrive da una chat Claude
cloud non ha mai funzionato: il connettore "Microsoft 365" non è mai stato
attivato per la sessione (va autorizzato dalle impostazioni Connectors di
claude.ai, richiede login Microsoft dell'utente — non è "discriminazione
verso account personali", è semplicemente un connettore mai collegato).
Google Drive invece risultava già connesso ma all'account di lavoro
sbagliato (michele.vaccaro@docusign.com invece di quello personale) e
quel disallineamento non è mai stato risolto.

## Gotcha ambientali incontrati (per non riscoprirli)

- **tensorflow spesso non ha wheel per le Python più recenti**: se resta in
  `requirements.txt` principale, fa fallire l'intera installazione anche
  per chi non usa `--use-yamnet`. Tenuto separato in
  `requirements-yamnet.txt`.
- **Python 3.14**: molto recente, `numba` (dipendenza di `librosa`) ha
  aggiunto supporto solo di recente (numba 0.66.0). Installazione può
  funzionare ma è bleeding-edge; il primo import/uso di librosa compila
  JIT e può sembrare "bloccato" per 30-60 secondi — non è un crash, solo
  pazienza.
- Su Windows, `dir` prima di dare per scontato un percorso: l'utente ha
  clonato l'intero repo `PublicLibrary` dentro una cartella chiamata
  `AudioDetect` (non dentro una sottocartella `PublicLibrary`) — il
  progetto vero resta comunque dentro `dog-bark-detector/` a un livello in
  più di quanto ci si aspetterebbe dal nome della cartella genitore.

## Come continuare da qui

1. Misura `260721_0046S3.wav` (gain +15dB) e riporta picco/RMS reali.
2. Se l'utente non ha ancora confermato quali sequenze del File 5 sono
   abbai veri, chiediglielo (serve per continuare a validare i default).
3. Costruisci la visualizzazione picco/dBFS nella web app (richiesta
   dall'utente, non ancora fatta).
4. Tieni traccia di eventuali nuovi falsi positivi/negativi con le stesse
   metriche già in uso (dominant_freq, band_energy_ratio, peak_concentration)
   prima di proporre modifiche ai default — sono già stati validati su 4
   file reali, non stravolgerli senza nuova evidenza concreta.
5. Il progetto voce umana (DeepFilterNet) è pianificato ma non iniziato:
   non cominciarlo di iniziativa, aspetta che l'utente lo chieda
   esplicitamente.
