/* PLUGIN file to use with plantri.c 

   To use this, compile plantri.c using 
       cc -o plantri_mdcount -O4 '-DPLUGIN="mdcount.c"' plantri.c

   This plug-in just counts the generated graphs according to
   minimum degree.
*/

static bigint mdcount[6];

#define PLUGIN_INIT {int ii; for (ii = 0; ii < 6; ++ii) mdcount[i] = 0;}
#define FILTER md_tally
#define SUMMARY md_summary

static int
md_tally(int nbtot, int nbop, int doflip)
{
    int wt,md,i;

    md = 6;
    for (i = 0; i < nv + (missing_vertex >= 0); ++i)
	if (i != missing_vertex && degree[i] < md) md = degree[i];

    wt = doflip ? 2 : 1;
    mdcount[md] += wt;
 
    return 1;
}

static void
md_summary(void)
{
    int i;

    fprintf(msgfile,"\n");
    for (i = 0; i < 6; ++i)
        if (mdcount[i] > 0)
	{
	    fprintf(msgfile," ");
	    PRINTBIG(msgfile,mdcount[i]);
	    fprintf(msgfile," have minimum degree %d\n",i);
	}
}
