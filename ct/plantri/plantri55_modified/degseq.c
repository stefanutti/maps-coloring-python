/* PLUGIN file to use with plantri.c 

   To use this, compile plantri.c using 
       cc -o plantri_deg -O4 '-DPLUGIN="degseq.c"' plantri.c

   This plug-in adds a count of the generated graphs by
   degree sequence.  Also report counts by minimum degree,
   maximum degree, and bipartiteness (i.e. even degrees).
*/

#define FILTER degseq_counter
#define SUMMARY summary

#define MAXNFT MAXN
typedef struct countrec
{
    struct countrec *left,*right;
    bigint count;
    unsigned char seq[MAXN+1];
} countnode;

static countnode *count_root = NULL;
static unsigned long seqcount = 0;

static bigint minmax[6][MAXN+1],bipcount;

#define PLUGIN_INIT \
  {if (maxnv > 72) \
    fprintf(stderr,"Warning, this plugin does not work well for n > 72\n");}

/*********************************************************************/

static void
print_counts(FILE *f, countnode *root)
{
    int i;

    if (root == NULL) return;

    print_counts(f,root->left);

    fprintf(f," ");
    for (i = 0; i < maxnv; ++i)
	fprintf(f,"%c",root->seq[i]<10?'0'+root->seq[i]:'A'-10+root->seq[i]);
    fprintf(f,"  ");
    PRINTBIG(f,root->count);
    fprintf(f,"\n");

    minmax[root->seq[0]][root->seq[maxnv-1]] += root->count;
    for (i = 0; i < maxnv; ++i)
	if (root->seq[i] & 1) break;
    if (i == maxnv) SUMBIGS(bipcount,root->count);
    
    print_counts(f,root->right);
}

/*********************************************************************/

static void
add_degseq(int num, unsigned char *seq)
{
    int i,cmp;
    countnode *p,*ppar,*new_node;

    p = count_root;
    cmp = 0;

    while (p != NULL)
    {
        cmp = strcmp(seq,p->seq);
        if (cmp == 0)
        {
            p->count += num;
            return;
        }
        else if (cmp < 0)
        {
            ppar = p;
            p = p->left;
        }
        else
        {
            ppar = p;
            p = p->right;
        }
    }

    if ((new_node = (countnode*)malloc(sizeof(countnode))) == NULL)
    {
        fprintf(stderr,">E malloc failed in add_degseq()\n");
        exit(1);
    }

    new_node->count = num;
    strcpy(new_node->seq,seq);
    new_node->left = new_node->right = NULL;
    ++seqcount;

    if (cmp == 0)
        count_root = new_node;
    else if (cmp < 0)
        ppar->left = new_node;
    else
        ppar->right = new_node;
}

/*********************************************************************/

static void
sortchar(unsigned char *x, int k)
{
        register int i,j,h;
        unsigned char iw;

        j = k / 3;
        h = 1;
        do
            h = 3 * h + 1;
        while (h < j);

        do
        {
            for (i = h; i < k; ++i)
            {
                iw = x[i];
                for (j = i; x[j-h] > iw; )
                {
                    x[j] = x[j-h];
                    if ((j -= h) < h) break;
                }
                x[j] = iw;
            }
            h /= 3;
        }
        while (h > 0);
}

/*********************************************************************/

static int
degseq_counter(int nbtot, int nbop, int doflip)
/* Assumption: all degrees are in 1..73 */
{
    int i,j;
    unsigned char degseq[MAXN+1];

    j = 0;
    for (i = (missing_vertex >= 0 ? nv+1 : nv); --i >= 0;)
        if (i != missing_vertex) degseq[j++] = degree[i];
    degseq[nv] = '\0';

    sortchar(degseq,nv);

    add_degseq(doflip+1,degseq); 

    return TRUE;
}

/*********************************************************************/

static void
summary()
{
    int i,j;

    for (i = 1; i < 6; ++i)
    for (j = 1; j <= maxnv; ++j)
	minmax[i][j] = 0;

    bipcount = 0;

    fprintf(msgfile,"%lu degree sequences:\n",seqcount);
    print_counts(msgfile,count_root);    

    fprintf(msgfile,"Counts by minimum and maximum degree:\n");
    for (i = 1; i < 6; ++i)
    for (j = 1; j <= maxnv; ++j)
	if (minmax[i][j] > 0)
	{
	    fprintf(msgfile," %2d-%2d : ",i,j);
	    PRINTBIG(msgfile,minmax[i][j]);
	    fprintf(msgfile,"\n");
	}

    fprintf(msgfile,"Bipartite : ");
    PRINTBIG(msgfile,bipcount);
    fprintf(msgfile,"\n");
}
