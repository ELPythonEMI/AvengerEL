# AvengerEL

**Trasforma il caos delle tue schede Chrome in una workstation ordinata.**

Realizzato da [ELpythonEMI](https://github.com/ELpythonEMI)  
Versione 1.0 | Richiede Python 3.8+

![AvengerEL Preview](assets/AvengerEL.png)

---

## L'idea dietro il progetto

Quante volte ti è capitato di premere Alt+Tab all'infinito, cercando freneticamente la scheda giusta tra decine di finestre aperte? A me succede spesso. È frustrante vedere il proprio tempo scivolare via solo per riorganizzare lo schermo invece di lavorare.

Ho scritto AvengerEL per risolvere questo piccolo ma fastidioso problema.

Non è un'estensione del browser complessa e nemmeno un software pesante da installare. È uno script Python leggero che organizza automaticamente le tue finestre di Google Chrome in modalità split-screen:
- Due finestre affiancate, per quando devi confrontare due documenti o video.
- Quattro quadranti precisi, per avere una panoramica completa di tutto ciò che stai facendo.

Il punto forte è la semplicità. Non devi creare account, non ci sono dipendenze esterne complicate da gestire. Se hai Python e Chrome, sei pronto a partire.

---

## Come iniziare

Non c'è bisogno di configurazioni lunghe. Scarica il progetto, entra nella cartella e avvialo:

```bash
git clone https://github.com/ELpythonEMI/AvengerEL.git
cd AvengerEL
python avenger_el.py
```

### Vuoi aprire siti specifici?
Puoi passare gli indirizzi web direttamente come argomenti. Lo script aprirà Chrome e posizionerà le pagine indicate nei vari quadranti:

```bash
python avenger_el.py https://youtube.com https://twitter.com https://instagram.com https://tiktok.com
```

**Nota per gli utenti Linux:**
Lo script utilizza `xdotool` per gestire le finestre. Se non lo hai già installato, puoi aggiungerlo con:

```bash
sudo apt install xdotool
```

---

## Come usare i controlli

Ho aggiunto una piccola interfaccia per darti controllo manuale senza dover modificare il codice:

- **Nascondi barra verticale**: La barra laterale scompare per lasciarti più spazio visivo.
- **Dividi in 4 (Split x4)**: Passa dalla vista a due finestre a quella a quattro quadranti. In questa modalità apparirà anche una barra orizzontale inferiore.
- **Nascondi barra orizzontale**: Disponibile solo nella modalità a 4 quadranti, ti permette di nascondere la barra inferiore.
- **Chiudi tutto (X)**: Chiude tutte le finestre aperte dallo script e termina l'esecuzione.
- **Tasto Esc**: Fa la stessa cosa del pulsante "Chiudi tutto", ma direttamente da tastiera.

---

## Compatibilità

Il comportamento dello script varia leggermente a seconda del sistema operativo, poiché si affida alle API native per il posizionamento delle finestre.


## Requisiti tecnici

- Python 3.8 o superiore
- Google Chrome installato e accessibile dal PATH di sistema
- xdotool (solo su Linux)

*Non sono necessarie librerie Python esterne. Lo script utilizza esclusivamente moduli standard.*

---

## Licenza e contributi

Questo progetto è rilasciato sotto licenza MIT. Sentiti libero di usarlo, studiarlo, modificarlo e condividerlo.

Se trovi utile questo strumento o se apporti miglioramenti (specialmente per il supporto Linux o macOS), fammelo sapere. Le pull request e i feedback sono sempre benvenuti.

Buon lavoro.