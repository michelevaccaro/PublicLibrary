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
   frequenza dominante sia in un range plausibile per un abbaio e che una
   quota sufficiente dell'energia totale sia nella banda 1000-4000 Hz
   (scarta rumori a banda larga come treni/traffico che superano la sola
   soglia di energia).

YAMNet resta disponibile come **conferma opzionale** (`--use-yamnet`) per
scartare ulteriori falsi positivi, ma non è necessario di default.

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
| `--use-yamnet` | off | Conferma aggiuntiva con YAMNet (richiede tensorflow) |

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
