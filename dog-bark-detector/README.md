# Dog Bark Detector

Rileva automaticamente gli abbai in registrazioni audio WAV lunghe (anche ore)
e produce un unico file con solo le sequenze di abbaio, con 3 secondi di
margine prima/dopo e sequenze vicine (gap < 5s) unite in un unico blocco.

## Perché niente YAMNet di default

Il primo approccio testato (YAMNet via TensorFlow.js) non riconosceva mai gli
abbai acuti di un Chihuahua come classe dominante, nemmeno a soglie di
confidenza molto basse — il modello è tarato principalmente su cani di taglia
medio-grande. L'analisi spettrale ha però mostrato che l'abbaio si concentra
nettamente nella banda 1000-4000 Hz (rumore di fondo: sotto i 500 Hz), quindi
il rilevatore di default funziona così:

1. **Filtro passa-banda** 1000-4000 Hz sul segnale.
2. **Energia RMS** sul segnale filtrato, confrontata con una soglia adattiva
   calcolata sul rumore di fondo locale (percentile mobile).
3. **Conferma di forma spettrale**: per ogni candidato controlla che la
   frequenza dominante sia in un range plausibile per un abbaio, che una
   quota sufficiente dell'energia totale sia nella banda 1000-4000 Hz
   (scarta rumori a banda larga come treni/traffico), e che l'energia sia
   concentrata in un picco stretto attorno alla frequenza dominante invece
   che dispersa su tutta la banda (scarta transienti a banda larga come
   passi/ciabatte, che superano la soglia di energia ma non hanno la forma
   armonica di un abbaio).
4. **Normalizzazione del volume** sull'output finale (default: picco a
   -1dBFS), perché le registrazioni fatte con headroom (es. -19dB di picco
   per evitare clipping) risultano altrimenti troppo silenziose da riascoltare.

YAMNet resta disponibile come **conferma opzionale** (`--use-yamnet`) per
scartare ulteriori falsi positivi, ma non è necessario di default.

## File grandi (anche >1GB)

L'analisi non carica mai l'intero file in RAM: legge il WAV a blocchi
(default 600s, configurabile con `--block-seconds`) con un margine di
contesto tra un blocco e l'altro (`--block-overlap-seconds`, default 10s)
per non perdere abbai a cavallo di un confine tra blocchi. Anche il taglio
finale legge solo gli intervalli di tempo effettivamente da estrarre, mai il
file intero.

## Esaltare l'abbaio nell'output (`--enhance`)

Il registratore, fermo e non direzionale, cattura molto più rumore di fondo
di quanto se ne percepisca a orecchio dalla propria posizione, dove l'abbaio
risulta relativamente più presente. `--enhance` taglia il rumore sotto
`--enhance-highpass` (default 400 Hz, sotto la frequenza dell'abbaio) e
aggiunge un boost parallelo sulla banda `--enhance-boost-band` (default
1200-2500 Hz, `--enhance-boost-db` default +6dB) invece di isolare l'abbaio
con un filtro stretto, che lo farebbe suonare innaturale.

È stato provato anche un gate di rumore (abbassare il volume fuori dalle
finestre di abbaio rilevate) ma è stato **rimosso**: introduceva cambi di
volume troppo bruschi e a tratti "cancellava" parzialmente l'abbaio,
suonando innaturale.

## Ridurre il rumore di fondo (`--denoise`)

Al posto del gate, riduzione del rumore continua e per-frequenza
([noisereduce](https://pypi.org/project/noisereduce/), modalità non
stazionaria — adatta a rumore variabile come treni/traffico). Combinabile
con `--enhance` (prima denoise, poi EQ): sul file di test porta il
contrasto abbaio/rumore a 10-16dB (a seconda della finestra di misura)
contro 5dB della sola EQ, senza gli scatti di volume del gate.
`--denoise-prop-decrease` (default 0.9) regola l'aggressività.

**Provato e scartato**: [DeepFilterNet](https://github.com/rikorose/deepfilternet),
rete neurale specializzata per rumore non stazionario, spesso citata come
superiore ai metodi tradizionali. Sul nostro caso **cancella l'abbaio quasi
del tutto insieme al rumore** (picco ridotto di ~50dB) perché è addestrata
specificamente sulla voce umana — un abbaio acuto di Chihuahua è troppo
diverso dal parlato per essere riconosciuto come segnale da preservare.
Stesso problema già visto con YAMNet. Da tenere in considerazione per un
futuro filtro di riconoscimento/pulizia della voce umana, dove invece è
probabilmente un'ottima scelta.

## Installazione

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`tensorflow` / `tensorflow-hub` (in requirements.txt) servono solo se usi
`--use-yamnet`: puoi ometterli se non ti interessa quella modalità.

## Uso

Analisi rapida senza tagliare l'audio (utile per tarare i parametri):

```bash
python3 detect_barks.py registrazione.wav --dry-run
```

Estrazione completa con file concatenato + clip separate per riascolto:

```bash
python3 detect_barks.py registrazione.wav -o output/combined.wav --export-segments
```

Più file insieme (concatenati in ordine cronologico):

```bash
python3 detect_barks.py giorno1.wav giorno2.wav giorno3.wav -o output/combined.wav --sort name
```

Output generati accanto al file indicato con `-o`:
- `combined.wav` — file finale con solo le sequenze di abbaio
- `combined/NNN_*.wav` — clip singole di ogni sequenza (con `--export-segments`)
- `combined_report.csv` / `.json` — timestamp originali, numero di abbai per
  sequenza, offset nel file finale
- `combined_labels.txt` — label track importabile in Audacity (File → Import
  → Labels) per verificare visivamente il file finale

## Parametri principali

| Parametro | Default | Significato |
|---|---|---|
| `--pad` | 3.0 | Margine (s) prima/dopo ogni sequenza |
| `--gap` | 5.0 | Gap massimo (s) tra abbai per considerarli la stessa sequenza |
| `--band` | 1000-4000 | Banda di frequenza dell'abbaio |
| `--threshold-factor` | 3.0 | Quanto deve superare il rumore di fondo locale per contare come candidato |
| `--min-band-energy-ratio` | 0.35 | Frazione minima di energia nella banda per confermare un candidato |
| `--min-peak-concentration` | 0.35 | Frazione minima di energia concentrata attorno al picco (scarta rumori a banda larga tipo passi) |
| `--normalize-dbfs` | -1.0 | Picco target (dBFS) di normalizzazione del volume in output |
| `--no-normalize` | off | Disabilita la normalizzazione del volume |
| `--use-yamnet` | off | Conferma aggiuntiva con YAMNet (richiede tensorflow) |
| `--block-seconds` | 600.0 | Dimensione dei blocchi letti dal disco durante l'analisi |
| `--block-overlap-seconds` | 10.0 | Margine di contesto tra un blocco e l'altro |
| `--enhance` | off | Esalta l'abbaio rispetto al rumore di fondo nell'output |
| `--enhance-highpass` | 400.0 | Frequenza (Hz) sotto cui tagliare il rumore di fondo (con `--enhance`) |
| `--enhance-boost-band` | 1200-2500 | Banda da rinforzare (con `--enhance`) |
| `--enhance-boost-db` | 6.0 | Guadagno (dB) applicato alla banda rinforzata (con `--enhance`) |
| `--denoise` | off | Riduce il rumore di fondo in modo continuo per-frequenza (noisereduce) |
| `--denoise-prop-decrease` | 0.9 | Aggressività della riduzione rumore, 0-1 (con `--denoise`) |
| `--denoise-stationary` | off | Usa il profilo di rumore stazionario invece di quello non-stazionario (con `--denoise`) |

Se il rilevamento perde abbai reali: abbassa `--threshold-factor` o
`--min-band-energy-ratio`. Se prende troppi falsi positivi: alzali, oppure
aggiungi `--use-yamnet`.

## Taratura sui propri file

I default sono stati calibrati su un file di test reale (Chihuahua, TASCAM
DR-44WL, 48kHz) con 4 abbai confermati a orecchio. Su file diversi (distanza,
rumore di fondo diverso) può servire un aggiustamento: usa `--dry-run` per
vedere i candidati grezzi stampati a schermo con frequenza dominante e
rapporto di energia in banda, e regola i parametri di conseguenza prima di
lanciare l'estrazione vera.
