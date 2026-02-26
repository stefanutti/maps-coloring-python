/* fullgen.c */
/* Aktuellste Version -- mit Symmetriebetrachtungen */
/* 12.9.1996:   - zusaetzliche Option "pid"   (fuer GenView) 
   17.7.1996:   - Fehler-Exits durchnumeriert (fuer GenView)
                - mehrere Symmetrien erlaubt 
  24.10.2000:   - added code 8 for sparse6 output
                    and made some other insignificant changes */
/* 24.2.2011: S+12 -> S+13 in dualcode arraygroesse. Hier wird ab 1 
   gezaehlt... */
/* 6.10.2011: Fehler verbessert, der ab 136 Knoten Fullerene (eins bei 136) faelschlicherweise verwarf. */
/* 16.6. 2014: problem mit code 3 und mehreren knotenzahlen und gleichzeitig
   output auf stdout geloest. */
/* 13.2.2016: Fehler bei Detektierung von Cs mit Fixkanten verbessert */
/* 23.2.2016: Den Effekt desselben Fehlers bei anderen Gruppen entfernt. */

#include<sys/types.h>
#include<unistd.h>
#include<stdlib.h>
#include<stdio.h>
#include<ctype.h>
#include<limits.h>
#include<sys/stat.h>
#include<string.h>

#ifndef NOTIMES
#include<time.h>
#include<sys/times.h>
#endif //NOTIMES

#define S        140           /* Maximale Anzahl der 6-Ecke */
#define N        ((4*S)+20)    /* Maximal moegliche Anzahl der Knoten */


#define aussen   (N+2) /* so werden kanten nach aussen markiert */

#define infty    LONG_MAX
#define FL_MAX   UCHAR_MAX
#define KN_MAX   USHRT_MAX
#define unbelegt FL_MAX
#define leer     KN_MAX-1
#define f_leer   FL_MAX-1
#define False    0
#define True     1
#define nil      0
#define reg      3
#define filenamenlaenge 200 /* sollte vorerst reichen */

#ifndef NOTIMES
#if !defined(CLK_TCK) && !defined(_SC_CLK_TCK)
#include <time.h>
#endif
#if !defined(CLK_TCK) && !defined(_SC_CLK_TCK)
#include <unistd.h>
#endif
#if !defined(CLK_TCK) && defined(_SC_CLK_TCK)
#define CLK_TCK sysconf(_SC_CLK_TCK)
#endif
#ifndef CLK_TCK
#define CLK_TCK 60     /* If the CPU time stated by the program appears
		      to be out by a constant ratio, the most likely
		      explanation is that the code got to this point but
		      60 is the wrong guess.  Another common value is 100. */
#endif

#define time_factor CLK_TCK
#endif //NOTIMES

/*
   the macro 'my_endianness' is a char value of 'b' for big-endian
   and 'l' for little-endian machines
*/
static unsigned short word = (((unsigned short) 'b') << 8) | 'l';
# define  my_endianness  (* (char *) &word)


/* weitere Konstanten (TH) fuer die Kennzeichnung der Symmetriegruppen: */
/* (Werte nicht veraendern - oder synchron dazu die Strings mit den
   Bezeichnungen der Symmetriegruppen aendern) */
#define C1__    1
#define C2__    2
#define Ci__    3
#define Cs__    4
#define C3__    5
#define D2__    6
#define S4__    7
#define C2v__   8
#define C2h__   9
#define D3__   10
#define S6__   11
#define C3v__  12
#define C3h__  13
#define D2h__  14
#define D2d__  15
#define D5__   16
#define D6__   17
#define D3h__  18
#define D3d__  19
#define T__    20
#define D5h__  21
#define D5d__  22
#define D6h__  23
#define D6d__  24
#define Td__   25
#define Th__   26
#define I__    27
#define Ih__   28


/* konstante Strings zur Kennzeichnung der Symmetriegruppen: */

char symm_name[29][4] =
  {{' ',' ',' ','\0'},  {'C','1',' ','\0'},  {'C','2',' ','\0'},
   {'C','i',' ','\0'},  {'C','s',' ','\0'},  {'C','3',' ','\0'},
   {'D','2',' ','\0'},  {'S','4',' ','\0'},  {'C','2','v','\0'},
   {'C','2','h','\0'},  {'D','3',' ','\0'},  {'S','6',' ','\0'},
   {'C','3','v','\0'},  {'C','3','h','\0'},  {'D','2','h','\0'},
   {'D','2','d','\0'},  {'D','5',' ','\0'},  {'D','6',' ','\0'},
   {'D','3','h','\0'},  {'D','3','d','\0'},  {'T',' ',' ','\0'},
   {'D','5','h','\0'},  {'D','5','d','\0'},  {'D','6','h','\0'},
   {'D','6','d','\0'},  {'T','d',' ','\0'},  {'T','h',' ','\0'},
   {'I',' ',' ','\0'},  {'I','h',' ','\0'}};

/* Typ-Deklarationen: */

typedef  char BOOL; /* von 0 verschieden entspricht True */

typedef unsigned short KNOTENTYP;   
typedef unsigned char FLAECHENTYP; /* Bereich 1..252 */ /* DO NOT CHANGE ! Changes in the coding
				      and at several places where FL_MAX is used (as a sign !)
				      are necessary */

typedef KNOTENTYP GRAPH[N+1][3]; /* fuer schreibegraph und Isomorphietest */

/* Element der Adjazenztabelle: */


typedef struct BBiL {
		  struct BBiL *next_item;
		  FLAECHENTYP code[8];
		} BBITEMLISTE; /* die BBItems -- d.h. Codes */

typedef struct BBiallocL {
		  struct BBiallocL *prev;
		  BBITEMLISTE *space;
		} BBALLOCLISTE; /* die allozierten 1000er BBitemfelder */


typedef struct iL {
		  struct iL *next_item;
		  FLAECHENTYP code[5];
		} ITEMLISTE; /* die Items -- d.h. Codes */


typedef struct BBsL {
		  int number_next;
		  BBITEMLISTE **items;
		} BBSEQUENZLISTE; /* die verzweigung der liste nach der Sequenz */


typedef struct sL {
                  struct sL **next_level;
		  int number_next;
		  ITEMLISTE *items;
		  ITEMLISTE *last_item;
		} SEQUENZLISTE; /* die verzweigung der liste nach der Sequenz */



typedef struct BBSL {
		  int total_items; 
		  int total_maps; 
                  BBSEQUENZLISTE *sechser[S+1];
 		  } BBS_LISTE; /* die erste stufe der liste -- verzweigung nach Anzahl der 6-Ecke */


typedef struct SL {
		  int total_maps; 
                  SEQUENZLISTE *sechser[S+1];
 		  } S_LISTE; /* die erste stufe der liste -- verzweigung nach Anzahl der 6-Ecke */


typedef struct K {
                   KNOTENTYP ursprung; /* bei welchem knoten startet die kante */
                   KNOTENTYP name;  /* Identifikation des Knotens, mit
                                       dem Verbindung besteht */
		   long dummy;   /* fuer alle moeglichen zwecke */
		   BOOL nostart;
		   BOOL noleft; /* fuer die Rekonstruktion: Keine Flaeche links hiervon */
		   BOOL noright; /* fuer die Rekonstruktion: Keine Flaeche rechts hiervon */
		   BOOL mirror_nostart;
		   KNOTENTYP mininame; /* jeweils fuer den minimalitaetstest */
                   struct K *prev;  /* vorige Kante im Uhrzeigersinn */
                   struct K *next;  /* naechste Kante im Uhrzeigersinn */
		   struct K *invers; /* die inverse Kante (in der Liste von "name") */
                  } KANTE;

typedef struct  {
                   int laenge;
                   int sequenz[7];  /* die laenge der luecke. Konvention: Beendet durch "leer" */
		   KANTE *kanten[7];/* die letzten aussenkanten vor der sequenz */
		   char k_marks[7]; /* 1 wenn anfang einer kanonischen Sequenz, 0 sonst */
		 } SEQUENZ;


typedef struct le { FLAECHENTYP code[12];
		    struct le *smaller;
		    struct le *larger; } LISTENTRY;


/* "Ueberschrift" der Adjazenztabelle (Array of Pointers): */
typedef KANTE PLANMAP[N+1][3];
                  /* Jeweils 3 KANTEn */
                  /* ACHTUNG: 1. Zeile der Adjazenztabelle hat Index 0 -
                     wird fast nicht benutzt, N Zeilen auch ausreichend
		     In [0][0].name wird aber die knotenzahl gespeichert */


/*********************GLOBALE*VARIABLEN********************************/

/* Die folgenden Variablen werden von fast allen Programmteilen benutzt
   oder werden aus anderen Gruenden global verwaltet. Trotzdem werden
   sie in einigen Faellen auch an Funktionen uebergeben, um die
   Parameterabhaengigkeit der Funktionen zu betonen */
/* Variablen-Deklarationen: */


int output; /* soll auf stdout geschrieben werden */
int knotenzahl;  /* Knotenzahl des Graphen;
		   ergibt sich aus Eingabe; wird im Verlauf
		   der Konstruktion nicht geaendert */

long long int non_iso_graphenzahl[N+1];
long long int graphenzahl[N+1];

S_LISTE mapliste;
BBS_LISTE bbliste;

KANTE *F_eck_kanten[60]; /* eine liste aller kanten, so dass links davon ein
			    5-Eck liegt */
int anzahl_5ek; /* die momentane Anzahl der eingetragenen kanten */

int max_sechsecke,min_sechsecke;

FLAECHENTYP **lastcode[N]; /* wird bei codeart 3 gebraucht */
FLAECHENTYP last_code[12]; /* wird bei codeart 2 gebraucht */

int minbbl=N, maxbbl=0;
int minbrillenglas=N, maxbrillenglas=0;
int min_2_3_4=N;
int no_penta_spiral=0, no_hexa_spiral=0;

BOOL bblmark[N+1], brillenglasmark[N+1], zwei_3_4_mark[N+1];
BOOL do_bauchbinde,do_brille,do_sandwich;

LISTENTRY codeliste[N+1];

FILE *fil[N+1];
int write_header_fil[N+1];
int write_header_stdout=1;
FILE *logfile;
char logfilename[filenamenlaenge], no_penta_spiral_filename[filenamenlaenge], no_spiral_filename[filenamenlaenge];
char no_hexa_spiral_filename[filenamenlaenge];

BOOL quiet=0;
BOOL IPR=0, is_ipr=1;
BOOL to_stdout=0;
BOOL hexspi=0, spistat=0;
BOOL spiralcheck=0;
int codenumber, listenlaenge, mod=0, rest=0;
int spiralnumbers[12*S+120+1];

/* weitere globale Variablen (TH) fuer die Statistik der Symmetriegruppen: */

BOOL symstat=0;    /* 1 -> Symmetriestatistik erstellen */
int symm_anz[29]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    /*  symm_anz[i] enthaelt die Anzahl der gefundenen Fullerene, die die
        Symmetrien der Symmetriegruppe mit der Nummer i besitzen */
char symm[29] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int symm_len = 0;
    /* Speicher fuer Nummern von Symmetriegruppen, die beruecksichtigt werden sollen
       und die Anzahl der Eintraege im Array (0 => alle Gruppen beruecksichtigen) */            
char symmstring[29*4];     /* Dateikennung, falls Symmetriegruppen gewaehlt */

/* Prototypen: */

void codiereplanar(PLANMAP map);
void common_history();
void schreibemap();
void schreibehistory();

/****************SCHREIBE_SYMMETRIESTATISTIK********TH*****/

void schreibe_symmetriestatistik()
{ int i, j=0;
  fprintf(stderr,"Symmetries:\n");
  for (i=1; i<=28; i++) {
    if (symm_anz[i]>0) {
      fprintf(stderr,"  %s: %10d ",symm_name[i],symm_anz[i]); 
      j++;
      if (j%4==0) {fprintf(stderr,"\n");}
    }
  }
  if (j%4) {fprintf(stderr,"\n");}
}        


/**********************CHECKSIZE_MARK_RETURN**************************************/

/* bestimmt die groesse der flaeche links von edge -- ist da keine gibt's Probleme 
   ausserdem setzt er fuer alle kanten, so dass diese flaeche links davon ist, dummy
   auf mark. In nextedge wird die im Gegen-Uhrzeigersinn letzte unmarkierte Kante
   (heisst: die letzte kante mit markierung < mark) zurueckgegeben -- und nil, wenn
   sie nicht existiert. */

int checksize_mark_return(KANTE* edge, int mark, KANTE **nextedge)

{
KANTE *run; 
int zaehler=1;

*nextedge=nil;
if (edge->dummy < mark) { *nextedge=edge->invers; edge->dummy=edge->invers->dummy=mark; }

for (run=edge->invers->next; run != edge; run=run->invers->next) 
        { if (run->dummy < mark) { *nextedge=run->invers; run->dummy=run->invers->dummy=mark; }
	  zaehler++; }
return(zaehler);
}



/**********************CHECKSIZE_MARK_RETURN_RIGHT**************************************/

/* bestimmt die groesse der flaeche rechts von edge -- sonst wie oben */

int checksize_mark_return_right(KANTE* edge, int mark, KANTE **nextedge)

{
KANTE *run; 
int zaehler=1;

*nextedge=nil;
if (edge->dummy < mark) { *nextedge=edge->invers; edge->dummy=edge->invers->dummy=mark; }

for (run=edge->invers->prev; run != edge; run=run->invers->prev) 
      {if (run->dummy < mark) { *nextedge=run->invers; run->dummy=run->invers->dummy=mark; }
       zaehler++;}
return(zaehler);
}




/************************GET_SPIRAL_CODE**********************************/

BOOL get_spiralcode ( KANTE *edge, int minmark, FLAECHENTYP cmpcode[12],
		 int sixgons)

/* entwickelt den Spiralcode, bei dem die erste Flaeche links von edge
   liegt, die zweite rechts davon und die Entwicklung im Uhrzeigersinn
   geht. Entwickelt wird solange der Code besser ist als cmpcode. Das
   Resultat wird in cmpcode geschrieben, wenn es besser ist. Wenn ein 
   Code gefunden wird, der besser ist, als cmpcode, wird 1 zurueckgegeben, 
   sonst 0.  Die aufrufende Funktion muss sicherstellen, dass alle Kanten
   kante->dummy <= minmark erfuellen.
*/

{
int mark, i;
KANTE *nextedge;
BOOL kleiner=0;
FLAECHENTYP code[12], zaehler;
int fuenfecke=0, sechsecke=0; /* zaehler fuer die wirklich eingefuegten Flaechen */
int stelle;

mark=minmark+1;  

if (checksize_mark_return(edge, mark, &nextedge)==5)
                      {  code[0]=1; stelle=0; fuenfecke=1; } 
else { stelle= -1; sechsecke=1; }
if (checksize_mark_return_right( edge, mark, &nextedge)==5)
    { stelle++; code[stelle]=2; fuenfecke++; } else sechsecke++;

for (i=0; (i<=stelle) && (!kleiner); i++)
  { if (code[i]>cmpcode[i]) return(0);
    if (code[i]<cmpcode[i]) kleiner=1; }

zaehler=3;

while (nextedge != nil)
  { if (checksize_mark_return_right(nextedge, mark, &nextedge)==5)
                       { fuenfecke++;
			 stelle++; code[stelle]=zaehler; 
		         if (!kleiner)
			    { if (zaehler>cmpcode[stelle]) { return(0); }
			      if (zaehler<cmpcode[stelle]) kleiner=1;
			    }
		       }
    else sechsecke++;
    zaehler++;
  }

if ((fuenfecke<12) || (sechsecke < sixgons)) return(0);

for (i=0; i<12; i++) cmpcode[i]=code[i];
return(1);
}


/************************GET_SPIRAL_CODE_INV**********************************/

BOOL get_spiralcode_inv ( KANTE *edge, int minmark, FLAECHENTYP cmpcode[12],
		 int sixgons)

/* entwickelt den Spiralcode, bei dem die erste Flaeche links von edge
   liegt, die zweite rechts davon und die Entwicklung im GEGEN-Uhrzeigersinn
   geht. Sonst wie oben */

{
int mark, i;
KANTE *nextedge;
BOOL kleiner=0;
FLAECHENTYP code[12], zaehler;
int fuenfecke=0, sechsecke=0; /* zaehler fuer die wirklich eingefuegten Flaechen */
int stelle;

mark=minmark+1;  

if (checksize_mark_return( edge, mark, &nextedge)==5)
                      { code[0]=1; stelle=0; fuenfecke=1; } 
else { stelle= -1; sechsecke=1; }
if (checksize_mark_return_right( edge, mark, &nextedge)==5)
    { stelle++; code[stelle]=2; fuenfecke++; } else sechsecke++;

nextedge=edge->invers->prev;

for (i=0; (i<=stelle) && (!kleiner); i++)
  { if (code[i]>cmpcode[i]) return(0);
    if (code[i]<cmpcode[i]) kleiner=1; }

zaehler=3;

while (nextedge != nil)
  { 
    if (checksize_mark_return( nextedge, mark, &nextedge)==5)
                       { fuenfecke++;
			 stelle++; code[stelle]=zaehler; 
		         if (!kleiner)
			    { if (zaehler>cmpcode[stelle]) { return(0); }
			      if (zaehler<cmpcode[stelle]) kleiner=1;
			    }
		       }
    else sechsecke++;
    zaehler++;
  }

if ((fuenfecke<12) || (sechsecke < sixgons)) return(0);

for (i=0; i<12; i++) cmpcode[i]=code[i];
return(1);
}


/************************VEGACODE*****************************/

void vegacode( FILE *fil, PLANMAP map )

{
static int erster_aufruf=1;
int i;

if (erster_aufruf)
  { fprintf(fil,">>writegraph3d planar <<\n");
    erster_aufruf=0; }

if (map[0][0].name >= 100)
  {
    for (i=1; i<=map[0][0].name; i++)
      fprintf(fil,"%3d  0 0 0   %3d %3d %3d\n",i,map[i][0].name,map[i][1].name,map[i][2].name);
  }
else 
  {
    for (i=1; i<=map[0][0].name; i++)
      fprintf(fil,"%2d  0 0 0   %2d %2d %2d\n",i,map[i][0].name,map[i][1].name,map[i][2].name);
  }
fprintf(fil,"0\n");

}

/************************BELEGEDUMMIES************************/

void belegedummies(KANTE *edge, int nummer)
/* belegt edge->dummy, edge->invers->pre->dummy, ... mit Nummer
   -- einmal rund um die Flaeche */

{
KANTE *merke;

merke=edge; edge->dummy=nummer;
edge=edge->invers->prev;

while (edge != merke) { edge->dummy=nummer;
			edge=edge->invers->prev; }
}


/************************DUALCODE*****************************/

int dualcode( PLANMAP map )

{
/* berechnet das Dual und schreibt es als planarcode auf stdout */

int flaechenzahl, knotenzahl, codelaenge=1,i,j, nextnumber=2;
FLAECHENTYP code[(S+13)*7]; /* In main wird schon abgefangen, wenn das nicht in
			       unsigned char passt */
KANTE *startedge[S+13];
KANTE *run, *merke;
static int write_header=1;

if (write_header)
  { write_header=0;
    fprintf(stdout,">>planar_code %ce<<", my_endianness);
  }
    

knotenzahl=map[0][0].name;
code[0]=flaechenzahl= 2 + (map[0][0].name / 2);


for (i=1; i<= knotenzahl; i++) for (j=0; j<3; j++) map[i][j].dummy=0;
/* dummy gibt die Nummer der Flaeche rechts der Kante an */

belegedummies(map[1],1);
startedge[1]=map[1];

for (i=1; i<=flaechenzahl; i++)
  { merke=startedge[i]; 
    if (merke->invers->dummy) { code[codelaenge]=merke->invers->dummy;
				codelaenge++; }
    else { code[codelaenge]= nextnumber; codelaenge++;
	   startedge[nextnumber]=merke->invers;
	   belegedummies(merke->invers,nextnumber);
	   nextnumber++; }
    for (run=merke->invers->prev; run != merke; run=run->invers->prev)
      { if (run->invers->dummy) { code[codelaenge]=run->invers->dummy;
				    codelaenge++; }
        else { code[codelaenge]= nextnumber; codelaenge++;
	     startedge[nextnumber]=run->invers;
	     belegedummies(run->invers,nextnumber);
	     nextnumber++; }
      }
    code[codelaenge]=0; codelaenge++;
  }

fwrite(code,sizeof(FLAECHENTYP),codelaenge,stdout);

return(codelaenge);
}
 
/*************************SPARSE6CODE*****************************/

int
sparse6code( PLANMAP map, FLAECHENTYP *code)
/* Make sparse6 code, including final '\n'. */
{
    FLAECHENTYP *p;
    int nb,i,j,lastj,x,k,r,rr,topbit;
    int nv;
    KANTE *merke, *lauf;

    nv = map[0][0].name;

    p = code;
    *p++ = ':';

    if (nv <= 62)
        *p++ = 63 + nv;
    else
    {
        *p++ = 63 + 63;
        *p++ = 63 + 0;
        *p++ = 63 + (nv >> 6);
        *p++ = 63 + (nv & 0x3F);
    }

    for (i = nv-1, nb = 0; i != 0 ; i >>= 1, ++nb) {}
    topbit = 1 << (nb-1);
    k = 6;
    x = 0;

    lastj = 0;
    for (j = 0; j < nv; ++j)
    {
        merke = lauf = map[j+1];
        do
        {
            i = lauf->name - 1;
            if (i <= j)
            {
                if (j == lastj)
                {
                    x <<= 1;
                    if (--k == 0)
                    {
                        *p++ = 63 + x;
                        k = 6;
                        x = 0;
                    }
                }
                else
                {
                    x = (x << 1) | 1;
                    if (--k == 0)
                    {
                        *p++ = 63 + x;
                        k = 6;
                        x = 0;
                    }
                    if (j > lastj+1)
                    {
                        for (r = 0, rr = j; r < nb; ++r, rr <<= 1)
                        {
                            if (rr & topbit) x = (x << 1) | 1;
                            else             x <<= 1;
                            if (--k == 0)
                            {
                                *p++ = 63 + x;
                                k = 6;
                                x = 0;
                            }
                        }
                        x <<= 1;
                        if (--k == 0)
                        {
                            *p++ = 63 + x;
                            k = 6;
                            x = 0;
                        }
                    }
                    lastj = j;
                }
                for (r = 0, rr = i; r < nb; ++r, rr <<= 1)
                {
                    if (rr & topbit) x = (x << 1) | 1;
                    else             x <<= 1;
                    if (--k == 0)
                    {
                        *p++ = 63 + x;
                        k = 6;
                        x = 0;
                    }
                }
            }
            lauf = lauf->next;
        } while (lauf != merke);
    }

    if (k != 6) *p++ = 63 + ((x << k) | ((1 << k) - 1));

    *p++ = '\n';
    return p - code;
}

/*************************LONGCODE*****************************/

#define TWOBYTES(x) {codeF[zaehler]=(x)&0xFF; codeF[zaehler+1]=((x)>>8)&0xFF;  zaehler += 2;}

int longcode( PLANMAP map, FLAECHENTYP *codeF )
{
/* Codiert die Einbettung in codeF und gibt die laenge des codes zurueck */
int i,zaehler;
KANTE *merke, *lauf;

if (map[0][0].name <= FL_MAX)
{
zaehler=1;
codeF[0]=map[0][0].name;
for(i=1;i<=map[0][0].name;i++)
    { merke=map[i]; codeF[zaehler]=merke->name; zaehler++;
      for(lauf=merke->next; lauf!=merke; lauf=lauf->next) 
	           { codeF[zaehler]=lauf->name; zaehler++; }
      codeF[zaehler]=0; zaehler++; }
}
else /* zu viele knoten fuer FLAECHENTYP */
{
zaehler=1;
codeF[0]=0;
TWOBYTES(map[0][0].name);
for(i=1;i<=map[0][0].name;i++)
    { merke=map[i]; TWOBYTES(merke->name)
      for(lauf=merke->next; lauf!=merke; lauf=lauf->next) TWOBYTES(lauf->name);
      TWOBYTES(0);}
}
return(zaehler);
}



/*************************SPIRALCODE*******************************/

BOOL spiralcode(PLANMAP map, FLAECHENTYP code[12])

/* berechnet irgendeinen Spiralcode von map und schreibt ihn in code.
   Gibt 1 zurueck, wenn der gefunden wurde und 0 sonst. versucht zuerst
   einen Code zu finden, der an einem 5-Eck startet. */

{ int zaehler, i,j, mark, sixgons;
  BOOL gefunden=0, hexgefunden=0;
  FLAECHENTYP codeF[2*(81+8*S)];
  FILE *fil2;
  FLAECHENTYP dummycode[12];
  FLAECHENTYP *dummy;
  static int write_nopentaheader=1, write_nohexaheader=1;

/*schreibemap(map);*/

sixgons= (map[0][0].name - 20)/2;

for (i=1; i<=map[0][0].name; i++)
  for (j=0; j<3; j++) { map[i][j].dummy=map[i][j].mininame=0; }
for (i=0; i<12; i++) code[i]=FL_MAX;


for (i=0; (i<60) && !gefunden; i++) 
  { gefunden= get_spiralcode ( F_eck_kanten[i], i, code, sixgons);
    (F_eck_kanten[i])->mininame=1; }

mark=61;

for (i=0; (i<60) && !gefunden; i++) 
  { gefunden= get_spiralcode_inv ( F_eck_kanten[i], mark, code, sixgons);
    mark++; }


if (!gefunden) { no_penta_spiral++;
		 zaehler=longcode(map,codeF);
		fil2=fopen(no_penta_spiral_filename,"ab");
		if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_penta_spiral_filename);
		                  exit(1); }
		if (write_nopentaheader)
		  { write_nopentaheader=0;
		  fprintf(fil2,">>planar_code %ce<<", my_endianness);
		  }
		fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		fclose(fil2);
	       }


if (!gefunden || hexspi)
{
if (!gefunden) dummy=code; else
  { for (i=0; i<12; i++) dummycode[i]=FL_MAX; dummy=dummycode; }
for (i=1; (i<=map[0][0].name) && !hexgefunden; i++) 
  for (j=0; j<3 && !hexgefunden; j++)
    if (!map[i][j].mininame) 
      { hexgefunden= get_spiralcode ( map[i]+j, mark, dummy, sixgons); mark++;
        if (!hexgefunden) 
	  { hexgefunden= get_spiralcode_inv ( map[i]+j, mark, dummy, sixgons); mark++; }
      }
}

if (hexspi && !hexgefunden) { no_hexa_spiral++;
		 zaehler=longcode(map,codeF);
		fil2=fopen(no_hexa_spiral_filename,"ab");
		if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_hexa_spiral_filename);
		                  exit(1); }
		if (write_nohexaheader)
		  { write_nohexaheader=0;
		  fprintf(fil2,">>planar_code %ce<<", my_endianness);
		  }
		fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		fclose(fil2);
	       }



return(gefunden || hexgefunden);
}


/*************************MINSPIRALCODE*******************************/

BOOL minspiralcode(PLANMAP map, FLAECHENTYP code[12])

/* berechnet den minimalen Spiralcode von map und schreibt ihn in code.
   Gibt 1 zurueck, wenn der gefunden wurde und 0 sonst. versucht zuerst
   einen Code zu finden, der an einem 5-Eck startet. */

{ int i,j, zaehler, mark, sixgons;
  BOOL gefunden=0, hexgefunden=0;
  FLAECHENTYP codeF[2*(81+8*S)];
  FILE *fil2;
  FLAECHENTYP dummycode[12];
  FLAECHENTYP *dummy;
  static int write_nopentaheader=1, write_nohexaheader=1;


/*schreibemap(map);*/

sixgons= (map[0][0].name - 20)/2;

for (i=1; i<=map[0][0].name; i++)
  for (j=0; j<3; j++) { map[i][j].dummy=map[i][j].mininame=0; }
for (i=0; i<12; i++) code[i]=FL_MAX;



for (i=0; (i<60); i++) 
  { if (get_spiralcode ( F_eck_kanten[i], i, code, sixgons)) gefunden=1;
    (F_eck_kanten[i])->mininame=1; }

mark=61;

for (i=0; (i<60); i++) 
  { if (get_spiralcode_inv ( F_eck_kanten[i], mark, code, sixgons)) gefunden=1;
    mark++; }


if (!gefunden) { no_penta_spiral++;
		 zaehler=longcode(map,codeF);
		fil2=fopen(no_penta_spiral_filename,"ab");
		if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_penta_spiral_filename);
		                  exit(1); }
		if (write_nopentaheader)
		  { write_nopentaheader=0;
		  fprintf(fil2,">>planar_code %ce<<", my_endianness);
		  }
		fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		fclose(fil2);
	       }


if (!gefunden || hexspi) /* sonst waeren die neuen codes eh alle groesser */
{
if (!gefunden) dummy=code; else
  { for (i=0; i<12; i++) dummycode[i]=FL_MAX; dummy=dummycode; }
for (i=1; (i<=map[0][0].name); i++) 
  for (j=0; j<3 ; j++)
    if (!map[i][j].mininame) 
      { if (get_spiralcode ( map[i]+j, mark, dummy, sixgons)) hexgefunden=1; mark++; 
	if (get_spiralcode_inv ( map[i]+j, mark, dummy, sixgons)) hexgefunden=1; mark++; 
      }
}

if (hexspi && !hexgefunden) { no_hexa_spiral++;
		 zaehler=longcode(map,codeF);
		fil2=fopen(no_hexa_spiral_filename,"ab");
		if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_hexa_spiral_filename);
		                  exit(1); }
		if (write_nohexaheader)
		  { write_nohexaheader=0;
		  fprintf(fil2,">>planar_code %ce<<", my_endianness);
		  }
		fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		fclose(fil2);
	       }


return(gefunden || hexgefunden);
}



/*************************SPIRALSTATISTIC*******************************/

void spiralstatistic(PLANMAP map)

/* berechnet die Statistik, wieviele Spiralen es gibt */

{ int zaehler=0, i,j, mark, sixgons;
  FLAECHENTYP code[12];


/*schreibemap(map);*/

sixgons= (map[0][0].name - 20)/2;

for (i=1; i<=map[0][0].name; i++)
  for (j=0; j<3; j++) { map[i][j].dummy=map[i][j].mininame=0; }
for (i=0; i<12; i++) code[i]=FL_MAX;

mark=1;

for (i=1; (i<=map[0][0].name); i++) 
  for (j=0; j<3; j++)
      { code[0]=FL_MAX; 
	if (get_spiralcode ( map[i]+j, mark, code, sixgons)) zaehler++; 
	/*else fprintf(stderr,"no %d %d \n",i,map[i][j].name);*/
	mark++;
	code[0]=FL_MAX;
	if (get_spiralcode_inv ( map[i]+j, mark, code, sixgons)) zaehler++; 
	/*else fprintf(stderr,"no inv %d %d \n",i,map[i][j].name); */
        mark++;}

spiralnumbers[zaehler]++;

}


/*********************CODECMP_KN*****************************************/

int codecmp_kn(KNOTENTYP *p1, KNOTENTYP *p2, int max)
{
max--;
while ((*p1==*p2) && max) { p1++; p2++; max--; }
return( (int)(*p1)-(int)(*p2) );
}

/*********************CODECMP*****************************************/

int codecmp(FLAECHENTYP *p1, FLAECHENTYP *p2, int max)
{
max--;
while ((*p1==*p2) && max) { p1++; p2++; max--; }
return( (int)(*p1)-(int)(*p2) );
}


/**************************IN_LISTE********************************/

void in_liste(FLAECHENTYP *code, LISTENTRY *el)
/* schreibt code in die liste */
{ int compare;
  int n;


if (el->code[0]==0)
    { 
      for (n=0; n<12; n++) (el->code)[n]= code[n];
      el->smaller=(LISTENTRY *)malloc(sizeof(LISTENTRY));
         (el->smaller->code)[0]=0;
      el->larger=(LISTENTRY *)malloc(sizeof(LISTENTRY));
         (el->larger->code)[0]=0;
      if ((el->smaller==nil) || (el->larger==nil)) 
	{ fprintf(stderr,"Cannot allocate memory in \"in_liste\" \n");
						     exit(1); }
    }

else { 
       compare=codecmp(code,el->code,12);
        if (compare<0) in_liste(code,el->smaller);
                else if (compare>0) in_liste(code,el->larger);
                   else { fprintf(stderr,"Dangerous error -- Two equal codes ! \n"); exit(2); }
     }
}


/*********************AUSGABE***********************************/

void ausgabe(LISTENTRY *liste,int knotenzahl,FLAECHENTYP **lastcode)

{ 
FLAECHENTYP i;

if ((liste->code)[0]==0) return;
ausgabe(liste->smaller,knotenzahl,lastcode);

for (i=0; (liste->code)[i]==(*lastcode)[i]; i++);
fwrite(&i,sizeof(FLAECHENTYP),1,fil[knotenzahl]);
fwrite((liste->code)+i,sizeof(FLAECHENTYP),12-i,fil[knotenzahl]);
*lastcode=liste->code;

ausgabe(liste->larger,knotenzahl,lastcode);
}

/********************LISTELEER********************************/

void listeleer(LISTENTRY *liste)
{
if ((liste->code)[0]==0) return;

listeleer(liste->smaller); free(liste->smaller);
listeleer(liste->larger); free(liste->larger);
}


/*************************CODIEREPLANAR*****************************/

void codiereplanar( PLANMAP map )
{
/* Codiert die Einbettung, schreibt sie in das entsprechende file oder
   auf stdout und gibt die laenge des codes zurueck */
int zaehler,knotenzahl;
FLAECHENTYP codeF[2*(81+8*S)];
FLAECHENTYP  *codeFPZ, i;
 static FLAECHENTYP dummycode[12]={UCHAR_MAX,UCHAR_MAX,UCHAR_MAX,0,0,0,0,0,0,0,0,0}; 
FILE *fil2;
BOOL test;
static int write_nospiheader=1;

knotenzahl=map[0][0].name;

if (spistat) spiralstatistic(map);

switch(codenumber)
  {
  case 0: {
           if (spiralcheck)
	     { test=spiralcode(map,codeF); 
	       if (!test)
		 { zaehler=longcode(map,codeF);
		   fil2=fopen(no_spiral_filename,"ab");
		if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_spiral_filename);
		                  exit(1); }
		if (write_nospiheader)
		  { write_nospiheader=0;
		  fprintf(fil2,">>planar_code %ce<<", my_endianness);
		  }
		   fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		   fclose(fil2);
		 }
	     }
	   break; }
  case 1: { 
           if (spiralcheck)
	     { test=spiralcode(map,codeF); 
	       if (!test)
		 { zaehler=longcode(map,codeF);
		   fil2=fopen(no_spiral_filename,"ab");
		   if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_spiral_filename);
		   exit(1); }
		   if (write_nospiheader)
		     { write_nospiheader=0;
		     fprintf(fil2,">>planar_code %ce<<", my_endianness);
		     }
		   fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		   fclose(fil2);
		 }
	     }
            zaehler=longcode(map,codeF);
	    if (fil[knotenzahl]==stdout) 
	      { if (write_header_stdout) 
		         { write_header_stdout=0;
		           fprintf(stdout,">>planar_code %ce<<", my_endianness);
			 }
	      }
	    else
	      { if (write_header_fil[knotenzahl]) 
		         { write_header_fil[knotenzahl]=0;
		           fprintf(fil[knotenzahl],">>planar_code %ce<<", my_endianness);
			 }
	      }
	    fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil[knotenzahl]);
	    break; }
  case 2: { test=spiralcode(map,codeF);
	    if (test) { for (i=0; codeF[i]==last_code[i]; i++);
			fwrite(&i,sizeof(FLAECHENTYP),1,fil[knotenzahl]);
	                fwrite(codeF+i,sizeof(FLAECHENTYP),12-i,fil[knotenzahl]);
		        for ( ; i<12; i++) last_code[i]=codeF[i];}
	    else
	      { zaehler=longcode(map,codeF);
		fil2=fopen(no_spiral_filename,"ab");
		if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_spiral_filename);
		exit(1); }
		if (write_nospiheader)
		  { write_nospiheader=0;
		  fprintf(fil2,">>planar_code %ce<<", my_endianness);
		  }
		fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		fclose(fil2);
	      }
	    break; }
  case 3: { 
            test=minspiralcode(map,codeF);
	    if (test) { in_liste(codeF,codeliste+knotenzahl);
			if (graphenzahl[knotenzahl]%((long long int)listenlaenge)==0)
			  {
			    if (fil[knotenzahl]==stdout)
			      codeFPZ = dummycode;
			    else codeFPZ = *(lastcode[knotenzahl]);
			  ausgabe(codeliste+(knotenzahl),knotenzahl,&codeFPZ);
			  for (i=0; i<12; i++) (*(lastcode[knotenzahl]))[i]= codeFPZ[i];
			  listeleer(codeliste+(knotenzahl));
			  (codeliste[knotenzahl].code)[0]=0;
			}
		      }
	    else
	      { zaehler=longcode(map,codeF);
		fil2=fopen(no_spiral_filename,"ab");
		if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_spiral_filename);
		exit(1); }
		if (write_nospiheader)
		  { write_nospiheader=0;
		  fprintf(fil2,">>planar_code %ce<<", my_endianness);
		  }
		fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		fclose(fil2);
	      }
	    break; }
  case 4: {
            if (spiralcheck)
	      { test=spiralcode(map,codeF); 
		if (!test)
		  { zaehler=longcode(map,codeF);
		    fil2=fopen(no_spiral_filename,"ab");
		   if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_spiral_filename);
		   exit(1); }
		   if (write_nospiheader)
		     { write_nospiheader=0;
		     fprintf(fil2,">>planar_code %ce<<", my_endianness);
		     }
		    fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		    fclose(fil2);
		  }
	      }
	    break; }
  case 5: { 
            zaehler=longcode(map,codeF);
	    if (fil[knotenzahl]==stdout) 
	      { if (write_header_stdout) 
		         { write_header_stdout=0;
		           fprintf(stdout,">>planar_code %ce<<", my_endianness);
			 }
	      }
	    else
	      if (write_header_fil[knotenzahl]) 
		         { write_header_fil[knotenzahl]=0;
		           fprintf(fil[knotenzahl],">>planar_code %ce<<", my_endianness);
			 }
	    fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil[knotenzahl]);
            test=spiralcode(map,codeF); 
	    if (!test)
	      { zaehler=longcode(map,codeF);
		fil2=fopen(no_spiral_filename,"ab");
		if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_spiral_filename);
		exit(1); }
		if (write_nospiheader)
		  { write_nospiheader=0;
		  fprintf(fil2,">>planar_code %ce<<", my_endianness);
		  }
		fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		fclose(fil2);
	      }
	    break; }

  case 6: { vegacode(stdout,map); 
            if (spiralcheck)
	      { test=spiralcode(map,codeF); 
		if (!test)
		  { zaehler=longcode(map,codeF);
		    fil2=fopen(no_spiral_filename,"ab");
		   if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_spiral_filename);
		   exit(1); }
		   if (write_nospiheader)
		     { write_nospiheader=0;
		     fprintf(fil2,">>planar_code %ce<<", my_endianness);
		     }
		    fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		    fclose(fil2);
		  }
	      }
	    break; }

  case 7: { dualcode(map); 
            if (spiralcheck)
	      { test=spiralcode(map,codeF); 
		if (!test)
		  { zaehler=longcode(map,codeF);
		    fil2=fopen(no_spiral_filename,"ab");
		    if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_spiral_filename);
		    exit(1); }
		    if (write_nospiheader)
		      { write_nospiheader=0;
		      fprintf(fil2,">>planar_code %ce<<", my_endianness);
		      }
		    fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
		    fclose(fil2);
		  }
	      }
	    break; }

  case 8: {
           if (spiralcheck)
             { test=spiralcode(map,codeF);
               if (!test)
                 { zaehler=longcode(map,codeF);
                   fil2=fopen(no_spiral_filename,"ab");
                   if (fil2==NULL) { fprintf(stderr,"Can't open %s\n",no_spiral_filename);
                   exit(1); }
                   if (write_nospiheader)
                     { write_nospiheader=0;
                     fprintf(fil2,">>planar_code %ce<<", my_endianness);
                     }
                   fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil2);
                   fclose(fil2);
                 }
             }
            zaehler=sparse6code(map,codeF);
            fwrite(codeF,sizeof(FLAECHENTYP),zaehler,fil[knotenzahl]);
            break; }

  default: { fprintf(stderr,"Dangerous error in switch (codiereplanar) ! \n"); exit(3); }
  }
}



/*******************INIT_MAP************************/

void init_map(PLANMAP map)
{
int i,j;

map[0][0].name=0;

for (i=1; i<=N; i++)
{
map[i][0].next= map[i]+1; map[i][0].prev= map[i]+2;
map[i][1].next= map[i]+2; map[i][1].prev= map[i];
map[i][2].next= map[i]; map[i][2].prev= map[i]+1;

for (j=0; j<3; j++) 
          { map[i][j].ursprung=i;
	    map[i][j].name=leer;
            map[i][j].invers=nil; }
}
}


/********************BAUE_POLYGON*******************/
/* Baut ein einzelnes leeres Polygon mit n Ecken (n>=3) 
   und initialisiert map */

void baue_polygon(int n, PLANMAP map, KANTE **marke )
{
int j;

if (n<3) { fprintf(stderr,"Error, no 2-gons allowed !\n"); return; }

/* sicherheitshalber erstmal loeschen und initialisieren */

init_map(map);

/* Immer: erster Eintrag zurueck, 2. nach aussen, dritter vor */

map[1][0].name=n;   map[1][1].name=aussen;   map[1][2].name=2;
map[1][0].invers=map[n]+2; map[1][1].invers=nil; map[1][2].invers=map[2];

(*marke)=map[1]+1;

for (j=2; j<n; j++)
{
map[j][0].name=j-1;   map[j][1].name=aussen;   map[j][2].name=j+1;
map[j][0].invers=map[j-1]+2; map[j][1].invers=nil; map[j][2].invers=map[j+1];
}

map[n][0].name=n-1;   map[n][1].name=aussen;   map[n][2].name=1;
map[n][0].invers=map[n-1]+2; map[n][1].invers=nil; map[n][2].invers=map[1];

map[0][0].name=n;

}

/**********************CHECKSIZE_RIGHT**************************************/

/* bestimmt die groesse der flaeche rechts von edge -- ist da keine gibt's Probleme */

int checksize_right( KANTE* edge)
{
KANTE *run; 
int zaehler=1;

for (run=edge->invers->prev; run != edge; run=run->invers->prev) zaehler++;
return(zaehler);
}




/*********************ADD_POLYGON***********************************/

void add_polygon(int n, PLANMAP map, KANTE *start, KANTE **lastout)
/* fuegt ein weiteres polygon einer Reihe an. Dabei ist n die groesse des polygons. 
   Angefuegt wird immer an start. Die Marke wird nicht versetzt. Ueber lastout wird
   die letzte Aussenkante des Polygons zurueckgegeben. */


{
int new_tempknz, tempknz;
KANTE *ende;
int common_vertices;


if (IPR && (n==5))
  {
    if (checksize_right(start->next)==5) is_ipr=0;
    for (ende=start->next->invers->next, common_vertices=2; ende->name != aussen; 
	  ende=ende->invers->next) { if (checksize_right(ende)==5) is_ipr=0;
                                     common_vertices++;
				   }
  }
else for (ende=start->next->invers->next, common_vertices=2; ende->name != aussen; 
	  ende=ende->invers->next) common_vertices++;


if (n<common_vertices) 
   { fprintf(stderr,"polygon to insert too small !\n"); 
     exit(4); }

/* es muessen also n-common_vertices knoten hinzugefuegt werden */

tempknz=map[0][0].name;
new_tempknz=tempknz+n-common_vertices;

if (n-common_vertices==0) /* dann kommt kein knoten dazu */
  { start->name=ende->ursprung; start->invers=ende;
    ende->name=start->ursprung; ende->invers=start;
    *lastout=nil;
    return;
  }

if (n-common_vertices==1) /* dann kommt nur ein knoten dazu */
 {
 tempknz++;
 start->name=tempknz; start->invers=map[tempknz];
 map[tempknz][0].name=start->ursprung; map[tempknz][0].invers=start;
 map[tempknz][1].name=aussen; map[tempknz][1].invers=nil;
 map[tempknz][2].name=ende->ursprung; map[tempknz][2].invers=ende;
 ende->name=tempknz; ende->invers=map[tempknz]+2;
 *lastout=map[tempknz]+1;
 map[0][0].name=tempknz;
 return;
 }


/* es bleibt: mindestens zwei neue knoten */

tempknz++;
start->name=tempknz; start->invers=map[tempknz];
map[tempknz][0].name=start->ursprung; map[tempknz][0].invers=start;
map[tempknz][1].name=aussen; map[tempknz][1].invers=nil;
map[tempknz][2].name=tempknz+1; map[tempknz][2].invers=map[tempknz+1];

for (tempknz++; tempknz<new_tempknz; tempknz++)
    { map[tempknz][0].name=tempknz-1; map[tempknz][0].invers=map[tempknz-1]+2;
      map[tempknz][1].name=aussen; map[tempknz][1].invers=nil;
      map[tempknz][2].name=tempknz+1; map[tempknz][2].invers=map[tempknz+1]; }

/* und nun noch den letzten knoten */
map[tempknz][0].name=tempknz-1; map[tempknz][0].invers=map[tempknz-1]+2;
map[tempknz][1].name=aussen; map[tempknz][1].invers=nil;
map[tempknz][2].name=ende->ursprung; map[tempknz][2].invers= ende;
ende->name=tempknz; ende->invers=map[tempknz]+2;
*lastout=map[tempknz]+1;
map[0][0].name=tempknz;
}


/**********************SEQUENZ_KANONISCH***********************************/

int sequenz_kanonisch( int sequenz[] )
/* checkt, ob eine sequenz kanonisch ist, gibt 1 zurueck wenn ja, 0 sonst */

{ int i,j, laenge, max;
  int longseq[14];


  max=sequenz[0]; j=1; /* j hier nur als merker */
  for (i=0; sequenz[i] != leer; i++) { longseq[i]=sequenz[i];
				       if (longseq[i]==max) j=0;
				         else if (longseq[i]>max) { return(0); }
				     }
  if (j) return(1); /* der erste ist eindeutig, also die ganze sequenz */

  laenge=i;
  for (j=0; j<laenge; i++, j++) longseq[i]=sequenz[j];

for (j=1; j<laenge; i++, j++)
    if (longseq[j]==max)
	{ for (i=1; (i<laenge) && (longseq[j+i]==sequenz[i]) ; i++);
	  if (longseq[j+i]>sequenz[i]) 
                        { return(0); }
        }
return(1);
}



/***********************BERECHNE_SEQUENZ********************************/

void berechne_sequenz(SEQUENZ *sq, SEQUENZ altsq, int start,int f_ecke)
/* berechnet die neue sequenz startend bei der Kante start */
/* geht fest davon aus, dass 2 mal nach innen hintereinander nicht vorkommt */
/* zwei der Kanten-Eintraege koennen noch nicht belegt werden (die ersten beiden) */
/* start ist der laufindex */
{
int i, j, k, laenge,alt_laenge;
int *sequenz; 
int puffer[13];
char *kan;
KANTE **sqkanten;
KANTE *kpuffer[13];


sequenz=sq->sequenz;
kan=sq->k_marks;
sqkanten=sq->kanten;

alt_laenge=altsq.laenge;
sq->laenge= alt_laenge-f_ecke;
laenge=sq->laenge;

for (i=0; i<alt_laenge; i++) { puffer[i]=puffer[i+alt_laenge]=altsq.sequenz[i];
			       kpuffer[i]=kpuffer[i+alt_laenge]=altsq.kanten[i]; }

if (puffer[start]==0) { fprintf(stderr,"Berechne_sequenz should not be called for 0-gaps ! \n");
                        exit(5); }

if (f_ecke==0)
  { if (laenge==1) sequenz[0]=puffer[0]+1;
    else 
    if (laenge==2)
         { if (puffer[start]>1) { sequenz[0]=puffer[start]-1; sequenz[1]=puffer[start+1]+2; }
	      else { sequenz[1]=0; sequenz[0]=puffer[start+1]+2; }
	 }
    else /* d.h. laenge > 2 */
      { if (puffer[start]>1)
	  {
	    sequenz[0]= puffer[start]-1;
	    sequenz[1]= puffer[start+1]+1;
	    sequenz[laenge-1]=puffer[start+laenge-1]+1;
	    sqkanten[laenge-1]=kpuffer[start+laenge-1];
	    for (j=2; j<laenge-1; j++) { sequenz[j]=puffer[start+j];
					 sqkanten[j]=kpuffer[start+j]; }
	  }
	else /* d.h. die luecke hat laenge 1 */
	  {
	    sequenz[laenge-1]= 0;
	    sequenz[0]= puffer[start+1]+1;
	    sequenz[laenge-2]=puffer[start+laenge-1]+1;
	    sqkanten[laenge-2]=kpuffer[start+laenge-1];
	    for (j=1; j<laenge-2; j++) { sequenz[j]=puffer[start+j+1];
					 sqkanten[j]=kpuffer[start+j+1]; }
	  }
      } /* ende laenge > 2 */
  } /* ende 0 Fuenfecke */

else
if (f_ecke==1)
  { if (laenge==0) sequenz[0]=puffer[0]+1;
    else
    if (laenge==1) sequenz[0]=puffer[0]+puffer[1]+1;
    else 
    if (laenge==2)
          { sequenz[0]=puffer[start] + puffer[start+1]; sequenz[1]=puffer[start+2]+1;
	    sqkanten[1]=kpuffer[start+2];}
    else /* d.h. laenge > 2 */
      { sequenz[0]= puffer[start]+puffer[start+1];
	sequenz[laenge-1]=puffer[start+laenge]+1;
	sqkanten[laenge-1]=kpuffer[start+laenge];
	for (j=1; j<laenge-1; j++) { sequenz[j]=puffer[start+j+1];
				     sqkanten[j]=kpuffer[start+j+1]; }
      }
  } /* ende 1 Fuenfecke */

else /* d.h. f_ecke==2 */
  { if (laenge==0) sequenz[0]=puffer[0]+puffer[1]+1;
    else { fprintf(stderr,"ERROR: Two 5-gons not leading to 0-Sequence !\n");
	   exit(6); }
  } /* ende 2 Fuenfecke */

if (sequenz[0]==0) /* nur im Fall eines einzelnen 6-Ecks moeglich */
  { puffer[0]=sequenz[0];
    for (i=0; i<laenge-1; i++) sequenz[i]=sequenz[i+1]; sequenz[laenge-1]=puffer[0];
    for (i=1; i<laenge-1; i++) sqkanten[i]=sqkanten[i+1]; }



if (laenge==0) { sequenz[1]=leer; kan[0]=1; return; }

sequenz[laenge]=leer;

kan[0]=sequenz_kanonisch(sequenz);

for (i=1; i < laenge; i++)
  { for (j=i, k=0; j<laenge; j++, k++) puffer[k]=sequenz[j];
    for (j=0; j<i; j++, k++) puffer[k]=sequenz[j];
    puffer[k]=leer;
    kan[i]=sequenz_kanonisch(puffer);
  }

}






/***********************BELEGE_SEQUENZ********************************/

void belege_sequenz( KANTE *start, SEQUENZ *sq)
/* belegt die sequenz startend bei der Kante start */
/* geht fest davon aus, dass 2 mal nach innen hintereinander nicht vorkommt */

{
int i, j, k, zaehler, position;
KANTE *run;
int *sequenz; 
KANTE **seqkanten;
int puffer[7];
char *kan;


sequenz=sq->sequenz;
seqkanten=sq->kanten;
kan=sq->k_marks;


if (start->next->invers->next->name == aussen) 
    { fprintf(stderr,"Achtung -- naechste Kante nicht nach innen -- FEHLER !\n");
      exit(7); }

for (i=0; i<7; i++) { sequenz[i]=leer; seqkanten[i]=nil; kan[i]=0;}

if (start->prev->invers->prev->name != aussen) /* d.h. vorige Kante nicht nach aussen, also nur
						  Randlaenge zu bestimmen */
    { sq->laenge=0;
      for (run=start->next->invers->next->invers->next, zaehler=1; run != start;
           run=run->next->invers->next->invers->next) zaehler++;
      sequenz[0]=zaehler;
      seqkanten[0]=start;
      return;
    }

sq->laenge=0;
zaehler=1;
position=0;
seqkanten[0]=start;


for (run=start->next->invers->next->invers->next; run->next->invers->next->name < aussen;
     run=run->next->invers->next->invers->next) zaehler++;
sequenz[0]=zaehler; position=1; 
if (run->next->invers->next != start) seqkanten[position]=run->next->invers->next;
for (run=run->next->invers->next; run->next->invers->next->name >= aussen;
     run=run->next->invers->next) 
{ sequenz[position]=0; position++;
if (run->next->invers->next != start) seqkanten[position]=run->next->invers->next; }
/* naechste Kante vor nicht-0-sequenz suchen */


while (run != start)
{
for (zaehler=0; run->next->invers->next->name < aussen; 
                run=run->next->invers->next->invers->next) zaehler++;
sequenz[position]=zaehler;  position++;
if (run->next->invers->next != start) seqkanten[position]=run->next->invers->next; 
for (run=run->next->invers->next; run->next->invers->next->name >= aussen;
     run=run->next->invers->next) { sequenz[position]=0;  position++;
if (run->next->invers->next != start) seqkanten[position]=run->next->invers->next; }

}

sequenz[position]=leer; seqkanten[position]=nil;
sq->laenge=position;

kan[0]=sequenz_kanonisch(sequenz);

for (i=1; sequenz[i] != leer; i++)
  { for (j=i, k=0; sequenz[j]!=leer; j++, k++) puffer[k]=sequenz[j];
    for (j=0; j<i; j++, k++) puffer[k]=sequenz[j];
    puffer[k]=leer;
    kan[i]=sequenz_kanonisch(puffer);
  }



}


/**********************CHECKSIZE**************************************/

/* bestimmt die groesse der flaeche links von edge -- ist da keine gibt's Probleme */

int checksize(KANTE* edge)
{
KANTE *run; 
int zaehler=1;

for (run=edge->invers->next; run != edge; run=run->invers->next) zaehler++;
return(zaehler);
}



/*************************CODIERE***************************************/
/* speziell fuer diese Flaechenstuecke. Sie werden ab der Marke von aussen
   in eine "Spirale" entwickelt. Die Eindeutigkeit ergibt sich nur zusammen
   mit der Sequenz. der "code" sind die stellen, an denen 5-Ecke vorkommen 

   Ein mieser sonderfall sind die 0-sequenzen. da kann nicht einfach nur abgewickelt
   werden. Die Codierung ist dort: erst die Anzahl der 6-Eck Schichten, dann die
   Anzahl der Spitzen, die man gegen den Uhrzeigersinn zurueckgehen muss, um ein 
   5-Eck zu finden und dann erst kann normal fortgefahren werden. Die schichten werden 
   spiralfoermig abgebaut.

   laenge !=0 gilt nur fuer diese Situation. Dann ist laenge die anzahl der
   aussenkanten auf dem rand.

   Im Falle von 6 Pentagonen wird 1 zurueckgegeben, wenn der entwickelte Code
   kleinstmoeglich ist und 0 sonst.

   Fuer den miesen sonderfall wird der code aber (in der aufrufroutine) zum wegspeichern 
   so geaendert, dass die zweite stelle immer die anzahl N der verschiedenen markierten 
   Pflasterungen ist. die koennen dann erzeugt werden, indem 0 bis N Schritte zum ersten 
   5-Eck zurueckgegangen wird bei der Rekonstruktion.

   Die Anzahl der 6-Eck-Ringe ist immer 0 beim Aufruf.

*/


int codiere(PLANMAP map, FLAECHENTYP *code, KANTE *start, int codesize, int laenge)
{
int i, j, stelle, zaehler, knotenzahl, flaechennumber, verschiebung, merkeknoten;
/* zaehler zaehlt die Flaechengroesse, knotenzahl die zahl der restlichen knoten */
int tempknz, laufzaehler, autozaehler, minitest;
KANTE *run, *merke, *run2;
FLAECHENTYP testcode[9];


if (start->name != aussen) { fprintf(stderr,"Codiere must start at external edge !\n"); 
			     exit(8); }

tempknz=map[0][0].name;

if (tempknz==5) { code[0]=1; return(1); }

for (i=1; i<=tempknz; i++) for (j=0; j<3; j++)
  if (map[i][j].name == aussen) map[i][j].dummy= infty; else map[i][j].dummy=0;

run=start; stelle=0; knotenzahl=tempknz;

if (laenge) /* d.h. 6-Fuenfecke-patch */
  { verschiebung=0;
    code[2]=unbelegt; 
    code[0]=0; /*code[1]=verschiebung;*/ stelle=2; 
    merkeknoten=knotenzahl;
    laufzaehler=1;
    /* Jetzt den minimalen Code ausrechnen: */
    for ( autozaehler=0, run2=start->prev; 
	 (verschiebung<laenge) && !autozaehler; verschiebung++, run2=run2->prev->invers->next->invers)
      if (checksize(run2)==5)
	{
	  laufzaehler++;
	  run=run2->next;
	  stelle=2; knotenzahl=merkeknoten;
	  flaechennumber=0;
	  while (stelle<codesize)
	    { flaechennumber++;
	      zaehler=2;
	      while (run->prev->invers->prev->dummy>=laufzaehler) 
		                                     run=run->prev->invers->prev; /* sicherstellen, dass davor
										     keine aussenkanten sind */
	      run->prev->invers->dummy=laufzaehler; run->next->invers->dummy=laufzaehler;
	      run=run->next->invers->next; knotenzahl--;
	      while (run->dummy>=laufzaehler)
		{ zaehler++; knotenzahl--; run->prev->invers->dummy=laufzaehler; 
		  run->next->invers->dummy=laufzaehler;
		  run=run->next->invers->next; }
	      merke=run->next;
	      run=run->prev;
	      while (merke->dummy<laufzaehler)
		{ zaehler++; merke=merke->invers->prev; }
	      if (zaehler==5) { testcode[stelle]=flaechennumber; stelle++; }
	      else if (zaehler!=6) { fprintf(stderr,"ERROR in CODIERE: No 5- or 6-Gon !\n"); exit(9); }
	      if (knotenzahl==5) { testcode[stelle]=flaechennumber+1; stelle++; }
	    } /* ende while */
	  if ((minitest=codecmp(code+2,testcode+2,6))>0) 
	    { if (verschiebung) return(0);
	      else { for (stelle=2; stelle<8; stelle++) code[stelle]=testcode[stelle]; }
	    }
	  if (minitest==0) autozaehler=1; /* verschiebung>=1 ist automatisch */
	} /* ende checksize==5 */
    if (autozaehler) code[1]=verschiebung-1;
    else code[1]=laenge;
    return(1);
  } /* ende if */



 flaechennumber=0;



while (stelle<codesize)
  { flaechennumber++;
    zaehler=2;
    while (run->prev->invers->prev->dummy) run=run->prev->invers->prev; /* sicherstellen, dass davor
									   keine aussenkanten sind */
    run->prev->invers->dummy=1; run->next->invers->dummy=1;
    run=run->next->invers->next; knotenzahl--;
    while (run->dummy)
      { zaehler++; knotenzahl--; run->prev->invers->dummy=1; run->next->invers->dummy=1;
	run=run->next->invers->next; }
    merke=run->next;
    run=run->prev;
    while (!(merke->dummy))
      { zaehler++; merke=merke->invers->prev; }
    if (zaehler==5) { code[stelle]=flaechennumber; stelle++; }
    else if (zaehler!=6) { fprintf(stderr,"ERROR in CODIERE(2): No 5- or 6-Gon !\n"); exit(10); }
    if (knotenzahl==5) { code[stelle]=flaechennumber+1; stelle++; }
  } /* ende while */

return(1);

}



/***********************BBITEMALLOC********************************************/

BBITEMLISTE *bbitemalloc()
/* gibt immer die Adresse eines neuen bbitems zurueck */
{
static BBITEMLISTE *back=nil; /* back enthaelt immer den letzten, der zurueckgegeben 
			       wurde -- erst hochsetzen -- wichtig */
static BBITEMLISTE *last=nil;

if (back==last) { back=(BBITEMLISTE *)malloc(sizeof(BBITEMLISTE)*1001);
		  if (back==NULL) { fprintf(stderr,"Can not get more memory for bbitems"); exit(11); }
		  last=back+1000;
		  return(back); }

/* else */
back++;
return(back);
}


/***********************ITEMALLOC********************************************/

ITEMLISTE *itemalloc()
/* gibt immer die Adresse eines neuen items zurueck */
{
static ITEMLISTE *back=nil; /* back enthaelt immer den letzten, der zurueckgegeben 
			       wurde -- erst hochsetzen -- wichtig */
static ITEMLISTE *last=nil;

if (back==last) { back=(ITEMLISTE *)malloc(sizeof(ITEMLISTE)*1001);
		  if (back==NULL) { fprintf(stderr,"Can not get more memory for items"); exit(12); }
		  last=back+1000;
		  return(back); }

/* else */
back++;
return(back);
}


/*******************PUT_IN_LISTE***********************************************/

void put_in_liste(int sechsecke, SEQUENZ sq, FLAECHENTYP *code, int codesize )
{

ITEMLISTE *item;
SEQUENZLISTE *anfang;
SEQUENZLISTE **puffer;
int i,j, s_eintrag;

/*schreibesequenz(sq);*/
/*schreibelistitems();*/

anfang=mapliste.sechser[sechsecke];
mapliste.total_maps++;
for (i=0; i<sq.laenge; i++)
  { s_eintrag=sq.sequenz[i];
    if (anfang->number_next <= s_eintrag)
      { puffer=anfang->next_level;
	anfang->next_level=(SEQUENZLISTE **)malloc((s_eintrag+1)*sizeof(SEQUENZLISTE *));
	if (anfang->next_level==NULL) { fprintf(stderr,"Can not get more memory"); exit(13); }
	for (j=0; j< anfang->number_next; j++) anfang->next_level[j]=puffer[j];
	for (   ; j <= s_eintrag; j++) anfang->next_level[j]=nil;
	anfang->number_next=s_eintrag+1;
	free(puffer);
      }
    if (anfang->next_level[s_eintrag]==nil)
      {	anfang->next_level[s_eintrag]=(SEQUENZLISTE *)malloc(sizeof(SEQUENZLISTE));
	if (anfang->next_level[s_eintrag]==NULL) { fprintf(stderr,"Can not get more memory"); exit(14); }
	anfang=anfang->next_level[s_eintrag];
	anfang->next_level=nil; anfang->number_next=0;
	anfang->items=anfang->last_item=nil;
      }
    else anfang=anfang->next_level[s_eintrag];
  } /* ende for */

/* jetzt muesste anfang passend stehen zum Eintragen des Codes */

if (anfang->items==nil) item=anfang->items=anfang->last_item=itemalloc(); 
   else { item=anfang->last_item->next_item=itemalloc(); 
	  anfang->last_item=item; }
item->next_item=nil;
for (j=0; j<codesize; j++) item->code[j]=code[j];
}


/*******************PUT_IN_BB_LISTE***********************************************/

void put_in_bb_liste(int sechsecke, SEQUENZ sq, FLAECHENTYP *code)
{

BBITEMLISTE *item, **puffer, *merke;
BBSEQUENZLISTE *anfang;
int j, s_eintrag;

/*schreibesequenz(sq);*/
/*schreibelistitems();*/



anfang=bbliste.sechser[sechsecke];
s_eintrag=sq.sequenz[0];
if (anfang->number_next <= s_eintrag)
  { puffer=anfang->items;
    anfang->items=(BBITEMLISTE **)malloc((s_eintrag+1)*sizeof(BBITEMLISTE *));
    if (anfang->items==NULL) { fprintf(stderr,"Can not get more memory"); exit(15); }
    for (j=0; j< anfang->number_next; j++) { anfang->items[j]=puffer[j]; }
    for (   ; j <= s_eintrag; j++) { anfang->items[j]=nil; }
    anfang->number_next=s_eintrag+1;
    free(puffer);
  }

bbliste.total_items++;
bbliste.total_maps += code[1];

if (anfang->items[s_eintrag]==nil) { item=anfang->items[s_eintrag]=bbitemalloc(); 
			              item->next_item=nil; }
   else { merke=anfang->items[s_eintrag];
	  item=anfang->items[s_eintrag]=bbitemalloc();
	  item->next_item=merke; }
if (item==NULL) { fprintf(stderr,"Can not get more memory"); exit(16); }
for (j=0; j<8; j++) item->code[j]=code[j];

}




/************************SCHREIBE_AUF************************************/

void schreibe_auf(PLANMAP map, SEQUENZ sq, int rest_sechsecke)
/* codiert und schreibt eine markierte Pflasterung -- wird nur fuer
   bis zu 5 Fuenfecken aufgerufen */
{
int fuenfecke, sechsecke, i, codesize, pfadlaenge, non_nuller;
FLAECHENTYP code[9];


if ( !(do_sandwich || do_brille) ) return;
if (IPR && (!is_ipr)) return;

fuenfecke=6-sq.laenge;

if (fuenfecke < 2) return; /* die werden bei der konstruktion nie gebraucht */
for (i=non_nuller=0; i< sq.laenge; i++) if (sq.sequenz[i] != 0) non_nuller++;
if (non_nuller >2) return; /* Bei jedem Patch der GEBRAUCHT wird, koennen nur
			      an 2 Stellen Probleme auftreten */


pfadlaenge=sq.laenge;
for (i=0; i< sq.laenge; i++) pfadlaenge += (2*sq.sequenz[i]);

switch (fuenfecke)
  {
  case 5: { brillenglasmark[pfadlaenge]=1;
	    break; }

  case 4: { zwei_3_4_mark[pfadlaenge]=1;
            if (sq.sequenz[1]==0) /* dann kann es auch ein brillenglas sein */
	        brillenglasmark[pfadlaenge]=1;
	    break; }
  default: { zwei_3_4_mark[pfadlaenge]=1; }
  }

sechsecke=(map[0][0].name)-10+sq.laenge-sq.sequenz[0];
for (i=1; i<sq.laenge; i++) sechsecke -= sq.sequenz[i];
sechsecke=sechsecke/2;        /* alles leicht aus Euler Formel */


if (sechsecke+rest_sechsecke != max_sechsecke) { fprintf(stderr,"Error in 6-gon calculation (schreibe_auf) !\n");
						 exit(17); }

codesize=fuenfecke; 
codiere(map, code, sq.kanten[0], fuenfecke,0);

put_in_liste(sechsecke, sq, code, codesize );

return;
	   }

/*************************CHECK_MARK_UND_SCHREIBE***************************/

/* Ueberprueft, ob eine Einbettung mit 6 5-Ecken, also ohne 
Doppelte Aussenkanten, neu ist. Wenn ja, codiert und speichert sie die Einbettung
und alle sich daraus durch hinzufuegen von 6-Eck-Ringen ergebenden */

void check_mark_und_schreibe(PLANMAP map, KANTE *first, int laenge, int rest_sechsecke)
{


SEQUENZ localsq;
int sechsecke;
FLAECHENTYP code[8];

if (!do_bauchbinde) return;
if (IPR && (!is_ipr))  return; 

localsq.laenge=0; localsq.sequenz[0]=laenge;
localsq.kanten[0]=first;

sechsecke=((map[0][0].name)-10-laenge)/2;
               /* leicht aus Euler Formel */

if (sechsecke+rest_sechsecke != max_sechsecke) 
  { fprintf(stderr,"Error in 6-gon calculation (check_mark_und_schreibe) !\n");
						 exit(18); }

if (!codiere(map, code, first, 8, laenge)) return; /* nicht kanonisch */
if (code[0] !=0) { fprintf(stderr," there was a hexagon ring.......\n"); exit(19); }
put_in_bb_liste(sechsecke, localsq, code);

bblmark[laenge]=1;

/* neue ringe hinzufuegen */
while (rest_sechsecke >= laenge)
  { 
    rest_sechsecke -= laenge;
    sechsecke+= laenge;
    (code[0])++;
    put_in_bb_liste(sechsecke, localsq, code);
  }

return;

}


/***************************BAUE_AUF**************************************/

/* die eigentliche konstruktionsroutine -- legt auf alle moeglichen arten eine
neue reihe an */

void baue_auf(PLANMAP map, SEQUENZ sq, int sechsecke)
{

SEQUENZ localseq;
int j, i, laenge;
KANTE *naechste, *nextmark, *run;
int anzahl, naechste_stelle, sql;


if (IPR && (!is_ipr))  return;

sql=sq.laenge;

if (sql >=2)
{
for (i=0; i<sql && ((i==0) || !((sq.k_marks)[i])); i++) 
                                            /* Schleife ueber alle moeglichen Startpunkte */
  {
    laenge=sq.sequenz[i]; 
    if (i==sql-1) naechste_stelle=0; else naechste_stelle=i+1;
    if (laenge==0)
    {
    /* da nie eine 0 am anfang einer kanonischen Sequenz stehen kann, kann die erste einer
       doppel-0 nie am ende stehen, also: */
      if ( (i<sql-1) && (sq.sequenz[i+1]==0) )
	{
	  if (sechsecke >= 1)
	    { 
	      naechste=sq.kanten[i];
	      { add_polygon(6,map,naechste,&naechste); nextmark=naechste; }
	      belege_sequenz(nextmark,&localseq); 
	      if (localseq.k_marks[0])
		{ schreibe_auf(map,localseq,sechsecke-1);
		  baue_auf(map, localseq, sechsecke-1); }
	      /* aufraeumen: */
	      (map[0][0].name) = (map[0][0].name) - 4;
	      run=sq.kanten[i]; run->name=aussen; run->invers=nil; 
	      run=run->next->invers->next; run->name=aussen; run->invers=nil;
	    }   /* ende if ...*/
	  naechste=sq.kanten[i];
	  { add_polygon(5,map,naechste,&naechste); nextmark=naechste; }
	  belege_sequenz(nextmark,&localseq); 
	  if (localseq.k_marks[0])
	    { schreibe_auf(map,localseq,sechsecke);
	      baue_auf(map, localseq, sechsecke); }
	  /* aufraeumen: */
	  is_ipr=1;
	  (map[0][0].name) = (map[0][0].name) - 3;
	  run=sq.kanten[i]; run->name=aussen; run->invers=nil; 
	  run=run->next->invers->next; run->name=aussen; run->invers=nil;

	}

    if (sq.laenge==2) /* nur dann oder im vorigen Fall muss auch an 0er angelegt werden */
    {
    /* In diesem Teil wird die Sequenz nicht a priori berechnet, sondern erst im nachhinein --
       das kostet zwar Zeit, ist aber einfacher und braucht nicht so wahnsinnig viele
       Fallunterscheidungen */

    if (i != 1) { fprintf(stderr,"ERROR: i should be 1 !\n"); exit(26); }
    anzahl= 2 + sq.sequenz[0]; /* Bei laenge 0 muss der naechste mit aufgefuellt werden,
					       um keine Doppel-Innenkanten zu erhalten */

    /* erst nur 6-Ecke */
    if (sechsecke >= anzahl)
      { 
      naechste=sq.kanten[i];
      if (anzahl==1) { add_polygon(6,map,naechste,&naechste); nextmark=naechste; }
        else {
               add_polygon(6,map,naechste,&naechste); nextmark=naechste->prev->invers->prev;
               for (j=1; j<anzahl; j++)  add_polygon(6,map,naechste,&naechste); }
      belege_sequenz(nextmark,&localseq); 
      if (localseq.k_marks[0])
	   { schreibe_auf(map,localseq,sechsecke-anzahl);
	     baue_auf(map, localseq, sechsecke-anzahl); }
      /* aufraeumen: */
      (map[0][0].name) = (map[0][0].name) - 2*anzahl -2;
      run=sq.kanten[i]; run->name=aussen; run->invers=nil; 
      run=run->next->invers->next; run->name=aussen; run->invers=nil;
      for (j=2 ; j<anzahl; j++) { run=run->next->invers->next->invers->next;
	                         run->name=aussen; run->invers=nil; }
      }   /* ende if ...*/



    /* dann ein 5- und 6-Ecke */
    if (sechsecke >= anzahl-1)
      { 
      naechste=sq.kanten[i];
      if (anzahl==1) { add_polygon(5,map,naechste,&naechste); nextmark=naechste; }
        else {
               add_polygon(6,map,naechste,&naechste); nextmark=naechste->prev->invers->prev;
               for (j=1; j<anzahl-1; j++)  add_polygon(6,map,naechste,&naechste);  
               add_polygon(5,map,naechste,&naechste);  }
      belege_sequenz(nextmark,&localseq);
      if (localseq.k_marks[0])
	   { schreibe_auf(map,localseq,sechsecke-anzahl+1);
	     baue_auf(map, localseq, sechsecke-anzahl+1); }
      /* aufraeumen: */
      is_ipr=1;
      (map[0][0].name) = (map[0][0].name) - 2*anzahl-1;
      run=sq.kanten[i]; run->name=aussen; run->invers=nil; 
      run=run->next->invers->next; run->name=aussen; run->invers=nil;
      for (j=2 ; j<anzahl; j++) { run=run->next->invers->next->invers->next;
	                         run->name=aussen; run->invers=nil; }
      }   /* ende if ... */

    /* dann eventuell zwei 5- und der Rest 6-Ecke um es zu 0-Sequenz zu machen */
    if (sechsecke >= anzahl-2)
      {
      naechste=sq.kanten[i];
      add_polygon(5,map,naechste,&naechste); nextmark=naechste->prev->invers->prev;
      for (j=1; j<anzahl-1; j++)  add_polygon(6,map,naechste,&naechste);  
      add_polygon(5,map,naechste,&naechste); 
      belege_sequenz(nextmark,&localseq);
      check_mark_und_schreibe(map,nextmark,localseq.sequenz[0],sechsecke-anzahl+2);

      /* aufraeumen: */
      is_ipr=1;
      (map[0][0].name) = (map[0][0].name) - 2*anzahl;
      run=sq.kanten[i]; run->name=aussen; run->invers=nil; 
      run=run->next->invers->next; run->name=aussen; run->invers=nil;
      for (j=2; j<anzahl; j++) { run=run->next->invers->next->invers->next;
	                         run->name=aussen; run->invers=nil; }

      }   /* ende if */
     } /* ende if sq.laenge==2 */
    } /* ende laenge==0 */


    else /* d.h. laenge !=0 */
    {

    /* ein sonderfall, wenn der naechste ein 0er ist (der erste aber nicht)--
       dann musss da noch ein 6-Eck mehr angefuegt werden: */

      if ((sq.sequenz[naechste_stelle]==0) && (sql>2))
	  { 
	    if (sechsecke >= laenge+1)
	    { 
	      naechste=sq.kanten[i];
              add_polygon(6,map,naechste,&naechste); nextmark=naechste->prev->invers->prev;
	      /* insgesamt laenge+1: */
	      for (j=1; j<=laenge; j++)  add_polygon(6,map,naechste,&naechste);  
	      belege_sequenz(nextmark,&localseq); 
	      if (localseq.k_marks[0])
		{ schreibe_auf(map,localseq,sechsecke-laenge-1);
		  baue_auf(map, localseq, sechsecke-laenge-1); }
              /* aufraeumen: */
	      (map[0][0].name) = (map[0][0].name) - 2*laenge -4;
	      run=sq.kanten[i]; run->name=aussen; run->invers=nil;
	      for (j=0; j<laenge; j++) { run=run->next->invers->next->invers->next;
					 run->name=aussen; run->invers=nil; }
	      run=run->next->invers->next; run->name=aussen; run->invers=nil;

	    }   /* ende if ...*/
	    if (sechsecke >= laenge)
	    { 
	      naechste=sq.kanten[i];
              add_polygon(6,map,naechste,&naechste); nextmark=naechste->prev->invers->prev;
	      /* insgesamt laenge+1: */
	      for (j=1; j<laenge; j++)  add_polygon(6,map,naechste,&naechste);  
	      add_polygon(5,map,naechste,&naechste);  
	      belege_sequenz(nextmark,&localseq); 
	      if (localseq.k_marks[0])
		{ schreibe_auf(map,localseq,sechsecke-laenge);
		  baue_auf(map, localseq, sechsecke-laenge); }
              /* aufraeumen: */
	      is_ipr=1;
	      (map[0][0].name) = (map[0][0].name) - 2*laenge -3;
	      run=sq.kanten[i]; run->name=aussen; run->invers=nil;
	      for (j=0; j<laenge; j++) { run=run->next->invers->next->invers->next;
					 run->name=aussen; run->invers=nil; }
	      run=run->next->invers->next; run->name=aussen; run->invers=nil;

	    }   /* ende if ...*/
	  } /* ende sonderfall naechste_stelle==0-sequenz */



    /* erst nur 6-Ecke */
    if (sechsecke >= laenge)
      { 
      naechste=sq.kanten[i];
      berechne_sequenz(&localseq,sq,i,0);
      if (localseq.k_marks[0])
      {
      if (laenge==1) { add_polygon(6,map,naechste,&naechste); nextmark=naechste;
                       localseq.kanten[0]=nextmark; 
		       localseq.kanten[localseq.laenge-1]=naechste->prev->invers->prev; }
        else {
               add_polygon(6,map,naechste,&naechste); nextmark=naechste->prev->invers->prev;
               for (j=1; j<laenge; j++)  add_polygon(6,map,naechste,&naechste); 
               localseq.kanten[0]=nextmark; localseq.kanten[1]=naechste; }
      if (localseq.k_marks[0])
	   { schreibe_auf(map,localseq,sechsecke-laenge);
	     baue_auf(map, localseq, sechsecke-laenge); }
      /* aufraeumen: */
      (map[0][0].name) = (map[0][0].name) - 2*laenge -1;

      run=sq.kanten[i]; run->name=aussen; run->invers=nil;
      for (j=0; j<laenge; j++) { run=run->next->invers->next->invers->next;
	                         run->name=aussen; run->invers=nil; }
    }/* ende if kanonisch */
      }   /* ende if ...*/



    /* dann ein 5- und 6-Ecke */
    if (sechsecke >= laenge-1)
      { 
      naechste=sq.kanten[i];
      berechne_sequenz(&localseq,sq,i,1); 
      if (localseq.k_marks[0])
      {
      if (laenge==1) { add_polygon(5,map,naechste,&naechste); nextmark=naechste; 
                       localseq.kanten[0]=nextmark; }
        else {
               add_polygon(6,map,naechste,&naechste); nextmark=naechste->prev->invers->prev;
               for (j=1; j<laenge-1; j++)  add_polygon(6,map,naechste,&naechste);  
               add_polygon(5,map,naechste,&naechste);  
               localseq.kanten[0]=nextmark; }
      if (localseq.k_marks[0])
	   { schreibe_auf(map,localseq,sechsecke-laenge+1);
	     baue_auf(map, localseq, sechsecke-laenge+1); }
      /* aufraeumen: */
      is_ipr=1;
      (map[0][0].name) = (map[0][0].name) - 2*laenge;
      run=sq.kanten[i]; run->name=aussen; run->invers=nil;
      for (j=0; j<laenge; j++) { run=run->next->invers->next->invers->next;
	                         run->name=aussen; run->invers=nil; }
    }/* ende if kanonisch */
      }   /* ende if ... */

    /* dann eventuell zwei 5- und der Rest 6-Ecke um es zu 0-Sequenz zu machen */
    if ((laenge>=2) && (sechsecke >= laenge-2) && (sq.laenge==2))
      { 
      naechste=sq.kanten[i];
      berechne_sequenz(&localseq,sq,i,2);
      add_polygon(5,map,naechste,&naechste); nextmark=naechste->prev->invers->prev;
      for (j=1; j<laenge-1; j++)  add_polygon(6,map,naechste,&naechste);  
      add_polygon(5,map,naechste,&naechste); 
      localseq.kanten[0]=nextmark;
      check_mark_und_schreibe(map,nextmark,localseq.sequenz[0],sechsecke-laenge+2);

      /* aufraeumen: */
      is_ipr=1;
      (map[0][0].name) = (map[0][0].name) - 2*laenge + 1;
      run=sq.kanten[i]; run->name=aussen; run->invers=nil;
      for (j=0; j<laenge; j++) { run=run->next->invers->next->invers->next;
	                         run->name=aussen; run->invers=nil; }
      }   /* ende if */
    }/* ende laenge != 0 */
   } /* ende for */

} /* ende if sequenzlaenge >=2 */

else /* d.h. sequenzlaenge==1 */
{
laenge=sq.sequenz[0];

/* erst nur 6-Ecke */
if (laenge && (sechsecke >= (laenge+1)))
 { 
 naechste=sq.kanten[0];
 berechne_sequenz(&localseq,sq,0,0);
 for (j=0; j<=laenge; j++)  add_polygon(6,map,naechste,&naechste);  
 nextmark=naechste;
 localseq.kanten[0]=nextmark;
 schreibe_auf(map,localseq,sechsecke-laenge-1);
 baue_auf(map, localseq, sechsecke-laenge-1); 
 /* aufraeumen: */
 (map[0][0].name) = (map[0][0].name) - 2*laenge -3;

      run=sq.kanten[0]; run->name=aussen; run->invers=nil;
      for (j=0; j<laenge; j++) { run=run->next->invers->next->invers->next;
	                         run->name=aussen; run->invers=nil; }
      }   /* ende if */

/* dann ein 5- und 6-Ecke */
if (laenge && (sechsecke >= laenge))
  {
  naechste=sq.kanten[0];
  berechne_sequenz(&localseq,sq,0,1);
  for (j=0; j<laenge; j++)  add_polygon(6,map,naechste,&naechste);  
  add_polygon(5,map,naechste,&naechste); 
  nextmark=naechste;
  /* das ist zwar zwangslaeufig kanonisch, aber trotzdem: */
  localseq.kanten[0]=nextmark; 
  check_mark_und_schreibe(map,nextmark,localseq.sequenz[0],sechsecke-laenge);
  /* aufraeumen: */
  is_ipr=1;
  (map[0][0].name) = (map[0][0].name) - 2*laenge -2;
  run=sq.kanten[0]; run->name=aussen; run->invers=nil;
  for (j=0; j<laenge; j++) { run=run->next->invers->next->invers->next;
			     run->name=aussen; run->invers=nil; }
      }   /* ende if */


} /* ende else */

}

/***************************BAUE_PATCHES************************************/

void baue_patches(int sechsecke)
{
PLANMAP map;
SEQUENZ sq;
KANTE *marke;
int i;


for (i=0; i<=N; i++) bblmark[i]=brillenglasmark[i]=zwei_3_4_mark[i]=0;


/* Patches, die nur aus einer Flaeche bestehen, brauchen nicht betrachtet zu
   werden */

if (sechsecke >=2)
/* zuerst Start mit 2 Sechsecken */
{
baue_polygon(6,map,&marke);
add_polygon(6,map,marke,&marke);
belege_sequenz(marke, &sq);
schreibe_auf(map,sq,sechsecke-2);
baue_auf( map, sq, sechsecke-2);
}

if (sechsecke >=1)
/* dann ein 5- und ein 6-Eck */
{
baue_polygon(5,map,&marke);
add_polygon(6,map,marke,&marke);
belege_sequenz( marke, &sq);
schreibe_auf(map,sq,sechsecke-1);
baue_auf( map, sq, sechsecke-1);
}

/* dann zwei 5-Ecke */
if (!IPR)
{
baue_polygon(5,map,&marke);
add_polygon(5,map,marke,&marke);
belege_sequenz( marke, &sq);
schreibe_auf(map,sq,sechsecke);
baue_auf( map, sq, sechsecke);
}


for (minbbl=1; bblmark[minbbl]==0; minbbl++);
for (maxbbl=N; bblmark[maxbbl]==0; maxbbl--);

for (minbrillenglas=1; brillenglasmark[minbrillenglas]==0; minbrillenglas++);
for (maxbrillenglas=N; brillenglasmark[maxbrillenglas]==0; maxbrillenglas--);

for (min_2_3_4=1; zwei_3_4_mark[min_2_3_4]==0; min_2_3_4++);


}

/***********************INITIALIZE_LIST**********************************/

void initialize_list()
{
int j;
SEQUENZLISTE *qq;
BBSEQUENZLISTE *bbqq;

mapliste.total_maps=0;

for (j=0; j<=max_sechsecke; j++)
  {
    qq=(mapliste.sechser)[j]=(SEQUENZLISTE *)malloc(sizeof(SEQUENZLISTE));
    if (qq==NULL) { fprintf(stderr,"Can not get more memory"); exit(27); }
    qq->next_level=nil;
    qq->number_next=0;
    qq->items=qq->last_item=nil;
  }


bbliste.total_items=bbliste.total_maps=0;
for (j=0; j<=max_sechsecke; j++)
  {
    bbqq=(bbliste.sechser)[j]=(BBSEQUENZLISTE *)malloc(sizeof(BBSEQUENZLISTE));
    if (bbqq==NULL) { fprintf(stderr,"Can not get more memory"); exit(28); }
    bbqq->items=nil;
    bbqq->number_next=0;
  }




}



/**********************ZAEHLE_KNOTEN*************************************/

void zaehle_knoten(PLANMAP map, KNOTENTYP knoten, BOOL mark[], int *patchknz)

/* zaehlt die knoten, belegt aber auch dummy */

{
int j;

for (j=0; j<3; j++) 
  if (map[knoten][j].mininame == aussen) map[knoten][j].dummy=infty;
   else { map[knoten][j].dummy=0;
	  if (!mark[map[knoten][j].mininame])
	    { (*patchknz)++;
	      mark[map[knoten][j].mininame]=1;
	      zaehle_knoten(map,map[knoten][j].mininame,mark,patchknz);
	    }
	}
}



/**********************REKO_BB_CODE***************************************/
/* Rekonstruiert den minimalen Code eines 6-Eck-patches */

void reko_bb_code(PLANMAP map, KNOTENTYP *code, KNOTENTYP *spiegelcode, int laenge, 
		  KANTE *start, KANTE *ministart[], KANTE *spiegelministart[], int *patchknz)
{
int i, j, stelle, zaehler, knotenzahl, flaechennumber, schichtenzaehler, verschiebung, merkeknoten;
/* zaehler zaehlt die Flaechengroesse, knotenzahl die zahl der restlichen knoten */
int laufzaehler;
KANTE *run, *merke, *run2, *merke_run, *mstart;
KNOTENTYP testcode[9];
int mstartzaehler, test, k, laenge_2;
BOOL mark[N+1];


if (start->mininame != aussen) { fprintf(stderr,"Reko_BB_code must start at external edge !\n"); 
			     exit(29); }
for (i=0; i<8; i++) { code[i]=spiegelcode[i]=unbelegt; testcode[i]=0; }

mstartzaehler=0;
for (i=0; i<7; i++) ministart[i]=spiegelministart[i]=nil;

for (i=1; i<=map[0][0].name; i++) mark[i]=0;
mark[start->ursprung]=1; *patchknz=1;

zaehle_knoten(map,start->ursprung,mark,patchknz);

laenge_2 = laenge/2;
run=start; knotenzahl=*patchknz;

verschiebung=schichtenzaehler=0;

while (!verschiebung)
  {for (i=1, run2=run->prev; (i<=laenge_2) && !verschiebung; i++, run2=run2->prev->invers->next->invers)
     /* muss bei 1 starten und nachher korrigiert werden, um den Abbruch bei 0 zu gewaehrleisten */
     { if (checksize(run2) == 5) { run=run2->next; verschiebung=i; } }
   if (!verschiebung) { schichtenzaehler++;
			knotenzahl -= laenge;
			run=run->prev->invers->next->invers;
			for (run2=run, i=0; i<laenge_2; i++, 
			     run2=run2->next->invers->next->invers->next)
			  { run2->dummy=infty; }
		      }
 } /* ende while */
code[0]=schichtenzaehler; code[1]=0; /* verschiebung wird nicht betrachtet */ stelle=2; 
merkeknoten=knotenzahl;
laufzaehler=1;
/* Jetzt den minimalen Code ausrechnen: */
for ( run2=run->prev; verschiebung<=laenge_2; verschiebung++, run2=run2->prev->invers->next->invers)
  if (checksize(run2)==5)
    { merke_run=run2->next; 
      laufzaehler++;
      run=run2->next;
      stelle=2; knotenzahl=merkeknoten;
      flaechennumber=0;
      while (stelle<8)
	{ 
	  flaechennumber++;
	  zaehler=2;
	  while (run->prev->invers->prev->dummy>=laufzaehler) 
	    run=run->prev->invers->prev; /* sicherstellen, dass davor
					    keine aussenkanten sind */
	  run->prev->invers->dummy=laufzaehler; run->next->invers->dummy=laufzaehler;
	  run=run->next->invers->next; knotenzahl--;
	  while (run->dummy>=laufzaehler)
	    { zaehler++; knotenzahl--; run->prev->invers->dummy=laufzaehler; 
	      run->next->invers->dummy=laufzaehler;
	      run=run->next->invers->next; }
	  merke=run->next;
	  run=run->prev;
	  while (merke->dummy<laufzaehler)
	    { zaehler++; merke=merke->invers->prev; }
	  if (zaehler==5) { testcode[stelle]=flaechennumber; stelle++; }
	  else if (zaehler!=6) { fprintf(stderr,"ERROR in REKO_BB_CODE: No 5- or 6-Gon !\n"); exit(30); }
	  if (knotenzahl==5) { testcode[stelle]=flaechennumber+1; stelle++; }
	} /* ende while */
      if ((test=codecmp_kn(code+2,testcode+2,6))>=0) 
	{ if (test>0) { for (stelle=2; stelle<8; stelle++) code[stelle]=testcode[stelle];
			for (k=0; k<mstartzaehler; k++) ministart[k]=nil;
		        mstartzaehler=0;}
	  mstart=merke_run;
	  for (k=0; k<schichtenzaehler; k++) mstart = mstart->invers->prev->invers->next;
	  ministart[mstartzaehler]=mstart->prev->invers->next;
	  mstartzaehler++;
	}
    } /* ende checksize==5 */



/* Jetzt den Spiegelcode */

for (i=1; i<=map[0][0].name; i++) 
  if (mark[i]) 
    for (j=0; j<3; j++) 
      { if (map[i][j].mininame==aussen) map[i][j].dummy=infty;
        else map[i][j].dummy=0; }

run=start; knotenzahl=*patchknz;

verschiebung=schichtenzaehler=mstartzaehler=0;

while (!verschiebung)
  {for (i=1, run2=run->prev; (i<=laenge_2) && !verschiebung; i++, run2=run2->invers->prev->invers->next)
     /* muss bei 1 starten und nachher korrigiert werden, um den Abbruch bei 0 zu gewaehrleisten */
     { if (checksize(run2) == 5) { run=run2->next; verschiebung=i; } }
   if (!verschiebung) { schichtenzaehler++;
			knotenzahl -= laenge;
			run=run->next->invers->prev->invers;
			for (run2=run, i=0; i<laenge_2; i++, 
			     run2=run2->prev->invers->prev->invers->prev)
			  { run2->dummy=infty; }
		      }
 } /* ende while */
spiegelcode[0]=schichtenzaehler; spiegelcode[1]=0; /* verschiebung wird nicht betrachtet */ stelle=2; 
merkeknoten=knotenzahl;
laufzaehler=1;
/* Jetzt den minimalen Code ausrechnen: */
for ( run2=run->prev; verschiebung<=laenge_2; verschiebung++, run2=run2->invers->prev->invers->next)
  if (checksize(run2)==5)
    { merke_run=run2->next; 
      laufzaehler++;
      run=run2->next;
      stelle=2; knotenzahl=merkeknoten;
      flaechennumber=0;
      while (stelle<8)
	{ flaechennumber++;
	  zaehler=2;
	  while (run->next->invers->next->dummy>=laufzaehler) 
	    run=run->next->invers->next; /* sicherstellen, dass davor
					    keine aussenkanten sind */
	  run->next->invers->dummy=laufzaehler; run->prev->invers->dummy=laufzaehler;
	  run=run->prev->invers->prev; knotenzahl--;
	  while (run->dummy>=laufzaehler)
	    { zaehler++; knotenzahl--; run->next->invers->dummy=laufzaehler; 
	      run->prev->invers->dummy=laufzaehler;
	      run=run->prev->invers->prev; }
	  merke=run->prev;
	  run=run->next;
	  while (merke->dummy<laufzaehler)
	    { zaehler++; merke=merke->invers->next; }
	  if (zaehler==5) { testcode[stelle]=flaechennumber; stelle++; }
	  else if (zaehler!=6) { fprintf(stderr,"ERROR in REKO_BB_CODE(2):  No 5- or 6-Gon !\n"); exit(31); }
	  if (knotenzahl==5) { testcode[stelle]=flaechennumber+1; stelle++; }
	} /* ende while */
      if ((test=codecmp_kn(spiegelcode+2,testcode+2,6))>=0) 
	{ if (test>0) { for (stelle=2; stelle<8; stelle++) spiegelcode[stelle]=testcode[stelle];
			for (k=0; k<mstartzaehler; k++) spiegelministart[k]=nil;
		        mstartzaehler=0;}
	  mstart=merke_run;
	  for (k=0; k<schichtenzaehler; k++) mstart = mstart->invers->next->invers->prev;
	  spiegelministart[mstartzaehler]=mstart->next->invers->prev;
	  mstartzaehler++;
	}
    } /* ende checksize==5 */

return;
}

/***********************BAUCHBINDE_REKO*******************************/

/* berechnet den minimalen Code, der sich aus der bei "anfangskante"
   beginnenden Bauchbinde ergibt */
/* TH:  Die Funktion wurde so geaendert, dass sie 
   0 zurueckgibt, wenn code > minimaler Code (wie bisher)
   1 zurueckgibt, wenn code < minimaler Code (wie bisher)
   2 zurueckgibt, wenn code== minimaler Code fuer die
                  Originalversion (Automorphismus existiert)
   4 zurueckgibt, wenn code== minimaler Code fuer die
                  gespiegelte Version (Automorphismus existiert) 
   6 zurueckgibt, wenn code== minimaler Code sowohl fuer die
                  Originalversion als auch fuer die gespiegelte
                  Version (Automorphismus existiert)              */

int bauchbinde_reko(PLANMAP map,KNOTENTYP *code,KANTE *anfangskante)
{
int i,j,k, patchknz1, patchknz2, test, test2, test3, test4, returnwert;
KANTE *run;
KNOTENTYP code1[8], code2[8], spiegelcode1[8], spiegelcode2[8];
KANTE *ministart1[7], *ministart2[7], *spiegelministart1[7], *spiegelministart2[7];
KNOTENTYP *ucode, *lcode, *uscode, *lscode;
KANTE **ustart, **lstart, **us_start, **ls_start;
BOOL gleich, ende;
BOOL j_gleich1, j_gleich2, j_gleich3, j_gleich4;                 /* TH */
FLAECHENTYP c3, c11;


c3=code[3]; c11=code[11];
code[3]=code[11]=0;

for (i=1; i<=map[0][0].name; i++) for (j=0;j<3; j++) { map[i][j].dummy=0;
						       map[i][j].mininame=map[i][j].name; }

for (i=1, run=anfangskante->invers->prev; i<code[0]; i+=2)
  { run->prev->mininame=aussen;
    run=run->invers->next->invers->prev; }

reko_bb_code(map, code1, spiegelcode1, code[0], anfangskante->invers->next, ministart1, spiegelministart1, 
	     &patchknz1);


for (i=1, run=anfangskante->invers->prev; i<code[0]; i+=2)
  { run->prev->mininame=run->prev->name;
    run->invers->prev->mininame=aussen;
    run=run->invers->next->invers->prev; }

reko_bb_code(map, code2, spiegelcode2, code[0], anfangskante->next, ministart2, spiegelministart2, 
	     &patchknz2);


if (patchknz2>patchknz1) { ucode=code2; uscode=spiegelcode2; lcode=code1; lscode=spiegelcode1; 
			   ustart=ministart2; lstart=ministart1; us_start=spiegelministart2;
			   ls_start=spiegelministart1; gleich=0; }
   else if (patchknz2<patchknz1) { ucode=code1; uscode=spiegelcode1; lcode=code2; lscode=spiegelcode2; 
				   ustart=ministart1; lstart=ministart2; us_start=spiegelministart1;
				   ls_start=spiegelministart2; gleich=0; }
        else /* d.h. beide patchknotenzahlen gleich */
	  { test=codecmp_kn(code1,code2,8);
	    if (test>0) { ucode=code1; lcode=code2; ustart=ministart1; lstart=ministart2; gleich=0; }
	      else { if (test<0) { ucode=code2; lcode=code1; ustart=ministart2; lstart=ministart1; gleich=0; }
		     else { ucode=code1; lcode=code2; ustart=ministart1; lstart=ministart2; /*vorerst*/ gleich=1;
			  }
		   }
	    test=codecmp_kn(spiegelcode1,spiegelcode2,8);
	    if (test>0) { uscode=spiegelcode1; lscode=spiegelcode2; us_start=spiegelministart1; 
			  ls_start=spiegelministart2;  }
	      else { if (test<0) { uscode=spiegelcode2; lscode=spiegelcode1; us_start=spiegelministart2; 
				   ls_start=spiegelministart1;  }
		     else { uscode=spiegelcode1; lscode=spiegelcode2; us_start=spiegelministart1; /*vorerst*/ 
			    ls_start=spiegelministart2; }
		   }
	  }

j_gleich1 = j_gleich2 = 0;       /* TH */
if ((test=codecmp_kn(lcode,code+2,8)) < 0) {code[3]=c3; code[11]=c11; return(0);}
   else if (test==0)
         { if ((test2=codecmp_kn(ucode,code+10,8)) < 0) {code[3]=c3; code[11]=c11; return(0);}
	   else if (test2==0) /* d.h. die verschiebung muss entscheiden */
	     { for (i=0; ustart[i]!=nil; i++)
		 { run=ustart[i]->next->invers->prev;
		   j=ende=0;
		   while (!ende)
		     { 
		       for (k=0; lstart[k] != nil; k++) if (lstart[k]==run) ende=1;
		       if (!ende) { j++; run=run->prev->invers->prev->invers->prev; }
		     }
		   if (j<code[18])  {code[3]=c3; code[11]=c11; return(0);}
		   if (j==code[18]) {j_gleich1 = 1;}            /* TH */
                 }
	       if (gleich) {
		 for (i=0; lstart[i]!=nil; i++)
		   { run=lstart[i]->next->invers->prev;
		     j=ende=0;
		     while (!ende)
		       {
		         for (k=0; ustart[k] != nil; k++) if (ustart[k]==run) ende=1;
		         if (!ende) { j++; run=run->prev->invers->prev->invers->prev; }
		       }
		     if (j<code[18]) {code[3]=c3; code[11]=c11; return(0);}
                     if (j==code[18]) {j_gleich2 = 1;}     /* TH */
                   }
               }
               else {j_gleich2 = 1;}     /* TH */
	     } /* ende test2==0 */
	 } /* ende test==0 */


/* nun fuer die gespiegelte version: */

j_gleich3 = j_gleich4 = 0;          /* TH */
if ((test3=codecmp_kn(lscode,code+2,8)) < 0) { code[3]=c3; code[11]=c11; return(0); }
   else if (test3==0)
         { if ((test4=codecmp_kn(uscode,code+10,8)) < 0) {code[3]=c3; code[11]=c11; return(0);}
	   else if (test4==0) /* d.h. die verschiebung muss entscheiden */
	     { 
	       for (i=0; us_start[i]!=nil; i++)
		 { run=us_start[i]->prev->invers->next;
		   j=ende=0;
		   while (!ende)
		     { for (k=0; ls_start[k] != nil; k++) if (ls_start[k]==run) ende=1;
		       if (!ende) { j++; run=run->next->invers->next->invers->next; }
		     }
		   if (j<code[18]) {code[3]=c3; code[11]=c11; return(0);}
                   if (j==code[18]) {j_gleich3 = 1;}         /* TH */
		 }
	       if (gleich) {
		 for (i=0; ls_start[i]!=nil; i++)
		 { run=ls_start[i]->prev->invers->next;
		   j=ende=0;
		   while (!ende)
		     { for (k=0; us_start[k] != nil; k++) if (us_start[k]==run) ende=1;
		       if (!ende) { j++; run=run->next->invers->next->invers->next; }
		     }
		   if (j<code[18]) {code[3]=c3; code[11]=c11; return(0);}
                   if (j==code[18]) {j_gleich4 = 1;}
		 }
               }
               else {j_gleich4 = 1;}      /* TH */
	     } /* ende test2==0 */
	 } /* ende test==0 */

code[3]=c3; code[11]=c11;

/* TH: Auswertung */
returnwert = 1;
if (test==0 && test2==0 && j_gleich1 && j_gleich2) {returnwert=2;}
if (test3==0 && test4==0 && j_gleich3 && j_gleich4) {
  if (returnwert==1) {returnwert=4;} else {returnwert=6;}
}
return(returnwert);

}



/***********************SUCHESTART_REKO********************************/

KANTE *suchestart_reko( KANTE *start, int *fuenfecke)
/* belegt eine sequenz und sucht die kanonische Kante mit dem kleinsten Namen 
   arbeitet "invers", d.h. es wird als Innenrand gesehen, der gefuellt werden
   muss. Wird aufgerufen fuer Brille und Sandwich. Start muss eine Kante sein, die
   ins innere zeigt.
   Funktioniert wie suchestart, nur dass mininame statt name benutzt wird und die
   Anzahl der 5-Ecke auch berechnet wird */

{
int i, j, k, zaehler, position, sqlaenge;
KANTE *run;
int sequenz[7]; 
KANTE *seqkanten[7];
int puffer[7];
char kan[7];



while (start->next->invers->next->invers->next->mininame == aussen) 
                      start=start->next->invers->next->invers->next;
/* Sucht 2 Kanten hintereinander nach aussen -- zu unterscheiden vom namen aussen, was 
   auch nach innen heissen kann. Duerfte nur fuer bauchbinden eine Endlosschleife sein */

for (i=0; i<7; i++) { sequenz[i]=leer; seqkanten[i]=nil; kan[i]=0; }

sqlaenge=0;
position=0;
seqkanten[0]=start;


for (zaehler=1, run=start;
     run->prev->invers->prev->invers->prev->mininame == aussen;
     run=run->prev->invers->prev->invers->prev) zaehler++;
sequenz[0]=zaehler; position=1; seqkanten[1]=nil;
for (run=run->prev->invers->prev->invers->prev->invers->prev; run->mininame != aussen;
     run=run->invers->prev) 
{ sequenz[position]=0; position++; seqkanten[position]=nil; }
/* naechste Kante vor nicht-0-sequenz suchen -- entsprechende innenkanten gibt es nicht
   und muessen sich dementsprechend auch nicht gemerkt werden */


while (run != start)
{
seqkanten[position]=run;
for (zaehler=1; 
     run->prev->invers->prev->invers->prev->mininame == aussen;
     run=run->prev->invers->prev->invers->prev) { zaehler++; }
sequenz[position]=zaehler; position++; seqkanten[position]=nil;
for (run=run->prev->invers->prev->invers->prev->invers->prev; run->mininame != aussen;
     run=run->invers->prev) 
{ sequenz[position]=0; position++; seqkanten[position]=nil; }
}


sequenz[position]=leer; seqkanten[position]=nil;
sqlaenge=position;

*fuenfecke=6-sqlaenge;

kan[0]=sequenz_kanonisch(sequenz);


for (i=0; sequenz[i] != leer; i++)
  { for (j=i, k=0; sequenz[j]!=leer; j++, k++) puffer[k]=sequenz[j];
    for (j=0; j<i; j++, k++) puffer[k]=sequenz[j];
    puffer[k]=leer;
    kan[i]=sequenz_kanonisch(puffer);
  }



for (i=0, run=nil; sequenz[i] != leer; i++)
  { if (kan[i])
      if ((run==nil) || (seqkanten[i]->dummy < run->dummy)) run=seqkanten[i];
      /* dummy ersetzt ursprung */
  }

/* Jetzt die vorige Innenkante suchen, um rechts davon dann einfuegen zu koennen */
for (run=run->next->invers->next->invers->next; run->mininame != aussen; run=run->invers->next);


return(run);

}

/**********************CHECKSIZE_AND_MARK**************************************/

/* bestimmt die groesse der flaeche links von edge -- ist da keine gibt's Probleme 
   ausserdem setzt er fuer alle kanten, so dass diese flaeche links davon ist, dummy
   auf 1*/

int checksize_and_mark( KANTE* edge)
{
KANTE *run; 
int zaehler=1;

edge->noleft=1;
for (run=edge->invers->next; run != edge; run=run->invers->next) {run->noleft=1; zaehler++;}
return(zaehler);
}




/**************************REKO_PATCH*****************************/

void reko_patch(KANTE *anfang,KNOTENTYP code[],int fuenfecke)
{
int i, position, zaehler, z2;
KANTE *run, *merke;


/* wenn bei einer kante hier noleft gesetzt ist, so heisst das, dass
   links davon keine Flaeche mehr ist. Bei den zur Brille gehoerenden Kanten
   ist das teilweise falsch --macht aber nichts */

for (i=0; i<=fuenfecke; i++) code[i]=0;

position=0; run=anfang;
zaehler=1;

while (position<fuenfecke)
  {
    if (checksize_and_mark(run)==5) { code[position]=zaehler; position++; 
					  if (position==fuenfecke) return; }
    zaehler++;
    merke=run->invers; run=run->prev; z2=1;
    while ((merke != run) && (run->noleft) && (z2 <=6))
      { run=run->invers->prev; z2++; }
    if ((merke==run) && (run->noleft)) /* dann muss die letzte flaeche das letzte 5-eck sein */
      { code[position]=zaehler; position++; 
	if (position<fuenfecke)  
		{ fprintf(stderr," ERROR in reko_patch ! Patch empty and missing 5-gon !\n"); exit(32); }
      }
  }
}
    
				    

/**********************BRILLE_REKO*******************************/

/* berechnet den minimalen Code, der sich aus der bei "anfangskante"
   beginnenden Brille ergibt */
/* TH:  Die Funktion wurde so geaendert, dass sie 
   0 zurueckgibt, wenn code > minimaler Code (wie bisher)
   1 zurueckgibt, wenn code < minimaler Code (wie bisher)
   2 zurueckgibt, wenn code== minimaler Code (Automorphismus existiert) */

int brille_reko(PLANMAP map,KNOTENTYP *code,KANTE *anfangskante)
{
int i,j, l1, l2, l3, fuenfecke, vergleichsanfang, test;
KANTE *run, *startkante1, *startkante2, *startkante3, *anfang;
KNOTENTYP testcode[6];


l1=code[2]; l3=code[3]; l2=code[0]-l1-l3;

for (i=1; i<=map[0][0].name; i++) for (j=0;j<3; j++) { map[i][j].dummy=map[i][j].noleft=0;
						       map[i][j].mininame=1; }

/* markieren der Brille: */

anfangskante->mininame=anfangskante->noleft=anfangskante->invers->noleft=1;
anfangskante->invers->mininame=l1;

for (i=1, run=anfangskante; i<code[0]; i++)
  { run=run->invers->prev; 
    run->noleft=run->invers->noleft=1;
    run->mininame=i+1;
    run->dummy=run->prev->dummy=run->next->dummy=i;
    run->invers->mininame=i;
    if (i!=l1) run->prev->mininame=aussen;
    i++;
    if (i<code[0])
      {
      run=run->invers->next;
      run->noleft=run->invers->noleft=1;
      run->dummy=run->prev->dummy=run->next->dummy=i;
      run->mininame=i+1;
      run->invers->mininame=i;
      if (i!=l1) run->next->mininame=aussen;
      }
  }

/*  reparieren: */ run->mininame=l1+l2;

if (l1%2) { startkante1=anfangskante->invers->next; 
	    startkante2=anfangskante->invers->prev->invers->prev; }
   else   { startkante2=anfangskante->invers->next; 
	    startkante1=anfangskante->invers->prev->invers->prev; }

if (code[0]%2) /* d.h. der knoten, bei dem run ist, ist gerade */
  { if (l3%2) startkante3=run->next;
         else startkante3=run->prev->invers->prev; } 
  else 
  { if (l3%2) startkante3=run->prev;
        else  startkante3=run->next->invers->next; }

vergleichsanfang=4;
anfang=suchestart_reko( startkante1, &fuenfecke);
reko_patch(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test>0) return(1);
vergleichsanfang+=fuenfecke;
anfang=suchestart_reko( startkante2, &fuenfecke);
reko_patch(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test>0) return(1);
vergleichsanfang+=fuenfecke;
anfang=suchestart_reko( startkante3, &fuenfecke);
reko_patch(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test==0) return(2);
return(1); 
}

/***********************SUCHESTART_REKO_SP********************************/

KANTE *suchestart_reko_sp( KANTE *start, int *fuenfecke)
/* Wie suchestart_reko -- nur die spiegelversion */

{
int i, j, k, zaehler, position, sqlaenge;
KANTE *run;
int sequenz[7]; 
KANTE *seqkanten[7];
int puffer[7];
char kan[7];



while (start->prev->invers->prev->invers->prev->mininame == aussen) 
                      start=start->prev->invers->prev->invers->prev;
/* Sucht 2 Kanten hintereinander nach aussen -- zu unterscheiden vom namen aussen, was 
   auch nach innen heissen kann. Duerfte nur fuer bauchbinden eine Endlosschleife sein */

for (i=0; i<7; i++) { sequenz[i]=leer; seqkanten[i]=nil; kan[i]=0; }

sqlaenge=0;
position=0;
seqkanten[0]=start;


for (zaehler=1, run=start;
     run->next->invers->next->invers->next->mininame == aussen;
     run=run->next->invers->next->invers->next) zaehler++;
sequenz[0]=zaehler; position=1; seqkanten[1]=nil;
for (run=run->next->invers->next->invers->next->invers->next; run->mininame != aussen;
     run=run->invers->next) 
{ sequenz[position]=0; position++; seqkanten[position]=nil; }
/* naechste Kante vor nicht-0-sequenz suchen -- entsprechende innenkanten gibt es nicht
   und muessen sich dementsprechend auch nicht gemerkt werden */


while (run != start)
{
seqkanten[position]=run;
for (zaehler=1; 
     run->next->invers->next->invers->next->mininame == aussen;
     run=run->next->invers->next->invers->next) { zaehler++; }
sequenz[position]=zaehler; position++; seqkanten[position]=nil;
for (run=run->next->invers->next->invers->next->invers->next; run->mininame != aussen;
     run=run->invers->next) 
{ sequenz[position]=0; position++; seqkanten[position]=nil; }
}


sequenz[position]=leer; seqkanten[position]=nil;
sqlaenge=position;

*fuenfecke=6-sqlaenge;

kan[0]=sequenz_kanonisch(sequenz);


for (i=0; sequenz[i] != leer; i++)
  { for (j=i, k=0; sequenz[j]!=leer; j++, k++) puffer[k]=sequenz[j];
    for (j=0; j<i; j++, k++) puffer[k]=sequenz[j];
    puffer[k]=leer;
    kan[i]=sequenz_kanonisch(puffer);
  }



for (i=0, run=nil; sequenz[i] != leer; i++)
  { if (kan[i])
      if ((run==nil) || (seqkanten[i]->dummy < run->dummy)) run=seqkanten[i];
      /* dummy ersetzt ursprung */
  }

/* Jetzt die vorige Innenkante suchen, um links (spiegel !!) davon dann einfuegen zu koennen */
for (run=run->prev->invers->prev->invers->prev; run->mininame != aussen; run=run->invers->prev);

return(run);

}

/**********************CHECKSIZE_AND_MARK_SP**************************************/

/* bestimmt die groesse der flaeche rechts von edge -- ist da keine gibt's Probleme 
   ausserdem setzt er fuer alle kanten, so dass diese flaeche rechts davon ist, 
   noright auf 1  */

int checksize_and_mark_sp( KANTE* edge)
{
KANTE *run; 
int zaehler=1;

edge->noright=1;
for (run=edge->invers->prev; run != edge; run=run->invers->prev) {run->noright=1; zaehler++;}
return(zaehler);
}




/**************************REKO_PATCH_SP*****************************/

void reko_patch_sp(KANTE *anfang,KNOTENTYP code[],int fuenfecke)
{
int i, position, zaehler, z2;
KANTE *run, *merke;


/* wenn bei einer kante hier noright gesetzt ist, so heisst das, dass
   rechts davon keine Flaeche mehr ist. Bei den zur Brille gehoerenden Kanten
   ist das teilweise falsch --macht aber nichts */

for (i=0; i<=fuenfecke; i++) code[i]=0;

position=0; run=anfang;
zaehler=1;

while (position<fuenfecke)
  { if (checksize_and_mark_sp(run)==5) { code[position]=zaehler; position++;
					     if (position==fuenfecke) return; }
    zaehler++;
    merke=run->invers; run=run->next; z2=1;
    while ((merke != run) && (run->noright) && (z2 <=6))
      { run=run->invers->next; z2++; }
    if ((merke==run) && (run->noright)) /* dann muss die letzte flaeche das letzte 5-eck sein */
      { code[position]=zaehler; position++; 
	if (position<fuenfecke)  
		{ fprintf(stderr," ERROR in reko_patch_sp ! Patch empty and missing 5-gon !\n"); exit(33); }
      }
  }
}
    


/***********************BRILLE_SP_REKO*******************************/

/* berechnet den minimalen Code, der sich aus der bei "anfangskante"
   beginnenden Brille ergibt -- allerdings unter der Voraussetzung,
   dass alles spiegelverkehrt gesehen wird */
/* TH:  Die Funktion wurde so geaendert, dass sie 
   0 zurueckgibt, wenn code > minimaler Code (wie bisher)
   1 zurueckgibt, wenn code < minimaler Code (wie bisher)
   2 zurueckgibt, wenn code== minimaler Code (Automorphismus existiert) */

int brille_sp_reko(PLANMAP map,KNOTENTYP *code,KANTE *anfangskante)
{
int i,j, l1, l2, l3, fuenfecke, vergleichsanfang, test;
KANTE *run, *startkante1, *startkante2, *startkante3, *anfang;
KNOTENTYP testcode[6];



l1=code[2]; l3=code[3]; l2=code[0]-l1-l3;

for (i=1; i<=map[0][0].name; i++) for (j=0;j<3; j++) { map[i][j].dummy=map[i][j].noright=0;
						       map[i][j].mininame=1; }

/* markieren der Brille: */

anfangskante->mininame=anfangskante->noright=anfangskante->invers->noright=1;
anfangskante->invers->mininame=l1;

for (i=1, run=anfangskante; i<code[0]; i++)
  { run=run->invers->next; 
    run->noright=run->invers->noright=1;
    run->mininame=i+1;
    run->dummy=run->prev->dummy=run->next->dummy=i;
    run->invers->mininame=i;
    if (i!=l1) run->next->mininame=aussen;
    i++;
    if (i<code[0])
      {
      run=run->invers->prev;
      run->noright=run->invers->noright=1;
      run->dummy=run->prev->dummy=run->next->dummy=i;
      run->mininame=i+1;
      run->invers->mininame=i;
      if (i!=l1) run->prev->mininame=aussen;
      }
  }

/*  reparieren: */ run->mininame=l1+l2;

if (l1%2) { startkante1=anfangskante->invers->prev; 
	    startkante2=anfangskante->invers->next->invers->next; }
   else   { startkante2=anfangskante->invers->prev; 
	    startkante1=anfangskante->invers->next->invers->next; }

if (code[0]%2) /* d.h. der knoten, bei dem run ist, ist gerade */
  { if (l3%2) startkante3=run->prev;
         else startkante3=run->next->invers->next; } 
  else 
  { if (l3%2) startkante3=run->next;
        else  startkante3=run->prev->invers->prev; }


vergleichsanfang=4;
anfang=suchestart_reko_sp( startkante1, &fuenfecke);
reko_patch_sp(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test>0) return(1);
vergleichsanfang+=fuenfecke;
anfang=suchestart_reko_sp( startkante2, &fuenfecke);
reko_patch_sp(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test>0) return(1);
vergleichsanfang+=fuenfecke;
anfang=suchestart_reko_sp( startkante3, &fuenfecke);
reko_patch_sp(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test==0) return(2);

return(1); 
}



/***********************SANDWICH_REKO*******************************/

/* berechnet den minimalen Code, der sich aus dem bei "anfangskante"
   beginnenden Sandwich ergibt */
/* TH:  Die Funktion wurde so geaendert, dass sie 
   0 zurueckgibt, wenn code > minimaler Code (wie bisher)
   1 zurueckgibt, wenn code < minimaler Code (wie bisher)
   2 zurueckgibt, wenn code== minimaler Code (Automorphismus existiert) */

int sandwich_reko(PLANMAP map,KNOTENTYP *code,KANTE *anfangskante)
{
int i,j, l1, l2, l1_p_l2, fuenfecke, vergleichsanfang, test;
KANTE *run, *startkante1, *startkante2, *startkante3, *anfang;
KNOTENTYP testcode[6];


l1=code[2]; l2=code[3]; 
l1_p_l2 = l1+l2;

for (i=1; i<=map[0][0].name; i++) for (j=0;j<3; j++) { map[i][j].dummy=map[i][j].noleft=0;
						       map[i][j].mininame=1; }

/* markieren der Brille: */

anfangskante->mininame=anfangskante->noleft=anfangskante->invers->noleft=1;
anfangskante->invers->mininame=l1_p_l2;

for (i=1, run=anfangskante; i<code[0]; i++)
  { run=run->invers->prev; 
    run->noleft=run->invers->noleft=1;
    run->mininame=i+1;
    run->dummy=run->prev->dummy=run->next->dummy=i;
    run->invers->mininame=i;
    if (i != l1_p_l2) run->prev->mininame=aussen;
    i++;
    if (i<code[0])
      {
      run=run->invers->next;
      run->noleft=run->invers->noleft=1;
      run->dummy=run->prev->dummy=run->next->dummy=i;
      run->mininame=i+1;
      run->invers->mininame=i;
      if (i != l1_p_l2) run->next->mininame=aussen;
      }
  }

/*  reparieren: */ run->mininame=l1;

/* l1 ist immer >= 3, also geht das folgende: */

if (l1_p_l2%2) { startkante1=anfangskante->invers->next; 
		 startkante3=startkante1->next->invers->prev;
		 if (l2>1) startkante2=anfangskante->prev->invers->next;
		 else /* dann ist l3 > 1 */
		   startkante2=anfangskante->next->invers->prev; }
   else
               { startkante3=anfangskante->invers->next; 
		 startkante1=startkante3->next->invers->prev;
		 if (l2>1) startkante2=anfangskante->next->invers->prev;
		 else /* dann ist l3 > 1 */
		   startkante2=anfangskante->prev->invers->next; }


vergleichsanfang=4;
anfang=suchestart_reko( startkante1, &fuenfecke);
reko_patch(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test>0) return(1);
vergleichsanfang+=fuenfecke;
anfang=suchestart_reko( startkante2, &fuenfecke);
reko_patch(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test>0) return(1);
vergleichsanfang+=fuenfecke;
anfang=suchestart_reko( startkante3, &fuenfecke);
reko_patch(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test==0) return(2);
return(1); 
}


/***********************SANDWICH_REKO_SP*******************************/

/* berechnet den minimalen Code, der sich aus dem bei "anfangskante"
   beginnenden Sandwich ergibt, wenn man es spiegelt */
/* TH:  Die Funktion wurde so geaendert, dass sie 
   0 zurueckgibt, wenn code > minimaler Code (wie bisher)
   1 zurueckgibt, wenn code < minimaler Code (wie bisher)
   2 zurueckgibt, wenn code== minimaler Code (Automorphismus existiert) */

int sandwich_reko_sp(PLANMAP map,KNOTENTYP *code,KANTE *anfangskante)
{
int i,j, l1, l2, l1_p_l2, fuenfecke, vergleichsanfang, test;
KANTE *run, *startkante1, *startkante2, *startkante3, *anfang;
KNOTENTYP testcode[6];


l1=code[2]; l2=code[3]; 
l1_p_l2 = l1+l2;

for (i=1; i<=map[0][0].name; i++) for (j=0;j<3; j++) { map[i][j].dummy=map[i][j].noright=0;
						       map[i][j].mininame=1; }

/* markieren der Brille: */

anfangskante->mininame=anfangskante->noright=anfangskante->invers->noright=1;
anfangskante->invers->mininame=l1_p_l2;

for (i=1, run=anfangskante; i<code[0]; i++)
  { run=run->invers->next; 
    run->noright=run->invers->noright=1;
    run->mininame=i+1;
    run->dummy=run->prev->dummy=run->next->dummy=i;
    run->invers->mininame=i;
    if (i != l1_p_l2) run->next->mininame=aussen;
    i++;
    if (i<code[0])
      {
      run=run->invers->prev;
      run->noright=run->invers->noright=1;
      run->dummy=run->prev->dummy=run->next->dummy=i;
      run->mininame=i+1;
      run->invers->mininame=i;
      if (i != l1_p_l2) run->prev->mininame=aussen;
      }
  }

/*  reparieren: */ run->mininame=l1;

/* l1 ist immer >= 3, also geht das folgende: */

if (l1_p_l2%2) { startkante1=anfangskante->invers->prev; 
		 startkante3=startkante1->prev->invers->next;
		 if (l2>1) startkante2=anfangskante->next->invers->prev;
		 else /* dann ist l3 > 1 */
		   startkante2=anfangskante->prev->invers->next; }
   else
               { startkante3=anfangskante->invers->prev; 
		 startkante1=startkante3->prev->invers->next;
		 if (l2>1) startkante2=anfangskante->prev->invers->next;
		 else /* dann ist l3 > 1 */
		   startkante2=anfangskante->next->invers->prev; }


vergleichsanfang=4;
anfang=suchestart_reko_sp( startkante1, &fuenfecke);
reko_patch_sp(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test>0) return(1);
vergleichsanfang+=fuenfecke;
anfang=suchestart_reko_sp( startkante2, &fuenfecke);
reko_patch_sp(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test>0) return(1);
vergleichsanfang+=fuenfecke;
anfang=suchestart_reko_sp( startkante3, &fuenfecke);
reko_patch_sp(anfang,testcode,fuenfecke);
if ((test=codecmp_kn(testcode,code+vergleichsanfang,fuenfecke))<0) return(0);
if (test==0) return(2);

return(1); 
}



/*********************bilde_f*****TH***********************************/

/* Die Funktion bilde_f bildet den kompletten Automorphismus f, der
   die Kante k1 in die Kante k2 ueberfuehrt. Dabei muss der Automorphismus
   ordnungserhaltend sein, es muss sich also um eine Drehung handeln.
   Das Fulleren, auf dem der Automorphismus berechnet wird, besitzt anz
   Ecken.  Es wird ein einfacher Backtrackingalgorithmus verwendet.
   Bei der Anwendung dieser Funktion ist nicht der gesamte Automorphismus
   interessant, sondern nur eine Auswahl von Ecken, deren Bilder errechnet
   werden sollen. Versuche, durch eine geschickte Auswahl der Ecken, 
   deren Bildpunkte errechnet werden, eine Laufzeitverbesserung zu erhalten,
   schlagen fehl. */	      

/* Die folgende Prozedur enthaelt den Rekursionsschritt */

void bilde_f_rek(KNOTENTYP *f, KANTE *k1, KANTE *k2) {
  KNOTENTYP u;
  k1 = k1->invers->prev;
  k2 = k2->invers->prev;   /* k1 und k2 im Gleichschritt nach rechts */
  u = k1->name;            /* von u wird der Funktionswert f[u] berechnet */
  if (!(f[u])) {          /* Funktionswert noch nicht bekannt */
    f[u] = k2->name;
    bilde_f_rek(f,k1,k2);  /* von u ausgehend weitere Funktionswerte ermitteln */
  }
  k1 = k1->prev;           /* k1 und k2 im Gleichschritt nach links */
  k2 = k2->prev;           /* denn: (k->invers->prev)->prev = k->invers->next */
  u = k1->name;
  if (!(f[u])) {
    f[u] = k2->name;
    bilde_f_rek(f,k1,k2);
  }
}

/* Die folgende Prozedur enthaelt den Rekursionsanfang */

void bilde_f(KNOTENTYP *f, KANTE *k1, KANTE *k2, KNOTENTYP anz) {
  KNOTENTYP i;
  for (i=1; i<=anz; i++) {f[i] = 0;}   /* Funktionstabelle loeschen */
  f[k1->ursprung] = k2->ursprung;
  f[k1->name]     = k2->name;           /* k1 wird auf k2 abgebildet */  
  bilde_f_rek(f,k1,k2);
}

/*********************bilde_f_sp*****TH***********************************/

/* Die Funktion bilde_f_sp bildet den kompletten Automorphismus f, der
   die Kante k1 in die Kante k2 ueberfuehrt. Dabei darf der Automorphismus
   NICHT ordnungserhaltend sein, es muss sich also um eine Spiegelung oder
   Drehspiegelung handeln. Dies ist der einzige Unterschied zu bilde_f. */	      

/* Die folgende Prozedur enthaelt den Rekursionsschritt */

void bilde_f_sp_rek(KNOTENTYP *f, KANTE *k1, KANTE *k2) {
  KNOTENTYP u;
  k1 = k1->invers->prev;
  k2 = k2->invers->next;   /* k1 und k2 spiegelverkehrt nach rechts und links */
  u = k1->name;            /* von u wird der Funktionswert f[u] berechnet */
  if (!(f[u])) {           /* Funktionswert noch nicht bekannt */
    f[u] = k2->name;
    bilde_f_sp_rek(f,k1,k2);  /* von u ausgehend weitere Funktionswerte ermitteln */
  }
  k1 = k1->prev;           /* k1 und k2 spiegelverkehrt nach links und rechts */
  k2 = k2->next;           /* denn: (k->invers->next)->next = k->invers->prev */
  u = k1->name;
  if (!(f[u])) {
    f[u] = k2->name;
    bilde_f_sp_rek(f,k1,k2);
  }
}

/* Die folgende Prozedur enthaelt den Rekursionsanfang */

void bilde_f_sp(KNOTENTYP *f, KANTE *k1, KANTE *k2, KNOTENTYP anz) {
  KNOTENTYP i;
  for (i=1; i<=anz; i++) {f[i] = 0;}   /* Funktionstabelle loeschen */
  f[k1->ursprung] = k2->ursprung;
  f[k1->name]     = k2->name;           /* k1 wird auf k2 abgebildet */  
  bilde_f_sp_rek(f,k1,k2);
}


/*********************bilde_f_und_g_sp*****TH***********************************/

/* Die Funktion bilde_f_und_g_sp bildet die komplette Funktion f, die die Kante
   k1 in die Kante k2 ueberfuehrt, und simultan die Funktion g, die die Kante
   k2 in die Kante k1 ueberfuehrt. Beide Funktionen sind NICHT ordnungserhaltend.
   Die Funktion prueft, ob g die Umkehrfunktion von f ist. Ist sie es, so liefert
   bild_f_und_g_sp den Wert 1, andernfalls den Wert 0. 
   Das Fulleren, auf dem die Funktion berechnet wird, besitzt anz Ecken.                                                                  
   Die Inhalte des Arrays g, die in der vorliegenden Funktion berechnet werden,
   werden in der uebergeordneten Prozedur minitest nicht gebraucht. Deshalb waere es
   eigentlich nicht notwendig, einen Zeiger auf dieses Array zu uebergeben. Es wuerde
   ausreichen, das Array innerhalb der Funktion bilde_f_und_g_sp lokal zu definieren.
   Da die Funktion aber haeufig aufgerufen wird, wuerde dies viel Zeit in Anspruch
   nehmen.   */	      

/* Die folgende Prozedur enthaelt den Rekursionsschritt */

BOOL bilde_f_und_g_sp_rek(KNOTENTYP *f, KNOTENTYP *g, KANTE *k1, KANTE *k2) {
  KNOTENTYP u,v;
  k1 = k1->invers->prev;
  k2 = k2->invers->next;   /* k1 und k2 spiegelverkehrt nach rechts und links */
  u = k1->name;            /* von u wird der Funktionswert f[u] berechnet */
  v = k2->name;
  if (!(f[u])) {          /* Funktionswert noch nicht bekannt */
    f[u] = v;
    if (g[v]) {return(0);}    /* Widerspruch gefunden */
    g[v] = u;
    if (!bilde_f_und_g_sp_rek(f,g,k1,k2))  {return(0);}  /* weitere Funktionswerte: Widerspruch? */
  }
  else { 
    if (!(g[v])) {return(0);}     /* Widerspruch gefunden. Diese Abfrage koennte aber auch
                                      entfallen, denn wenn ein Wert von g noch nicht festgelegt
        ist, obwohl der zugehoerige Wert von f bereits feststeht, so wird an anderer Stelle ein
        Wert von g zuviel festgelegt sein, obwohl der zugehoerige Wert von f noch nicht feststeht */
  }
  k1 = k1->prev;           /* k1 und k2 spiegelverkehrt nach links und rechts */
  k2 = k2->next;           /* denn: (k->invers->next)->next = k->invers->prev */
  u = k1->name;
  v = k2->name;
  if (!(f[u])) {
    f[u] = v;
    if (g[v]) {return(0);}
    g[v] = u;
    if (!bilde_f_und_g_sp_rek(f,g,k1,k2))  {return(0);}
  }
  else {
    if (!(g[v])) {return(0);}
  }
  return(1);       /* keinen Widerspruch festgestellt */
}

/* Die folgende Prozedur enthaelt den Rekursionsanfang */

BOOL bilde_f_und_g_sp(KNOTENTYP *f, KNOTENTYP *g, KANTE *k1, KANTE *k2, KNOTENTYP anz) {
  KNOTENTYP i;
  for (i=1; i<=anz; i++) {f[i]=0; g[i]=0;}   /* Funktionstabellen loeschen */
  f[k1->ursprung] = k2->ursprung;
  f[k1->name]     = k2->name;           /* f: k1 wird auf k2 abgebildet */  
  g[k2->ursprung] = k1->ursprung;
  g[k2->name]     = k1->name;           /* g: k2 wird auf k1 abgebildet */
  return(bilde_f_und_g_sp_rek(f,g,k1,k2));
}

/*********************bilde_f_und_g********TH***********************************/

/* Die Funktion bilde_f_und_g  bildet die komplette Funktion f, die die Kante
   k1 in die Kante k2 ueberfuehrt, und simultan die Funktion g, die die Kante
   k2 in die Kante k1 ueberfuehrt. Beide Funktionen sind ordnungserhaltend.
   Die Funktion prueft, ob g die Umkehrfunktion von f ist. Ist sie es, so liefert
   bild_f_und_g den Wert 1, andernfalls den Wert 0. 
   Weitere Anmerkungen siehe bilde_f_und_g_sp. */      

/* Die folgende Prozedur enthaelt den Rekursionsschritt */

BOOL bilde_f_und_g_rek(KNOTENTYP *f, KNOTENTYP *g, KANTE *k1, KANTE *k2) {
  KNOTENTYP u,v;
  k1 = k1->invers->prev;
  k2 = k2->invers->prev;   /* k1 und k2 im Gleichschritt nach rechts und links */
  u = k1->name;            /* von u wird der Funktionswert f[u] berechnet */
  v = k2->name;
  if (!(f[u])) {          /* Funktionswert noch nicht bekannt */
    f[u] = v;
    if (g[v]) {return(0);}    /* Widerspruch gefunden */
    g[v] = u;
    if (!bilde_f_und_g_rek(f,g,k1,k2))  {return(0);}  /* weitere Funktionswerte: Widerspruch? */
  }
  else { 
    if (!(g[v])) {return(0);}     /* Widerspruch gefunden. Diese Abfrage koennte aber auch
                                      entfallen, denn wenn ein Wert von g noch nicht festgelegt
        ist, obwohl der zugehoerige Wert von f bereits feststeht, so wird an anderer Stelle ein
        Wert von g zuviel festgelegt sein, obwohl der zugehoerige Wert von f noch nicht feststeht */
  }
  k1 = k1->prev;           /* k1 und k2 spiegelverkehrt nach links und rechts */
  k2 = k2->prev;           /* denn: (k->invers->prev)->prev = k->invers->next */
  u = k1->name;
  v = k2->name;
  if (!(f[u])) {
    f[u] = v;
    if (g[v]) {return(0);}
    g[v] = u;
    if (!bilde_f_und_g_rek(f,g,k1,k2))  {return(0);}
  }
  else {
    if (!(g[v])) {return(0);}
  }
  return(1);       /* keinen Widerspruch festgestellt */
}

/* Die folgende Prozedur enthaelt den Rekursionsanfang */

BOOL bilde_f_und_g(KNOTENTYP *f, KNOTENTYP *g, KANTE *k1, KANTE *k2, KNOTENTYP anz) {
  KNOTENTYP i;
  for (i=1; i<=anz; i++) {f[i]=0; g[i]=0;}   /* Funktionstabellen loeschen */
  f[k1->ursprung] = k2->ursprung;
  f[k1->name]     = k2->name;           /* f: k1 wird auf k2 abgebildet */  
  g[k2->ursprung] = k1->ursprung;
  g[k2->name]     = k1->name;           /* g: k2 wird auf k1 abgebildet */
  return(bilde_f_und_g_rek(f,g,k1,k2));
}


/************************MINITEST***********TH***************************/

int minitest(PLANMAP map, KNOTENTYP *code)

/* WICHTIG: Bei der bauchbinde muss auch ueberprueft werden, ob sie wirklich
   minimal gebaut ist. Moeglich: Verdrehen und hinterher ist das Spiegelbild
   mit der gleichen Binde kleiner verklebt. (Beispiele schon mit 32 Knoten) 

   Hier werden nur Pfade betrachtet, an denen mindestens ein 5-Eck liegt.  

   Zu einer 5-Eck-Kante gehoert der Pfad, der entsteht, wenn man zur vorigen
   Kante (prev) geht und dann wechselnd weiter, bis es nicht mehr geht (d.h. man
   muesste eine bereits benutzte Kante nochmal benutzen). (Eigentlich gehoert er zu 
   dem Winkel aud dieser und der vorigen Kante des 5-Ecks.) Dann geht man in die andere
   Richtung weiter, bis es nicht mehr geht. Aber auch in der anderen Reihenfolge 
   muss der Pfad konstruiert werden, da die Orientierung schon durch andere
   Festlegungen bestimmt wurde.

   Akzeptiert werden nur Graphen, bei denen der Weg zu einem 5-Eck korrespondiert,
   d.h. aus einer 5-Eck-Kante konstruiert werden kann (im normal ODER im
   Spiegel-modus). Jeder Graph hat so einen Weg. Fuer die Minimalitaet werden 
   auch nur solche Pfade betrachtet. Das ist etwas anderes, als dass nur ein 5-Eck 
   am Weg liegt. (BSP: Sandwich mit 5-Eck am Stueck l2.)


   Obwohl viele Pfade sowohl in normalem, als auch im Mirror-Modus konstruiert
   werden koennen, gibt es auch Pfade, die nur in einem Modus konstruiert
   werden koennen.


              /<
        Kante/  \
            /    \
           <      --------------> dazugehoerige erste Richtung


    Anmerkung: Wenn eine 5-Eck-Kante zu einem Endpunkt des Pfades fuehrt, so hat dasselbe
    Fuenfeck auch einen Winkel mit dem Pfad gemeinsam (sonst haette man eine Bauchbinde).

*/


{
int i, j, ii, m_laenge, ms_laenge, knoten_auf_pfad;
int l1, l2, l3, ll1, ll2, ll3, edgemark, middle, lower_border;
KANTE *miniliste[120], *mini_spiegel[120];
KANTE  *run, *start, *merke_1, *merke_2;
long mark[N+1];
int zaehler, stelle_1, stelle_2, pfadlaenge;
KNOTENTYP cpcode[20];
int test, runzaehler;
BOOL rekonstruiert;
int minierg[120];          /* fuer Bauchbinden */

rekonstruiert=0;
if (code[1]==1) knoten_auf_pfad=code[0]; else knoten_auf_pfad=code[0]-1;
/* die knoten auf dem Pfad sind immer mit 1..k_a_p nummeriert */


test=1;
m_laenge=ms_laenge=0;

for (i=1; i<=map[0][0].name; i++) { mark[i]=0;
				    for(j=0;j<3;j++) 
				      { run=map[i]+j;
					run->dummy=run->mininame=0;
				      }
				  }


l1=code[2];
    if (code[1]==2) { l3=code[3]; l2=code[0]-l1-l3; }
    else { l2=code[3]; l3=code[0]-l1-l2; }

if (code[1]==1) { rekonstruiert=1; /* Bei bauchbinden ist das immer der Fall */
		  for (i=0; (i<60); i++) 
                         { run=F_eck_kanten[i];
			   run->nostart=run->mirror_nostart=0; } 
		}
else if (code[1]==2) /* muss irgendwo am Pfad liegen */
  { for (i=0; (i<60) && !rekonstruiert; i++) 
                         { run=F_eck_kanten[i];
			   if (run->ursprung <= knoten_auf_pfad) rekonstruiert=1;
			   run->nostart=run->mirror_nostart=0; }
    for (; i<60 ; i++)   { run=F_eck_kanten[i];
			   run->nostart=run->mirror_nostart=0; }
  }
else /* d.h. code[1]==3 -- also sandwich */
  { for (i=0; (i<60) && !rekonstruiert; i++) 
                         { run=F_eck_kanten[i];
			   if (run->ursprung <= knoten_auf_pfad) 
			     {
			       if (run->prev->name==run->ursprung-1)
				 {
				  if ((run->ursprung <=l1) || (run->ursprung >= l1+l2)) rekonstruiert=1;
			          else { if (run->prev->name==l1)
					   { if ((l2+l3) % 2) rekonstruiert=1; }
					 else
					   if (run->name==l1+l2)
					     { if ((l1+l2) % 2) rekonstruiert=1; }
				       }
				 } /* ende "die beiden kanten liegen in laufrichtung */
			       else 
				 if (run->prev->name==run->ursprung+1) /* d.h. entgegen der Laufrichtung */
				 { if ((run->ursprung <=l1) || (run->ursprung >= l1+l2)) rekonstruiert=1;
			          else { if (run->prev->name==l1+l2)
					   { if ((l1+l2) % 2) rekonstruiert=1; }
					 else
					   if (run->name==l1)
					     { if ((l2+l3) % 2) rekonstruiert=1; }
				       }
				 } /* ende "die beiden kanten liegen entgegen der laufrichtung */
			     } /* ende if auf pfad */
			   run->nostart=run->mirror_nostart=0; } /* ende for */
    for (; i<60 ; i++)   { run=F_eck_kanten[i];
			   run->nostart=run->mirror_nostart=0; }
  } /* ende sandwich */


if (!rekonstruiert) { return(0); }


/* Jetzt die Kanten markieren, bei denen man den Originalpfad rekonstruieren wuerde,
   dabei werden 6-Eck-Kanten einfach mitmarkiert */
if (code[1]!=1)
  { 
    /* Von stelle_1 bis ende kann in Richtung auf 1 rekonstruiert werden. Von 1 bis stelle_2 kann in Richtung
       aufs ende rekonstruiert werden. Die stellen geben die position des valenz 2 knotens in dem
       winkel an. Beachten: bei "invers" ist der valenz-2-knoten immer um eins groesser ? */


    if (code[1]==2) { if (l1%2) stelle_1=l1-1; else stelle_1=l1;
		      if (l3%2) stelle_2=l1+l2+1; else stelle_2=l1+l2; }
    else /* d.h. sandwich */
                    { if ((l1+l2)%2) stelle_1=l1+l2-1; else stelle_1=l1+l2;
		      if ((l2+l3)%2) stelle_2=l1+1; else stelle_2=l1; }

    map[1][0].nostart=1;
    for (run=map[1][2].invers->next, zaehler=2; zaehler < code[0]; zaehler+=2)
      { if (zaehler<=stelle_2) { run->mirror_nostart=1;
				if (zaehler<stelle_2) run->invers->nostart=1; }
	if (zaehler>=stelle_1-1) 
	                      { if (zaehler>=stelle_1) run->nostart=1;
				if (zaehler<knoten_auf_pfad) run->invers->mirror_nostart=1; }
	run=run->invers->prev->invers->next;
      }

    /* Da jetzt aber die letzte Kante nicht als Startkante markiert werden kann, da dieser Pfad ja nicht
       mehr konstruiert wird, muss das nachgeholt werden: */
    if (l1==l3)
      { if (knoten_auf_pfad % 2) { mini_spiegel[0]=map[knoten_auf_pfad][2].invers; ms_laenge=1; }
	else { miniliste[0]=map[knoten_auf_pfad][1].invers; m_laenge=1; }
      }
  }


/* Jetzt ans konstruieren: */

edgemark=1;

for (i=0; i<60; i++) /* for ueber alle kanten, von denen links ein 5-Eck ist */
  { 
    start=F_eck_kanten[i];
    
    if (! start->nostart)
      { 
	middle= 2*N*edgemark;
	lower_border=middle-N;

	mark[start->ursprung]=middle;
	runzaehler=middle-1;

	start->dummy=start->invers->dummy=edgemark;
	run=start->prev;
	run->dummy=run->invers->dummy=edgemark;
	run=run->invers->next;
	pfadlaenge=2;

	/* nach rechts laufen: */
	while (run->dummy < edgemark) /* neue kante */
	  { mark[run->ursprung]=runzaehler; runzaehler--;
	    pfadlaenge++;
	    run->dummy=run->invers->dummy=edgemark;
	    merke_1=run; /* letzte neue kante */
	    run=run->invers->prev;
	    if (run->dummy < edgemark)
	      { mark[run->ursprung]=runzaehler; runzaehler--; 
		pfadlaenge++;
		run->dummy=run->invers->dummy=edgemark;
		merke_1=run;
		run=run->invers->next; }
	  }

	/* nach links laufen: */

	run=start->invers->prev;
	runzaehler=middle+1;
	if (mark[run->ursprung]<lower_border) mark[run->ursprung]=runzaehler;
	                                      /* kann (z.b. bei bauchbinde) vor der schleife noetig
						 sein */
	merke_2=start;
	while (run->dummy < edgemark) /* neue kante */
	  { mark[run->ursprung]=runzaehler; runzaehler++; 
	    pfadlaenge++;
	    run->dummy=run->invers->dummy=edgemark;
	    merke_2=run; /* letzte neue kante */
	    run=run->invers->next;
	    if (run->dummy < edgemark)
	      { mark[run->ursprung]=runzaehler; runzaehler++; 
		pfadlaenge++;
		run->dummy=run->invers->dummy=edgemark;
		merke_2=run;
		run=run->invers->prev; }
	  }
	
         /* Jetzt auswerten, was fuer ein pfad gebaut wurde */

	if (pfadlaenge<code[0]) return(0);
        cpcode[0]=pfadlaenge;
	if (merke_1==merke_2->invers->prev->invers) cpcode[1]=1;
	else if (mark[merke_1->name]<mark[merke_2->name]) cpcode[1]=2;
	else cpcode[1]=3;


	/* zuerst zum markieren der in zukunft nicht mehr zu testenden Kanten (Winkel): */
	switch(cpcode[1])
	  {
	  case 1: { 
	            for (j=0, run=start; j<pfadlaenge; j+=2)
		      { run->nostart=run->mirror_nostart=1;
			run=run->invers;
			run->nostart=run->mirror_nostart=1;
			run=run->prev->invers->next; }
		    break;
		  }
	  case 2: { ll1=mark[merke_1->name]-mark[merke_1->ursprung]+1;
		    ll3=mark[merke_2->ursprung]-mark[merke_2->name]+1; 
		    if (ll1 >= ll3) { cpcode[2]=ll1; cpcode[3]=ll3; }
		      else { cpcode[2]=ll3; cpcode[3]=ll1; }
		    if (ll1%2) stelle_1=mark[merke_1->name]-1; else stelle_1=mark[merke_1->name];
		    if (ll3%2) stelle_2=mark[merke_2->name]+1; else stelle_2=mark[merke_2->name];
		    break; }
	  case 3: { ll1=mark[merke_2->name]-mark[merke_1->ursprung]+1;
		    ll3=mark[merke_2->ursprung]-mark[merke_1->name]+1; 
		    ll2=pfadlaenge-ll1-ll3;
		    if (ll1>=ll3) { cpcode[2]=ll1; cpcode[3]=ll2; }
		       else { cpcode[2]=ll3; cpcode[3]=ll2; }
                    if ((ll1+ll2)%2) stelle_1=mark[merke_1->name]-1; else stelle_1=mark[merke_1->name];
		    if ((ll2+ll3)%2) stelle_2=mark[merke_2->name]+1; else stelle_2=mark[merke_2->name];
		    break; }
	  default: { fprintf(stderr,"Dangerous error in switch (minitest) !\n"); exit(34); }
	  } /* ende switch */


if (cpcode[1]==1) { if ((test=codecmp_kn(code,cpcode,2))>0) return(0); }
      else { if ((test=codecmp_kn(code,cpcode,4))>0) return(0); }


if (code[1]!=1) /* fuer bauchbinden wurde in switch schon markiert */
  { 
    /* Von stelle_1 bis ende kann in Richtung auf den Anfang rekonstruiert werden. Von 1 bis stelle_2 kann 
       in Richtung aufs ende rekonstruiert werden */

    if (mark[merke_1->ursprung]%2)
      { merke_1->nostart=1;
	for (run=merke_1->prev->invers->next, zaehler=mark[merke_1->ursprung]+1; 
	                              zaehler <= mark[merke_2->ursprung]; zaehler+=2)
	  { if (zaehler<=stelle_2) { run->mirror_nostart=1;
				    if (zaehler<stelle_2) run->invers->nostart=1; }
	    if (zaehler>=stelle_1-1) { if (zaehler>=stelle_1) run->nostart=1;
				      if (zaehler<mark[merke_2->ursprung]) run->invers->mirror_nostart=1; }
	    run=run->invers->prev->invers->next;
	  }
      }
    else /* d.h. mark[merke_1->ursprung] gerade */
      {
	for (run=merke_1->next, zaehler=mark[merke_1->ursprung]; 
	                              zaehler <= mark[merke_2->ursprung]; zaehler+=2)
	  { if (zaehler<=stelle_2) { run->mirror_nostart=1;
				    if (zaehler<stelle_2) run->invers->nostart=1; }
	    if (zaehler>=stelle_1-1) { if (zaehler>=stelle_1) run->nostart=1;
				      if (zaehler<mark[merke_2->ursprung]) run->invers->mirror_nostart=1; }
	    run=run->invers->prev->invers->next;
	  }
      }
  } /* ende code[1] != 1 und damit ende des markierens */ 

	/* jetzt eventuell neue Kanten in die Listen: */
	if (test==0)
          {
	  if (code[1]==1) { miniliste[m_laenge]=start; m_laenge++; }
	     else { if (ll1>=ll3)
		      { if (mark[merke_1->ursprung]%2)
			  { miniliste[m_laenge]=merke_1->invers; m_laenge++; }
		      else
			{ mini_spiegel[ms_laenge]=merke_1->invers; ms_laenge++; }
		      }
		    if (ll3>=ll1)
		      { if (mark[merke_2->ursprung]%2)
			  { mini_spiegel[ms_laenge]=merke_2->invers; ms_laenge++; }
		      else
			{ miniliste[m_laenge]=merke_2->invers; m_laenge++; }
		      }
		  } /* ende else */
	  }
        edgemark++;
      } /* ende if (!start->nostart) */



/* nun in die andere Richtung zuerst */


    if (! start->mirror_nostart)
      { 

	middle= 2*N*edgemark;
	lower_border=middle-N;

	mark[start->ursprung]=middle;
	runzaehler=middle-1;

	start->dummy=start->invers->dummy=edgemark;
	run=start->prev;
	run->dummy=run->invers->dummy=edgemark;
	pfadlaenge=2;

	/* nach links laufen: */
	run=start->invers->prev;
	while (run->dummy < edgemark) /* neue kante */
	  { mark[run->ursprung]=runzaehler; runzaehler--; 
	    pfadlaenge++;
	    run->dummy=run->invers->dummy=edgemark;
	    merke_1=run; /* letzte neue kante */
	    run=run->invers->next;
	    if (run->dummy < edgemark)
	      { mark[run->ursprung]=runzaehler; runzaehler--; 
		pfadlaenge++;
		run->dummy=run->invers->dummy=edgemark;
		merke_1=run;
		run=run->invers->prev; }
	  }

	/* nach rechts laufen: */

	run=start->prev->invers->next;
	runzaehler=middle+1;
	if (mark[run->ursprung]<lower_border) mark[run->ursprung]=runzaehler;
	                                      /* kann (z.b. bei bauchbinde) vor der schleife noetig
						 sein */
	merke_2=start->prev;
	while (run->dummy < edgemark) /* neue kante */
	  { mark[run->ursprung]=runzaehler; runzaehler++; 
	    pfadlaenge++;
	    run->dummy=run->invers->dummy=edgemark;
	    merke_2=run; /* letzte neue kante */
	    run=run->invers->prev;
	    if (run->dummy < edgemark)
	      { mark[run->ursprung]=runzaehler; runzaehler++;
		pfadlaenge++;
		run->dummy=run->invers->dummy=edgemark;
		merke_2=run;
		run=run->invers->next; }
	  }
	
         /* Jetzt auswerten, was fuer ein pfad gebaut wurde */

	if (pfadlaenge<code[0]) return(0);
        cpcode[0]=pfadlaenge;
	if (merke_1==merke_2->invers->next->invers) cpcode[1]=1;
	else if (mark[merke_1->name]<mark[merke_2->name]) cpcode[1]=2;
	else cpcode[1]=3;

	/* zuerst zum markieren der in zukunft nicht mehr zu testenden Kanten (Winkel): */
	switch(cpcode[1])
	  {
	  case 1: { fprintf(stderr,"ERROR: BAUCHBINDEN should not be possible in mirror modus \n");
		    exit(35);
		    break;
		  }
	  case 2: { ll1=mark[merke_1->name]-mark[merke_1->ursprung]+1;
		    ll3=mark[merke_2->ursprung]-mark[merke_2->name]+1; 
		    if (ll1 >= ll3) { cpcode[2]=ll1; cpcode[3]=ll3; }
		      else { cpcode[2]=ll3; cpcode[3]=ll1; }
		    if (ll1%2) stelle_1=mark[merke_1->name]-1; else stelle_1=mark[merke_1->name];
		    if (ll3%2) stelle_2=mark[merke_2->name]+1; else stelle_2=mark[merke_2->name];
		    break; }
	  case 3: { ll1=mark[merke_2->name]-mark[merke_1->ursprung]+1;
		    ll3=mark[merke_2->ursprung]-mark[merke_1->name]+1; 
		    ll2=pfadlaenge-ll1-ll3;
		    if (ll1>=ll3) { cpcode[2]=ll1; cpcode[3]=ll2; }
		       else { cpcode[2]=ll3; cpcode[3]=ll2; }
                    if ((ll1+ll2)%2) stelle_1=mark[merke_1->name]-1; else stelle_1=mark[merke_1->name];
		    if ((ll2+ll3)%2) stelle_2=mark[merke_2->name]+1; else stelle_2=mark[merke_2->name];
		    break; }
	  default: { fprintf(stderr,"Dangerous error in switch (minitest mirror) !\n"); exit(36); }
	  } /* ende switch */

	if ((test=codecmp_kn(code,cpcode,4))>0) return(0); 


    /* Von stelle_1 bis ende kann in Richtung auf den Anfang rekonstruiert werden. Von 1 bis stelle_2 kann 
       in Richtung aufs ende rekonstruiert werden */

    if ((mark[merke_1->ursprung]%2)==0) /* umgekehrter laufsinn als bei der anderen entwicklungsrichtung */
      { merke_1->nostart=1;
	for (run=merke_1->prev->invers->next, zaehler=mark[merke_1->ursprung]+1; 
	                              zaehler <= mark[merke_2->ursprung]; zaehler+=2)
	  { if (zaehler<=stelle_2) { run->mirror_nostart=1;
				    if (zaehler<stelle_2) run->invers->nostart=1; }
	    if (zaehler>=stelle_1-1) { if (zaehler>=stelle_1) run->nostart=1;
				      if (zaehler<mark[merke_2->ursprung]) run->invers->mirror_nostart=1; }
	    run=run->invers->prev->invers->next;
	  }
      }
    else /* d.h. mark[merke_1->ursprung] ungerade */
      {
	for (run=merke_1->next, zaehler=mark[merke_1->ursprung]; 
	                              zaehler <= mark[merke_2->ursprung]; zaehler+=2)
	  { if (zaehler<=stelle_2) { run->mirror_nostart=1;
				    if (zaehler<stelle_2) run->invers->nostart=1; }
	    if (zaehler>=stelle_1-1) { if (zaehler>=stelle_1) run->nostart=1;
				      if (zaehler<mark[merke_2->ursprung]) run->invers->mirror_nostart=1; }
	    run=run->invers->prev->invers->next;
	  }
      }
   /* ende des markierens */ 

	/* jetzt eventuell neue Kanten in die Listen: */
	if (test==0)
	  { if (ll1>=ll3) /* jeweils vertauscht zum nicht-mirror-fall */
		      { if (mark[merke_1->ursprung]%2)
			  { mini_spiegel[ms_laenge]=merke_1->invers; ms_laenge++; }
		      else
			  { miniliste[m_laenge]=merke_1->invers; m_laenge++; }
		      }
		    if (ll3>=ll1)
		      { if (mark[merke_2->ursprung]%2)
			{ miniliste[m_laenge]=merke_2->invers; m_laenge++; }
		      else
			{ mini_spiegel[ms_laenge]=merke_2->invers; ms_laenge++; }
		      }
	    } /* ende test==0 */
        edgemark++;
      } /* ende if (!start->mirror_nostart) */

  } /* ende for ueber alle 5-Eck-Kanten */



/* TH:  ab hier ist alles massiv veraendert */
/* Nun wird geprueft, ob der uebergebene Code der kleinstmoegliche ist. */

if (code[1]==1) /* Bauchbinde */
  { i=0;
    while (i<m_laenge)
      { if ((test = bauchbinde_reko(map,code,miniliste[i]))==0) return(0);
        if (test==1) {miniliste[i] = miniliste[m_laenge-1];  m_laenge--;}
        else         {minierg[i] = test;  i++;}
      }
    i=0;
    while (i<m_laenge && minierg[i]==4) {i++;}
    if (i==m_laenge) {fprintf(stderr,"Es fehlt Originalbauchbinde!\n"); exit(37);}
    test = minierg[0];    minierg[0] = minierg[i];      minierg[i] = test;
    run  = miniliste[0];  miniliste[0] = miniliste[i];  miniliste[i] = run;        
    /* Nun befindet sich im ersten Listeneintrag ein Pfad, der durch Drehung des
       Originals zustande kommt oder selbst das Original ist. Es gilt dann fuer den
       Wert von minierg[i]:
       2 = es gibt eine Drehung zwischen Bauchbinde 0 (erster Listeneintrag) und Bauchbinde i
       4 = es gibt eine Spiegelung/Drehspiegelung zwischen Bauchbinde 0 und Bcc Thauchbinde i
       6 = es gibt eine Drehung und eine Spiegelung zwischen Bauchbinde 0 und Bauchbinde i */
  }
else {

  /* Es koennen doppelte Eintraege in der miniliste vorkommen. Diese werden geloescht. */
  for (i=0; i<m_laenge-1; i++) {
    ii=i+1;
    while (ii<m_laenge) {
      if (miniliste[i]==miniliste[ii]) {miniliste[ii] = miniliste[m_laenge-1];  m_laenge--;}
      else {ii++;}
    }
  }
  for (i=0; i<ms_laenge-1; i++) {
    ii=i+1;
    while (ii<ms_laenge) {
      if (mini_spiegel[i]==mini_spiegel[ii]) {mini_spiegel[ii] = mini_spiegel[ms_laenge-1];  ms_laenge--;}
      else {ii++;}
    }
  }

  if (code[1]==2) /* Brille */
     { i=0;
       while (i<m_laenge) {
	 if ((test = brille_reko(map,code,miniliste[i]))==0) return(0);
         if (test==1) {miniliste[i]=miniliste[m_laenge-1];  m_laenge--;}
         else         {i++;}
       }
       i=0;
       while (i<ms_laenge) {
	 if ((test = brille_sp_reko(map,code,mini_spiegel[i]))==0) return(0);
         if (test==1) {mini_spiegel[i]=mini_spiegel[ms_laenge-1];  ms_laenge--;}
         else         {i++;}
       } 
     }   /* if */
  else /* d.h. (code[1]==3) d.h. Sandwich */
     { i=0;
       while (i<m_laenge) {
         if ((test = sandwich_reko(map,code,miniliste[i]))==0) return(0);
         if (test==1) {miniliste[i]=miniliste[m_laenge-1];  m_laenge--;}
         else         {i++;}
       }
       i=0;
       while (i<ms_laenge) {
         if ((test = sandwich_reko_sp(map,code,mini_spiegel[i]))==0) return(0); 
         if (test==1) {mini_spiegel[i]=mini_spiegel[ms_laenge-1];  ms_laenge--;}
         else         {i++;}
       }
     }  /* else */
}       /* else */


if (!symstat) return(1);     /* 1 ist hier ein beliebiger Rueckgabewert ungleich 0 */


/* Nun wird versucht, die Symmetriegruppe des erzeugten Fullerens herauszufinden */

{      /* Klammer zur Abgrenzung der neuen Variablen */
KNOTENTYP f[N+1];                    /* f[x] enthaelt den Bildknoten von Knoten x */
KNOTENTYP e1,e2,e3;
char ordnung[32];                    /* Ordnung einer Drehung */
     /* Es treten maximal 31 Drehungen auf (bei Ih__ und I__). Zwar werden bei Bauchbinden 
        zwischenzeitlich einige Drehungen mehrfach gespeichert, jedoch nicht bei I__ und Ih__, 
	da diese Abbildungen keine Sechserdrehungen enthalten. 32 reicht also als Obergrenze. */
BOOL dreh;
KANTE *k1, *k2;
int jj,ord,n,n2;
BOOL geloescht, gefunden, alt;
char symm_ord;                     /* Gesamtordnung der Symmetriegruppe */

/* zunaechst bei Brillen und Sandwiches */

if (code[1]!=1) {      /* keine Bauchbinde */
  KNOTENTYP f1[24][12],f2[24][12];      /* speichert Abbildung der ersten beiden Ecken eines Pfades */

  symm_ord = m_laenge + ms_laenge + 1;    /* Ordnung der Symmetriegruppe */
  switch (symm_ord) {                     /* eindeutige Symmetriegruppe ? */
    case 1:   return(C1__);
    case 3:   return(C3__);
    case 10:  return(D5__);
    case 60:  return(I__);
    case 120: return(Ih__);
  }
  
  /* Teil 1:  Nun werden alle Drehungen untersucht und die Zahl und die Art der
              Drehungen ermittelt */

  n = 0;                  /* n: laufende Nummer des aktuellen Automorphismus */
  while (m_laenge>0) {    /* Liste mit Drehungen durchforsten und dabei aufloesen */  
    k1 = map[1][0].invers;
    k2 = miniliste[0];    /* es wird immer der erste Pfad in der Liste betrachtet */
    bilde_f(&f[0],k1,k2,map[0][0].name);
      /* Automorphismus, bei dem k1 auf k2 abgebildet wird, wird gebildet */

    /* Nun wird betrachtet:  Wie werden die Ecken e1 und e2 abgebildet und nach
       wie vielen Schritten werden wieder e1 und e2 erreicht (Ordnung des
       Automorphismus)? Dabei werden die zwischenzeitlich erreichten Ecken
       in den Arrays f1[n][...] und f2[n][...] zwischengespeichert. Also:
       f1[n][0] = f[e1],  f1[n][1] = f[f[e1]],  f1[n][2] = f[f[f[e1]]], ... ,
       f1[n][x] = f[...[f[e1]]...] = e1  (mit x = Ordnung des Automorphismus = Endwert von ord) */ 
    ord = 0;                  /* Ordnung des Automorphismus */
    e1 = k1->ursprung;
    e2 = k1->name;
    do {
      f1[n][ord] = e1 = f[e1];
      f2[n][ord] = e2 = f[e2];
      ord++;
      if (ord>12) {fprintf(stderr,"Ordnung eines Automorphismus groesser als 12!\n"); exit(38);}
    } while ((e1!=k1->ursprung) || (e2!=k1->name));   /* bis Identitaet erreicht */
    ordnung[n] = ord;    

    /* Nun ist die Ordnung des Automorphismus bekannt (=ordnung[n]) und es muessen noch
       die zugehoerigen Pfade in der miniliste gefunden und geloescht werden */
    miniliste[0] = miniliste[m_laenge-1];   m_laenge--;    /* erster Pfad wird geloescht */
    i = 1;    /* Anzahl der geloeschten Pfade */
    j = 0;    /* laufende Nummer des Pfades, ueber den entschieden wird, ob er geloescht wird */
    while (j<m_laenge) {
      ii=0;   geloescht=0;
      while (ii<ord-1 && !geloescht) {
        if (miniliste[j]->ursprung==f1[n][ii] && miniliste[j]->name==f2[n][ii])
          {miniliste[j]=miniliste[m_laenge-1];  m_laenge--;  geloescht=1;  i++;}
          /* Der Pfad wird geloescht, weil sein Anfang durch den aktuellen Automorphismus erreicht wird */ 
        ii++;
      }
      if (!geloescht) {j++;}  /*falls geloescht, so ist in Position j neuer Pfad => nicht ueberspringen*/ 
    }   /* while */
    
    if (i+1>ord) {fprintf(stderr,"Zu viele Pfade geloescht!\n");  exit(39);}
    
    /* Nun wird folgender Fall behandelt:
       Bei einem Automorphismus der Ordnung ord muessen ord-1 Pfade geloescht
       werden (alle bis auf den Originalpfad, der nicht in der Liste enthalten
       ist). Wenn weniger Pfade geloescht wurden, so sind zuvor schon einige
       Pfade des Automorphismus geloescht worden. Es gibt folgende Moeglichkeiten:
       - es wurde schon frueher eine Zweierdrehung entdeckt, die Bestandteil einer Sechserdrehung ist
       - es wurde schon frueher eine Dreierdrehung entdeckt, die Bestandteil einer Sechserdrehung ist
       - es wurden schon frueher eine Zweier- und eine Dreierdrehung entdeckt, die beide Bestandteil
         einer Sechserdrehung sind.
       In diesen Faellen muessen die zuerst gefundenen Zweier- bzw. Dreierdrehungen geloescht werden
       und in Sechserdrehungen umgewandelt werden.
       Falls einer der drei Faelle vorliegt, so ist der erste Eintrag f1[j][0] und f2[j][0]
       des zuerst gefundenen Automorphismus j auch im zweiten Automorphismus n enthalten. Also:
       f1[j][0] = f1[n][ii]  und  f2[j][0] = f2[n][ii]   fuer ein ii                             */

    if (i+1<ord) {              /* zuwenig Pfade geloescht */
      j=0;                      /* laufende Nummer des Automorphismus, mit dem verglichen wird */
      while (j<n && i+1<ord) {  /* es sind noch Automorphismen zu untersuchen */
        ii=0;   geloescht=0;
        while (ii<ord-1 && !geloescht) {
          if (f1[j][0]==f1[n][ii] && f2[j][0]==f2[n][ii]) {
            i += ordnung[j]-1;     /* die Anzahl der zuvor geloeschten Pfade */
            /* nun wird der zuvor gefundene Automorphismus geloescht (ueberschrieben) */
            ordnung[j] = ordnung[n-1];
            for (jj=0; jj<ordnung[n-1]; jj++) {f1[j][jj]=f1[n-1][jj];  f2[j][jj]=f2[n-1][jj];}
            ordnung[n-1] = ordnung[n];
            for (jj=0; jj<ordnung[n]; jj++)   {f1[n-1][jj]=f1[n][jj];  f2[n-1][jj]=f2[n][jj];}
            n--;
            geloescht=1;
          }   /* if */
          ii++;
        }     /* while */
        if (!geloescht) {j++;}
      }       /* while */
      if (i+1!=ord) {fprintf(stderr,"Falsche Ordnung des Automorphismus.\n"); exit(40);}
    }         /* if i+1<ord */

    n++;      /* nun wird der naechste Automorphismus behandelt */
  }           /* while m_laenge>0 */

  /* Jetzt sind die Anzahl der Drehungen (n) und zu jeder Drehung j die Art der Drehung
     (ordnung[j]) bekannt.

     Es folgt dieselbe Vorgehensweise fuer Spiegelungen. Es wird die Liste minispiegel
     aufgeloest. Es werden n2 Spiegelungen festgestellt. Da die Ordnung einer Ebenen-
     spiegelung immer 2 betraegt, ist eine Speicherung der Automorphismen in Arrays
     wie f1, f2 und ordnung nicht notwendig.
     In der Liste minispiegel befinden sich auch Drehspiegelungen (und Punktspiegelungen,
     die nichts anderes sind als 2er-Drehspiegelungen). Diese verursachen
     Probleme. Deshalb werden Drehspiegelungen, die gefunden werden, vernachlaessigt.
     Das ist moeglich, denn sobald die Ordnung einer Symmetriegruppe hoeher als 6 ist, ist
     jede Drehspiegelung schon in Form einer Drehung und einer Ebenenspiegelung berueck-
     sichtigt (das Fulleren enthaelt auch die einzelnen Symmetrien der zusammengesetzten
     Drehspiegelung). Es faellt also nichts unter den Tisch.
     Falls die Symmetriegruppe des Fullerens die Ordnung 4 oder 6 besitzt,
     ist es moeglich, anhand der gespeicherten Zahlen n und n2 auf die Existenz einer
     Drehspiegelung zu schliessen (deren einzelne Bestandteile nicht als Symmetrien in dem
     Fulleren vorhanden sind).
     Eine Drehspiegelung erkennt man daran, dass der Automorphismus im Gegensatz zur
     Ebenenspiegelung keine Ecken auf sich selbst oder benachbarte Ecken abbildet (letzteres
     ist durch die Mindestgroesse eines Fullerens gewaehrleistet).
     Falls der Automorphismus eine Ordnung besitzt, die groesser als 2 ist, so erkennt
     man die Drehspiegelung unmittelbar, denn Ebenenspiegelungen haben immer die Ordnung 2.

     Ein Beispiel fuer ein Problem mit Drehspiegelungen:
     Die Symmetriegruppe C3h besteht aus einer Dreierdrehung und einer Ebenenspiegelung senk-
     recht zur Dreierdrehung. Das Programm koennte einen Automorphismus bilden, der einer 
     6er-Drehspiegelung gleichkommt. Dabei wuerde dann sogar die Ebenenspiegelung uebersehen.  */
 
  /* Teil 2:  Nun werden alle Spiegelungen untersucht und die Zahl und die Art der
              Spiegelungen ermittelt */

  n2 = 0;                    /* n2: laufende Nummer des aktuellen Automorphismus */
  while (ms_laenge>0) {      /* Liste mit Spiegelungen durchforsten und dabei aufloesen */  
    k1 = map[1][0].invers;
    k2 = mini_spiegel[ms_laenge-1];     /* es wird immer der letzte Pfad in der Liste betrachtet */
    bilde_f_sp(&f[0],k1,k2,map[0][0].name);
    // Fehler bei Detektierung von Cs mit Fixkanten -- Aenderung: GB 13.2.2016
    if (symm_ord==2) ord=2; // GB
    else// GB
      {//GB

	/* Automorphismus, bei dem k1 auf k2 abgebildet wird, wird gebildet */
	ord = 0;                  /* Ordnung des Automorphismus */
	/* es reicht, den Funktionswert der Kante k1={e1,e2} zu verfolgen, da k1!=k2, 
	   also k1 keine Fixkante unter f, also f[e1]!=e1 oder f[e2]!=e2 */
	e1 = k1->ursprung;
	e2 = k1->name;  
	do {
	  e1 = f[e1];
	  e2 = f[e2];
	  ord++;
	  // commented out by GB: if (ord>12) {fprintf(stderr,"Ordnung eines Automorphismus groesser als 12!\n"); exit(41);}
	} while (((e1!=k1->ursprung) || (e2!=k1->name)) && ord<=2);   /* bis Identitaet erreicht oder
									 bis klar ist, dass es sich um Drehspiegelung handelt (wegen ord>2) */   
	/* Nun wird ueberprueft, ob es sich bei der Spiegelung um eine reine Ebenenspiegelung oder um eine
	   Drehspiegelung handelt. Bei einer Spiegelung mit der Ordnung >2  handelt es sich eindeutig um
	   eine Drehspiegelung. Bei einer Spiegelung mit der Ordnung 2 ist zu pruefen, ob der Automorphismus
	   Punkte auf sich selbst oder auf benachbarte Punkte abbildet (dann reine Ebenenspiegelung).
	   Der aktuelle Automorphismus ist noch im Array f vorhanden.     */
      } //GB
    if (ord==1) ord=2; /* GB: wenn eine gerichtete Kante fix ist unter einem orientierungsumkehrenden Automorphismus
			               ist die Ordnung 2 */
    dreh = 1;                /* falls keine andere Entdeckung:  Drehspiegelung */
    if (ord==2) {            /* Ebenenspiegelung oder Punktspiegelung ? */
      i=1;
      while (dreh && i<=map[0][0].name) {
        if (f[i]==map[i][0].name || f[i]==map[i][1].name || f[i]==map[i][2].name || f[i]==i) {dreh=0;}
        i++;
      }
    }
    if (!dreh) {n2++;}    
    ms_laenge--;                                           /* letzter Pfad wird geloescht */
  }               /* while ms_laenge>0 */
  /* Jetzt ist die Anzahl der Ebenenspiegelungen (n2) bekannt */

  /* Es folgt die Bestimmung der Symmetriegruppe. */
  switch(symm_ord) {
    case 1:  return(C1__);
    case 2:  if (n)  {return(C2__);}
             else {
               if (n2) {return(Cs__);}
               else    {return(Ci__);}
             }
    case 3:  return(C3__);
    case 4:  if (!n2) {
               if (n==3) {return(D2__);}
               else      {return(S4__);}
             }
             else {
               if (n2==2) {return(C2v__);}
               else       {return(C2h__);}
             }
    case 6:  if (!n2) {
               if (n==4) {return(D3__);}
               else      {return(S6__);}
             }
             else {
               if (n2==3) {return(C3v__);}
               else       {return(C3h__);}
             }
    case 8:  if (n2==3)  {return(D2h__);}
             else        {return(D2d__);}
    case 10: return(D5__);
    case 12: if (!n2) {
               BOOL d6=0;
               for (i=0; i<n; i++) {if (ordnung[i]==6) {d6=1;} }
               if (d6) {return(D6__);}
               else    {return(T__);}
             }
             else {
	       if (n2==4) {return(D3h__);}
               else       {return(D3d__);}
             }
    case 20: if (n2==6) {return(D5h__);}
             else       {return(D5d__);}
    case 24: { if (n2==7) {return(D6h__);}
               if (n2==6) {
                 BOOL d6=0;
                 for (i=0; i<n; i++) {if (ordnung[i]==6) {d6=1;} }
                 if (d6)  {return(D6d__);}
                 else     {return(Td__);}
               }
               else {return(Th__);}
             }
    case 60: return(I__);
    case 120: return(Ih__);
    default:  {fprintf(stderr,"Unbekannte Ordnung %d! %d\n",symm_ord,code[1]);  exit(42);}
  }      /* switch symm_ord */

}             /* if code[1]!=1 */


/* Es folgt dasselbe fuer Bauchbinden */

if (code[1]==1) {      /* Bauchbinde  (redundante if-Abfrage) */
  /* Bei der Bauchbinde befindet sich der Originalpfad in der miniliste. Also wird einfach
     der erste Pfad in der Liste als Originalpfad genommen. */
  /* Bei der Bauchbinde sind verschiedene Symmetrien zu untersuchen, bei denen die
     Bauchbinde auf sich selbst abgebildet wird (so dass diese Symmetrien nicht
     direkt aus der miniliste abzulesen sind). Dies sind Drehungen um die Achse
     senkrecht zur Bauchbinde und Spiegelungen an Ebenen senkrecht zur Bauchbinde.
     Falls die Bauchbinde das Fulleren in zwei gleiche Teile zerteilt (lowercode==uppercode),
     so kommen noch Drehspiegelungen um die Achse senkrecht zur Bauchbinde und 
     Zweierdrehungen um die Achse, die durch die Mittelpunkte zweier gegenueberliegender Kanten der
     Bauchbinde verlaeuft, hinzu. Falls die Bauchbinde das Fulleren in zwei ungleiche Teile zerteilt,
     so werden diese Symmetrien in der miniliste festgehalten und muessen erst spaeter
     betrachtet werden. */

  KNOTENTYP f1[24][2];   /* speichert bei gefundenen SPIEGELEBENEN eine Beispielkante */
                         /* 15 als Maximalzahl wuerde ausreichen (bei Ih__) */
  KNOTENTYP f2[32][2];   /* speichert bei gefundenen DREHUNGEN eine Beispielkante */
                         /* 31 als Maximalzahl wuerde ausreichen (bei I__ und Ih__) */
  KNOTENTYP g[N+1];    
  char ordnung2;        /* Ordnung bei Spiegelungen */
  char drehung;         /* Art der Drehung um Achse senkrecht zur Bauchbinde */
  char sp_ebene;        /* Spiegelebene(n) senkrecht zur Bauchbinde */
  char drehsp;          /* Drehspiegelung um Achse senkrecht zur Bauchbinde */
  char zdrehung;        /* Zweierdrehung(en) wie oben beschrieben. */  
 
  n = 0;                          /* Anzahl der gefundenen Drehungen */
  i = (code[0]/2)/code[3];        /* Drehung im oberen Teil des Fullerens  */
  j = (code[0]/2)/code[11];       /* Drehung im unteren Teil des Fullerens */
  drehung = i<j ? i : j;          /* groesser auf keinen Fall */
  if (i%drehung || j%drehung) {drehung = 1;}  /* Drehung um die Achse senkrecht zur Bauchbinde */  
  if (drehung>1) {                /* Drehung in die Liste eintragen */
    k2 = miniliste[0];
    for (j=1; j<=knoten_auf_pfad/drehung; j++) {
      if (j%2) {k2 = k2->invers->prev;}  else  {k2 = k2->invers->next;}
    }
    f2[n][0] = k2->ursprung;     /* Beispielkante */
    f2[n][1] = k2->name;    
    ordnung[n] = drehung;
    n++;
  }

  /* Nun wird versucht, Spiegelebenen zu ermitteln, die senkrecht auf der Bauchbinde 
     stehen. Wenn es eine solche Spiegelebene gibt, dann schneidet sie die Bauchbinde
     in zwei Ecken. Es ist nicht moeglich, dass die Spiegelebene die Bauchbinde in
     einer Ecke und einer Kante oder in zwei Kanten schneidet. 
     Also werden im folgenden je zwei gegenueberliegende Ecken betrachtet. Ausgehend
     von den Winkeln, die diese Ecken einschliessen, wird eine nicht ordnungserhaltene
     Abbildung gebildet und es wird untersucht, ob es sich dabei um einen Automorphismus 
     der Ordnung 2 handelt. 
     Damit nicht jede Spiegelebene doppelt betrachtet wird, reicht es aus bzw. ist es
     sogar erforderlich, nur die Ecken auf einer Haelfte des Pfades zu betrachten.
     Die gegenueberliegenden Ecken tauchen im Programmcode nicht auf.
     Sobald eine Spiegelebene gefunden wurde, wird die Suche nach weiteren Spiegelebenen
     vereinfacht, denn die Anzahl der Spiegelebenen senkrecht zur Bauchbinde entspricht
     dem Wert von "drehung" und die Spiegelebenen treten in regelmaessigen Abstaenden auf.
     Es verdoppelt sich die Symmetrieordnung unabhaengig von der Anzahl der Spiegelebenen. */
  
  n2 = 0;            /* Anzahl der gefundenen Spiegelebenen */
  sp_ebene = 1;      /* noch keine gefundene Spiegelebene */
  k1 = miniliste[0];               /* erste Kante */
  k2 = k1;   
  j=1; i=0;
  while (j<=knoten_auf_pfad/2) {     /* den halben Pfad entlanggehen */
    if (j%2) {k2 = k1->invers->prev;}  else  {k2 = k1->invers->next;}
    /* Nun ist k2 im Pfad der Nachfolger von k1 */
    /* Wenn durch den Knoten k1->name eine Spiegelebene verlaeuft, so wird k1 auf k2->invers
       abgebildet und umgekehrt. Man kann nun eine nicht ordnungserhaltene Funktion f bilden,
       die k1 auf k2->invers abbildet, und eine nicht ordnungserhaltene Funktion g, die k2->invers auf 
       k1 abbildet. Wenn g die Umkehrfunktion zu f ist, so ist f ein nicht ordnungserhaltender
       Automorphismus mit ordnung 2, es liegt also eine Spiegelebene vor (denn k1->name = k2->invers->name,
       es exisitiert also ein Fixpunkt). */
    if (sp_ebene==1 || (sp_ebene==2 && i==knoten_auf_pfad/(2*drehung))) {      /* Suche lohnt sich */
      if (bilde_f_und_g_sp(&f[0],&g[0],k1,k2->invers,map[0][0].name)) {
        sp_ebene=2;    /* fuendig */ 
        f1[n2][0] = f[miniliste[0]->ursprung];    f1[n2][1] = f[miniliste[0]->name]; 
        n2++;
        i=0;           /* Zaehler fuer jetzt beginnende schnelle Suche */
      }  
    }
    k1 = k2;       /* zur naechsten Kante des Pfades */
    j++;  i++;
  }                    /* while j */
  
  /* Nun werden die oben beschriebenen Zweierdrehungen und Drehspiegelungen betrachtet, und zwar 
     die Zweierdrehungen nur dann, wenn lowercode==uppercode.
     Zunaechst zu den Zweierdrehungen. Sobald man eine Zweierdrehung gefunden hat, ergeben sich 
     Anzahl und Lage von (eventuell) weiteren Zweierdrehungen aus dem Wert von "drehung".
     Zu der Ordnung der Symmetriegruppe tragen die weiteren Zweierdrehungen nichts bei.
     Wie bei den Spiegelebenen werden die Kanten der Bauchbinde betrachtet und es werden ordnungs-
     erhaltende Funktionen gebildet, bei denen eine Kante k1 auf k1->invers abgebildet wird und
     umgekehrt.
     Eine auf diese Weise ermittelte Zweierdrehung kann nicht Bestandteil einer Sechserdrehung sein,
     da um den Mittelpunkt einer Kante nur Zweierdrehungen moeglich sind.
     Theoretisch kann eine solche Zweierdrehung Bestandteil einer Viererdrehspiegelung sein. Dies
     wird in diesem Zusammenhang ebenfalls geprueft. Falls eine Viererdrehspiegelung vorliegt, so
     wird die Kante k1 auf die "gegenueberliegende" Kante (bezogen auf die Laenge der Bauchbinde)
     abgebildet. Eine Viererdrehspiegelung ist nur dann interessant, wenn es die einzige innerhalb
     des Fullerens ist. Insbesondere liegt dann auch nur EINE Zweierdrehung und KEINE Ebenenspiegelung
     vor. Es wird also nur bei der ersten gefundenen Zweierdrehung geprueft und auch nur dann, wenn 
     drehung==1 (keine weitere Drehung) und m_laenge==1 und sp_ebene==1. */
     
  zdrehung = drehsp = 1;                    /* 1 = noch nichts gefunden, 2 = gefunden */
  if (codecmp_kn(code+2,code+10,8)==0) {               /* lowercode==uppercode */
    k1 = miniliste[0];               /* erste Kante */   
    j=1;  i=0;
    while (j<=knoten_auf_pfad/2) {     /* den halben Pfad entlanggehen */
      if (zdrehung==1 || (zdrehung==2 && i==knoten_auf_pfad/(2*drehung))) {            /* Suche lohnt sich */
        if (bilde_f_und_g(&f[0],&g[0],k1,k1->invers,map[0][0].name)) {  
          f2[n][0] = f[miniliste[0]->ursprung];    f2[n][1] = f[miniliste[0]->name];
          ordnung[n] = 2;
          n++;
          if (zdrehung==1 && m_laenge==1 && sp_ebene==1 && drehung==1) {   /* Drehspiegelung? */
            k2 = k1;
            for (ii=0; ii<knoten_auf_pfad/2; ii++) {
              if ((j+ii)%2) {k2 = k2->invers->prev;} else {k2 = k2->invers->next;}  /* halber Pfad */
            }                        
            if (bilde_f_und_g_sp(&f[0],&g[0],k1,k2,map[0][0].name)) {
                fprintf(stderr,"Z-Viererdrehspiegelung\n");  /* sollte eine derartige Drehspiegelung
                                                    tatsaechlich auftreten, so ist sie eine Zeile wert */
                drehsp=4;
            }
            /* Drehspiegel-Abbildung von k1 nach k2->invers braucht nicht betrachtet zu werden:
               dasselbe Ergebnis wegen zdrehung=2 */
          }  
          i=0;            /* Zaehler fuer jetzt beginnende schnelle Suche */
          zdrehung=2;     /* fuendig */
        }
      }
      if (j%2) {k1 = k1->invers->prev;}  else  {k1 = k1->invers->next;}  /* zur naechsten Kante des Pfades */
      j++;   i++;
    }                /*while */
  }                  /* if */
 
  /* Nun ist noch zu pruefen, ob eine Drehspiegelung mit einer Drehung um die Bauchbinde vorliegt. 
     Die einzigen interessanten Faelle sind
     Ci, S4 und S6. Liegt einer dieser Faelle vor, so gibt es keine Spiegelebene (also sp_ebene==1 als
     Voraussetzung) und nur einen Listeneintrag (also m_laenge==1) und keine weitere Drehung (zdrehung==1).
     drehung==1:        moeglicherweise Punktspiegelung
     drehung==2:        moeglicherweise Viererdrehspiegelung
     drehung==3:        moeglicherweise Sechserdrehspiegelung
     =>  drehung==n/2:  moeglicherweise n-Drehspiegelung
     Fuer eine n-Drehspiegelung muss die Laenge des Pfades durch n teilbar sein (damit zugehoerige
     n/2-Drehung moeglich ist), darf aber nicht durch 2n teilbar sein. */
  if (m_laenge==1 && sp_ebene==1 && drehung<=3 && zdrehung==1 && knoten_auf_pfad%(2*drehung)==0 && 
      knoten_auf_pfad%(4*drehung)!=0)  {
    k1 = miniliste[0];            /* erste Kante */
    k2 = k1;
    for (j=1; j<=knoten_auf_pfad/(2*drehung); j++) {   /* einen Teil des Pfades entlanggehen */
      if (j%2) {k2 = k2->invers->prev;}  else  {k2=k2->invers->next;}
    } 
    /* Wenn eine Drehspiegelung der Ordnung 2*drehung vorliegt, so wird durch sie k1 auf k2 abgebildet
       und umgekehrt. */
    if (bilde_f_und_g_sp(&f[0],&g[0],k1,k2,map[0][0].name)) {drehsp=2*drehung;}    /* fuendig */  
  }    /* if */

  symm_ord = m_laenge * drehung * sp_ebene * zdrehung;   /* Mindestordnung der Symmetriegruppe */
  /* Fast immer ist dies auch die tatsaechliche Ordnung der Symmetriegruppe. Falls m_laenge>1,
     so kann es jedoch sein, dass zwei Pfade sowohl durch eine Drehung als auch durch eine Spiegelung
     aufeinander abgebildet werden (minierg==6). Falls diese Drehungen oder Spiegelungen nicht auch 
     auf eine andere Weise entdeckt werden koennen, so ist die tatsaechliche Ordnung der Symmetriegruppe
     hoeher als symm_ord. Folgende Beobachtung wurde gemacht:  Wenn zwischen zwei Bauchbinden eines
     Fullerens die Relation minierg==6 auftritt, dann auch zwischen allen anderen Bauchbinden des
     Fullerens. */

  if (m_laenge==1) {       /* schnelle Entscheidung anhand der symm_ord moeglich */
    switch (symm_ord) {    
      case 1:   if (drehsp==2) {return(Ci__);} else {return(C1__);}
      case 2:{  if (drehsp==4) {return(S4__);}
                if (drehung==2 || zdrehung==2 || (m_laenge==2 && minierg[1]==2)) {return(C2__);}
                if (sp_ebene==2) {return(Cs__);}
                break;}
      case 3:   if (drehsp==6) {return(S6__);} else {return(C3__);}
      case 10:  return(D5__);
    }    /* switch */
  }      /* if */
   
  /*  Nun werden alle Eintraege in der miniliste untersucht.   */
 
  /* Es treten folgende Probleme im Vergleich zu Sandwiches und Brillen auf:
     1.  Ein Eintrag in der miniliste muss nicht aus einer Drehung resultieren, sondern
         kann auch von einer Ebenenspiegelung stammen. Deshalb muss zu jedem Eintrag
         eine ordnungserhaltende und eine nicht ordnungserhaltende Funktion gebildet
         werden.  Allerdings kann man sich die Liste minierg[] zunutze machen, die 
         Auskunft darueber gibt, welche Funktion Aussicht auf Erfolg verspricht.
     2.  Es steht nicht fest, wohin der Anfang des Originalpfades abgebildet wird, da die
         Bauchbinde keinen fest definierten Anfang besitzt. Deshalb muss der "Anfang" der
         Originalbauchbinde (mit "Original" ist miniliste[0] gemeint) auf alle Kanten der 
	 in der miniliste (weiter hinten) gespeicherten Bauchbinde
         abgebildet werden. Es ergeben sich verschiedene Abbildungen. Teilweise handelt es
         sich dabei natuerlich nicht um Automorphismen. Die verbleibenden Spiegelabbildungen, bei
         denen es sich wirklich um Automorphismen handelt, koennen sogar unterschiedliche
         Ordnungen haben (Beispiel:  drehung==5 und in der miniliste steht Ebenenspiegelung
         an Ebene parallel zur Bauchbinde.  Eine Abbildung spiegelt nur => Ordnung 2. Eine
         andere Abbildung spiegelt und macht eine Fuenfteldrehung um die Bauchbinde
         => Ordnung 10).  Sobald eine Ebenenspiegelung gefunden wurde, eruebrigt sich NICHT die Suche
         nach anderen Spiegelabbildungen zwischen den beiden betrachteten Bauchbinden, denn
         andere Spiegelebenen koennen gefunden werden: Es ist zwar nicht moeglich, dass zwei verschiedene
         Spiegelebenen eine einzelne Kante aufeinander abbilden, aber es ist moeglich, dass zwei verschie-
         dene Spiegelebenen zwei verschiedene Bauchbinden als Gesamtes jeweils aufeinander abbilden,
         wobei die einzelnen Kanten der Bauchbinden jeweils unterschiedlich aufeinander abgebildet werden
         (Beispiel:  Fulleren Nummer 145886 bei C100).  */
 
  while (m_laenge>1) {      /* Liste durchforsten und dabei aufloesen */  
    /* Zunaechst wird versucht, weitere Spiegelebenen zu ermitteln, die senkrecht auf der Bauchbinde 
       stehen, die mit k1 beginnt, und die diese Bauchbinde auf sich selbst abbilden.
       Das Verfahren ist dasselbe wie oben. Es kann sein, dass eine
       gefundene Spiegelebene bereits gespeichert ist, weil sie z.B. gleichzeitig senkrecht auf zwei
       Bauchbinden steht. Deshalb muessen neu gefundene Spiegelebenen mit bereits gefundenen
       Spiegelebenen verglichen werden. */
    if (sp_ebene==2) {     /* falls bei Originalpfad Spiegelebene vorhanden <=> so auch hier */
      k1 = miniliste[m_laenge-1];               /* erste Kante */
      k2 = k1;   
      gefunden = 0;         /* noch keine Spiegelebene gefunden */      
      j=1; i=0;
      while (j<=knoten_auf_pfad/2) {     /* den halben Pfad entlanggehen */
        if (j%2) {k2 = k1->invers->prev;}  else  {k2 = k1->invers->next;}
        if (gefunden==0 || (gefunden==1 && i==knoten_auf_pfad/(2*drehung))) {      /* Suche lohnt sich */
          if (bilde_f_und_g_sp(&f[0],&g[0],k1,k2->invers,map[0][0].name)) {
            gefunden=1;    /* fuendig */ 
            alt = ii = 0;
            while (!alt && ii<n2) {          /* Spiegelung bereits gespeichert? */
              if (f1[ii][0]==f[miniliste[0]->ursprung] && f1[ii][1]==f[miniliste[0]->name]) {alt=1;}
              ii++;
            }
            if (!alt) {f1[n2][0]=f[miniliste[0]->ursprung];    f1[n2][1]=f[miniliste[0]->name];    n2++;}
            i=0;           /* Zaehler fuer jetzt beginnende schnelle Suche */
          }  
        }
        k1 = k2;       /* zur naechsten Kante des Pfades */
        j++;  i++;
      }                    /* while j */
    }     /* if sp_ebene==2 */    
   
    /* Nun wird versucht, weitere Drehungen zu ermitteln, die die Bauchbinde auf sich selbst abbilden.
       Auch hier muessen neu gefundene Drehungen mit bereits gefundenen Drehungen verglichen werden. */
    /* zunaechst zur inneren Drehung */
    if (drehung>1) {     /* falls bei Originalpfad innere Drehung <=> so auch hier */
      k2 = miniliste[m_laenge-1];
      for (j=1; j<=knoten_auf_pfad/drehung; j++) {
        if (j%2) {k2 = k2->invers->prev;}  else  {k2 = k2->invers->next;}
      }
      if (bilde_f_und_g(&f[0],&g[0],miniliste[m_laenge-1],k2,map[0][0].name)) {    /* Abbildung holen */
        alt = ii = ord = 0;
        while (!alt && ii<n) {           /* Drehung bereits gespeichert? */
          if (ordnung[ii]==drehung) {
            e1 = miniliste[0]->ursprung;  e2 = miniliste[0]->name;  i = 0;
            do {
              e1 = f[e1];   e2 = f[e2];   i++;
            } while (i<drehung && (e1!=f2[ii][0] || e2!=f2[ii][1]));
            if (i<drehung) {alt=1;}
          }
          ii++;
        }
        if (!alt) {
          f2[n][0] = f[e1];     /* Beispielkante */
          f2[n][1] = f[e2];    
          ordnung[n] = drehung;
          n++;
        }
      }       /* if */
    }         /* if drehung>1 */

    /* Nun zu den Zweierdrehungen an den Kantenzentren der Bauchbinde */
    if (zdrehung==2) {          /* Zweierdrehung(en) beim Originalpfad <=> so auch hier */
      k1 = miniliste[m_laenge-1];               /* erste Kante */   
      j=1;  i=0;  gefunden=0;
      while (j<=knoten_auf_pfad/2) {            /* den halben Pfad entlanggehen */
        if (gefunden==0 || (gefunden==1 && i==knoten_auf_pfad/(2*drehung))) {            /* Suche lohnt sich */
          if (bilde_f_und_g(&f[0],&g[0],k1,k1->invers,map[0][0].name)) {
            gefunden=1;     /* fuendig */  
            alt = ii = 0;   
            while (!alt && ii<n) {
              if (ordnung[ii]==2) {
                if (f2[ii][0]==f[miniliste[0]->ursprung] && f2[ii][1]==f[miniliste[0]->name]) {alt=1;}
              }
              ii++;
            }
            if (!alt) {
              f2[n][0] = f[miniliste[0]->ursprung];    f2[n][1] = f[miniliste[0]->name];
              ordnung[n] = 2;  n++;
            }
            i=0;         /* Zaehler fuer jetzt beginnende schnelle Suche */
          }
        }
        if (j%2) {k1 = k1->invers->prev;}  else  {k1 = k1->invers->next;}  /* zur naechsten Kante des Pfades */
        j++;   i++;
      }                /* while */
    }
             
    /* Nun werden Abbildungen zwischen der Bauchbinde 0 und der letzten Bauchbinde in der Liste
       betrachtet, und zwar wie oben beschrieben. */
    k1 = miniliste[0];
    k2 = miniliste[m_laenge-1];      /* es wird immer der letzte Pfad in der Liste betrachtet */
    ordnung2 = 0;           /* Ordnung des gefundenen nicht ordnungserhaltenden Automorphismus */
    j = 1; 
    while (j<=knoten_auf_pfad) {            /* den Bildpfad entlanggehen */
      if (minierg[m_laenge-1]&2) {          /* Drehung moeglich */
        if (bilde_f_und_g(&f[0],&g[0],k1,k2,map[0][0].name)) {
          /* ordnungserhaltenden Automorphismus gefunden */
          ord = 0;                   /* Ordnung des Automorphismus ermitteln */
          e1 = k1->ursprung;  e2 = k1->name;
          do {
            e1 = f[e1];  e2 = f[e2];
            ord++;
            if (ord>12) {fprintf(stderr,"Ordnung eines Automorphismus groesser als 12!\n"); exit(43);}
          } while ((e1!=k1->ursprung) || (e2!=k1->name));   /* bis Identitaet erreicht */    
          alt = ii = 0;             /* mit bereits gefundenen Drehungen vergleichen */
          while (!alt && ii<n) {           /* Drehung bereits gespeichert? */
            if (ordnung[ii]==ord) {
              e1 = k1->ursprung;  e2 = k1->name;  i = 0;
              do {
                e1 = f[e1];   e2 = f[e2];   i++;
              } while (i<ord && (e1!=f2[ii][0] || e2!=f2[ii][1]));
              if (i<ord) {alt=1;}
            }
            ii++;
          }
          if (!alt) {
            f2[n][0] = f[e1];     /* Beispielkante */
            f2[n][1] = f[e2];     /* e1 und e2  haben wieder die urspruenglichen Werte */
            ordnung[n] = ord;
	    n++;
          }          /* if */
        }            /* if */

        /* dasselbe mit spiegelverkehrtem Pfad */      
        if (bilde_f_und_g(&f[0],&g[0],k1,k2->invers,map[0][0].name)) {
          /* ordnungserhaltenden Automorphismus gefunden */
          ord = 0;                   /* Ordnung des Automorphismus ermitteln */
          e1 = k1->ursprung;  e2 = k1->name;
          do {
            e1 = f[e1];  e2 = f[e2];
            ord++;
            if (ord>12) {fprintf(stderr,"Ordnung eines Automorphismus groesser als 12!\n"); exit(44);}
          } while ((e1!=k1->ursprung) || (e2!=k1->name));   /* bis Identitaet erreicht */
          alt = ii = 0;             /* mit bereits gefundenen Drehungen vergleichen */
          while (!alt && ii<n) {           /* Drehung bereits gespeichert? */
            if (ordnung[ii]==ord) {
              e1 = k1->ursprung;  e2 = k1->name;  i = 0;
              do {
                e1 = f[e1];   e2 = f[e2];    i++;
              } while (i<ord && (e1!=f2[ii][0] || e2!=f2[ii][1]));
              if (i<ord) {alt=1;}
            }
            ii++;
          }
          if (!alt) {
            f2[n][0] = f[e1];     /* Beispielkante */
            f2[n][1] = f[e2];
            ordnung[n] = ord;   
            n++;
          }          /* if */
        }          /* if */
      }         /* if minierg&2 */

      if (minierg[m_laenge-1]&4) {            /* Ebenenspiegelung moeglich */ 
        if (bilde_f_und_g_sp(&f[0],&g[0],k1,k2->invers->prev,map[0][0].name)) {
          /* nicht ordnungserhaltenden Automorphismus gefunden */
          ord = 0;                   /* Ordnung des Automorphismus */
          /* da {e1,e2} eventuell Fixkante ist, muss eine weitere Kante {e1,e3} betrachtet werden */
          e1 = k1->ursprung;  e2 = k1->name;  e3 = k1->prev->name;
          do {
            e1 = f[e1];  e2 = f[e2];  e3 = f[e3];
            ord++;
            if (ord>12) {fprintf(stderr,"Ordnung eines Automorphismus groesser als 12!\n"); exit(45);}
          } while ((e1!=k1->ursprung) || (e2!=k1->name) || (e3!=k1->prev->name));  /* Identitaet erreicht */
          if (ordnung2==0 || ordnung2>ord)  {ordnung2=ord;} 
	  if (ord>drehsp) {drehsp=ord;}     /* groesste gefundene Drehspiegelung speichern */   
            /* falls in Wirklichkeit Ebenenspiegelung => egal, denn => n2>0 => drehsp wird nicht abgefragt */
          if (ord==2) {                /* testen: ist gefundene Funktion Ebenenspiegelung? */
            i = dreh = 1;
            while (dreh && i<=map[0][0].name) {            /* Fixpunkte/Beruehrungspunkte suchen */
              if (f[i]==map[i][0].name || f[i]==map[i][1].name || f[i]==map[i][2].name || f[i]==i) {dreh=0;}
              i++;
            }
            if (!dreh) {              /* Ebenenspiegelung gefunden */
              alt = ii = 0;
              while (!alt && ii<n2) {          /* Spiegelung bereits gespeichert? */
                if (f1[ii][0]==f[k1->ursprung] && f1[ii][1]==f[k1->name]) {alt=1;}
                ii++;
              }
              if (!alt) {f1[n2][0]=f[k1->ursprung];    f1[n2][1]=f[k1->name];   n2++;}
            }     /* if */
          }       /* if */ 
        }         /* if */

        /* dasselbe mit spiegelverkehrtem Pfad */
        if (bilde_f_und_g_sp(&f[0],&g[0],k1,k2->invers->prev->invers,map[0][0].name)) {
          /* nicht ordnungserhaltenden Automorphismus gefunden */
          ord = 0;                   /* Ordnung des Automorphismus */
          /* da {e1,e2} eventuell Fixkante ist, muss eine weitere Kante {e1,e3} betrachtet werden */
          e1 = k1->ursprung;  e2 = k1->name;  e3 = k1->prev->name;
          do {
            e1 = f[e1];   e2 = f[e2];   e3 = f[e3];
            ord++;
            if (ord>12) {fprintf(stderr,"Ordnung eines Automorphismus groesser als 12!\n"); exit(46);}
          } while ((e1!=k1->ursprung) || (e2!=k1->name) || (e3!=k1->prev->name));   /* Identitaet erreicht */
          if (ordnung2==0 || ordnung2>ord)  {ordnung2=ord;}    
          if (ord>drehsp) {drehsp=ord;}    /* groesste gefundene Drehspiegelung speichern */
	  if (ord==2) {               /* testen: ist gefundene Funktion Ebenenspiegelung? */
            i = dreh = 1;
            while (dreh && i<=map[0][0].name) {
              if (f[i]==map[i][0].name || f[i]==map[i][1].name || f[i]==map[i][2].name || f[i]==i) {dreh=0;}
              i++;
            }
            if (!dreh) {              /* Ebenenspiegelung gefunden */
              alt = ii = 0;
              while (!alt && ii<n2) {          /* Spiegelung bereits gespeichert? */
                if (f1[ii][0]==f[k1->ursprung] && f1[ii][1]==f[k1->name]) {alt=1;}
                ii++;
              }
              if (!alt) {f1[n2][0]=f[k1->ursprung];    f1[n2][1]=f[k1->name];   n2++;}
            }     /* if */
          }       /* if */ 
        }         /* if */
      }           /* if (minierg&4) */

      k2 = k2->invers->prev->invers->next;     /* zwei Kanten weiter */
      j+=2;
    }                /* while j */

    m_laenge--;    /* letzter (untersuchter) Pfad wird geloescht */
  }     /* while m_laenge>1 */

  /* Nun werden Drehungen, die doppelt gezaehlt wurden, aus der Liste ordnung[] genommen. Folgender
     Fall:
     - Sechserdrehung in der Liste:   eine Zweierdrehung und eine Dreierdrehung zuviel, aber nur
       dann,  wenn die Sechserdrehung aus zwei verschiedenen Pfaden rekonstruiert wurde und nicht, 
       wenn die Sechserdrehung aus dem Wert von "drehung" folgt.
     Die Inhalte der Arrays f1 und f2 werden nicht zusammen mit den Inhalten von ordnung verschoben,
     da sie nicht mehr gebraucht werden.  */    
  if (drehung!=6) {
    j=0;
    while (j<n) {
      if (ordnung[j]==6) {
        ii = 0;   i = 0;
        while (ii<1 && i<n) {
          if (ordnung[i]==3) {
            if (i>j) {ordnung[i]=ordnung[n-1];  n--;  ii++;}
            else     {ordnung[i]=ordnung[j-1];  ordnung[j-1]=ordnung[j];     /* i<j */
                      ordnung[j]=ordnung[n-1];  n--;  ii++;  j--;}
          }
          else  {i++;}
        }
        if (ii<1) {fprintf(stderr,"Es fehlt eine Dreierdrehung.\n"); exit(47);}
        ii = 0;   i = 0;
        while (ii<1 && i<n) {
          if (ordnung[i]==2) {
            if (i>j) {ordnung[i]=ordnung[n-1];  n--;  ii++;}
            else     {ordnung[i]=ordnung[j-1];  ordnung[j-1]=ordnung[j];
                      ordnung[j]=ordnung[n-1];  n--;  ii++;  j--;}
          }
          else  {i++;}
        }
        if (ii<1) {fprintf(stderr,"Es fehlt eine Zweierdrehung.\n"); exit(48);}
        j=n;     /* Es tritt hoechstens eine Sechserdrehung auf => Abbruch */
      }   /* if */
      j++;
    }     /* while */
  }       /* if */
  
  /* Jetzt ist die Anzahl der Ebenenspiegelungen (n2) und die Anzahl (n) und Art (ordnung[]) der
     Drehungen bekannt. */
  /* Es folgt die Bestimmung der Symmetriegruppe. */

  /* Testblock: funktioniert das Programm richtig? */
  /* der gesamte Switch-Block kann entfallen, sobald das Vertrauen in die Prozedur gross genug ist */
  switch(n2) {
    case 0: {switch(n) {
               case 0:  {if (drehsp!=2) {fprintf(stderr, "%lld: Fehler bei Ci %d\n", graphenzahl[map[0][0].name]+1,
                                         drehsp); exit(49);}
                         break;}
               case 1:  {if (drehsp==4) {if (ordnung[0]!=2) 
                            {fprintf(stderr,"%lld: Fehler bei S4\n", graphenzahl[map[0][0].name]+1); exit(50);} }
	                 if (drehsp==6) {if (ordnung[0]!=3) 
                            {fprintf(stderr,"%lld: Fehler bei S6\n", graphenzahl[map[0][0].name]+1); exit(51);} }
		         if (ordnung[0]!=2 && ordnung[0]!=3) 
                            {fprintf(stderr, "%lld: Fehler bei C%d\n", graphenzahl[map[0][0].name]+1, ordnung[0]);
                             exit(52);}
		         break;}
	       case 3:  {if (ordnung[0]!=2 || ordnung[1]!=2 || ordnung[2]!=2)
                            {fprintf(stderr, "%lld: Fehler bei D2\n", graphenzahl[map[0][0].name]+1); exit(53);}
	                 break;}
	       case 4:  {if (ordnung[0]+ordnung[1]+ordnung[2]+ordnung[3]!=9) 
                            {fprintf(stderr, "%lld: Fehler bei D3\n", graphenzahl[map[0][0].name]+1); exit(54);}
	                 break;}
	       case 6:  {if (ordnung[0]+ordnung[1]+ordnung[2]+ordnung[3]+ordnung[4]+ordnung[5] !=15)
	                    {fprintf(stderr, "%lld: Fehler bei D5\n", graphenzahl[map[0][0].name]+1); exit(55);}
                         break;}
	       case 7:  {BOOL d6=0;  int k=1;
                         for (i=0; i<7; i++) {k*=(int)(ordnung[i]); if (ordnung[i]==6) {d6=1;} }
                         if (d6) {if (k!=64*6) 
                                  {fprintf(stderr, "%lld: Fehler bei D6\n", graphenzahl[map[0][0].name]+1); exit(56);} }
                         else    {if (k!=81*8) 
                                  {fprintf(stderr, "%lld: Fehler bei T\n", graphenzahl[map[0][0].name]+1); exit(57);} }
         		 break;
		        }
               case 31: break;
	       default: {fprintf(stderr, "%lld: Fehler 0 %d\n", graphenzahl[map[0][0].name]+1, n);  exit(58);}
	     } 
	     break;}
    case 1: {switch(n) {
               case 0:  break;
   	       case 1:  {switch(ordnung[0]) {
	                   case 2:  break;
	   		   case 3:  break;
			   default: {fprintf(stderr, "%lld: Fehler 1 1 %d\n", graphenzahl[map[0][0].name]+1, 
                                     ordnung[0]); exit(59);}
		        } break;}
               default: {fprintf(stderr, "%lld: Fehler 1 %d\n", graphenzahl[map[0][0].name]+1, n); exit(60);}
	     }
	     break;}    
    case 2: {switch(n) {
               case 1:  {if (ordnung[0]!=2) 
                            {fprintf(stderr, "%lld: Fehler bei C2v\n", graphenzahl[map[0][0].name]+1); exit(61);}
                         break;}
	       case 3:  {if (ordnung[0]!=2 || ordnung[1]!=2 || ordnung[2]!=2) 
	                    {fprintf(stderr, "%lld: Fehler bei D2d\n", graphenzahl[map[0][0].name]+1); exit(62);}
                         break;}
	       default: {fprintf(stderr, "%lld: Fehler 2 %d\n", graphenzahl[map[0][0].name]+1, n);  exit(63);}
	     }
	     break;}
    case 3: {switch(n) {
               case 1:  {if (ordnung[0]!=3)
                            {fprintf(stderr, "%lld: Fehler bei C3v\n", graphenzahl[map[0][0].name]+1);  exit(64);}
                         break;}
	       case 3:  {if (ordnung[0]!=2 || ordnung[1]!=2 || ordnung[2]!=2) 
                            {fprintf(stderr, "%lld: Fehler bei D2h\n", graphenzahl[map[0][0].name]+1);  exit(65);}
                         break;}
	       case 4:  {if (ordnung[0]+ordnung[1]+ordnung[2]+ordnung[3]!=9) 
                            {fprintf(stderr, "%lld: Fehler bei D3d\n", graphenzahl[map[0][0].name]+1);  exit(66);}
                         break;}
	       case 7:  {int k=1;
                         for (i=0; i<7; i++) {k*=(int)(ordnung[i]);}
                         if (k!=81*8) 
                            {fprintf(stderr, "%lld: Fehler bei Th\n", graphenzahl[map[0][0].name]+1);  exit(67);}  
                         break;}
	       default: {fprintf(stderr, "%lld: Fehler 3 %d\n", graphenzahl[map[0][0].name]+1, n);  exit(68);}
	     }
	     break;}
    case 4: {if (n!=4 || ordnung[0]+ordnung[1]+ordnung[2]+ordnung[3]!=9)
                {fprintf(stderr, "%lld: Fehler bei D3h\n", graphenzahl[map[0][0].name]+1); exit(69);}
             break;}
    case 5: {if (n!=6 || ordnung[0]*ordnung[1]*ordnung[2]*ordnung[3]*ordnung[4]*ordnung[5]!=32*5)
                {fprintf(stderr, "%lld: Fehler bei D5d\n", graphenzahl[map[0][0].name]+1); exit(77);}
             break;}
    case 6: {switch(n) {
               case 6: {if (ordnung[0]*ordnung[1]*ordnung[2]*ordnung[3]*ordnung[4]*ordnung[5]!=32*5)
                            {fprintf(stderr, "%lld: Fehler bei D5h\n", graphenzahl[map[0][0].name]+1); exit(70);}
                        break;}
	       case 7: {BOOL d6=0;  int k=1;
                        for (i=0; i<7; i++) {k*=(int)(ordnung[i]); if (ordnung[i]==6) {d6=1;} }
                        if (d6) {if (k!=64*6)
                                {fprintf(stderr, "%lld: Fehler bei D6d\n", graphenzahl[map[0][0].name]+1); exit(71);} }
                        else    {if (k!=81*8)
                                {fprintf(stderr, "%lld: Fehler bei Td\n", graphenzahl[map[0][0].name]+1); exit(72);} }	     	   	   
                        break;}
  	       default: {fprintf(stderr, "%lld: Fehler 6 %d\n", graphenzahl[map[0][0].name]+1, n); exit(73);}
	     }
	     break;}
    case 7: {BOOL d6=0; int k=1;
             for (i=0; i<7; i++) {k*=(int)(ordnung[i]); if (ordnung[i]==6) {d6=1;} }
             if (d6==0 || n!=7 || k!=64*6)
                {fprintf(stderr, "%lld: Fehler bei D6h\n", graphenzahl[map[0][0].name]+1); exit(74);}
             break;}
    case 15: {if (n!=31) {fprintf(stderr, "%lld: Fehler bei Ih\n", graphenzahl[map[0][0].name]+1); exit(75);}
              break;}
    default: {fprintf(stderr, "%lld: Fehler %d %d\n", graphenzahl[map[0][0].name]+1, n2, n); exit(76);}
  }

  /* Nun tatsaechliche Auswertung */
  switch(n2) {
    case 0: {switch(n) {
               case 0:  return(Ci__);
	       case 1:  {if (drehsp==4) {return(S4__);}
	                 if (drehsp==6) {return(S6__);}
		         switch(ordnung[0]) {
		    	   case 2:  return(C2__);
			   case 3:  return(C3__);
			   default: exit(78);
		         }
		         break;}
  	       case 3:  return(D2__);
	       case 4:  return(D3__);
	       case 6:  return(D5__);
	       case 7:  {BOOL d6=0;
                         for (i=0; i<7; i++) {if (ordnung[i]==6) {d6=1;} }
                         if (d6) {return(D6__);}
                         else    {return(T__);}
		        }
               case 31: return(I__);
	       default: exit(79);
	     } 
	     break;}
    case 1: {switch(n) {
               case 0:  return(Cs__);
	       case 1:  switch(ordnung[0]) {
	                   case 2:  return(C2h__);
		  	   case 3:  return(C3h__);
			   default: exit(80);
		        }
               default: exit(0);
	     }
	     break;}    
    case 2: {switch(n) {
               case 1:  return(C2v__);
	       case 3:  return(D2d__);
	       default: exit(81);
	     }
	     break;}
    case 3: {switch(n) {
               case 1:  return(C3v__);
    	       case 3:  return(D2h__);
	       case 4:  return(D3d__);
	       case 7:  return(Th__);
	       default: exit(82);
	     }
	     break;}
    case 4: return(D3h__);
    case 5: return(D5d__);
    case 6: {switch(n) {
               case 6: return(D5h__);
	       case 7: {BOOL d6=0;
                        for (i=0; i<7; i++) {if (ordnung[i]==6) {d6=1;} }
                        if (d6) {return(D6d__);}
                        else    {return(Td__);}	     	   	   
                       }
	       default: exit(83);
	     }
	     break;}
    case 7: return(D6h__);
    case 15: return(Ih__);
    default: exit(84);
  }   /* switch */

}      /* if code[1]==1 */

}      /* Abgrenzung des Symmetrieteils (neue Variablen) */
 return 1; /* wird nie erreicht -- nur um Compilerwarnungen vorzubeugen */
}      /* Ende der Prozedur */


/**********************CHECKSIZE_RIGHT_2**************************************/

/* bestimmt die groesse der flaeche rechts von edge -- ist da keine gibt's 
   hier aber keine Probleme, sondern 6 wird zurueckgegeben -- dient nur
   zur Ueberpruefung, ob da ein 5-Eck ist.

   Es wird allerdings angenommen, dass edge->name nicht aussen ist
*/


int checksize_right_2( KANTE* edge)
{
KANTE *run; 
int zaehler=1;

for (run=edge->invers->prev; run != edge; run=run->invers->prev) 
  { if (run->name==aussen) return(6); zaehler++; }
return(zaehler);
}




/**********************CHECKSIZE_2**************************************/

/* bestimmt die groesse der flaeche links von edge -- ist da keine gibt's 
   hier aber keine Probleme, sondern 6 wird zurueckgegeben -- dient nur
   zur Ueberpruefung, ob da ein 5-Eck ist.

   Es wird allerdings angenommen, dass edge->name nicht aussen ist
*/


int checksize_2( KANTE* edge)
{
KANTE *run; 
int zaehler=1;

for (run=edge->invers->next; run != edge; run=run->invers->next) 
  { if (run->name==aussen) return(6); 
    zaehler++;  }
return(zaehler);
}


      

/******************VERGLEICHE_SYMM************TH**************************/
/*  Diese Funktion prueft, ob die Nummer "nr" im Array "symm" auftritt,
    wobei die ersten "symm_len" Arrayelemente belegt sind.               */

BOOL vergleiche_symm(char nr) {
  int i;
  for (i=0; i<symm_len; i++) {
    if (symm[i]==nr) {return(True);}
  }
  return(False);
}


/***********************TESTE_UND_SCHREIBE*******TH***********************/

/* ueberprueft ein fertiges Fulleren, testet es auf Kanonizitaet und schreibt
   es gegebenenfalls auf */

void teste_und_schreibe(PLANMAP map, KNOTENTYP *code)
{ int erg;

(non_iso_graphenzahl[map[0][0].name])++;
if ((erg=minitest(map,code))) { 
  (graphenzahl[map[0][0].name])++;
  if (symm_len==0 || vergleiche_symm(erg)) codiereplanar(map);
  (symm_anz[erg])++;                  /* fuer die Symmetriestatistik */  
}

}


/***********************SUCHE_ITEM**************************************/

ITEMLISTE *suche_item(KNOTENTYP *adresse)
{
int i, laenge;
SEQUENZLISTE *sq;

laenge=8-adresse[0];

sq=mapliste.sechser[adresse[1]];

for (i=2; i<laenge; i++)
  { if (sq->number_next <= adresse[i]) return(nil);
    if (sq->next_level[adresse[i]]==nil) return(nil);
    sq=sq->next_level[adresse[i]]; }
return(sq->items);
}


/***********************SUCHE_ITEM_BB**************************************/

BBITEMLISTE *suche_item_bb(KNOTENTYP *adresse)
{

BBSEQUENZLISTE *sq;

sq=bbliste.sechser[adresse[1]];

if (sq->number_next <= adresse[2]) return(nil);
return(sq->items[adresse[2]]);
}



/*********************ADD_POLYGON_INVERS***********************************/

void add_polygon_invers(int n, PLANMAP map, KANTE *start, KANTE **lastout)
/* fuegt ein weiteres polygon einer Reihe an. Dabei ist n die groesse des polygons. 
   Angefuegt wird immer an start. Ueber lastout wird die letzte Aussenkante des 
   Polygons zurueckgegeben.
   Es arbeitet wie add_polygon nur im anderen Drehsinn. Das wird fuer die REkonstruktion
   der Patches gebraucht
   Im Falle, dass nur eine Kante eingefuegt werden muss, wird *lastout auf die naechste 
   zu benutzende Aussenkante gesetzt. Die ist nicht mit dem gebauten Polygon
   inzident. Im Falle, dass es sie nicht gibt, wird *lastout auf nil gesetzt.

   angefuegt wird in den Winkel in prev-Richtung, d.h. zwischen start und start->prev

 */


{
int i, new_tempknz, tempknz;
KANTE *ende, *run;
int common_vertices;


if (start->name != aussen) { fprintf(stderr,"ERROR ADD_P_INV not starting at external edge\n");
			     exit(86); }

if (IPR && (n==5))
  { 
    if (checksize_2(start->prev)==5) is_ipr=0;
    for (ende=start->prev->invers->prev, common_vertices=2; ende->name != aussen; 
	  ende=ende->invers->prev) {if (checksize_2(ende)==5) is_ipr=0;
                                     common_vertices++;
				   }
  }
else for (ende=start->prev->invers->prev, common_vertices=2; ende->name != aussen; 
	  ende=ende->invers->prev) common_vertices++;


if (n<common_vertices) 
   { fprintf(stderr,"polygon to insert (inv) too small !\n"); 
     exit(87); }

/* es muessen also n-common_vertices knoten hinzugefuegt werden */

tempknz=map[0][0].name;
new_tempknz=tempknz+n-common_vertices;

if (n-common_vertices==0) /* dann kommt kein knoten dazu */
  { start->name=ende->ursprung; start->invers=ende;
    ende->name=start->ursprung; ende->invers=start;

    for (ende=start->next->invers->next, common_vertices=2; 
	 (ende->name != aussen) && (common_vertices<6); 
         ende=ende->invers->next) common_vertices++;
    if (common_vertices<6) *lastout=ende; /* ein common_vertices+1 -- Eck ist noch moeglich */
    else { *lastout=nil;
	   if (ende==start->next) /* dann ist nur noch eine 5-Eck Luecke */
	     { for (i=anzahl_5ek+5, run=start->invers; anzahl_5ek<i; 
		  anzahl_5ek++, run=run->invers->next) { F_eck_kanten[anzahl_5ek]=run;
							 if (IPR)
							   if (checksize_right_2(run)==5) is_ipr=0; }
	     }
	 }
  }
else
  {
    if (n-common_vertices==1) /* dann kommt nur ein knoten dazu */
      {
	tempknz++;
	start->name=tempknz; start->invers=map[tempknz];
	map[tempknz][0].name=start->ursprung; map[tempknz][0].invers=start;
	map[tempknz][1].name=ende->ursprung; map[tempknz][1].invers=ende;
	ende->name=tempknz; ende->invers=map[tempknz]+1;
	map[tempknz][2].name=aussen; map[tempknz][2].invers=nil;
	*lastout=map[tempknz]+2;
	map[0][0].name=tempknz;
      }
    else
      {
	
	/* es bleibt: mindestens zwei neue knoten */
	
	tempknz++;
	start->name=tempknz; start->invers=map[tempknz];
	map[tempknz][0].name=start->ursprung; map[tempknz][0].invers=start;
	map[tempknz][1].name=tempknz+1; map[tempknz][1].invers=map[tempknz+1];
	map[tempknz][2].name=aussen; map[tempknz][2].invers=nil;
	
	for (tempknz++; tempknz<new_tempknz; tempknz++)
	  { map[tempknz][0].name=tempknz-1; map[tempknz][0].invers=map[tempknz-1]+1;
	    map[tempknz][1].name=tempknz+1; map[tempknz][1].invers=map[tempknz+1]; 
	    map[tempknz][2].name=aussen; map[tempknz][2].invers=nil; }
	
	/* und nun noch den letzten knoten */
	map[tempknz][0].name=tempknz-1; map[tempknz][0].invers=map[tempknz-1]+1;
	map[tempknz][1].name=ende->ursprung; map[tempknz][1].invers= ende;
	ende->name=tempknz; ende->invers=map[tempknz]+1;
	map[tempknz][2].name=aussen; map[tempknz][2].invers=nil;
	*lastout=map[tempknz]+2;
	map[0][0].name=tempknz;
      } /* ende zweites else */
  } /* ende erstes else */

if (n==5)
  for (i=anzahl_5ek+5, run=start; anzahl_5ek<i; 
       anzahl_5ek++, run=run->invers->next) F_eck_kanten[anzahl_5ek]=run;

return;
}


/***************************BAUE_KUPPE********************************/

void baue_kuppe(PLANMAP map, int bblaenge, FLAECHENTYP code[], KANTE **anfang, int flaechenzahl)
{
int i, puffer, codestelle, zaehler, flaechenzaehler;
KANTE *run;



puffer=2*bblaenge;

if (*anfang==nil) /* d.h. Bauchbinde und obere Kuppe bauen und Anfang zurueckgeben */
  { 
        map[1][0].name=puffer; map[1][0].invers=map[puffer]+1;
	map[1][1].name=aussen; map[1][1].invers=nil;
	map[1][2].name=2; map[1][2].invers=map[2];

   for (i=2; i<2*bblaenge; i++)
      { map[i][0].name=i-1; map[i][0].invers=map[i-1]+2;
	map[i][1].name=i+1; map[i][1].invers=map[i+1];
	map[i][2].name=aussen; map[i][2].invers=nil;
	i++;
        map[i][0].name=i-1; map[i][0].invers=map[i-1]+1;
	map[i][1].name=aussen; map[i][1].invers=nil;
	map[i][2].name=i+1; map[i][2].invers=map[i+1];
      }
	map[puffer][0].name=puffer-1; map[puffer][0].invers=map[puffer-1]+2;
	map[puffer][1].name=1; map[puffer][1].invers=map[1];
	map[puffer][2].name=aussen; map[puffer][2].invers=nil;
	
	map[0][0].name= puffer;
	*anfang=map[2]+2;

	for (run=map[1]+1, zaehler=1; zaehler<= bblaenge*code[0]; zaehler++ )
	  { add_polygon_invers(6, map, run, &run);
	    if (run==nil) { fprintf(stderr,"ERROR: nil-edge while building hexagon rings\n");
			    exit(88); }
	  } 
	flaechenzaehler=zaehler;
	for (codestelle=2, zaehler=1; run != nil; zaehler++, flaechenzaehler++ )
	  { 
	    if ((codestelle<8) && (code[codestelle]==zaehler))
	      { add_polygon_invers(5, map, run, &run); codestelle++; }
	    else add_polygon_invers(6, map, run, &run);
	  } 
        if (flaechenzaehler != flaechenzahl) 
	  { fprintf(stderr,"Baue_Kuppe: Could not insert enough faces: ");
	    fprintf(stderr,"%d instead of %d\n (upper half)\n",flaechenzaehler,flaechenzahl);
	    exit(89); }
      } /* ende if *anfang==nil) */
else /* d.h. untere Kuppe bauen */
  {
  for (run= *anfang, zaehler=1; zaehler <= bblaenge*code[0]; zaehler++ )
      { add_polygon_invers(6, map, run, &run);
	if (run==nil) { fprintf(stderr,"ERROR: nil-edge while building hexagon rings\n");
    		    exit(90); }
      } 
    flaechenzaehler=zaehler;
    for (codestelle=2, zaehler=1; run != nil; zaehler++, flaechenzaehler++ )
      { if ((codestelle<8) && (code[codestelle]==zaehler))
          { add_polygon_invers(5, map, run, &run); codestelle++; }
        else add_polygon_invers(6, map, run, &run);
      }
        if (flaechenzaehler != flaechenzahl) 
	  { fprintf(stderr,"Baue_Kuppe: Could not insert enough faces: ");
	    fprintf(stderr,"%d instead of %d\n (upper half)\n",flaechenzaehler,flaechenzahl);
	    exit(91); }
  } /* ende else */

}



/*********************BAUCHBINDE****************************************/

/* Der erste Fall der Fullerenkonstruktion: Fullerene mit Bauchbinde */
/*           ___________________________
	    /                           \
	    |                           |
	    |                           |
	    |                           |
	    \__________________________/       */


/* konvention: Die obere haelfte is die mit mehr sechsecken. Ist die
Anzahl der sechsecke gleich, so ist es die mit dem groesseren code ohne
Beruecksichtigung der verschiebung. Wenn eine code-kombination betrachtet 
wird, wo die haelfte mit weniger sechsecken noch 6-Eck-Ringe hat, ist sie 
eh nicht minimal, da der Gesamt-code rekonstruiert von der bauchbinde aus, 
die man erhaelt, wenn man die Ringe nach oben verschiebt, kleiner ist. */

/* gesamtcode: (pfadlaenge,1,lowercode[],uppercode[],verschiebung)
   dabei wird beim vergleich die stelle, die in den codes die 
   verschiebungsmoeglichkeiten beschreibt, nicht beruecksichtigt 
   gesamtcodelaenge: 19 stellen */


void bauchbinde(int min_sechsecke, int max_sechsecke)
{
int sechsecke, i, j, k, bblaenge, upper6gons, lower6gons;
KNOTENTYP adresse[4];
KANTE *anfang, *merkeanfang; /* eine kante auf dem Rand zum Anfangen */
KANTE *run;
PLANMAP map;
BBITEMLISTE *upitem, *lowitem;
KNOTENTYP code[20];
int modulozaehler;

modulozaehler=rest;

init_map(map);

adresse[0]=6;
code[1]=1; code[19]=leer;

for (bblaenge=minbbl; bblaenge <= maxbbl; bblaenge++)
  if (bblmark[bblaenge])
  { adresse[2]=bblaenge;
    code[0]=2*bblaenge;
    for (sechsecke=min_sechsecke; sechsecke <= max_sechsecke; sechsecke++)
    for (upper6gons=sechsecke, lower6gons=0; upper6gons >= lower6gons;
	 upper6gons--, lower6gons++)
         { adresse[1]=upper6gons;
	   for (upitem=suche_item_bb(adresse); upitem != nil;
		upitem=upitem->next_item)
	       { adresse[1]=lower6gons; merkeanfang=nil;
		 for (k=0; k<8; k++) code[k+10]=upitem->code[k];
		 for (lowitem=suche_item_bb(adresse); lowitem!=nil; lowitem=lowitem->next_item)
		   if ((lowitem->code[0]==0) && 
		        ((upper6gons>lower6gons) || (codecmp(upitem->code+2,lowitem->code+2,6)>=0)))
		     /* hier geht schon die minimalitaet ein: Wenn es einen 6-Eck-Ring gibt, kann der
			nach oben verschoben werden und upper6gons wird noch groesser, lowercode
			noch kleiner, der code also besser
			Im Fall upper6gons==lower6gons,"(uppercode+2)<(lowercode+2)",aber upper6gons hat
			einen 6-eck-ring, kann ein besserer code durch verschieben des ringes und vertauschen
			von oben und unten gebaut werden  */
		     { modulozaehler++;
		       if (modulozaehler==mod) modulozaehler=0;
		       if (!mod || (modulozaehler==0))
			 { /* so dass nur gebaut wird, wenn auch ein passendes Unterteil gefunden wird
			      und auch dann nur einmal: */
			   if (merkeanfang==nil) { map[0][0].name=0;
						   anzahl_5ek=0;
						   baue_kuppe(map,bblaenge,upitem->code,&merkeanfang,upper6gons+6); }
			   for (k=0; k<8; k++) code[k+2]=lowitem->code[k];
			   for (i=0, anfang=merkeanfang; (i<lowitem->code[1]) && (i<upitem->code[1]); i++, 
				anfang=anfang->prev->invers->prev->invers->prev)
			     { code[18]=i;
			       anzahl_5ek=30;
			       baue_kuppe(map,bblaenge,lowitem->code,&anfang,lower6gons+6);
			       if ( is_ipr ) teste_und_schreibe(map,code); else is_ipr=1;
			       /* Falls IPR nicht gesetzt ist, ist is_ipr immer 1 */
			       /* Aufraeumen: */
			       for (run=anfang, j=0; j<bblaenge; 
				    j++, run=run->next->invers->next->invers->next) run->name = aussen;
			       map[0][0].name -= (2*lower6gons + 10 -bblaenge);
			     } /* ende for ueber moegliche Marken bei lowitems */
			 } /* ende if modulo */
		     } /* ende for ueber lowitems */
	       } /* ende for ueber upitems */
	 } /* ende for ueber 6-Eckverteilung */
  } /* ende for ueber bauchbindenlaenge */
} /* ende funktion */



/***********************SUCHESTART********************************/

KANTE *suchestart( KANTE *start)
/* belegt eine sequenz und sucht die kanonische Kante mit dem kleinsten Namen 
   arbeitet "invers", d.h. es wird als Innenrand gesehen, der gefuellt werden
   muss. Wird aufgerufen fuer Brille und Sandwich. Start muss eine Kante sein, die
   ins innere zeigt.*/

{
int i, j, k, zaehler, position;
KANTE *run;
int sequenz[7]; 
KANTE *seqkanten[7];
int puffer[7];
char kan[7];



while (start->next->invers->next->invers->next->name == aussen) 
                      start=start->next->invers->next->invers->next;
/* Sucht 2 Kanten hintereinander nach aussen -- zu unterscheiden vom namen aussen, was 
   auch nach innen heissen kann. Duerfte nur fuer bauchbinden eine Endlosschleife sein */

for (i=0; i<7; i++) { sequenz[i]=leer; seqkanten[i]=nil; kan[i]=0; }

position=0;
seqkanten[0]=start;


for (zaehler=1, run=start;
     run->prev->invers->prev->invers->prev->name == aussen;
     run=run->prev->invers->prev->invers->prev) zaehler++;
sequenz[0]=zaehler; position=1; seqkanten[1]=nil;
for (run=run->prev->invers->prev->invers->prev->invers->prev; run->name != aussen;
     run=run->invers->prev) 
{ sequenz[position]=0; position++; seqkanten[position]=nil; }
/* naechste Kante vor nicht-0-sequenz suchen -- entsprechende innenkanten gibt es nicht
   und muessen sich dementsprechend auch nicht gemerkt werden */


while (run != start)
{
seqkanten[position]=run;
for (zaehler=1; 
     run->prev->invers->prev->invers->prev->name == aussen;
     run=run->prev->invers->prev->invers->prev) { zaehler++; }
sequenz[position]=zaehler; position++; seqkanten[position]=nil;
for (run=run->prev->invers->prev->invers->prev->invers->prev; run->name != aussen;
     run=run->invers->prev) 
{ sequenz[position]=0; position++; seqkanten[position]=nil; }
}


sequenz[position]=leer; seqkanten[position]=nil;

kan[0]=sequenz_kanonisch(sequenz);


for (i=0; sequenz[i] != leer; i++)
  { for (j=i, k=0; sequenz[j]!=leer; j++, k++) puffer[k]=sequenz[j];
    for (j=0; j<i; j++, k++) puffer[k]=sequenz[j];
    puffer[k]=leer;
    kan[i]=sequenz_kanonisch(puffer);
  }



for (i=0, run=nil; sequenz[i] != leer; i++)
  { if (kan[i])
      if ((run==nil) || (seqkanten[i]->ursprung < run->ursprung)) run=seqkanten[i];
  }

/* Jetzt die vorige Innenkante suchen, um rechts davon dann einfuegen zu koennen */
for (run=run->next->invers->next->invers->next; run->name != aussen; run=run->invers->next);


return(run);


}

/*******************BERECHNE_BRILLENADRESSEN*************************/

/* berechnet die adressen 2 und 3 im Brillenfall .
   uebergeben werden l1 l3 und lgesamt. berechnet werden die
   sequenzen */

void berechne_brillenadressen( int l1, int lg, int l3, KNOTENTYP *seg,
			      KNOTENTYP *se3 )
{int l2, zaehler;
 int bogen1, bogen3; 

l2 = lg - l1 - l3;


if ((l1%2) != 0) lg--;

if ((l3 % 2) ==0)   /* l3 gerade */
  { se3[0]=4; se3[2]= (l3-2)/2; se3[3]=0; }
else { se3[0]=5; se3[2]= (l3-1)/2; lg--; }

/* Jetzt die grosse Sequenz: */

if ((l2 % 2) == 0) /* "normale" Brille */
  {
    if (l1%2) /* d.h. ungerade -- bestimmt den Umlaufsinn */
       { if ((lg % 2)==0) seg[2]=lg/2; else seg[2]= (lg-1)/2;
         zaehler=3;
	 if (l3 % 2) { seg[zaehler]=0; zaehler++; }
	 seg[zaehler]= (l2-2)/2; zaehler++; 
	 if (l1 % 2) { seg[zaehler]=0; zaehler++; }
	 seg[0]=8-zaehler;
       }
    else /* d.h. l1 gerade -- anderer Umlaufsinn */
       { if ((lg % 2)==0) seg[2]=lg/2; else seg[2]= (lg-1)/2;
         zaehler=3;
	 if (l1 % 2) { seg[zaehler]=0; zaehler++; }
	 seg[zaehler]= (l2-2)/2; zaehler++; 
	 if (l3 % 2) { seg[zaehler]=0; zaehler++; }
	 seg[0]=8-zaehler;
       }
  }/* ende "normale" Brille */ 
else /* d.h. "verbogene" Brille */
  {
    if (l1%2) bogen1= (l1+l2-2)/2; else bogen1=(l1+l2-1)/2; 
    if (l3%2) bogen3= (l3+l2-2)/2; else bogen3=(l3+l2-1)/2; 
    /* um das gleich kanonisch geordnet zu haben, muss da unterschieden werden */
    if (l1%2){
             /* l1 >= l3 reicht nicht, um die folgende Fallunterscheidung zu vermeiden */
             if ((bogen1 > bogen3) || ((bogen1==bogen3) && ((l3 % 2) == 0)))
	       { seg[2]=bogen1;
		 zaehler=3;
		 if (l3 % 2) { seg[zaehler]=0; zaehler++; }
		 seg[zaehler]=bogen3; zaehler++;
		 if (l1 % 2) { seg[zaehler]=0; zaehler++; }
		 seg[0]=8-zaehler;
	       }
	     else /* d.h. bogen3 kommt zuerst */
	       { seg[2]=bogen3;
		 zaehler=3;
		 if (l1 % 2) { seg[zaehler]=0; zaehler++; }
		 seg[zaehler]=bogen1; zaehler++;
		 if (l3 % 2) { seg[zaehler]=0; zaehler++; }
		 seg[0]=8-zaehler;
	       }
	   }
    else /* d.h. l1 gerade */
      { 
	/* keine Fallunterscheidung, da if immer true durch konvention l1>=l3 */
        /* if ((bogen1 > bogen3) || ((bogen1==bogen3) && ((l1 % 2) == 0))) */
	         seg[2]=bogen1;
		 seg[3]=bogen3; 
		 zaehler=4;
		 if (l3 % 2) { seg[zaehler]=0; zaehler++; }
		 seg[0]=8-zaehler;
       } 
  } /* ende verbogene brille */

}

/********************BAUE_BRILLE***********************************/

/* baut eine Brille. Dabei ist die Orientierung von Knoten mit 
   ungerader Nummer auf dem Pfad  immer vorher->aussen->nachher 
   GEWAEHLT.  Da zu jedem Patch frueher oder spaeter
   auch das Spiegelbild behandelt wird, ist diese Festlegung moeglich,
   aber Achtung -- das ist wichtig fuer die kanonische Darstellung */

void baue_brille(int pfadlaenge,int laenge_1,int laenge_3,PLANMAP map, 
		 KANTE **anfang_1, KANTE **anfang_2, KANTE **anfang_3)
{
int stelle_2, knotenzahl, i;
KANTE *aussenzeiger, *letzte_Kante, *startkante_1, *startkante_2;

knotenzahl=pfadlaenge-1;

/* zuerst:

    knotenzahl-------stelle_2----------stelle1-------
                                                    |
                                           1        |
					   |        |
					   2--3-----
ohne die zykelschliessenden Kanten */



map[1][1].name=2; map[1][1].invers=map[2]+0; 
for (i=1; i<=knotenzahl; i++)
  { map[i][0].name=i-1; map[i][0].invers=map[i-1]+1; 
    map[i][1].name=aussen; map[i][1].invers=nil;
    map[i][2].name=i+1; map[i][2].invers=map[i+1]+0; 
    i++;
    if (i<=knotenzahl)
      { map[i][0].name=i-1; map[i][0].invers=map[i-1]+2; 
	map[i][2].name=aussen; map[i][2].invers=nil;
	map[i][1].name=i+1; map[i][1].invers=map[i+1]+0; }
   }

/* Knoten 1 und Knoten knotenzahl haben jetzt falsche vorher bzw nachher
   werte, sie muessen jetzt mit der Brille verklebt werden */
   
if ((laenge_1%2)==0) aussenzeiger=map[laenge_1]+2; else aussenzeiger=map[laenge_1]+1;

aussenzeiger->name=1; aussenzeiger->invers=map[1]+0;
map[1][0].name=laenge_1; map[1][0].invers=aussenzeiger;

stelle_2=pfadlaenge-laenge_3;
if ((stelle_2%2)==0) aussenzeiger=map[stelle_2]+2; else aussenzeiger=map[stelle_2]+1;
if ((knotenzahl%2)==0) letzte_Kante=map[knotenzahl]+1; else letzte_Kante=map[knotenzahl]+2;

letzte_Kante->name=stelle_2; letzte_Kante->invers=aussenzeiger;
aussenzeiger->name=knotenzahl; aussenzeiger->invers=letzte_Kante;

map[0][0].name=knotenzahl;

/* Jetzt die anfangskanten belegen: */

if ((laenge_1 %2)==0) { startkante_1=map[2]+2; startkante_2=map[1]+1; }
                     /* dann zeigt die Aussenkante von Knoten 2 ins innere von zykel_1 */
               else  { startkante_2=map[2]+2; startkante_1=map[1]+1; }
*anfang_1=suchestart(startkante_1);
*anfang_2=suchestart(startkante_2);

if ((knotenzahl%2)==0)
  { if ((laenge_3 % 2)==0) startkante_1=map[knotenzahl-1]+1;
       else startkante_1=map[knotenzahl]+2; }
  else /* d.h. knotenzahl ungerade */
  { if ((laenge_3 % 2)==0) startkante_1=map[knotenzahl-1]+2;
       else startkante_1=map[knotenzahl]+1; }
*anfang_3=suchestart(startkante_1);

} /* ende funktion */



/*********************INSERT_PATCH*********************************/

void insert_patch(PLANMAP map, KANTE *anfang, ITEMLISTE *item, int flaechenzahl, int fuenfecke)
{

FLAECHENTYP *code;
KANTE *run;
int zaehler, codestelle;

code=item->code;
    for (codestelle=0, zaehler=1, run=anfang; run != nil; zaehler++ )
      { 
	if ((codestelle<fuenfecke) && (code[codestelle]==zaehler))
          { add_polygon_invers(5, map, run, &run); codestelle++; }
        else add_polygon_invers(6, map, run, &run);
      }
        if (zaehler != flaechenzahl) 
	  { fprintf(stderr,"Insert_patch: Could not insert enough faces: ");
	    fprintf(stderr,"%d instead of %d\n (insert_patch)\n",zaehler,flaechenzahl);
	    exit(92); }
}


/**********************DELETE_PATCH**************************************/

void delete_patch(PLANMAP map, KANTE *anfang, KNOTENTYP *adresse)
{
int sqlaenge, randlaenge, i, j, knotenverlust;
KANTE *run;

sqlaenge=6-adresse[0];
for (i=2, randlaenge=sqlaenge; i<= 1+sqlaenge; i++) randlaenge+=(2*adresse[i]);

knotenverlust=(3*adresse[0])+randlaenge;
knotenverlust= knotenverlust/2;  /* diese konstruktion nur Sicherheitshalber, damit kein
				    Compiler die Ordnung "erst 3a[0]+r" aufloest */
knotenverlust= knotenverlust+(2*adresse[1])+1-randlaenge;
/*alles nur Euler-Formel*/

map[0][0].name = map[0][0].name - knotenverlust;

for (i=1+sqlaenge; adresse[i]==0; i--);
for ( run=anfang ; i>1 ; i--)
  { if (adresse[i])
      { for (j=0; j < adresse[i]; j++)
	  { 
	    run->name=aussen; run->invers=nil; run = run->next->invers->next->invers->next; }
	run=run->invers->next;
      }
    else { run=run->invers->next; }
  }
}



/*********************BRILLE****************************************/

/* Der zweite Fall der Fullerenkonstruktion: Fullerene mit Brille */
/*

                          | l2 |
                 _________________________ 
        	/       |         |       \
               |   l3   |         |   l1   |
                \______/           \______/


                 _______ 	 oder 
               /        \
              |          |
               \_________|_____________________
                                     |         \
                                     |          |
                                      \________/

Der Unterschied ist, ob das Mittelstueck l2 gerade oder ungerade viele
Kanten enthaelt --- kombinatorisch ist es einfach ein Graph mit 2
Knoten, die durch eine Kante verbunden sind und jeder hat eine
Schleife (eine "Hantel").

Die Brille wird als Pfad mit Anfang und Ende interpretiert mit l1 >=
l3, d.h. erste Schleife nicht kleiner als zweite und Orientierung um
ungerade Knoten vorher->aussen->nachher

Die Markierungen sind die nach dieser Ordnung vom kleinsten Knoten
ausgehenden Kanten mit folgender kanonischer Sequenz. Sie sind an der
letzten Innenkante des ersten einzufuegenden Polygons.


Der gesamtcode: (pfadlaenge,2,l1,l3,code1[],code2[],code3[])
gesamtcodelaenge:16

 */



void brille(int min_sechsecke, int max_sechsecke) 
{ 
int knotenzahl, pfadlaenge, s1ps2; 
int laenge_1, laenge_3; 
KNOTENTYP adresse_1[6], adresse_2[6],adresse_3[6];
int sixgons_1, sixgons_2, sixgons_3; /* zur besseren lesbarkeit -- es koennte auch immer adresse_i[1] 
					benutzt werden */
KANTE *anfang_1, *anfang_2, *anfang_3; /* eine kanonische Kante auf dem Rand zum Anfangen */ 
ITEMLISTE *item_1, *item_2, *item_3; 
BOOL gebaut_1, gebaut_2, ipr_fault_item2; 
PLANMAP map;
KNOTENTYP code[20];
int j, czmerke_1, czmerke_2, czmerke_3;
int modulozaehler;

modulozaehler=rest;

knotenzahl= 20 + 2*max_sechsecke;

init_map(map);

code[1]=2;

for (pfadlaenge=2*minbrillenglas+1; pfadlaenge <= knotenzahl+1; pfadlaenge++) 
  { /* EINZIGE Konvention: laenge_1 >= laenge_3 --- dann darf keine konvention 
       fuer die 6-Ecke mehr erfolgen ! */ 
    code[0]=pfadlaenge;
    for (laenge_1=minbrillenglas; (laenge_1 <= maxbrillenglas) &&
	                            (laenge_1 < pfadlaenge-minbrillenglas); laenge_1++) 
      if (brillenglasmark[laenge_1])
      { if ((laenge_1 % 2)==0) 
	  { adresse_1[0]=4; adresse_1[2]=(laenge_1-2)/2; adresse_1[3]=0; } 
        else { adresse_1[0]=5; adresse_1[2]=(laenge_1-1)/2; } 	
	code[2]=laenge_1;
	for (sixgons_1=0; sixgons_1 <= max_sechsecke; sixgons_1++) 
	  /* auch hier kann man besser abschaetzen */ 	 
	  { adresse_1[1]=sixgons_1;
	    for (item_1=suche_item(adresse_1); item_1 != nil; item_1=item_1->next_item) 	 
	      { 
		czmerke_1=4+adresse_1[0];
		for (j=4; j<czmerke_1; j++) code[j]=item_1->code[j-4];
 		for (laenge_3=minbrillenglas; 
		     (laenge_3 <= laenge_1) && (laenge_1+laenge_3 < pfadlaenge); laenge_3++)
		 if (brillenglasmark[laenge_3])
 		 {
		   modulozaehler++;
		   if (modulozaehler==mod) modulozaehler=0;
		   if (!mod || (modulozaehler==0))
		     {
		       code[3]=laenge_3;
		       berechne_brillenadressen(laenge_1,pfadlaenge,laenge_3,adresse_2,adresse_3);
		       gebaut_1=0; /* Man koennte auch patch_1 immer in der aeusseren
				      Schleife bauen und dann die Brille verschieden fortsetzen, aber erst Brille bauen 
				      und dann die patches einkleben erscheint mir sympathischer und weniger fehleranfaellig --
				      wenn auch von der Komplexitaet her ein wenig schlechter */ 
		       for (sixgons_2=0; sixgons_2 <= max_sechsecke-sixgons_1; sixgons_2++)
			 { s1ps2=sixgons_1 + sixgons_2;
			   adresse_2[1]=sixgons_2;
			   for (sixgons_3=max_sechsecke-s1ps2; (sixgons_3>=min_sechsecke-s1ps2) && (sixgons_3>=0);
				sixgons_3--)
			     {
			       adresse_3[1]=sixgons_3;
			       for (item_2=suche_item(adresse_2); item_2 != nil; item_2=item_2->next_item)
				 { is_ipr=1; ipr_fault_item2=0;
				   gebaut_2=0;
				   czmerke_2=czmerke_1+adresse_2[0];
				   for (j=czmerke_1; j<czmerke_2; j++) code[j]=item_2->code[j-czmerke_1];
				   for (item_3=suche_item(adresse_3); (item_3 != nil) && (!ipr_fault_item2); 
					item_3=item_3->next_item) 	  
				     { czmerke_3=czmerke_2+adresse_3[0];
				       for (j=czmerke_2; j<czmerke_3; j++) code[j]=item_3->code[j-czmerke_2];
				       if (gebaut_1==0) {
					 anzahl_5ek=0;
					 baue_brille(pfadlaenge,laenge_1,laenge_3,map, &anfang_1, &anfang_2,&anfang_3);
					 insert_patch(map,anfang_1,item_1,sixgons_1+adresse_1[0],adresse_1[0]); 
					 gebaut_1=1;
				       }
				       if (gebaut_2==0) 
					 { anzahl_5ek=5*adresse_1[0];
					   insert_patch(map,anfang_2,item_2,sixgons_2+adresse_2[0],adresse_2[0]); 
					   gebaut_2=1;
					   if (is_ipr==0) ipr_fault_item2=1;}
				       anzahl_5ek=5*(12-adresse_3[0]);
				       if (is_ipr) 
					 { insert_patch(map,anfang_3,item_3,sixgons_3+adresse_3[0],adresse_3[0]);
					   if (is_ipr) teste_und_schreibe(map,code); else is_ipr=1;
					   delete_patch(map,anfang_3,adresse_3); }
				     } /* ende for ueber item_3 */
				   if (gebaut_2) delete_patch(map,anfang_2,adresse_2);
				 } /* ende for ueber item_2 */
			     } /* ende for ueber sixgons_3 */
			 } /* ende for ueber sixgons_2 */
		       map[0][0].name=0; /* entspricht loeschen von map */
		     }
 		 } /* ende for ueber laenge_3 */
	      } /* ende for ueber item_1 */
	  } /* ende for ueber sixgons_1 */
      } /* ende for ueber laenge_1 */ 
  } /* ende for ueber pfadlaenge */
 } /* ende funktion */


/*********************BERECHNE_ADRESSE3********************************/

void berechne_adresse3(int l1, int l3, KNOTENTYP adresse[]) 
{
int sl1, sl3;

if (l1%2) { sl1=(l1-1)/2; 
	    if (l3%2) { sl3=(l3-1)/2; adresse[0]=4;
			if (sl3>sl1) { adresse[2]=sl3; adresse[3]=sl1; } 
			else { adresse[2]=sl1; adresse[3]=sl3; }
		      } else /* d.h. l3 gerade */
			{ sl3=(l3-2)/2;
			  adresse[0]=3;
			  if (sl3>sl1) { adresse[2]=sl3; adresse[3]=0; adresse[4]=sl1; }
			  else { adresse[2]=sl1;
				 adresse[3]=sl3; adresse[4]=0; }
			}
	  }

else { sl1=(l1-2)/2; 
       if (l3%2) { sl3=(l3-1)/2;
		   adresse[0]=3;
		   if (sl3>sl1) { adresse[2]=sl3; adresse[3]=0; adresse[4]=sl1; } 
		   else { adresse[2]=sl1; adresse[3]=sl3; adresse[4]=0; }
		 } else /*d.h. l3 gerade */ 
		   { sl3=(l3-2)/2;
		     adresse[0]=2; 
		     if (sl3>sl1) { adresse[2]=sl3; adresse[3]=0; adresse[4]=sl1; adresse[5]=0; } 
		     else { adresse[2]=sl1; adresse[3]=0; adresse[4]=sl3; adresse[5]=0; }
		   }
     }
 }


/*********************BAUE_SANDWICH***********************************/

void baue_sandwich(PLANMAP map, int laenge_1, int laenge_2, int laenge_3,
		   KANTE **anfang_1, KANTE **anfang_2, KANTE **anfang_3) 

{ int stelle_2, knotenzahl, i, stelle, pfadlaenge; 
KANTE *aussenzeiger, *letzte_Kante, *startkante_1, *startkante_2,*startkante_3;

pfadlaenge=laenge_1+laenge_2+laenge_3; knotenzahl=pfadlaenge-1;


map[1][1].name=2; map[1][1].invers=map[2]+0; 
for (i=1; i<=knotenzahl; i++) 
  { map[i][0].name=i-1; map[i][0].invers=map[i-1]+1;
    map[i][1].name=aussen; map[i][1].invers=nil; 
    map[i][2].name=i+1; map[i][2].invers=map[i+1]+0; 
    i++; 
    if (i<=knotenzahl) {
      map[i][0].name=i-1; map[i][0].invers=map[i-1]+2;
      map[i][2].name=aussen; map[i][2].invers=nil;
      map[i][1].name=i+1; map[i][1].invers=map[i+1]+0;
    }
  }

/* Knoten 1 und Knoten knotenzahl haben jetzt falsche vorher bzw
   nachher werte, sie muessen jetzt mit dem Sandwich verklebt werden */

stelle=laenge_1+laenge_2; 
if ((stelle%2)==0) aussenzeiger=map[stelle]+2; else aussenzeiger=map[stelle]+1;

aussenzeiger->name=1; aussenzeiger->invers=map[1]+0;
map[1][0].name=stelle; map[1][0].invers=aussenzeiger;

if ((laenge_1%2)==0) aussenzeiger=map[laenge_1]+2; 
else aussenzeiger=map[laenge_1]+1; 
if ((knotenzahl%2)==0) letzte_Kante=map[knotenzahl]+1; else letzte_Kante=map[knotenzahl]+2;

letzte_Kante->name=laenge_1; letzte_Kante->invers=aussenzeiger;
aussenzeiger->name=knotenzahl; aussenzeiger->invers=letzte_Kante;

map[0][0].name=knotenzahl;

/* Jetzt die anfangskanten belegen: */

if (laenge_2==1) stelle_2= stelle+1; else stelle_2=stelle-1;
if (stelle %2) { startkante_1=map[1]+1; startkante_2=map[stelle_2]+2; startkante_3=map[2]+2; } 
/* dann zeigt die Aussenkante von Knoten 1 ins innere von zykel_1 */ 
else { startkante_1=map[2]+2; startkante_2=map[stelle_2]+1; startkante_3=map[1]+1; }
*anfang_1=suchestart(startkante_1);
*anfang_2=suchestart(startkante_2);
*anfang_3=suchestart(startkante_3);

} /* ende funktion */







/************************SANDWICH***************************************/

/* Sandwich ist der 3. Fall :

                          l1 
		   -------------------- 	 
		 /                      \
		/      l2 oder l3        \
       	       O--------------------------O
	        \                        /
		 \     l2 oder l3       /
 		   --------------------

d.h.:

		        l1 
		  -----------------
 		/                   \ 
	       O                     |
	         ______l2___________/
		/ 
	       |                   ^ 
	       |                   |
	        \______l3_________/

oder das Spiegelbild:

		        l1 
		  -----------------
	        /                   \ 
	       O                     |
	          ______l3_________> |
		 /                   |
		|                    | 
		|                    |
		 \______l2__________/


 l2 muss immer ungerade sein !

Konvention: Die Orientierung um Knoten 1 und damit alle ungeraden
Knoten auf dem Pfad ist vorher->aussen->nachher und desweiteren: 
l1 >= l3 

Der gesamtcode: (pfadlaenge,3,l1,l2,code1[],code2[],code3[])
gesamtcodelaenge:16


*/



void sandwich (int min_sechsecke, int max_sechsecke)

{ 
int knotenzahl, maxpfadlaenge, s1ps2; 
int laenge_1, laenge_2, laenge_3;
KNOTENTYP adresse_1[6], adresse_2[6], adresse_3[6]; 
int sixgons_1, sixgons_2, sixgons_3; /* zur besseren lesbarkeit -- es koennte auch
					immer adresse_i[1] benutzt werden. s_1 ist 
					die Anzahl der 6-Ecke zwischen l1 und l2. s_2 zwischen
					l2 und l3 und s_3..... analog fuer adresse und item */ 
KANTE *anfang_1, *anfang_2, *anfang_3; /* eine kanonische Kante auf dem Rand zum Anfangen */ 
ITEMLISTE *item_1, *item_2, *item_3; 
int randl_p1, randl_p2, randl_p3; 
BOOL gebaut_1, gebaut_2, ipr_fault_item2; 
PLANMAP map;
KNOTENTYP code[20];
int j, czmerke_1, czmerke_2, czmerke_3;
int modulozaehler;

modulozaehler=rest;
/* l1--l2  und  l2--l3  bilden je ein brillenglas */


knotenzahl= 20 + 2*max_sechsecke; maxpfadlaenge=knotenzahl+1;
init_map(map);
code[1]=3;

for (laenge_1=(min_2_3_4 /2); laenge_1 <= maxpfadlaenge-minbrillenglas; laenge_1++) 
  { 
  code[2]=laenge_1;
  for (laenge_2=1; laenge_2 <= maxpfadlaenge-min_2_3_4; laenge_2 += 2) /* muss immer ungerade sein ! */ 
  { randl_p1=laenge_1+laenge_2;
    if (brillenglasmark[randl_p1])
    { /* l1+l2 umrahmt patch 1 */
       code[3]=laenge_2;
 	if (randl_p1%2) { adresse_1[0]=5; adresse_1[2]=(randl_p1-1)/2; }
 	 else { adresse_1[0]=4; adresse_1[2]=(randl_p1-2)/2; adresse_1[3]=0; }
 	for (sixgons_1=0; sixgons_1 <= max_sechsecke; sixgons_1++)
 	 { 	
	   adresse_1[1]=sixgons_1;
	   for (item_1=suche_item(adresse_1); item_1 != nil; item_1=item_1->next_item)
	     { 	
	       modulozaehler++;
	       if (modulozaehler==mod) modulozaehler=0;
	       if (!mod || (modulozaehler==0))
		 {
		   czmerke_1=4+adresse_1[0];
		   for (j=4; j<czmerke_1; j++) code[j]=item_1->code[j-4];
		   for (laenge_3=1; ((randl_p1 + laenge_3) <= maxpfadlaenge) && (laenge_1>= laenge_3); laenge_3++)
		     { randl_p2=laenge_2+laenge_3;
		       randl_p3=laenge_3+laenge_1;
		       if (brillenglasmark[randl_p2] && zwei_3_4_mark[randl_p3])
			 { code[0]=laenge_3 + randl_p1;
			   gebaut_1=0;
			   if (randl_p2%2) { adresse_2[0]=5; adresse_2[2]=(randl_p2-1)/2; } 	 
			   else { adresse_2[0]=4; adresse_2[2]=(randl_p2-2)/2; adresse_2[3]=0; }
			   /* fuer den patch zwischen l1 und l3 ist die Lage leider komplizierter */ 	
			   berechne_adresse3(laenge_1,laenge_3,adresse_3);
			   for (sixgons_2=0; sixgons_2 <= max_sechsecke-sixgons_1; sixgons_2++)
			     { s1ps2=sixgons_1 + sixgons_2;
			       adresse_2[1]=sixgons_2;
			       for (sixgons_3=max_sechsecke-s1ps2; (sixgons_3>=min_sechsecke-s1ps2) && (sixgons_3>=0);
				    sixgons_3--)
				 { 
				   adresse_3[1]=sixgons_3;
				   for (item_2=suche_item(adresse_2); item_2 != nil; item_2=item_2->next_item)
				     { is_ipr=1; ipr_fault_item2=0;
				       gebaut_2=0;
				       czmerke_2=czmerke_1+adresse_2[0];
				       for (j=czmerke_1; j<czmerke_2; j++) code[j]=item_2->code[j-czmerke_1];
				       for (item_3=suche_item(adresse_3); (item_3 != nil) && (!ipr_fault_item2); 
					    item_3=item_3->next_item)
					 {
					   czmerke_3=czmerke_2+adresse_3[0];
					   for (j=czmerke_2; j<czmerke_3; j++) code[j]=item_3->code[j-czmerke_2];
					   /* Der Kern */
					   if (gebaut_1==0) 			 
					     { anzahl_5ek=0;
					       baue_sandwich(map,laenge_1,laenge_2,laenge_3,&anfang_1,&anfang_2,&anfang_3);
					       gebaut_1=1;
					       insert_patch(map,anfang_1,item_1,sixgons_1+adresse_1[0],adresse_1[0]); }
					   if (gebaut_2==0)
					     { anzahl_5ek= 5*adresse_1[0];
					       insert_patch(map,anfang_2,item_2,sixgons_2+adresse_2[0],adresse_2[0]); 
					       gebaut_2=1;
					       if (is_ipr==0) ipr_fault_item2=1; }
					   anzahl_5ek=5*(12-adresse_3[0]);
					   if (is_ipr) 
					     { insert_patch(map,anfang_3,item_3,sixgons_3+adresse_3[0],adresse_3[0]);
					       if (is_ipr) teste_und_schreibe(map,code); else is_ipr=1;
					       delete_patch(map,anfang_3,adresse_3); }
					   /* Ende Kern */
					   
					   
					 } /* ende for ueber item_3 */ 
				       if (gebaut_2) delete_patch(map,anfang_2,adresse_2);
				     } /*ende for ueber item_2 */
				 } /* ende for ueber sixgons_3 */
			     } /* ende for ueber sixgons_2 */ 
			   map[0][0].name=0; /* entspricht loeschen */
			 } /* ende if randl_p2 und randl_p3 OK */
		     } /* ende for ueber laenge_3 */
		 }
	     } /* ende for ueber item_1 */
	 } /* ende for ueber sixgons_1 */ 
     } /* ende if randl_p1 OK */
  } /* ende for ueber laenge_2; */
} /* ende for ueber laenge_1 */

} /* ende funktion */


/**************************MAIN*********************************************/

int main(int argc, char *argv[])

{ int sechsecke, i, puffer, do_case;
  char strpuf[filenamenlaenge], strpuf2[filenamenlaenge], strdummy[filenamenlaenge+3];
  struct stat buf;
  char name[4];     /* TH - fuer die Option "symm" */
  FLAECHENTYP dummycode[12]={UCHAR_MAX,UCHAR_MAX,UCHAR_MAX,0,0,0,0,0,0,0,0,0}; 
  FLAECHENTYP *dummypointer;

#ifndef NOTIMES
  clock_t savetime=0, buffertime;
  struct tms TMS;
#endif //NOTIMES

  int separate_logfile = 1;

#ifdef __GNUC__
#ifdef __alpha__
fprintf(stderr,"With gcc on alphas some errors might occur if you use -O3 or more.\n");
fprintf(stderr,"This is a bug of the compiler.\n");
fprintf(stderr,"Please use cc on alphas -- the result will be a faster program anyway.\n");
exit(0);
#endif
#endif


for (i=1;i<=N;i++) graphenzahl[i]=non_iso_graphenzahl[i]=0;

do_brille=do_sandwich=do_bauchbinde=1;

do_case=0;


symmstring[0] = 0;       /* TH - Filekennung loeschen */

if (argc<2) exit(93);


knotenzahl=atoi(argv[1]);
if ((knotenzahl%2) || (knotenzahl<20)) { fprintf(stderr,"Impossible vertex number. \n"); exit(94); }

min_sechsecke=max_sechsecke=sechsecke=(knotenzahl-20)/2;


if (knotenzahl >= leer) { fprintf(stderr,"Number of vertices too large for the data-types used. \n"); exit(95); }
if (aussen >= leer) { fprintf(stderr,"Definition of \"S\" too large for the data-types used. \n"); exit(96); }
if (S+12 > FL_MAX) { fprintf(stderr,"Definition of \"S\" too large for the data-types used for FLAECHENTYP. \n");
		     exit(97); }

if (sechsecke > S) { fprintf(stderr,"Fix the constant \"S\" to at least %d\n",sechsecke); exit(98); }

codenumber=listenlaenge=0;

for (i=2; i<argc; i++)
    switch (argv[i][0])
      {
      case 'i': { if (strcmp(argv[i],"ipr")==0) IPR=1;
		    else { fprintf(stderr,"Nonidentified option: %s \n",argv[i]); exit(99); }
		  break; }

      case 'h': { if (strcmp(argv[i],"hexspi")==0) hexspi=1;
		    else { fprintf(stderr,"Nonidentified option: %s \n",argv[i]); exit(100); }
		  break; }

      case 's': { if (strcmp(argv[i],"start")==0)
		    { i++; puffer=atoi(argv[i]); 
		      if ((puffer%2) || (puffer<20)) 
			{ fprintf(stderr,"Impossible vertex number to start. \n"); exit(101); }
		      min_sechsecke=(puffer-20)/2; }
                    else
		      if (strcmp(argv[i],"stdout")==0) to_stdout=1;
                    else
		      if (strcmp(argv[i],"spistat")==0) spistat=1;
                    else
		      if (strcmp(argv[i],"spiralcheck")==0) spiralcheck=1;
                    else
                      if (strcmp(argv[i],"symstat")==0) symstat=1;   /* TH */
                    else
                      if (strcmp(argv[i],"symm")==0) {               /* TH */
                        int j=28, ii;
                        BOOL gefunden = False;
 			symstat=1;                /* immer -- kostet ja nichts extra */
                        i++;
                        if (i<argc) {
                          while (j>0 && !gefunden) {
                            for (ii=0; ii<=3; ii++) {
                              name[ii] = (symm_name[j][ii]==' ') ? '\0' : symm_name[j][ii]; 
                            }
                            if (strcmp(argv[i],name)==0) {      /* Symmetrie j gefunden */
                              gefunden = True;
                              if (!vergleiche_symm(j))   /* Symmetrie noch nicht in Liste */
                                {symm[symm_len++] = j;  
                                 strcat(symmstring,(char *)"_"); strcat(symmstring,name);}
                            } 
                            j--;
                          }
                        }
                        if (!gefunden) 
                           {fprintf(stderr,"Unknown symmetry identifier. \n"); exit(102);}
                        break;
                      }  /* if */ 
		    else { fprintf(stderr,"Nonidentified option: %s \n",argv[i]); exit(103); }
		  break; }
      case 'c': { if (strcmp(argv[i],"code")==0)
		    { i++; codenumber=atoi(argv[i]); }
		  else
		    if (strcmp(argv[i],"case")==0)
		    { i++; do_case=atoi(argv[i]);
		      switch (do_case)
			{ case 1: { do_brille=do_sandwich=0; do_bauchbinde=1; break; }
			  case 2: { do_brille=1; do_sandwich=do_bauchbinde=0; break; }
			  case 3: { do_brille=do_bauchbinde=0; do_sandwich=1; break; }
			 default: { fprintf(stderr,"No such case !\n"); exit(104); }
			}
		      }
		    else { fprintf(stderr,"Nonidentified option: %s \n",argv[i]); exit(105); }
		  break; }
      case 'p': { if (strcmp(argv[i],"pid")==0) {fprintf(stdout,"%d\n",getpid());  fflush(stdout);}
                  else {fprintf(stderr,"Nonidentified option: %s \n",argv[i]); exit(119);}
                  break;
                }   
      case 'q': { if (strcmp(argv[i],"quiet")==0) quiet=1;
                  else {fprintf(stderr,"Nonidentified option: %s \n",argv[i]); exit(120);}
                  break;
                }   
      case 'l': { if (strcmp(argv[i],"list")==0)
		    { i++; listenlaenge=atoi(argv[i]); }
		  else if (strcmp(argv[i],"logerr")==0) {
		    logfile = stderr;
		    separate_logfile = 0;
		  }
		  else { fprintf(stderr,"Nonidentified option: %s \n",argv[i]); exit(106); }
		  break; }

      case 'm': { if (strcmp(argv[i],"mod")==0)
		    { i++; rest=atoi(argv[i]); i++; mod=atoi(argv[i]);
		      if ((mod<=0) || (rest<0) || (rest>=mod))
		        { fprintf(stderr,"Bad values for option mod \n"); exit(0); }
		    }
		    else { fprintf(stderr,"Nonidentified option: %s \n",argv[i]); exit(106); }
		  break; }



      default: { fprintf(stderr,"Nonidentified option: %s \n",argv[i]); exit(107); }
      }


switch (codenumber)
  {
  case 0: break;
  case 1:
  case 8: { for (i=20+(2*min_sechsecke); i<=knotenzahl; i+=2)
	      { if (IPR) sprintf(strpuf,"Full_codes_%d_ipr",i);
		  else sprintf(strpuf,"Full_codes_%d",i);
		if (do_case) { sprintf(strpuf2,"_c%d",do_case); strcat(strpuf,strpuf2); }
		if (mod) { sprintf(strpuf2,"_m_%d_%d",rest,mod); strcat(strpuf,strpuf2); }
                if (symm_len>0)    {strcat(strpuf,symmstring);}
		if (to_stdout) fil[i]=stdout; else fil[i]=fopen(strpuf,"wb");
		if (!to_stdout) write_header_fil[i]=1;
	        if (fil[i]==nil) { fprintf(stderr,"Can not open file %s. \n",strpuf); exit(109);}
	      }
	    break; }
  case 2: { for (i=20+(2*min_sechsecke); i<=knotenzahl; i+=2)
	      { if (IPR) sprintf(strpuf,"Spiral_codes_%d_ipr",i);
		  else sprintf(strpuf,"Spiral_codes_%d",i);
		if (do_case) { sprintf(strpuf2,"_c%d",do_case); strcat(strpuf,strpuf2); }
		if (mod) { sprintf(strpuf2,"_m_%d_%d",rest,mod); strcat(strpuf,strpuf2); }
                if (symm_len>0)    {strcat(strpuf,symmstring);}
		if (to_stdout) fil[i]=stdout; else fil[i]=fopen(strpuf,"wb");
		if (!to_stdout) write_header_fil[i]=1;
	        if (fil[i]==nil) { fprintf(stderr,"Can not open file %s. \n",strpuf); exit(110);}
	      }
	    spiralcheck=1;
	    last_code[0]=FL_MAX;
	    break; }
  case 3: { spiralcheck=1;
            if (listenlaenge==0) listenlaenge=2000;
            for (i=20+(2*min_sechsecke); i<=knotenzahl; i+=2)
	      { (codeliste[i].code)[0]=0;
		if (IPR) sprintf(strpuf,"Spiral_codes_%d_ipr",i);
		  else sprintf(strpuf,"Spiral_codes_%d",i);
		if (do_case) { sprintf(strpuf2,"_c%d",do_case); strcat(strpuf,strpuf2); }
		if (mod) { sprintf(strpuf2,"_m_%d_%d",rest,mod); strcat(strpuf,strpuf2); }
                if (symm_len>0)    {strcat(strpuf,symmstring);}
		if (to_stdout) fil[i]=stdout; else fil[i]=fopen(strpuf,"wb");
                if (!to_stdout) write_header_fil[i]=1;
	        if (fil[i]==nil) { fprintf(stderr,"Can not open file %s. \n",strpuf); exit(111);}
		lastcode[i]=(FLAECHENTYP **)malloc(sizeof(FLAECHENTYP *));
		if (lastcode[i] ==nil) { fprintf(stderr,"Can not get memory for lastcode. \n"); exit(112); }
		(*(lastcode[i]))=(FLAECHENTYP *)malloc(sizeof(FLAECHENTYP)*12);
		(*(lastcode[i]))[0]=FL_MAX;
	      }
	    break; }
  case 4: spiralcheck=1; break; /* Nur nicht-spiral-codes schreiben */
  case 5: { spiralcheck=1;
            for (i=20+(2*min_sechsecke); i<=knotenzahl; i+=2)
	      { if (IPR) sprintf(strpuf,"Full_codes_%d_ipr",i);
		  else sprintf(strpuf,"Full_codes_%d",i);
		if (do_case) { sprintf(strpuf2,"_c%d",do_case); strcat(strpuf,strpuf2); }
		if (mod) { sprintf(strpuf2,"_m_%d_%d",rest,mod); strcat(strpuf,strpuf2); }
                if (symm_len>0)    {strcat(strpuf,symmstring);}
		if (to_stdout) fil[i]=stdout; else fil[i]=fopen(strpuf,"wb");
	        if (fil[i]==nil) { fprintf(stderr,"Can not open file %s. \n",strpuf); exit(113);}
                if (!to_stdout) write_header_fil[i]=1;
	      }
	    break; }

  case 6: { break; }

  case 7: { break; }

  default: { fprintf(stderr,"No coding number %d. \n", codenumber); exit(114); }
  }

if (hexspi && !spiralcheck) 
  { fprintf(stderr,"The option \"hexspi\" must be used together with some code involving spiral checking \n");
    exit(115); }

if (spistat && (min_sechsecke != max_sechsecke)) 
  { fprintf(stderr,"The option \"spistat\" must be used only for fullerenes of ONE size \n");
    exit(116); }

if (spistat) for (i=0; i<=12*max_sechsecke+120; i++) spiralnumbers[i]=0;


if (IPR)
  {  if (min_sechsecke==max_sechsecke) sprintf(logfilename,"Full_gen_%d_ipr",knotenzahl);
    else sprintf(logfilename,"Full_gen_%d_%d_ipr",knotenzahl,(2*min_sechsecke)+20); }
else
  {  if (min_sechsecke==max_sechsecke) sprintf(logfilename,"Full_gen_%d",knotenzahl);
  else sprintf(logfilename,"Full_gen_%d_%d",knotenzahl,(2*min_sechsecke)+20); }

  if (do_case) { sprintf(strpuf2,"_c%d",do_case); strcat(logfilename,strpuf2); }
  if (mod) { sprintf(strpuf2,"_m_%d_%d",rest,mod); strcat(logfilename,strpuf2); }
  if (spiralcheck) { sprintf(no_spiral_filename,"No_spiral_");
		     strcat(no_spiral_filename,logfilename+9);
		     sprintf(strdummy,"rm %s",no_spiral_filename);
		     if (!stat(strdummy,&buf)) {
                         if(system (strdummy)==-1){
                             fprintf(stderr,"Could not execute system call.\n");
                         }
                     }
		     sprintf(no_penta_spiral_filename,"No_pentagon_spiral_");
		     strcat(no_penta_spiral_filename,logfilename+9);
		     sprintf(strdummy,"rm %s",no_penta_spiral_filename);
		     if (!stat(strdummy,&buf)) {
                         if(system (strdummy)==-1){
                             fprintf(stderr,"Could not execute system call.\n");
                         }
                     }
		      }
  if (hexspi) { sprintf(no_hexa_spiral_filename,"No_hexagon_spiral_");
		strcat(no_hexa_spiral_filename,logfilename+9);
		sprintf(strdummy,"rm %s",no_hexa_spiral_filename);
		if (!stat(strdummy,&buf)) {
                     if(system (strdummy)==-1){
                         fprintf(stderr,"Could not execute system call.\n");
                     }
                }
	      }

if (!quiet)
  {
    strcat(logfilename,".log");
    if (separate_logfile) logfile=fopen(logfilename,"w");
    if (logfile==nil) { fprintf(stderr,"Can not open file %s. \n",logfilename); exit(118);}
    fprintf(logfile,"Minimal vertex number: %d \n",(2*min_sechsecke)+20);
    fprintf(logfile,"Maximal vertex number: %d \n",knotenzahl);
    fprintf(logfile,"Code_type: %d \n",codenumber);
    if (codenumber==3) fprintf(logfile,"List length: %d \n",listenlaenge);
    if (separate_logfile) fclose(logfile);
  }


initialize_list();

baue_patches(sechsecke); 
#ifndef NOTIMES
times(&TMS);
savetime= TMS.tms_utime;
if (!quiet) 
  { fprintf(stderr,"Time for generating the patches: %.1f seconds \n",(double)savetime/time_factor);
    if (separate_logfile) {
      logfile=fopen(logfilename,"a");
      fprintf(logfile,"Time for generating the patches: %.1f seconds \n",(double)savetime/time_factor);
      fclose(logfile);
    }
  }
#endif //NOTIMES

if (do_bauchbinde)
{
bauchbinde(min_sechsecke,max_sechsecke);
#ifndef NOTIMES
times(&TMS);
buffertime= TMS.tms_utime;
if (!quiet) 
  { fprintf(stderr,"Time for case 1 (Jordan-Curve Petrie Path): %.1f seconds \n",(double)(buffertime-savetime)/time_factor);
    if (separate_logfile) {
      logfile=fopen(logfilename,"a");
      fprintf(logfile,"Time for case 1 (Jordan-Curve Petrie Path): %.1f seconds \n",(double)(buffertime-savetime)/time_factor);
      fclose(logfile);
    }
  }
savetime=buffertime;
#endif //NOTIMES
}

if (do_brille)
{
brille(min_sechsecke,max_sechsecke);
#ifndef NOTIMES
times(&TMS);
buffertime= TMS.tms_utime;
if (!quiet) 
  { fprintf(stderr,"Time for case 2 (Dumb-bell): %.1f seconds \n",(double)(buffertime-savetime)/time_factor);
    if (separate_logfile) {
      logfile=fopen(logfilename,"a");
      fprintf(logfile,"Time for case 2 (Dumb-bell): %.1f seconds \n",(double)(buffertime-savetime)/time_factor);
      fclose(logfile);
    }
    savetime=buffertime;
  }
#endif //NOTIMES
}

if (do_sandwich)
{
sandwich(min_sechsecke,max_sechsecke);
#ifndef NOTIMES
times(&TMS);
buffertime= TMS.tms_utime;
if (!quiet) 
  { fprintf(stderr,"Time for case 3 (Sandwich): %.1f seconds \n\n",(double)(buffertime-savetime)/time_factor);
    if (separate_logfile) {
      logfile=fopen(logfilename,"a");
      fprintf(logfile,"Time for case 3 (Sandwich): %.1f seconds \n\n",(double)(buffertime-savetime)/time_factor);
      fclose(logfile);
    }
  }
#endif //NOTIMES
}

if (codenumber==3) 
  for (i=20+(2*min_sechsecke); i<=knotenzahl; i++) { dummypointer=dummycode; ausgabe(codeliste+i,i,&dummypointer); }


if (!quiet) 
 { 
   fprintf(stderr,"MAPLIST: number of patches: %d\n",mapliste.total_maps);
   fprintf(stderr,"BBLIST: number of items in list: %d  number of patches: %d\n\n",bbliste.total_items,bbliste.total_maps);
   for (i=20+(2*min_sechsecke); i<=20+(2*max_sechsecke); i+=2)
     fprintf(stderr,"Generated %lld maps on %d vertices -- reduced to %lld non-isomorphic maps. \n",non_iso_graphenzahl[i],i,graphenzahl[i]);
   if (spistat) for (i=0; i<=12*max_sechsecke+120; i++) 
     if (spiralnumbers[i]) fprintf(stderr,"Fullerenes with %d spirals: %d \n",i,spiralnumbers[i]);
   if (spiralcheck) fprintf(stderr,"Graphs without a spiral starting at a pentagon: %d \n",no_penta_spiral);
   if (hexspi) fprintf(stderr,"Graphs without a spiral starting at a hexagon: %d \n",no_hexa_spiral);
   if (symstat) schreibe_symmetriestatistik();
#ifndef NOTIMES 
  fprintf(stderr,"\nTotal generation time: %.1f seconds \n",(double)buffertime/time_factor);
#endif //NOTIMES   
   fprintf(stderr,"end of program\n");
   
   if (separate_logfile) {
     logfile=fopen(logfilename,"a");
     fprintf(logfile,"MAPLIST: number of patches: %d\n",mapliste.total_maps);
     fprintf(logfile,"BBLIST: number of items in list: %d  number of patches: %d\n\n",bbliste.total_items,bbliste.total_maps);
     for (i=20+(2*min_sechsecke); i<=20+(2*max_sechsecke); i+=2)
       fprintf(logfile,"Generated %lld maps on %d vertices -- reduced to %lld non-isomorphic maps. \n",non_iso_graphenzahl[i],i,graphenzahl[i]);
     if (spistat) for (i=0; i<=12*max_sechsecke+120; i++) 
       if (spiralnumbers[i]) fprintf(logfile,"Fullerenes with %d spirals: %d \n",i,spiralnumbers[i]);
     if (spiralcheck) fprintf(logfile,"Graphs without a spiral starting at a pentagon: %d \n",no_penta_spiral);
     if (hexspi) fprintf(logfile,"Graphs without a spiral starting at a hexagon: %d \n",no_hexa_spiral);
     if (symstat) {    /* schreibe Symmetriestatistik */
       int j=0;
       fprintf(logfile,"Symmetries:\n");
       for (i=1; i<=28; i++) {
	 if (symm_anz[i]>0) {
	   fprintf(logfile,"  %s: %10d ",symm_name[i],symm_anz[i]); 
	   j++;
	   if (j%4==0) {fprintf(logfile,"\n");}
	 }
       }
       if (j%4) {fprintf(logfile,"\n");}
     }        
#ifndef NOTIMES
     fprintf(logfile,"\nTotal generation time: %.1f seconds \n",(double)buffertime/time_factor);
#endif //NOTIMES     
     fprintf(logfile,"end of program\n");
   }
 }

return(0);
}

