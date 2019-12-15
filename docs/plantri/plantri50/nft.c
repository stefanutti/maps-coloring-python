/* PLUGIN file to use with plantri.c 

   To use this, compile plantri.c using 
       cc -o plantri_nft -O4 '-DPLUGIN="nft.c"' plantri.c

   This plug-in adds a count of non-facial triangles to the
   statistics at the end.  It not been checked too well in
   the case of -c1 or -c2, or for disk triangulations, so
   those cases are excluded.
*/

#define FILTER nft_counter
#define SUMMARY summary

static int non_facial_triangles(void);   /* included in plantri.c */

#define MAXNFT MAXN
static bigint nftcount[MAXNFT+1];

#undef SWITCHES
#define SWITCHES "[-uagsh -xm#bpe#f# -odG -v]"

#define PLUGIN_INIT \
   PERROR(minconnec==1 || minconnec==2 || polygonsize >= 0, \
             "-c1, -c2 or -P are not allowed"); \
   { int ii;  for (ii = 0; ii <= MAXNFT; ++ii) ZEROBIG(nftcount[ii]); }

/*********************************************************************/

static int
nft_counter(int nbtot, int nbop, int doflip)
{
    int nft;

    nft = non_facial_triangles();
    if (nft > MAXNFT)
    {
	fprintf(stderr,"%s: increase MAXNFT to at least %d\n",cmdname,nft);
	exit(1);
    }
    ADDBIG(nftcount[nft],doflip+1);

    return TRUE;
}

static void
summary()
{
    int i;

    fprintf(msgfile,"Counts by number of non-facial triangles\n");
    for (i = 0; i <= MAXNFT; ++i)
    if (!ISZEROBIG(nftcount[i]))
    {
        fprintf(msgfile,"%3d : ",i);
	PRINTBIG(msgfile,nftcount[i]);
 	fprintf(msgfile,"\n");
    }
}
