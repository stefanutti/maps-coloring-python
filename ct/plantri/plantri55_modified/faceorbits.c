/* PLUGIN file to use with plantri.c 

   To use this, compile plantri.c using 
       cc -o plantri_fo -O4 '-DPLUGIN="faceorbits.c"' plantri.c

   This reports the number of graphs weighted by the number of
   orbits of faces they have.  The full group or the orientation-
   preserving group is used according to the -o switch.

   The value is equal to the number of ways that this sphere 
   imbedding can be drawn on the plane with distinguished outer
   face.  The dual graph is handled correctly.
*/

static int numoporbits(int,int);
static int numorbits(int,int);
static int numopfaceorbits(int,int);
static int numfaceorbits(int,int);
#define SUMMARY printresult
#define FILTER facecounter
#define PLUGIN_INIT Gswitch = TRUE;  facecount = 0; \
                    INCOMPAT(polygonsize!=0,"plantri_fo","-P");

static bigint facecount;

void printresult(void)
{
    fprintf(msgfile,"Total plane imbeddings = ");
    PRINTBIG(msgfile,facecount);
    fprintf(msgfile,"\n");
}

int facecounter(int nbtot, int nbop, int doflip)
/* Increment facecount by the number of face orbits */
{
    int nf,wt;

    if (dswitch)
        if (oswitch) nf = numoporbits(nbtot,nbop);
        else         nf = numorbits(nbtot,nbop);
    else
        if (oswitch) nf = numopfaceorbits(nbtot,nbop);
        else         nf = numfaceorbits(nbtot,nbop);

    wt = doflip ? 2 : 1;
    facecount += nf*wt;

    return 1;
}
