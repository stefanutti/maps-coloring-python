#define VERSION "5.0 - Oct 1, 2015"
#define SWITCHES "[-uagsEh -Ac#txm#P#bpe#f#q -odGV -v]"
#define TMP

/* plantri.c :  generate imbedded planar graphs 

  This program generates many different classes of graph imbedded on 
  a sphere.  Exact specifications and instructions for use can be found
  in the separate manual plantri-guide.txt.

  The latest edition of plantri is available from the plantri page
  http://cs.anu.edu.au/~bdm/plantri .

  Authors:  Gunnar Brinkmann   gunnar@mathematik.uni-bielefeld.de
            Brendan McKay      bdm@cs.anu.edu.au

---------

   Output formats: 

      The output for each graph consists of the number of vertices,
      then for each vertex a list of all its neighbours in clockwise
      order.  These neighbour lists are separated by a "separator",
      and terminated by a "terminator".

                             planar_code          ascii format
                              (default)            (with -a)

      file type               binary               text
      number of vertices      one byte          decimal + blank
      vertex names          bytes 1,2,3...        letters 'a','b',...
      separators              zero byte           comma ','
      terminator              zero byte           newline '\n'

      For example, the planar dual of the cube appears like this:

      planar_code: 
         6 4 3 2 5 0 3 6 5 1 0 1 4 6 2 0 5 6 3 1 0 4 1 2 6 0 4 5 2 3 0
         (One number per byte, no newlines).

      ascii format: 
         6 dcbe,cfea,adfb,efca,dabf,debc
         (Including the space after "6".  Followed by newline.)

      edge_code:
	 See the manual.  At the moment there is a limit of 256 on the
         number of undirected edges.  This could be increased.

      For planar_code, the standard header ">>planar_code<<"
      (without null or newline) is written at the start of the
      output unless the -h switch is given.  Similarly for edge_code
      and the header ">>edge_code<<".

      Using -g or -s, the graph6 or sparse6 formats can be selected instead. 
      These are ASCII formats for general undirected graphs, and do not
      encode the imbedding.  graph6 does not represent loops or edge
      multiplicities either.  They are described in plantri-guide.txt.

---------

Size limits:
 
The space used by plantri is O(n^2).  Apart from that, the only
practical limits on MAXN (the maximum permitted number of vertices)
is determined by the limits imposed by the output syntax.
 
The following table gives the largest legal MAXN value.
 
 Switches:    none    -d    -a    -ad    -g    -gd   -s    -sd      -u
 Output:      planar_code     ascii        graph6     sparse6      none
             primal  dual  primal dual  primal dual  primal dual
 MAXN limit:  255    129     99     51   255   129    255   129    1023

 Switch -E and -Ed give edge_code output.  These have no limit on the
 number of vertices but (currently) a limit of 256 on the number of
 undirected edges.
 
The limits for ascii code could be raised to 114 and 59 easily.
For connectivity < 3, there is also a limit on n of the number of
bits in a long int (usually 32 or 64).
 
Change History:
 
        5-Jun-1996 : initial release of version 1.0
        7-Jun-1996 : fixed writing of planar_code header
                     small changes to plug-in facility
                     -- making 1.0.1
        9-Jun-1996 : included PLUGIN_INIT facility
                     -- making 1.0.2
       13-Jul-1996 : added -g switch
                     -- making 1.0.3
       31-Jul-1997 : added BIGTODOUBLE macro
                     -- making 1.0.4
        5-Aug-1997 : relaxed and documented MAXN limit
                     -- making 1.0.5
       20-Sep-1998 : improved performance about 25%
                     replaced -A by -g and -g by -G
                     added 1-connected and 2-connected (-c and -x)
                     added 3-connected polytopes (-p)
                     added -s for sparse6 output
                     many small changes
                     -- making 2.0
        1-Sep-1999 : massive changes, including:
                     added minimum degree 4 case (-m4 and -c4)
                     added eulerian (dual bipartite) case (-b and -bc4)
                     added polygon triangulations (-P)
                     made some statistics optional (-v)
                     -- making 3.0
        2-Jul-2000 : fixed an error causing problems for minimum
                     degree 5 on 26 or more vertices.  Many thanks
                     to Thom Sulanke for finding it.  (Two changes in
                     scansimple().)
                     -- making 3.1
        5-Jul-2000 : removed some useless code from scansimple()

       11-Apr-2001 : added code for -c1 and -c2.
                     added -m5 native support (min5 plugin now obsolete)
                     added -q for quadrangulations
		     improved polytope generation
                     sparse6 output now represents loops only once
		     revised output format for -v
                     -- making 4.0

       20-Jul-2001 : extended make_dual() to set facesize[] (note that
                     make_dual() is not actually used, but may be 
                     useful for plug-ins)

       30-Aug-2001 : avoided all possible reads from elements outside arrays
		     (no known problem occured for distributed editions)

        5-Oct-2001 : corrected -m5 splitting (but it was probably not wrong)
 
       27-Oct-2001 : removed quadrangulations warning (now proved!)

       21-Nov-2001 : make quadrangulations from pseudo-double wheels
		     added -qc2

       23-Nov-2001 : added -qc4

        2-Dec-2001 : added -qc2m2

        8-Mar-2002 : added FAST_FILTER_* hooks
		     improved switch checking
		     added HELPMESSAGE option

        3-Oct-2004 : added PRE_FILTER_DISK

       27-Jul-2005 : added "void" prototypes, make CPUTIME more robust
                     -- making 4.1

        3-Aug-2005 : added -V

       13-Mar-2007 : some warnings removed, added dummy function to 
                     avoid warnings of unused functions

       28-Jul-2007 : added -E for edge_code output

        2-Aug-2007 : added -bp for bipartite graphs
                   : added general planar graphs (-p) of 2 and 3 vertices

       19-Feb-2008 : fixed -pc1x and -pc2x

       21-Feb-2008 : slightly improved -p for minimal edge counts
                   : -p rejects some impossible edge counts with error msg

        2-May-2009 : fix incorrect connectivity computation in -p and -pb,
		       only known problems were with -c1x, -c2x and statistics
                       reported by -v
                     -- making 4.4

        2-Sep-2011 : also apply FAST_FILTER_* to starting graphs  (all uses
		       need checking against code as more than one filter
		       might need defining)
                     -- making 4.5

       19-Sep-2011 : don't use rightface field in output routines, to avoid
                     confusing generators and filters

        7-Mar-2014 : add -A for Appolonian networks

        2-Oct-2015 : add -pc4
                     -- making 5.0

**************************************************************************/

#include <stdio.h>

#if __STDC__
#include <stdlib.h>
#include <errno.h>
#else
extern int errno;
#endif

#include <string.h>
#include <limits.h>

#define CPUTIME 1 /* Whether to measure the cpu time or not */

#if CPUTIME
#include <sys/times.h>
#include <time.h>
#if !defined(CLK_TCK) && !defined(_SC_CLK_TCK)
#include <unistd.h>
#endif
#if !defined(CLK_TCK) && defined(_SC_CLK_TCK)
#define CLK_TCK sysconf(_SC_CLK_TCK)
#endif
#if !defined(CLK_TCK) && defined(CLOCKS_PER_SEC)
#define CLK_TCK CLOCKS_PER_SEC
#endif
#if !defined(CLK_TCK)
#define CLK_TCK 60 /* If the CPU time stated by the program appears \
          to be out by a constant ratio, the most likely            \
          explanation is that the code got to this point but        \
          60 is the wrong guess.  Another common value is 100. */
#endif
#endif

#ifndef MAXN
#define MAXN 64 /* the maximum number of vertices; see above */
#endif
#define MAXE (6 * MAXN - 12) /* the maximum number of oriented edges */
#define MAXF (2 * MAXN - 4)  /* the maximum number of faces */

typedef struct e /* The data type used for edges */
{
    int start;           /* vertex where the edge starts */
    int end;             /* vertex where the edge ends */
    int rightface;       /* face on the right side of the edge
                          note: only valid if make_dual() called */
    struct e *prev;      /* previous edge in clockwise direction */
    struct e *next;      /* next edge in clockwise direction */
    struct e *invers;    /* the edge that is inverse to this one */
    struct e *min;       /* the least of e and e->invers */
    int mark, index, rf; /* three ints for temporary use;
			  rf is only for the printing routines;
                          Only access mark via the MARK macros. */
    int left_facesize;   /* size of the face in prev-direction of the edge.
        		  Only used for -p option. */
} EDGE;

typedef struct
{
    EDGE *e1, *e2, *e3;
} triangle;

#undef FALSE
#undef TRUE
#define FALSE 0
#define TRUE 1

/* Global variables */

static char *outfilename; /* name of output file (NULL for stdout) */
static FILE *outfile;     /* output file for graphs */
static FILE *msgfile;     /* file for informational messages */

static int maxnv;    /* order of output graphs */
static int res, mod; /* res/mod from command line (default 0/1) */
static int splitlevel,
    splitcount; /* used for res/mod splitting */
#ifdef PLUGIN
static int splithint = -1; /* used by plugins to set splitting level */
#endif
static int minconnec;     /* lower bound on minimum connectivity */
static int minpolyconnec; /* lower bound on minumum connectivity for
			      polytopes.  Defaults to same as minconnec. */
static int xconnec;       /* Value of connectivity appropriate for -x.
                              The same as either minconnec or minpolyconnec. */
static int edgebound[2];  /* edge count min,max for polytopes */
static int maxfacesize;   /* maximum face size for polytopes */

static int polygonsize; /* polygon size for -P.
                              -1 means -P is absent
                               0 means size is unrestricted */

static int minimumdeg; /* lower bound on minimum degree.
                              -1 means nothing specified */
static int minpolydeg; /* lower bound on minimum degree for polytopes.
                              -1 will cause it to be reset to the same as
                              minimumdeg, but plugins can set it otherwise. */

static int aswitch, /* presence of command-line switches */
    Aswitch,
    bswitch,
    gswitch,
    sswitch,
    Eswitch,
    hswitch,
    dswitch,
    Gswitch,
    oswitch,
    qswitch,
    tswitch,
    pswitch,
    uswitch,
    vswitch,
    Vswitch,
    xswitch;

static int zeroswitch;  /* Undocumented option -0 */
static int oneswitch;   /* Undocumented option -1, implies -0 */
static int twoswitch;   /*  Undocumented option -2 */
static int needgroup;   /* Is group needed at end of scansimple()
			      and similar routines? */
static int gotone_nbop; /* Used only by got_one() */
static int gotone_nbtot;

static int dosummary; /* used by plugin */
static char *cmdname; /* points to arg[0] */

/* The variables below are used at each level of the iteration,
   updating and restoring as we move up and down the search tree */

static int nv; /* number of vertices; they are 0..nv-1 */
static int ne; /* number of directed edges (at most 6*nv-12) */

#define NUMEDGES (24 + 70 * MAXN)
static EDGE edges[NUMEDGES];

#define init_edge edges
#define STAR3(n) (edges + 6 + ((n) << 3))
#define STAR4(n) (edges + 6 + 8 * MAXN + ((n) << 3))
#define STAR5(n) (edges + 6 + 16 * MAXN + ((n) << 4))

#define P_op(n) (edges + 24 + 12 * (n))
#define Q_op(n) (edges + 24 + 12 * MAXN + 6 * (n))

#define four_op(n) (edges + 6 * (n))
#define five_op(n) (edges + 6 * MAXN + 6 * (n))
#define S_op(n) (edges + 12 * MAXN + 18 * (n))

#define min5_a(n) (edges - 12 + 6 * (n))
/* edges + 60 + 6*(n) - 12*6 since the smallest n for which it is possibly
   called is n=12 and then it should start at edge 60 */
#define min5_b0(n) (edges - 156 + 6 * MAXN + 12 * (n))
/* edges - 12 + 6*MAXN + 12*(n) - 12*12, again since the smallest  
   possible n is 12 */
#define min5_b1(n) (edges - 300 + 18 * MAXN + 12 * (n))
/* edges - 156 + 18*MAXN + 12*(n) - 12*12 */
#define min5_c(n) (edges - 780 + 30 * MAXN + 40 * (n))
/* edges - 300 + 30*MAXN + 40*(n) - 12*40 */

#define quadr_P0(n) (edges - 8 + 4 * MAXN + 4 * (n))
/* The smallest n for which it is called is 3. Then it should start at entry 
   edges +4 + 4*MAXN -- right AFTER the edges for quadr_P1(n) which is
   used in the same run. */
#define quadr_P1(n) (edges + 4 + 4 * (n))
/* edges + 24 + 4*(n) - 5*4 since the smallest n for which it is possibly
   called is n=5  and then it should start at edge 24 */
#define quadr_P2(n) (edges - 60 + 4 * MAXN + 8 * (n))
/* edges +4 + 4*MAXN + 8*(n) - 8*8, again since the smallest
   possible n is 8 */
#define quadr_P3(n) (edges - 188 + 12 * MAXN + 16 * (n))
/* edges - 60 + 12*MAXN + 16*(n) - 8*16 */

static int degree[MAXN];      /* the degrees of the vertices */
static EDGE *firstedge[MAXN]; /* pointer to arbitrary edge out of vertex i. */
                              /* This pointer may change during the run, so all one can rely on is that
     at any point it is "some" edge out of i */

static EDGE *facestart[MAXF]; /* an edge in the clockwise orientation of
                                 each face.  Only valid when computed. */
static int facesize[MAXF];    /* size of each face.  Only valid when computed. */

static EDGE *numbering[2 * MAXE][MAXE];
/* holds numberings produced by canon() or canon_edge() */
static EDGE *saved_numbering[2 * MAXE][MAXE];
/* a copy of numbering used by scanordloops() */

/* The following packed adjacency matrix is used for triangulations
   of minconnec < 3. */

static long am[MAXN];
#define BIT(i) (1L << (i))
#define ISADJ(i, j) (am[i] & BIT(j))

/* The following unpacked adjacency matrix is used for general planar
   graphs of connectivity 1 and 2. */

static char am2[MAXN][64];
#define AMADDEDGE(i, j)            \
    {                              \
        am2[i][j] = am2[j][i] = 1; \
    }
#define AMDELEDGE(i, j)            \
    {                              \
        am2[i][j] = am2[j][i] = 0; \
    }
#define ISEQADJ(i, j) (am2[i][j] != 0)
#define ISNEQADJ(i, j) (am2[i][j] == 0)

static EDGE *doubles[MAXE]; /* holds edges with parallel mates */

#define PCODE ">>planar_code<<"
#define PCODELEN (sizeof(PCODE) - 1) /* "-1" to avoid the null */
#define ECODE ">>edge_code<<"
#define ECODELEN (sizeof(ECODE) - 1) /* "-1" to avoid the null */
#define G6CODE ">>graph6<<"
#define G6CODELEN (sizeof(G6CODE) - 1) /* "-1" to avoid the null */
#define S6CODE ">>sparse6<<"
#define S6CODELEN (sizeof(S6CODE) - 1) /* "-1" to avoid the null */

static EDGE *code_edge = NULL;
/* if code_edge is not NULL, it is taken as the start for coding for
   ASCII or planar_code. Otherwise firstedge[0] is the start. This
   method implies comparatively few changes due to outputting 
   triangulations of disks. 

   In case of triangulations of disks, *code_edge should be an edge
   with the "outer" face on the left for the non-mirror case and on
   the right for the mirror case to have the outer face left of 1->2.

   In case of dual output (mirror image or not), the face on the left 
   of *code_edge gets the number 1. So for duals of triangulations of 
   disks, handing in an edge with the disk on the right outputs the 
   "marked" vertex as 1.
*/

static int missing_vertex = -1;
/* The vertices are numbered 0..nv-1 if missing_vertex<0, and
   0..missing_vertex-1,missing_vertex..nv otherwise.  This is
   only used in the code for polygon triangulations. */

static int outside_face_size; /* Used for polygon triangulations. */

static int zero[MAXN]; /* permanently 0 */

/* The program is so fast that the count of output graphs can quickly
   overflow a 32-bit integer.  Therefore, we use two long values
   for each count, with a ratio of 10^9 between them.  The macro
   ADDBIG adds a small number to one of these big numbers.  
   BIGTODOUBLE converts a big number to a double (approximately).
   SUMBIGS adds a second big number into a first big number.
   SUBBIGS subtracts a second big number from a first big number.
   PRINTBIG prints a big number in decimal.
   ZEROBIG sets the value of a big number to 0.
   ISZEROBIG tests if the value is 0.
   SETBIG sets a big number to a value at most 10^9-1.
   ISEQBIG tests if two big numbers are equal.
*/

typedef struct
{
    long hi, lo;
} bigint;

#define ZEROBIG(big) big.hi = big.lo = 0L
#define ISZEROBIG(big) (big.lo == 0 && big.hi == 0)
#define SETBIG(big, value) \
    {                      \
        big.hi = 0L;       \
        big.lo = (value);  \
    }
#define ADDBIG(big, extra)                  \
    if ((big.lo += (extra)) >= 1000000000L) \
    {                                       \
        ++big.hi;                           \
        big.lo -= 1000000000L;              \
    }
#define PRINTBIG(file, big)           \
    if (big.hi == 0)                  \
        fprintf(file, "%ld", big.lo); \
    else                              \
        fprintf(file, "%ld%09ld", big.hi, big.lo)
#define BIGTODOUBLE(big) (big.hi * 1000000000.0 + big.lo)
#define SUMBIGS(big1, big2)                      \
    {                                            \
        if ((big1.lo += big2.lo) >= 1000000000L) \
        {                                        \
            big1.lo -= 1000000000L;              \
            big1.hi += big2.hi + 1L;             \
        }                                        \
        else                                     \
            big1.hi += big2.hi;                  \
    }
#define SUBBIGS(big1, big2)            \
    {                                  \
        if ((big1.lo -= big2.lo) < 0L) \
        {                              \
            big1.lo += 1000000000L;    \
            big1.hi -= big2.hi + 1L;   \
        }                              \
        else                           \
            big1.hi -= big2.hi;        \
    }
/* Note: SUBBIGS must not allow the value to go negative.
   SUMBIGS and SUBBIGS both permit big1 and big2 to be the same bigint. */
#define ISEQBIG(big1, big2) (big1.lo == big2.lo && big1.hi == big2.hi)

static bigint nout[6];                 /* counts of output graphs, per connectivity */
static bigint nout_op[6];              /* counts of output graphs, per connectivity, OP */
static bigint nout_e[MAXE / 2 + 1];    /* .. per undirected edge number */
static bigint nout_e_op[MAXE / 2 + 1]; /* .. per undirected edge number, OP */
static bigint nout_p[MAXN + 1];        /* .. per polygon size */
static bigint nout_p_op[MAXN + 1];     /* .. per polygon size, OP */
static bigint totalout;                /* Sum of nout[] (always) */
static bigint totalout_op;             /* Sum of nout_op[] (only if -o) */
static bigint nout_V;                  /* Deletions due to -V */

static char outtypename[50]; /* How to describe output objects */

#ifdef STATS                             /* optional statistics collection */
static bigint numrooted;                 /* rooted maps */
static bigint ntriv;                     /* counter of those with trivial groups 
    (needs -G or something that implies it, like -o, -p, -P)  */
static bigint nummindeg[6];              /* count according to min degree */
static bigint numbigface[MAXN + 1];      /* count according to outside face */
static bigint numrooted_e[MAXE / 2 + 1]; /* rooted maps per undirected edges */
#endif
#if defined(STATS2) && defined(STATS) /* even more statistics collection */
static bigint numtwos[MAXN + 1];      /* number of vertices of degree 2 */
#endif

static int markvalue = 30000;
#define RESETMARKS                               \
    {                                            \
        int mki;                                 \
        if ((markvalue += 2) > 30000)            \
        {                                        \
            markvalue = 2;                       \
            for (mki = 0; mki < NUMEDGES; ++mki) \
                edges[mki].mark = 0;             \
        }                                        \
    }
#define MARK(e) (e)->mark = markvalue
#define MARKLO(e) (e)->mark = markvalue
#define MARKHI(e) (e)->mark = markvalue + 1
#define UNMARK(e) (e)->mark = markvalue - 1
#define ISMARKED(e) ((e)->mark >= markvalue)
#define ISMARKEDLO(e) ((e)->mark == markvalue)
#define ISMARKEDHI(e) ((e)->mark > markvalue)

/* and the same for vertices */

static int markvalue_v = 30000;
static int marks__v[MAXN];
#define RESETMARKS_V                         \
    {                                        \
        int mki;                             \
        if ((++markvalue_v) > 30000)         \
        {                                    \
            markvalue_v = 1;                 \
            for (mki = 0; mki < MAXN; ++mki) \
                marks__v[mki] = 0;           \
        }                                    \
    }
#define UNMARK_V(x) (marks__v[x] = 0)
#define ISMARKED_V(x) (marks__v[x] == markvalue_v)
#define MARK_V(x) (marks__v[x] = markvalue_v)

static EDGE *inmaxface[MAXN * MAXN - 3 * MAXN / 2]; /* Used for polytope
  generation - lists edges whose left face is maximum size */

static void (*write_graph)(FILE *, int);
static void (*write_dual_graph)(FILE *, int);

#define CHECKSWITCH(name) check_switch(name, ok_switches)
#define OK_SWITCHES(name) ok_switches[(unsigned char)(name)]
#define INCOMPAT(cond, x, y)                                                   \
    if (cond)                                                                  \
    {                                                                          \
        fprintf(stderr, ">E %s: %s and %s are incompatible\n", cmdname, x, y); \
        exit(1);                                                               \
    }
#define CHECKRANGE(var, varname, lo, hi)                                      \
    if ((var) < (lo) || (var) > (hi))                                         \
    {                                                                         \
        fprintf(stderr, ">E %s: the value of %s must be ", cmdname, varname); \
        if ((lo) == (hi))                                                     \
            fprintf(stderr, "%d\n", lo);                                      \
        else                                                                  \
            fprintf(stderr, "%d..%d\n", lo, hi);                              \
        exit(1);                                                              \
    }
#define PERROR(cond, msg)                             \
    if (cond)                                         \
    {                                                 \
        fprintf(stderr, ">E %s: %s\n", cmdname, msg); \
        exit(1);                                      \
    }

#define BOOLSWITCH(name, var) \
    else if (arg[j] == name)  \
    {                         \
        CHECKSWITCH(name);    \
        var = TRUE;           \
    }
#define INTSWITCH(name, var)           \
    else if (arg[j] == name)           \
    {                                  \
        CHECKSWITCH(name);             \
        var = getswitchvalue(arg, &j); \
    }

#define SECRET_SWITCHES "012"

#define MAX(x, y) ((x) < (y) ? (y) : (x))
#define MIN(x, y) ((x) > (y) ? (y) : (x))

#ifdef SPLITTEST
static bigint splitcases;
#endif

/**************************************************************************/

/* Include optional file for special processing. */

#ifdef PLUGIN
#include PLUGIN
#endif

#ifdef PRE_FILTER
Error - Trying to use an obsolete plugin
#endif

    /**************************************************************************/

    static int
    maxdegree(void)

/* Find the maximum degree */

{
    int maxd, i;

    maxd = 0;
    for (i = 0; i < nv; ++i)
        if (degree[i] > maxd)
            maxd = degree[i];

    return maxd;
}

/**************************************************************************/

static void
show_group(FILE *f, int nbtot, int nbop)

/* Display the group stored in the usual place */

{
    EDGE **nb, **nblim;
    int i;

    fprintf(f, "nv=%d ne=%d nbtot=%d nbop=%d\n", nv, ne, nbtot, nbop);

    if (nbtot == 1)
        return;

    nblim = (EDGE **)numbering[nbtot];
    for (nb = (EDGE **)numbering[0]; nb < nblim; nb += MAXE)
    {
        for (i = 0; i < ne; ++i)
            fprintf(f, " %x-%x", nb[i]->start, nb[i]->end);
        fprintf(f, "\n");
    }
}

/**************************************************************************/

/* Routines for extending and reducing a triangulation.
   General principle:  extendx(e); reducex(e)  will extend by one 
   vertex of degree x (x=3,4,5) then reduce it to the original graph.  
   The final graph is exactly the same as the original
   (including pointer values) except that possibly the values of
   firstedge[] might be different.
*/

static void
extend3(EDGE *e)

/* inserts a vertex with valence 3 in the triangle on the right hand
   side (->next direction) of the edge e */
{
    register EDGE *work1, *work2, *work3;

    work1 = STAR3(nv);
    work2 = work1 + 1;
    work3 = work2 + 1;
    firstedge[nv] = work3 + 1;

    /* work1 starts at the beginning of e: */

    work1->start = work1->invers->end = e->start;
    e->next->prev = work1;
    work1->next = e->next;
    work1->prev = e;
    e->next = work1;
    (degree[e->start])++;

    /* Now go one edge further around the triangle and the same once more */

    e = e->invers->prev;

    work2->start = work2->invers->end = e->start;
    e->next->prev = work2;
    work2->next = e->next;
    work2->prev = e;
    e->next = work2;
    (degree[e->start])++;

    e = e->invers->prev;

    work3->start = work3->invers->end = e->start;
    e->next->prev = work3;
    work3->next = e->next;
    work3->prev = e;
    e->next = work3;
    (degree[e->start])++;

    degree[nv] = 3;

    /* Now I have 6 edges and one vertex more */

    ne += 6;
    nv++;
}

/****************************************/

static void
reduce3(EDGE *e)

/* deletes a vertex with valence 3 in the triangle on the right hand side
 (->next-direction) of the edge e. It is not checked whether the vertex
 really has valence 3 -- this has to be made sure in advance      */
{
    /* It might be that one of the edges leading to the new vertex now is
       an entry of firstedge[] */

    /* If (firstedge[e->start]==e->next) would take too much time, so just*/

    firstedge[e->start] = e;
    e->next = e->next->next;
    e->next->prev = e;
    (degree[e->start])--;
    e = e->invers;

    firstedge[e->start] = e;
    /* Now delete on the ->prev side */
    e->prev = e->prev->prev;
    e->prev->next = e;
    (degree[e->start])--;
    e = e->prev->invers;

    firstedge[e->start] = e;
    /* Again on the ->prev side: */
    e->prev = e->prev->prev;
    e->prev->next = e;
    (degree[e->start])--;

    nv--;
    ne -= 6;
}

/************************************************************************/

static void
extend4(EDGE *e, EDGE *list[])

/* Deletes e->next and its inverse and puts a valence 4 vertex into the
   resulting square.
   In list[0..1] the deleted edges are stored. This list must be handed 
   to reduce4() */
{
    register EDGE *work1, *work2, *work3, *work4;

    list[0] = e->next;
    list[1] = e->next->invers;

    work1 = STAR4(nv);
    work2 = work1 + 1;
    work3 = work2 + 1;
    work4 = work3 + 1;
    firstedge[nv] = work4 + 1;
    ;

    firstedge[e->start] = e;
    /* make sure firstedge points at a valid edge afterwards */

    /* work1 starts at the beginning of e: */

    work1->start = work1->invers->end = e->start;
    work1->next = e->next->next;
    work1->next->prev = work1;
    work1->prev = e;
    e->next = work1;
    /* the degree of e->start doesn't change */

    /* Now go one edge further around the square: */

    e = e->invers->prev;

    work2->start = work2->invers->end = e->start;
    e->next->prev = work2;
    work2->next = e->next;
    work2->prev = e;
    e->next = work2;
    (degree[e->start])++;

    /* Now we have one edge to jump about again: */
    e = e->invers->prev->prev;

    firstedge[e->start] = e;
    /* Again an edge is deleted... */

    work3->start = work3->invers->end = e->start;
    work3->next = e->next->next;
    work3->next->prev = work3;
    work3->prev = e;
    e->next = work3;
    /* the degree of e->start doesn't change */

    /* Now go again one edge further around the square: */

    e = e->invers->prev;

    work4->start = work4->invers->end = e->start;
    e->next->prev = work4;
    work4->next = e->next;
    work4->prev = e;
    e->next = work4;
    (degree[e->start])++;

    degree[nv] = 4;

    /* Now I have 6 edges and one vertex more */

    ne += 6;
    nv++;
}

/**************************/

static void
reduce4(EDGE *e, EDGE *list[])

/* The inverse operation to extend4().
   Deletes the vertex with valence 4 in the triangle on the right hand side
   (->next-direction) of the edge e that is not contained in e. It is not 
   checked whether the vertex really has valence 4 -- this has to be made
   sure in advance. The vector list[] must contain the edges deleted before. 
   It might be that one of the edges leading to the new vertex now is
   an entry of firstedge[] */
{

    firstedge[e->start] = e;

    list[0]->next->prev = list[0];
    e->next = list[0];
    e = e->invers;

    firstedge[e->start] = e;
    /* Now delete on the ->prev side */
    e->prev = e->prev->prev;
    e->prev->next = e;
    (degree[e->start])--;
    e = e->prev->invers;

    firstedge[e->start] = e;
    /* Again on the ->prev side: */
    list[1]->prev->next = list[1];
    e->prev = list[1];

    e = list[1]->prev->invers;
    firstedge[e->start] = e;
    e->prev = e->prev->prev;
    e->prev->next = e;
    (degree[e->start])--;

    nv--;
    ne -= 6;
}

/**********************************************************************/

static void
extend5(EDGE *e, EDGE *list[])

/* Deletes e->next, e->next->next and their inverse and puts a valence 
   5 vertex into the resulting pentagon.
   In list[0..3] the deleted edges are stored. This list must be handed 
   to reduce5() */
{
    register EDGE *work1, *work2, *work3, *work4, *work5;

    list[0] = e->next;
    list[1] = e->next->invers;
    list[2] = e->next->next;
    list[3] = list[2]->invers;

    work1 = STAR5(nv);
    work2 = work1 + 1;
    work3 = work2 + 1;
    work4 = work3 + 1;
    work5 = work4 + 1;
    firstedge[nv] = work5 + 1;
    ;

    firstedge[e->start] = e;
    /* make sure firstedge points at a valid edge afterwards */

    /* work1 starts at the beginning of e: */

    work1->start = work1->invers->end = e->start;
    work1->next = e->next->next->next;
    work1->next->prev = work1;
    work1->prev = e;
    e->next = work1;
    (degree[e->start])--;

    /* Now go one edge further around the pentagon: */
    e = e->invers->prev;

    work2->start = work2->invers->end = e->start;
    e->next->prev = work2;
    work2->next = e->next;
    work2->prev = e;
    e->next = work2;
    (degree[e->start])++;

    /* Now go one edge further around the pentagon jumping over one edge: */

    e = e->invers->prev->prev;

    firstedge[e->start] = e;
    /* here also an edge is deleted */

    work3->start = work3->invers->end = e->start;
    work3->next = e->next->next;
    work3->next->prev = work3;
    work3->prev = e;
    e->next = work3;
    /* the degree of e->start doesn't change */

    /* Again go one edge further around the pentagon jumping over one edge: */

    e = e->invers->prev->prev;

    firstedge[e->start] = e;
    /* here also an edge is deleted */

    work4->start = work4->invers->end = e->start;
    work4->next = e->next->next;
    work4->next->prev = work4;
    work4->prev = e;
    e->next = work4;
    /* the degree of e->start doesn't change */

    /* Finally go one edge further around the pentagon: */
    e = e->invers->prev;

    work5->start = work5->invers->end = e->start;
    e->next->prev = work5;
    work5->next = e->next;
    work5->prev = e;
    e->next = work5;
    (degree[e->start])++;

    degree[nv] = 5;

    /* Now I have 6 edges and one vertex more */

    ne += 6;
    nv++;
}

/*****************************/

static void
reduce5(EDGE *e, EDGE *list[])

/* The inverse operation to extend5().
   Deletes the vertex with valence 5 at the end of e->next. It is not 
   checked whether the vertex really has valence 5 -- this has to be made
   sure in advance. The vector list[] must contain the edges deleted before.
   It might be that one of the edges leading to the new vertex now is
   an entry of firstedge[] */
{
    firstedge[e->start] = e;

    e->next = list[0];
    list[2]->next->prev = list[2];
    (degree[e->start])++;

    e = e->invers;

    /* Delete the edge on the prev side */
    firstedge[e->start] = e;
    e->prev = e->prev->prev;
    e->prev->next = e;
    (degree[e->start])--;

    e = e->prev->invers;

    firstedge[e->start] = e;
    /* Delete the edge and insert the old edge: */
    e->prev = list[1];
    list[1]->prev->next = list[1];

    e = e->prev->prev->invers;

    firstedge[e->start] = e;
    /* Delete the edge and insert the old edge: */
    e->prev = list[3];
    list[3]->prev->next = list[3];

    e = e->prev->prev->invers;

    firstedge[e->start] = e;
    e->prev = e->prev->prev;
    e->prev->next = e;
    (degree[e->start])--;

    nv--;
    ne -= 6;
}

/*************************************************************************/

static void
switch_edge(EDGE *e)

/* switches edge e -- that is: removes e and puts in the other diagonal in 
   the 4-gon given by the two triangles adjacent to e */
{
    register EDGE *work1, *work2;

    /* closing the gap when e is removed */
    firstedge[e->start] = e->next;
    e->prev->next = e->next;
    e->next->prev = e->prev;
    (degree[e->start])--;

    /* rotating e */
    work1 = e->next->invers;
    work2 = work1->next;
    e->start = work1->start;
    e->end = e->prev->end;
    e->prev = work1;
    e->next = work2;
    work1->next = e;
    work2->prev = e;
    (degree[work1->start])++;

    /* Now doing the same with e->invers */

    e = e->invers;
    firstedge[e->start] = e->next;
    e->prev->next = e->next;
    e->next->prev = e->prev;
    (degree[e->start])--;
    work1 = e->next->invers;
    work2 = work1->next;
    e->start = work1->start;
    e->end = e->prev->end;
    e->prev = work1;
    e->next = work2;
    work1->next = e;
    work2->prev = e;
    (degree[work1->start])++;
}

/***************************************************************************/

static void
switch_edge_back(EDGE *e)

/* Although switching twice is the identity on the graph, it is not on the
   data structure used. In the extend() routines the special order given
   in the initialisation is used */
{
    register EDGE *work1, *work2;

    /* closing the gap when e is removed */
    firstedge[e->start] = e->next;
    e->prev->next = e->next;
    e->next->prev = e->prev;
    (degree[e->start])--;

    /* rotating e */
    work2 = e->prev->invers;
    work1 = work2->prev;
    e->start = work1->start;
    e->end = e->next->end;
    e->prev = work1;
    e->next = work2;
    work1->next = e;
    work2->prev = e;
    (degree[work1->start])++;

    /* Now doing the same with e->invers */

    e = e->invers;
    firstedge[e->start] = e->next;
    e->prev->next = e->next;
    e->next->prev = e->prev;
    (degree[e->start])--;

    work2 = e->prev->invers;
    work1 = work2->prev;
    e->start = work1->start;
    e->end = e->next->end;
    e->prev = work1;
    e->next = work2;
    work1->next = e;
    work2->prev = e;
    (degree[work1->start])++;
}

/**************************************************************************/

static int
testcanon(EDGE *givenedge, int representation[], int colour[])

/* Tests whether starting from a given edge and constructing the code in
   "->next" direction, an automorphism or even a better representation 
   can be found. Returns 0 for failure, 1 for an automorphism and 2 for 
   a better representation.  This function exits as soon as a better 
   representation is found. A function that computes and returns the 
   complete better representation can work pretty similar.*/
{
    EDGE *temp, *run;
    EDGE *startedge[MAXN + 1]; /* startedge[i] is the starting edge for 
                        exploring the vertex with the number i+1 */
    int number[MAXN], i;       /* The new numbers of the vertices, starting 
                        at 1 in order to have "0" as a possibility to
                        mark ends of lists and not yet given numbers */
    int last_number, actual_number, vertex;

    for (i = 0; i < nv; i++)
        number[i] = 0;

    number[givenedge->start] = 1;

    if (givenedge->start != givenedge->end) /* no loop start */
    {
        number[givenedge->end] = 2;
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge;

    /* A representation is a clockwise ordering of all neighbours ended with a 0.
   The neighbours are numbered in the order that they are reached by the BFS 
   procedure. In case a vertex is reached for the first time, not the (new)
   number of the vertex is listed, but its colour. When the list around a
   vertex is finished, it is ended with a 0. Since the colours can be 
   distinguished from the vertices (requirement for the colour function), the
   adjacency list can be reconstructed: Every time a colour is listed, its
   number would be the smallest number not given yet.
   Since the edges when a vertex is reached for the first time are remembered,
   for these edges we in fact have more than just the vertex information -- for
   these edges we also have the exact information which edge occurs in the
   cyclic order. This makes the routine work also for double edges.

   Since every representation starts with the colour of vertex 2, which is
   the same colour all the time, we do not have to store that. 

   In case of a loop as the starting point, the colour of 1 is omitted. 
   Nevertheless also in this case it cannot be mixed up with a non-loop
   starting point, since the number of times a colour occurs is larger
   for loop starters than for non-loop starters.

   Every first entry in a new clockwise ordering (the starting point of the
   edge it was numbered from is determined by the entries before (the first
   time it occurs in the list to be exact), so this is not given either. 
   The K4 could be denoted  c3 c4 0 4 3 0 2 3 0 3 2 0 if ci is the colour
   of vertex i.  Note that the colour of vertex 1 is -- by definition --
   always the smallest one */

    while (last_number < nv)
    {
        for (run = temp->next; run != temp; run = run->next)
        /* this loop marks all edges around temp->origin. */
        {
            vertex = run->end;
            if (!number[vertex])
            {
                startedge[last_number] = run->invers;
                last_number++;
                number[vertex] = last_number;
                vertex = colour[vertex];
            }
            else
                vertex = number[vertex];
            if (vertex > (*representation))
                return 0;
            if (vertex < (*representation))
                return 2;
            representation++;
        }
        /* check whether representation[] is also at the end of a cyclic list */
        if ((*representation) != 0)
            return 2;
        representation++;
        /* Next vertex to explore: */
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nv)
    /* Now we know that all numbers have been given */
    {
        for (run = temp->next; run != temp; run = run->next)
        /* this loop marks all edges around temp->origin. */
        {
            vertex = number[run->end];
            if (vertex > (*representation))
                return 0;
            if (vertex < (*representation))
                return 2;
            representation++;
        }
        /* check whether representation[] is also at the end of a cyclic list */
        if ((*representation) != 0)
            return 2;
        representation++;
        /* Next vertex to explore: */
        temp = startedge[actual_number];
        actual_number++;
    }

    return 1;
}

/*****************************************************************************/

static int
testcanon_mirror(EDGE *givenedge, int representation[], int colour[])

/* Tests whether starting from a given edge and constructing the code in
   "->prev" direction, an automorphism or even a better representation can 
   be found. Comments see testcanon -- it is exactly the same except for 
   the orientation */
{
    EDGE *temp, *run;
    EDGE *startedge[MAXN + 1];
    int number[MAXN], i;
    int last_number, actual_number, vertex;

    for (i = 0; i < nv; i++)
        number[i] = 0;

    number[givenedge->start] = 1;

    if (givenedge->start != givenedge->end)
    {
        number[givenedge->end] = 2;
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge;

    while (last_number < nv)
    {
        for (run = temp->prev; run != temp; run = run->prev)
        {
            vertex = run->end;
            if (!number[vertex])
            {
                startedge[last_number] = run->invers;
                last_number++;
                number[vertex] = last_number;
                vertex = colour[vertex];
            }
            else
                vertex = number[vertex];
            if (vertex > (*representation))
                return 0;
            if (vertex < (*representation))
                return 2;
            representation++;
        }
        if ((*representation) != 0)
            return 2;
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nv)
    {
        for (run = temp->prev; run != temp; run = run->prev)
        {
            vertex = number[run->end];
            if (vertex > (*representation))
                return 0;
            if (vertex < (*representation))
                return 2;
            representation++;
        }
        if ((*representation) != 0)
            return 2;
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    return 1;
}

/****************************************************************************/

static void
testcanon_first_init(EDGE *givenedge, int representation[], int colour[])

/* Tests whether starting from a given edge and constructing the code in
   "->next" direction, an automorphism or even a better representation can 
   be found. A better representation will be completely constructed and 
   returned in "representation".  It works pretty similar to testcanon except 
   for obviously necessary changes, so for extensive comments see testcanon */
{
    register EDGE *run;
    register int vertex;
    EDGE *temp;
    EDGE *startedge[MAXN + 1];
    int number[MAXN], i;
    int last_number, actual_number;

    for (i = 0; i < nv; i++)
        number[i] = 0;

    number[givenedge->start] = 1;
    if (givenedge->start != givenedge->end)
    {
        number[givenedge->end] = 2;
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge;

    while (last_number < nv)
    {
        for (run = temp->next; run != temp; run = run->next)
        {
            vertex = run->end;
            if (!number[vertex])
            {
                startedge[last_number] = run->invers;
                last_number++;
                number[vertex] = last_number;
                *representation = colour[vertex];
            }
            else
                *representation = number[vertex];
            representation++;
        }
        *representation = 0;
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nv)
    {
        for (run = temp->next; run != temp; run = run->next)
        {
            *representation = number[run->end];
            representation++;
        }
        *representation = 0;
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    return;
}

/****************************************************************************/

static void
testcanon_first_init_mirror(EDGE *givenedge, int representation[],
                            int colour[])

/* Tests whether starting from a given edge and constructing the code in
   "->prev" direction, an automorphism or even a better representation can
   be found. A better representation will be completely constructed and
   returned in "representation".  It works pretty similar to testcanon except
   for obviously necessary changes, so for extensive comments see testcanon */
{
    register EDGE *run;
    register int vertex;
    EDGE *temp;
    EDGE *startedge[MAXN + 1];
    int number[MAXN], i;
    int last_number, actual_number;

    for (i = 0; i < nv; i++)
        number[i] = 0;

    number[givenedge->start] = 1;
    if (givenedge->start != givenedge->end)
    {
        number[givenedge->end] = 2;
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge;

    while (last_number < nv)
    {
        for (run = temp->prev; run != temp; run = run->prev)
        {
            vertex = run->end;
            if (!number[vertex])
            {
                startedge[last_number] = run->invers;
                last_number++;
                number[vertex] = last_number;
                *representation = colour[vertex];
            }
            else
                *representation = number[vertex];
            representation++;
        }
        *representation = 0;
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nv)
    {
        for (run = temp->prev; run != temp; run = run->prev)
        {
            *representation = number[run->end];
            representation++;
        }
        *representation = 0;
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    return;
}

/****************************************************************************/

static int
testcanon_init(EDGE *givenedge, int representation[], int colour[])

/* Tests whether starting from a given edge and constructing the code in
   "->next" direction, an automorphism or even a better representation can 
   be found. A better representation will be completely constructed and 
   returned in "representation".  It works pretty similar to testcanon except 
   for obviously necessary changes, so for extensive comments see testcanon */
{
    register EDGE *run;
    register int vertex;
    EDGE *temp;
    EDGE *startedge[MAXN + 1];
    int number[MAXN], i;
    int better = 0; /* is the representation already better ? */
    int last_number, actual_number;

    for (i = 0; i < nv; i++)
        number[i] = 0;

    number[givenedge->start] = 1;
    if (givenedge->start != givenedge->end)
    {
        number[givenedge->end] = 2;
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge;

    while (last_number < nv)
    {
        for (run = temp->next; run != temp; run = run->next)
        {
            vertex = run->end;
            if (!number[vertex])
            {
                startedge[last_number] = run->invers;
                last_number++;
                number[vertex] = last_number;
                vertex = colour[vertex];
            }
            else
                vertex = number[vertex];
            if (better)
                *representation = vertex;
            else
            {
                if (vertex > (*representation))
                    return 0;
                else if (vertex < (*representation))
                {
                    better = 1;
                    *representation = vertex;
                }
            }
            representation++;
        }
        if ((*representation) != 0)
        {
            better = 1;
            *representation = 0;
        }
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nv)
    {
        for (run = temp->next; run != temp; run = run->next)
        {
            vertex = number[run->end];
            if (better)
                *representation = vertex;
            else
            {
                if (vertex > (*representation))
                    return 0;
                if (vertex < (*representation))
                {
                    better = 1;
                    *representation = vertex;
                }
            }
            representation++;
        }
        if ((*representation) != 0)
        {
            better = 1;
            *representation = 0;
        }
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    if (better)
        return 2;
    return 1;
}

/****************************************************************************/

static int
testcanon_mirror_init(EDGE *givenedge, int representation[], int colour[])

/* Tests whether starting from a given edge and constructing the code in
   "->prev" direction, an automorphism or even a better representation can 
   be found. A better representation will be completely constructed and 
   returned in "representation".  It works pretty similar to testcanon except 
   for obviously necessary changes, so for extensive comments see testcanon */
{
    EDGE *temp, *run;
    EDGE *startedge[MAXN + 1];
    int number[MAXN], i;
    int better = 0; /* is the representation already better ? */
    int last_number, actual_number, vertex;

    for (i = 0; i < nv; i++)
        number[i] = 0;

    number[givenedge->start] = 1;
    if (givenedge->start != givenedge->end)
    {
        number[givenedge->end] = 2;
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge;

    while (last_number < nv)
    {
        for (run = temp->prev; run != temp; run = run->prev)
        {
            vertex = run->end;
            if (!number[vertex])
            {
                startedge[last_number] = run->invers;
                last_number++;
                number[vertex] = last_number;
                vertex = colour[vertex];
            }
            else
                vertex = number[vertex];
            if (better)
                *representation = vertex;
            else
            {
                if (vertex > (*representation))
                    return 0;
                else if (vertex < (*representation))
                {
                    better = 1;
                    *representation = vertex;
                }
            }
            representation++;
        }
        if ((*representation) != 0)
        {
            better = 1;
            *representation = 0;
        }
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nv)
    {
        for (run = temp->prev; run != temp; run = run->prev)
        {
            vertex = number[run->end];
            if (better)
                *representation = vertex;
            else
            {
                if (vertex > (*representation))
                    return 0;
                if (vertex < (*representation))
                {
                    better = 1;
                    *representation = vertex;
                }
            }
            representation++;
        }
        if ((*representation) != 0)
        {
            better = 1;
            *representation = 0;
        }
        representation++;
        temp = startedge[actual_number];
        actual_number++;
    }

    if (better)
        return 2;
    return 1;
}

/****************************************************************************/

static void
construct_numb(EDGE *givenedge, EDGE *numbering[])

/* Starts at givenedge and writes the edges in the well defined order 
   into the list.  Works like testcanon. Look there for comments. */
{
    EDGE *temp, **tail, **limit, *run;
    EDGE *startedge[MAXN + 1];
    int last_number, actual_number, vertex;

    RESETMARKS_V;

    tail = numbering;
    limit = numbering + ne - 1;

    MARK_V(givenedge->start);
    if (givenedge->start != givenedge->end)
    {
        MARK_V(givenedge->end);
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = *tail = givenedge;

    while (last_number < nv)
    {
        for (run = temp->next; run != temp; run = run->next)
        /* this loop marks all edges around temp->origin. */
        {
            vertex = run->end;
            if (!ISMARKED_V(vertex))
            {
                startedge[last_number] = run->invers;
                last_number++;
                MARK_V(vertex);
            }
            tail++;
            *tail = run;
        }
        if (tail != limit)
        {
            tail++;
            *tail = temp = startedge[actual_number];
            actual_number++;
        }
    }

    while (tail != limit)
    /* Now we know that all numbers have been given */
    {
        for (run = temp->next; run != temp; run = run->next)
        /* this loop marks all edges around temp->origin. */
        {
            tail++;
            *tail = run;
        }
        if (tail != limit)
        {
            /* Next vertex to explore: */
            tail++;
            *tail = temp = startedge[actual_number];
            actual_number++;
        }
    }
}

/****************************************************************************/

static void
construct_numb_mirror(EDGE *givenedge, EDGE *numbering[])

/* Starts at givenedge and writes the edges in the well defined order 
   into the list.  Works like testcanon. Look there for comments.  */
{
    EDGE *temp, **tail, **limit, *run;
    EDGE *startedge[MAXN + 1];
    int last_number, actual_number, vertex;

    RESETMARKS_V;

    tail = numbering;           /* The first entry of the numbering list */
    limit = numbering + ne - 1; /* Last valid entry of the numbering list */

    MARK_V(givenedge->start);
    if (givenedge->start != givenedge->end)
    {
        MARK_V(givenedge->end);
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = *tail = givenedge;

    while (last_number < nv)
    {
        for (run = temp->prev; run != temp; run = run->prev)
        /* this loop marks all edges around temp->origin. */
        {
            vertex = run->end;
            if (!ISMARKED_V(vertex))
            {
                startedge[last_number] = run->invers;
                last_number++;
                MARK_V(vertex);
            }
            tail++;
            *tail = run;
        }
        if (tail != limit)
        {
            tail++;
            *tail = temp = startedge[actual_number];
            actual_number++;
        }
    }

    while (tail != limit)
    /* Now we know that all numbers have been given */
    {
        for (run = temp->prev; run != temp; run = run->prev)
        /* this loop marks all edges around temp->origin. */
        {
            tail++;
            *tail = run;
        }
        if (tail != limit)
        {
            /* Next vertex to explore: */
            tail++;
            *tail = temp = startedge[actual_number];
            actual_number++;
        }
    }
}

/****************************************************************************/

static int
canon(int lcolour[], EDGE *can_numberings[][MAXE], int *nbtot, int *nbop)

/* Checks whether the last vertex (number: nv-1) is canonical or not. 
   Returns 1 if yes, 0 if not. One of the criterions a canonical vertex 
   must fulfill is that its colour is minimal.

   IT IS ASSUMED that the values of the colour function are positive
   and at most INT_MAX-MAXN.
 
   A possible starting edge for the construction of a representation is 
   one with lexicographically minimal colour pair (start,INT_MAX-end).
   In can_numberings[][] the canonical numberings are stored as sequences 
   of oriented edges.  For every 0 <= i,j < *nbtot and every 
   0 <= k < ne the edges can_numberings[i][k] and can_numberings[j][k] can 
   be mapped onto each other by an automorphism. The first 
   *nbop numberings are orientation preserving while 
   the rest is orientation reversing.

   In case of only 1 automorphism, in can_numberings[0][0] the "canonical" 
   edge is given.  It is one edge emanating at the canonical vertex. The 
   rest of the numbering is not given. 

   In case of nontrivial automorphisms, can[0] starts with a list of edges 
   adjacent to nv-1. In case of an orientation preserving numbering the deges 
   are listed in ->next direction, otherwise in ->prev direction.

   Works OK if at least one vertex has valence >= 3. Otherwise some numberings 
   are computed twice, since changing the orientation (the cyclic order around 
   each vertex) doesn't change anything */
{
    int i, last_vertex, test;
    int minstart, maxend; /* (minstart,maxend) will be the chosen colour 
                                pair of an edge */
    EDGE *startlist_last[5], *startlist[5 * MAXN], *run, *end;
    int list_length_last, list_length;
    int representation[MAXE];
    EDGE *numblist[MAXE], *numblist_mirror[MAXE]; /* lists of edges where 
                        starting gives a canonical representation */
    int numbs = 1, numbs_mirror = 0;
    int colour[MAXN];

    for (i = 0; i < nv; i++)
        colour[i] = lcolour[i] + MAXN;
    /* to distinguish colours from vertices */
    last_vertex = nv - 1;
    minstart = colour[last_vertex];

    /* determine the smallest possible end for the vertex "last_vertex" */

    list_length_last = 1;
    startlist_last[0] = end = firstedge[last_vertex];
    maxend = colour[end->end];

    for (run = end->next; run != end; run = run->next)
    {
        if (colour[run->end] > maxend)
        {
            startlist_last[0] = run;
            list_length_last = 1;
            maxend = colour[run->end];
        }
        else if (colour[run->end] == maxend)
        {
            startlist_last[list_length_last] = run;
            list_length_last++;
        }
    }

    /* Now we know the pair that SHOULD be minimal and we can determine a list 
   of all edges with this colour pair. If a new pair is found that is even 
   smaller, we can return 0 at once */

    list_length = 0;

    for (i = 0; i < last_vertex; i++)
    {
        if (colour[i] < minstart)
            return 0;
        if (colour[i] == minstart)
        {
            run = end = firstedge[i];
            do
            {
                if (colour[run->end] > maxend)
                    return 0;
                if (colour[run->end] == maxend)
                {
                    startlist[list_length] = run;
                    list_length++;
                }
                run = run->next;
            } while (run != end);
        }
    }

    /* OK -- so there is no smaller pair and now we have to determine the 
   smallest representation around vertex "last_vertex": */

    testcanon_first_init(startlist_last[0], representation, colour);
    numblist[0] = startlist_last[0];
    test = testcanon_mirror_init(startlist_last[0], representation, colour);
    if (test == 1)
    {
        numbs_mirror = 1;
        numblist_mirror[0] = startlist_last[0];
    }
    else if (test == 2)
    {
        numbs_mirror = 1;
        numbs = 0;
        numblist_mirror[0] = startlist_last[0];
    }

    for (i = 1; i < list_length_last; i++)
    {
        test = testcanon_init(startlist_last[i], representation, colour);
        if (test == 1)
        {
            numblist[numbs] = startlist_last[i];
            numbs++;
        }
        else if (test == 2)
        {
            numbs_mirror = 0;
            numbs = 1;
            numblist[0] = startlist_last[i];
        }
        test = testcanon_mirror_init(startlist_last[i],
                                     representation, colour);
        if (test == 1)
        {
            numblist_mirror[numbs_mirror] = startlist_last[i];
            numbs_mirror++;
        }
        else if (test == 2)
        {
            numbs_mirror = 1;
            numbs = 0;
            numblist_mirror[0] = startlist_last[i];
        }
    }

    /* Now we know the best representation we can obtain starting at last_vertex. 
   Now we will check all the others. We can return 0 at once if we find a 
   better one */

    for (i = 0; i < list_length; i++)
    {
        test = testcanon(startlist[i], representation, colour);
        if (test == 1)
        {
            numblist[numbs] = startlist[i];
            numbs++;
        }
        else if (test == 2)
            return 0;
        test = testcanon_mirror(startlist[i], representation, colour);
        if (test == 1)
        {
            numblist_mirror[numbs_mirror] = startlist[i];
            numbs_mirror++;
        }
        else if (test == 2)
            return 0;
    }

    *nbop = numbs;
    *nbtot = numbs + numbs_mirror;

    if (*nbtot > 1)
    {
        for (i = 0; i < numbs; i++)
            construct_numb(numblist[i], can_numberings[i]);
        for (i = 0; i < numbs_mirror; i++, numbs++)
            construct_numb_mirror(numblist_mirror[i], can_numberings[numbs]);
    }
    else
    {
        if (numbs)
            can_numberings[0][0] = numblist[0];
        else
            can_numberings[0][0] = numblist_mirror[0];
    }

    return 1;
}

/****************************************************************************/

static int
canon_edge(EDGE *edgelist[], int num_edges,
           int lcolour[], EDGE *can_numberings[][MAXE],
           int *nbtot, int *nbop)

/* 
   IT IS ASSUMED that the values of the colour function are positive and
   at most INT_MAX-MAXN.

   In case edgelist[0] == edgelist[1]->inverse, it checks whether 
   edgelist[0] or edgelist[1] are canonical. Otherwise only
   edgelist[0] is checked to be canonical.

   It is only compared with the other edges contained in edgelist.
   The number of those edges in the list is given in num_edges.
   Returns 1 if yes, 0 if not. 

   Edges given are not in minimal form -- but it is guaranteed that all
   colours of the startpoints are the same and all colours of the endpoints
   are the same.

   In case of only the identity automorphism, the entries of can_numberings[][]
   are undefined.

   Otherwise in can_numberings[][] the canonical numberings are stored as
   sequences of oriented edges.  For every 0 <= i,j < *nbtot
   and every 0 <= k < ne the edges can_numberings[i][k] and
   can_numberings[j][k] can be mapped onto each other by an automorphism.
   The first *nbop numberings are orientation
   preserving while the rest are orientation reversing.

   In case of an orientation preserving numbering the edges are listed in 
   ->next direction, otherwise in ->prev direction.

   Works OK if at least one vertex has valence >= 3. Otherwise some numberings 
   are computed twice, since changing the orientation (the cyclic order around 
   each vertex) doesn't change anything */
{
    int i, test;
    int representation[MAXE];
    EDGE *numblist[MAXE], *numblist_mirror[MAXE]; /* lists of edges where 
                            starting gives a canonical representation */
    int numbs = 1, numbs_mirror = 0;
    int colour[MAXN];

    for (i = 0; i < nv; i++)
        colour[i] = lcolour[i] + MAXN;
    /* to distinguish colours from vertices */

    /* First we have to determine the smallest representation of edgelist[0] */

    testcanon_first_init(edgelist[0], representation, colour);
    numblist[0] = edgelist[0];
    test = testcanon_mirror_init(edgelist[0], representation, colour);
    if (test == 1)
    {
        numbs_mirror = 1;
        numblist_mirror[0] = edgelist[0];
    }
    else if (test == 2)
    {
        numbs_mirror = 1;
        numbs = 0;
        numblist_mirror[0] = edgelist[0];
    }

    if ((num_edges > 1) && (edgelist[0] == edgelist[1]->invers))
    {
        test = testcanon_init(edgelist[1], representation, colour);
        if (test == 1)
        {
            numblist[numbs] = edgelist[1];
            numbs++;
        }
        else if (test == 2)
        {
            numbs_mirror = 0;
            numbs = 1;
            numblist[0] = edgelist[1];
        }
        test = testcanon_mirror_init(edgelist[1], representation, colour);
        if (test == 1)
        {
            numblist_mirror[numbs_mirror] = edgelist[1];
            numbs_mirror++;
        }
        else if (test == 2)
        {
            numbs_mirror = 1;
            numbs = 0;
            numblist_mirror[0] = edgelist[1];
        }
        i = 2; /* start rejecting at the second entry */
    }
    else
        i = 1; /* start rejecting at the first entry */
               /* Now we know the best representation we can obtain with testedge.
   Next we will check all the others. We can return 0 at once if we find a 
   better one */

    for (; i < num_edges; i++)
    {
        test = testcanon(edgelist[i], representation, colour);
        if (test == 1)
        {
            numblist[numbs] = edgelist[i];
            numbs++;
        }
        else if (test == 2)
            return 0;
        test = testcanon_mirror(edgelist[i], representation, colour);
        if (test == 1)
        {
            numblist_mirror[numbs_mirror] = edgelist[i];
            numbs_mirror++;
        }
        else if (test == 2)
            return 0;
    }

    *nbop = numbs;
    *nbtot = numbs + numbs_mirror;

    if (*nbtot > 1)
    {
        for (i = 0; i < numbs; i++)
            construct_numb(numblist[i], can_numberings[i]);
        for (i = 0; i < numbs_mirror; i++, numbs++)
            construct_numb_mirror(numblist_mirror[i], can_numberings[numbs]);
    }

    return 1;
}

/****************************************************************************/

static int
canon_edge_oriented(EDGE *edgelist_or[], int num_edges_or, int can_edges_or,
                    EDGE *edgelist_inv[], int num_edges_inv, int can_edges_inv,
                    int lcolour[], EDGE *can_numberings[][MAXE],
                    int *nbtot, int *nbop)

/* 
   IT IS ASSUMED that the values of the colour function are positive
   and at most INT_MAX-MAXN.

   This routine checks all num_edges_or elements of edgelist_or just for one 
   orientation and all num_edges_inv elements of the list edgelist_inv just
   for the other. It returns 1 if and only if one of the first can_edges_or
   elements of the first list or first can_edges_inv elements of the second 
   give an optimal numbering among all the possibilities provided by the
   lists.

   Edges given are not in minimal form -- but it is guaranteed that all
   colours of the startpoints are the same and all colours of the endpoints
   are the same.

   In case of only the identity automorphism, the entries of can_numberings[][]
   are undefined.

   Otherwise in can_numberings[][] the canonical numberings are stored as
   sequences of oriented edges.  For every 0 <= i,j < *nbtot
   and every 0 <= k < ne the edges can_numberings[i][k] and
   can_numberings[j][k] can be mapped onto each other by an automorphism.
   The first *nbop numberings are orientation
   preserving while the rest are orientation reversing.

   In case of an orientation preserving numbering the edges are listed in 
   ->next direction, otherwise in ->prev direction.

   Works OK if at least one vertex has valence >= 3. Otherwise some numberings 
   are computed twice, since changing the orientation (the cyclic order around 
   each vertex) doesn't change anything */
{
    int i, test;
    int representation[MAXE];
    EDGE *numblist[MAXE], *numblist_mirror[MAXE]; /* lists of edges where 
                            starting gives a canonical representation */
    int numbs = 1, numbs_mirror = 0;
    int colour[MAXN];

    for (i = 0; i < nv; i++)
        colour[i] = lcolour[i] + MAXN;
    /* to distinguish colours from vertices */

    /* First we have to determine the smallest representation possible with
   edgelist_or */

    if (can_edges_or > 0)
    {
        testcanon_first_init(edgelist_or[0], representation, colour);
        numblist[0] = edgelist_or[0];
        for (i = 1; i < can_edges_or; i++)
        {
            test = testcanon_init(edgelist_or[i], representation, colour);
            if (test == 1)
            {
                numblist[numbs] = edgelist_or[i];
                numbs++;
            }
            else if (test == 2)
            {
                numbs = 1;
                numblist[0] = edgelist_or[i];
            }
        }
        i = 0; /* the next for-loop can start at the beginning */
    }
    else
    {
        numbs = 0;
        numbs_mirror = 1;
        testcanon_first_init_mirror(edgelist_inv[0], representation, colour);
        numblist_mirror[0] = edgelist_inv[0];
        i = 1; /* the next for-loop must start at position 1 */
    }

    for (; i < can_edges_inv; i++)
    {
        test = testcanon_mirror_init(edgelist_inv[i], representation, colour);
        if (test == 1)
        {
            numblist_mirror[numbs_mirror] = edgelist_inv[i];
            numbs_mirror++;
        }
        else if (test == 2)
        {
            numbs = 0;
            numbs_mirror = 1;
            numblist_mirror[0] = edgelist_inv[i];
        }
    }

    /* now we know the best we can get for a "canonical edge".
       Next we will check all the others. We can return 0 at once if we find a 
       better one */

    for (i = can_edges_or; i < num_edges_or; i++)
    {
        test = testcanon(edgelist_or[i], representation, colour);
        if (test == 1)
        {
            numblist[numbs] = edgelist_or[i];
            numbs++;
        }
        else if (test == 2)
            return 0;
    }
    for (i = can_edges_inv; i < num_edges_inv; i++)
    {
        test = testcanon_mirror(edgelist_inv[i], representation, colour);
        if (test == 1)
        {
            numblist_mirror[numbs_mirror] = edgelist_inv[i];
            numbs_mirror++;
        }
        else if (test == 2)
            return 0;
    }

    *nbop = numbs;
    *nbtot = numbs + numbs_mirror;

    if (*nbtot > 1)
    {
        for (i = 0; i < numbs; i++)
            construct_numb(numblist[i], can_numberings[i]);
        for (i = 0; i < numbs_mirror; i++, numbs++)
            construct_numb_mirror(numblist_mirror[i], can_numberings[numbs]);
    }

    return 1;
}

/**************************************************************************/

static int
non_facial_triangles(void)

/* Count the non_facial triangles.
   Algorithm: we look for such triangles a-b-c-a, where a<b<c.
   For each b, mark the neighbours a < b.  Then, for each neighbour
   c > b, count the marked neighbours not consecutive to b.
*/
{
    int b, nt;
    EDGE *e, *elast, *ec, *eclast;

    nt = 0;
    for (b = 1; b < nv - 1; ++b)
    {
        RESETMARKS_V;
        e = elast = firstedge[b];
        do
        {
            if (e->end < b)
                MARK_V(e->end);
            e = e->next;
        } while (e != elast);
        do
        {
            if (e->end > b && degree[e->end] >= 4)
            {
                eclast = e->invers;
                ec = eclast->next->next;
                eclast = eclast->prev;
                for (; ec != eclast; ec = ec->next)
                    if (ISMARKED_V(ec->end))
                        ++nt;
            }
            e = e->next;
        } while (e != elast);
    }

    return nt;
}

/**************************************************************************/

static int
has_non_facial_triangle(void)

/* Test if there is a non-facial-triangle in a triangulation.
   Algorithm: we look for such triangles a-b-c-a, where a<b<c.
   For each b, mark the neighbours a < b.  Then, for each neighbour
   c > b, count the marked neighbours not consecutive to b.
*/
{
    int b;
    EDGE *e, *elast, *ec, *eclast;

    for (b = 1; b < nv - 1; ++b)
    {
        RESETMARKS_V;
        e = elast = firstedge[b];
        do
        {
            if (e->end < b)
                MARK_V(e->end);
            e = e->next;
        } while (e != elast);
        do
        {
            if (e->end > b && degree[e->end] >= 4)
            {
                eclast = e->invers;
                ec = eclast->next->next;
                eclast = eclast->prev;
                for (; ec != eclast; ec = ec->next)
                    if (ISMARKED_V(ec->end))
                        return TRUE;
            }
            e = e->next;
        } while (e != elast);
    }

    return FALSE;
}

/****************************************************************************/

static int
numbermarked(void)
{
    int list[MAXN], i, index, number, dummy, top, buffer;
    EDGE *run;

    for (top = 0; (top < nv) && ISMARKED_V(top); top++)
        ;
    if (top == nv)
    {
        fprintf(stderr, "SHIT\n");
        exit(1);
    }

    MARK_V(top);
    list[0] = top;
    number = 1;
    index = 0;

    while (index < number)
    {
        dummy = list[index];
        run = firstedge[dummy];
        for (i = 0; i < degree[dummy]; i++, run = run->next)
        {
            buffer = run->end;
            if (!ISMARKED_V(buffer))
            {
                MARK_V(buffer);
                list[number] = buffer;
                number++;
            }
        }
        index++;
    }
    return number;
}

static int
hastwocut(void)
{
    int i, j;

    for (i = 0; i < nv - 1; i++)
        for (j = i + 1; j < nv; j++)
        {
            RESETMARKS_V;
            MARK_V(i);
            MARK_V(j);
            if (numbermarked() < (nv - 2))
                return 1;
        }
    return 0;
}

static int
hascutvertex(void)
{
    int i;

    if (nv > 2)
    {
        for (i = 0; i < nv; i++)
            if (degree[i] == 1)
                return 1;
    }

    for (i = 0; i < nv; i++)
    {
        RESETMARKS_V;
        MARK_V(i);
        if (numbermarked() < (nv - 1))
            return 1;
    }

    return 0;
}

static int
connectivity(void)
/* Connectivity - very slow, testing only.
   Returns 3 for connectivity >= 3. */
{

    if (hascutvertex())
        return 1;
    if (hastwocut())
        return 2;
    return 3;
}

/****************************************************************************/

static int
numedgeorbits(int nbtot, int nbop)

/* return number of orbits of directed edges, under the
   orientation-preserving automorphism group (assumed computed) */
{
    register EDGE **nb0, **nblim, **nb;
    register int i, j;

    if (nbtot == 1)
        return ne;
    else
    {
        nb0 = (EDGE **)numbering[0];
        if (nbop == 0)
            nblim = (EDGE **)numbering[nbtot];
        else
            nblim = (EDGE **)numbering[nbop];

        RESETMARKS;

        j = 0;
        for (i = 0; i < ne; ++i, ++nb0)
            if (!ISMARKEDLO(*nb0))
            {
                ++j;
                for (nb = nb0; nb < nblim; nb += MAXE)
                    MARKLO(*nb);
            }
        return j;
    }
}

/****************************************************************************/

static int
numfaceorbits(int nbtot, int nbop)

/* return number of orbits of faces, under the full group
   (assumed computed).  This is supposed to work even if the
   graph is only 1-connected. */
{
    EDGE **nb0, **nblim, **nb, **nboplim;
    EDGE *e, *elast, *ee;
    int i, count;

    RESETMARKS;
    count = 0;

    if (nbtot == 1)
    {
        for (i = 0; i < nv; ++i)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e))
                {
                    ++count;
                    ee = e;
                    do
                    {
                        MARKLO(ee);
                        ee = ee->invers->prev;
                    } while (ee != e);
                }
                e = e->next;
            } while (e != elast);
        }
    }
    else
    {
        nb0 = (EDGE **)numbering[0];
        nblim = (EDGE **)numbering[nbtot];
        nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];

        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        for (i = 0; i < nv; ++i)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e))
                {
                    ++count;
                    ee = e;
                    do
                    {
                        for (nb = nb0 + ee->index; nb < nboplim; nb += MAXE)
                            MARKLO(*nb);
                        for (; nb < nblim; nb += MAXE)
                            MARKLO((*nb)->invers);
                        ee = ee->invers->prev;
                    } while (ee != e);
                }
                e = e->next;
            } while (e != elast);
        }
    }

    return count;
}

/****************************************************************************/

static int
numopfaceorbits(int nbtot, int nbop)

/* return number of orbits of faces, under the orientation-preserving
   group (assumed computed).  This is supposed to work even if the
   graph is only 1-connected. */
{
    EDGE **nb0, **nb, **nboplim;
    EDGE *e, *elast, *ee;
    int i, count;

    RESETMARKS;
    count = 0;

    if (nbtot == 1)
    {
        for (i = 0; i < nv; ++i)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e))
                {
                    ++count;
                    ee = e;
                    do
                    {
                        MARKLO(ee);
                        ee = ee->invers->prev;
                    } while (ee != e);
                }
                e = e->next;
            } while (e != elast);
        }
    }
    else
    {
        nb0 = (EDGE **)numbering[0];
        nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];

        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        for (i = 0; i < nv; ++i)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e))
                {
                    ++count;
                    ee = e;
                    do
                    {
                        for (nb = nb0 + ee->index; nb < nboplim; nb += MAXE)
                            MARKLO(*nb);
                        ee = ee->invers->prev;
                    } while (ee != e);
                }
                e = e->next;
            } while (e != elast);
        }
    }

    return count;
}

/****************************************************************************/

static int
numorbits(int nbtot, int nbop)

/* return number of orbits of vertices, under the full group
   (assumed computed). */

{
    EDGE **nb0, **nblim, **nb;
    int vindex[MAXN];
    int i, count;

    if (nbtot == 1)
        return nv;

    nb0 = (EDGE **)numbering[0];
    nblim = (EDGE **)numbering[nbtot];

    for (i = 0; i < ne; ++i)
        vindex[nb0[i]->start] = i;

    RESETMARKS_V;

    count = 0;
    for (i = 0; i < nv; ++i)
        if (!ISMARKED_V(i))
        {
            ++count;
            for (nb = nb0 + vindex[i]; nb < nblim; nb += MAXE)
                MARK_V((*nb)->start);
        }

    return count;
}

/****************************************************************************/

static int
numoporbits(int nbtot, int nbop)

/* return number of orbits of vertices, under the orientation-preserving
   group (assumed computed). */

{
    EDGE **nb0, **nb, **nboplim;
    int vindex[MAXN];
    int i, count;

    if (nbtot == 1)
        return nv;

    nb0 = (EDGE **)numbering[0];
    nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];

    for (i = 0; i < ne; ++i)
        vindex[nb0[i]->start] = i;

    RESETMARKS_V;

    count = 0;
    for (i = 0; i < nv; ++i)
        if (!ISMARKED_V(i))
        {
            ++count;
            for (nb = nb0 + vindex[i]; nb < nboplim; nb += MAXE)
                MARK_V((*nb)->start);
        }

    return count;
}

/****************************************************************************/

static int
numorbitsonface(int nbtot, int nbop, EDGE *e)

/* return number of orbits of directed edges in the face to
   the left of edge e, under the orientation-preserving
   automorphism group (assumed computed) */
{
    register EDGE **nb0, **nblim, **nb;
    register EDGE *e1;
    register int i, j;

    RESETMARKS;

    j = 0;
    e1 = e;
    do
    {
        MARKLO(e1);
        ++j;
        e1 = e1->invers->next;
    } while (e1 != e);

    if (nbtot == 1)
        return j;
    else
    {
        nb0 = (EDGE **)numbering[0];
        if (nbop == 0)
            nblim = (EDGE **)numbering[nbtot];
        else
            nblim = (EDGE **)numbering[nbop];

        j = 0;
        for (i = 0; i < ne; ++i, ++nb0)
            if (ISMARKEDLO(*nb0))
            {
                ++j;
                for (nb = nb0; nb < nblim; nb += MAXE)
                    UNMARK(*nb);
            }
        return j;
    }
}

/**************************************************************************/

static void
make_octahedron(void)

/* Make an octahedron using the first 24 edges */
{
    int i;
    EDGE *buffer;

    for (i = 0; i <= 5; i++)
    {
        buffer = edges + 4 * i;
        firstedge[i] = buffer;
        degree[i] = 4;
        buffer->next = buffer + 1;
        buffer->prev = buffer + 3;
        buffer->start = i;
        buffer++;
        buffer->next = buffer + 1;
        buffer->prev = buffer - 1;
        buffer->start = i;
        buffer++;
        buffer->next = buffer + 1;
        buffer->prev = buffer - 1;
        buffer->start = i;
        buffer++;
        buffer->next = buffer - 3;
        buffer->prev = buffer - 1;
        buffer->start = i;
    }

    buffer = edges; /* edge number 0 */
    buffer->end = 4;
    buffer->invers = edges + 16;
    buffer->min = buffer;

    buffer++; /* edge number 1 */
    buffer->end = 1;
    buffer->invers = edges + 4;
    buffer->min = buffer;

    buffer++; /* edge number 2 */
    buffer->end = 2;
    buffer->invers = edges + 8;
    buffer->min = buffer;

    buffer++; /* edge number 3 */
    buffer->end = 3;
    buffer->invers = edges + 12;
    buffer->min = buffer;

    buffer++; /* edge number 4 */
    buffer->end = 0;
    buffer->invers = edges + 1;
    buffer->min = buffer->invers;

    buffer++; /* edge number 5 */
    buffer->end = 4;
    buffer->invers = edges + 19;
    buffer->min = buffer;

    buffer++; /* edge number 6 */
    buffer->end = 5;
    buffer->invers = edges + 20;
    buffer->min = buffer;

    buffer++; /* edge number 7 */
    buffer->end = 2;
    buffer->invers = edges + 9;
    buffer->min = buffer;

    buffer++; /* edge number 8 */
    buffer->end = 0;
    buffer->invers = edges + 2;
    buffer->min = buffer->invers;

    buffer++; /* edge number 9 */
    buffer->end = 1;
    buffer->invers = edges + 7;
    buffer->min = buffer->invers;

    buffer++; /* edge number 10 */
    buffer->end = 5;
    buffer->invers = edges + 23;
    buffer->min = buffer;

    buffer++; /* edge number 11 */
    buffer->end = 3;
    buffer->invers = edges + 13;
    buffer->min = buffer;

    buffer++; /* edge number 12 */
    buffer->end = 0;
    buffer->invers = edges + 3;
    buffer->min = buffer->invers;

    buffer++; /* edge number 13 */
    buffer->end = 2;
    buffer->invers = edges + 11;
    buffer->min = buffer->invers;

    buffer++; /* edge number 14 */
    buffer->end = 5;
    buffer->invers = edges + 22;
    buffer->min = buffer;

    buffer++; /* edge number 15 */
    buffer->end = 4;
    buffer->invers = edges + 17;
    buffer->min = buffer;

    buffer++; /* edge number 16 */
    buffer->end = 0;
    buffer->invers = edges;
    buffer->min = buffer->invers;

    buffer++; /* edge number 17 */
    buffer->end = 3;
    buffer->invers = edges + 15;
    buffer->min = buffer->invers;

    buffer++; /* edge number 18 */
    buffer->end = 5;
    buffer->invers = edges + 21;
    buffer->min = buffer;

    buffer++; /* edge number 19  */
    buffer->end = 1;
    buffer->invers = edges + 5;
    buffer->min = buffer->invers;

    buffer++; /* edge number 20 */
    buffer->end = 1;
    buffer->invers = edges + 6;
    buffer->min = buffer->invers;

    buffer++; /* edge number 21 */
    buffer->end = 4;
    buffer->invers = edges + 18;
    buffer->min = buffer->invers;

    buffer++; /* edge number 22 */
    buffer->end = 3;
    buffer->invers = edges + 14;
    buffer->min = buffer->invers;

    buffer++; /* edge number 23 */
    buffer->end = 2;
    buffer->invers = edges + 10;
    buffer->min = buffer->invers;

    nv = 6;
    ne = 24;
}

/**************************************************************************/

static void
initialize_bip(void)

/* initialize edges for bipartite generation, and make the
   inital octahedron */
{
    EDGE *run, *start;
    int n;

    /* First initialize the edges for the P-operation. They look like

       a
      / \
  ---b---c   Vertex c is the point where the reference edge is glued to.
      \ /      c--->b is the first edge P_op(n)
       d

a and d will be from the old graph -- they cannot be initialised so far.
It is assumed that for 0<=n<MAXN after P_op(n) there is room for 12 edges.
*/

    for (n = 6; n <= MAXN - 2; n++)
    {
        run = start = P_op(n);
        run->start = n;
        run->end = n + 1;
        run->min = run;
        run->invers = start + 1;
        run->next = start + 2;
        run->prev = start + 4;
        run = start + 1;
        run->start = n + 1;
        run->end = n;
        run->min = run->invers = start;
        run->next = start + 7;
        run->prev = start + 11;
        run = start + 2;
        run->start = n;
        run->min = run;
        run->invers = start + 3;
        run->prev = start;
        run = start + 3;
        run->end = n;
        run->min = run->invers = start + 2;
        run->next = start + 10;
        run = start + 4;
        run->start = n;
        run->min = run;
        run->invers = start + 5;
        run->next = start;
        run = start + 5;
        run->end = n;
        run->min = run->invers = start + 4;
        run->prev = start + 6;
        run = start + 6;
        run->end = n + 1;
        run->min = run;
        run->invers = start + 7;
        run->next = start + 5;
        run = start + 7;
        run->start = n + 1;
        run->min = run->invers = start + 6;
        run->next = start + 9;
        run->prev = start + 1;
        run = start + 8;
        run->end = n + 1;
        run->min = run;
        run->invers = start + 9;
        run = start + 9;
        run->start = n + 1;
        run->min = run->invers = start + 8;
        run->next = start + 11;
        run->prev = start + 7;
        run = start + 10;
        run->end = n + 1;
        run->min = run;
        run->invers = start + 11;
        run->prev = start + 3;
        run = start + 11;
        run->start = n + 1;
        run->min = run->invers = start + 10;
        run->next = start + 1;
        run->prev = start + 9;
    }

    /* The new edges for the Q-operations look like

   |\
   | \ c  Vertex c is the point where the reference edge is glued to
   | /    and the only new vertex
   |/

*/

    for (n = 6; n <= MAXN - 1; n++)
    {
        run = start = Q_op(n);
        run->min = run;
        run->start = n;
        run->invers = start + 1;
        run->next = start + 4;
        run = start + 1;
        run->end = n;
        run->invers = run->min = start;
        run->prev = start + 2;
        run = start + 2;
        run->invers = start + 3;
        run->next = start + 1;
        run->min = run;
        run = start + 3;
        run->invers = run->min = start + 2;
        run->prev = start + 5;
        run = start + 4;
        run->start = n;
        run->invers = start + 5;
        run->prev = start;
        run->min = run;
        run = start + 5;
        run->end = n;
        run->invers = run->min = start + 4;
        run->next = start + 3;
    }

    make_octahedron();
}

/**************************************************************************/

static void
initialize_min4(void)

/* initialize edges for mindegree=4 generation, and make the
   inital octahedron */
{
    EDGE *run, *start;
    int i, n;

    /* First initialise the edges for the four-operation. */

    for (n = 6; n <= MAXN; n++)
    {
        start = four_op(n);
        for (i = 0, run = start; i < 6; i += 2)
        {
            run->start = n;
            run->min = run;
            run->invers = run + 1;
            run++;
            run->end = n;
            run->invers = run->min = run - 1;
            run++;
        }
        run = start;
        run->next = run + 2;
        run += 2; /*2*/
        run->prev = start;
        run->next = run + 2;
        run += 2; /*4*/
        run->prev = start + 2;
    }

    /* Then initialise the edges for the five-operation. */

    for (n = 6; n <= MAXN; n++)
    {
        start = five_op(n);
        for (i = 0, run = start; i < 6; i += 2)
        {
            run->start = n;
            run->min = run;
            run->invers = run + 1;
            run++;
            run->end = n;
            run->invers = run->min = run - 1;
            run++;
        }
        run = start;
        run->next = run + 2;
        run += 2; /*2*/
        run->prev = start;
    }

    /* Then initialise the edges for the S-operation. */

    for (n = 6; n <= MAXN - 3; n++)
    {
        start = S_op(n);
        for (i = 0; i < 18; i += 2)
        {
            run = start + i;
            run->invers = run + 1;
            run->min = run;
            run++;
            run->invers = run->min = run - 1;
        }

        run = start;
        run->start = n + 1;
        run->end = n;
        run->next = start + 4;
        run->prev = start + 9;
        run++; /*1*/
        run->start = n;
        run->end = n + 1;
        run->next = start + 11;
        run->prev = start + 3;
        run++; /*2*/
        run->start = n + 2;
        run->end = n;
        run->next = start + 15;
        run->prev = start + 5;
        run++; /*3*/
        run->start = n;
        run->end = n + 2;
        run->next = start + 1;
        run->prev = start + 13;
        run++; /*4*/
        run->start = n + 1;
        run->end = n + 2;
        run->next = start + 7;
        run->prev = start;
        run++; /*5*/
        run->start = n + 2;
        run->end = n + 1;
        run->next = start + 2;
        run->prev = start + 17;
        run++; /*6*/
        run->end = n + 1;
        run->next = start + 16;
        run++; /*7*/
        run->start = n + 1;
        run->next = start + 9;
        run->prev = start + 4;
        run++; /*8*/
        run->end = n + 1;
        run->prev = start + 10;
        run++; /*9*/
        run->start = n + 1;
        run->next = start;
        run->prev = start + 7;
        run++; /*10*/
        run->end = n;
        run->next = start + 8;
        run++; /*11*/
        run->start = n;
        run->next = start + 13;
        run->prev = start + 1;
        run++; /*12*/
        run->end = n;
        run->prev = start + 14;
        run++; /*13*/
        run->start = n;
        run->next = start + 3;
        run->prev = start + 11;
        run++; /*14*/
        run->end = n + 2;
        run->next = start + 12;
        run++; /*15*/
        run->start = n + 2;
        run->next = start + 17;
        run->prev = start + 2;
        run++; /*16*/
        run->end = n + 2;
        run->prev = start + 6;
        run++; /*17*/
        run->start = n + 2;
        run->next = start + 5;
        run->prev = start + 15;
    }

    make_octahedron();
}

/**************************************************************************/

static void
initialize_triang(void)

/* initialize stars and create initial K4, for ordinary triangulations */
{
    register int i, j;
    register EDGE *si;

    for (i = 0; i < MAXN; ++i)
    {
        si = STAR3(i);

        for (j = 0; j < 3; ++j)
        {
            si[j].end = si[j + 3].start = i;
            si[j].invers = si + 3 + j;
            si[j + 3].invers = si + j;
            si[j].min = si[j + 3].min = si + j;
            si[j + 3].next = si + 3 + (j + 1) % 3;
            si[j + 3].prev = si + 3 + (j + 2) % 3;
        }

        si = STAR4(i);

        for (j = 0; j < 4; ++j)
        {
            si[j].end = si[j + 4].start = i;
            si[j].invers = si + 4 + j;
            si[j + 4].invers = si + j;
            si[j].min = si[j + 4].min = si + j;
            si[j + 4].next = si + 4 + (j + 1) % 4;
            si[j + 4].prev = si + 4 + (j + 3) % 4;
        }

        si = STAR5(i);

        for (j = 0; j < 5; ++j)
        {
            si[j].end = si[j + 5].start = i;
            si[j].invers = si + 5 + j;
            si[j + 5].invers = si + j;
            si[j].min = si[j + 5].min = si + j;
            si[j + 5].next = si + 5 + (j + 1) % 5;
            si[j + 5].prev = si + 5 + (j + 4) % 5;
        }
    }

    init_edge[0].start = 0;
    init_edge[0].end = 1;
    init_edge[0].next = init_edge[0].prev = init_edge + 2;
    init_edge[0].invers = init_edge + 1;
    init_edge[0].min = init_edge;

    init_edge[1].start = 1;
    init_edge[1].end = 0;
    init_edge[1].next = init_edge[1].prev = init_edge + 4;
    init_edge[1].invers = init_edge + 0;
    init_edge[1].min = init_edge;

    init_edge[2].start = 0;
    init_edge[2].end = 2;
    init_edge[2].next = init_edge[2].prev = init_edge + 0;
    init_edge[2].invers = init_edge + 3;
    init_edge[2].min = init_edge + 2;

    init_edge[3].start = 2;
    init_edge[3].end = 0;
    init_edge[3].next = init_edge[3].prev = init_edge + 5;
    init_edge[3].invers = init_edge + 2;
    init_edge[3].min = init_edge + 2;

    init_edge[4].start = 1;
    init_edge[4].end = 2;
    init_edge[4].next = init_edge[4].prev = init_edge + 1;
    init_edge[4].invers = init_edge + 5;
    init_edge[4].min = init_edge + 4;

    init_edge[5].start = 2;
    init_edge[5].end = 1;
    init_edge[5].next = init_edge[5].prev = init_edge + 3;
    init_edge[5].invers = init_edge + 4;
    init_edge[5].min = init_edge + 4;

    nv = 3;
    ne = 6;

    degree[0] = degree[1] = degree[2] = 2;
    firstedge[0] = init_edge;
    firstedge[1] = init_edge + 1;
    firstedge[2] = init_edge + 3;

    extend3(init_edge);
}

/**************************************************************************/

static void
find_extensions(int numb_total, int numb_pres,
                EDGE *ext3[], int *numext3,
                EDGE *ext4[], int *numext4,
                EDGE *ext5[], int *numext5)

/* Find all nonequivalent places for extension.
   These are listed in ext# according to the degree of the future new vertex.  
   The number of cases is returned in next# (#=3,4,5). */
{
    register int i, k;
    int deg3, deg4;
    register EDGE *e, *e1, *e2, *ex;
    EDGE **nb0, **nb1, **nbop, **nblim;

    deg3 = deg4 = 0;
    for (i = 0; i < nv; ++i)
        if (degree[i] == 3)
            ++deg3;
        else if (degree[i] == 4)
            ++deg4;

    /* code for trivial group */

    if (numb_total == 1)
    {
        k = 0;
        for (i = 0; i < nv; ++i)
        {
            e = ex = firstedge[i];
            do
            {
                e1 = e->invers->prev;
                if (e1 > e)
                {
                    e1 = e1->invers->prev;
                    if (e1 > e)
                        ext3[k++] = e;
                }
                e = e->next;
            } while (e != ex);
        }
        *numext3 = k;

        if (deg3 <= 2 && !Aswitch)
        {
            k = 0;
            for (i = 0; i < nv; ++i)
            {
                if (degree[i] == 3)
                    continue;
                e = ex = firstedge[i];
                do
                {
                    e1 = e->next;
                    if (e1->invers > e1)
                    {
                        e2 = e1->invers->prev;
                        if ((degree[e->end] == 3) + (degree[e2->end] == 3) == deg3)
                            ext4[k++] = e;
                    }
                    e = e->next;
                } while (e != ex);
            }
            *numext4 = k;
        }
        else
            *numext4 = 0;

        if (deg3 == 0 && deg4 <= 2 && !Aswitch)
        {
            k = 0;
            for (i = 0; i < nv; ++i)
            {
                if (degree[i] < 6)
                    continue;
                e = ex = firstedge[i];
                do
                {
                    e1 = e->next->next->next;
                    if ((degree[e->end] == 4) + (degree[e1->end] == 4) == deg4)
                        ext5[k++] = e;
                    e = e->next;
                } while (e != ex);
            }
            *numext5 = k;
        }
        else
            *numext5 = 0;
    }

    /* code for nontrivial group */

    else
    {
        nb0 = (EDGE **)numbering[0];
        nbop = (EDGE **)numbering[numb_pres == 0 ? numb_total : numb_pres];
        nblim = (EDGE **)numbering[numb_total];

        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        RESETMARKS;

        k = 0;
        for (i = 0; i < ne; ++i)
        {
            e = nb0[i];
            if (ISMARKEDLO(e))
                continue;
            ext3[k++] = e;

            for (nb1 = nb0 + i; nb1 < nbop; nb1 += MAXE)
                MARKLO(*nb1);

            for (; nb1 < nblim; nb1 += MAXE)
                MARKLO((*nb1)->invers);

            e1 = e->invers->prev;
            for (nb1 = nb0 + e1->index; nb1 < nbop; nb1 += MAXE)
                MARKLO(*nb1);

            for (; nb1 < nblim; nb1 += MAXE)
                MARKLO((*nb1)->invers);

            e1 = e1->invers->prev;
            for (nb1 = nb0 + e1->index; nb1 < nbop; nb1 += MAXE)
                MARKLO(*nb1);

            for (; nb1 < nblim; nb1 += MAXE)
                MARKLO((*nb1)->invers);
        }
        *numext3 = k;

        if (deg3 <= 2 && !Aswitch)
        {
            RESETMARKS;

            k = 0;
            for (i = 0; i < ne; ++i)
            {
                e = nb0[i];
                if (ISMARKEDLO(e))
                    continue;
                e1 = e->next->invers->prev;
                if ((degree[e->end] == 3) + (degree[e1->end] == 3) != deg3)
                    continue;
                ext4[k++] = e;

                for (nb1 = nb0 + i; nb1 < nbop; nb1 += MAXE)
                    MARKLO(*nb1);

                for (; nb1 < nblim; nb1 += MAXE)
                    MARKLO((*nb1)->prev->prev);

                for (nb1 = nb0 + e1->index; nb1 < nbop; nb1 += MAXE)
                    MARKLO(*nb1);

                for (; nb1 < nblim; nb1 += MAXE)
                    MARKLO((*nb1)->prev->prev);
            }
            *numext4 = k;
        }
        else
            *numext4 = 0;

        if (deg3 == 0 && deg4 <= 2 && !Aswitch)
        {
            RESETMARKS;

            k = 0;
            for (i = 0; i < ne; ++i)
            {
                e = nb0[i];
                if (ISMARKEDLO(e) || degree[e->start] < 6)
                    continue;

                if ((degree[e->end] == 4) + (degree[e->next->next->next->end] == 4) != deg4)
                    continue;
                ext5[k++] = e;

                for (nb1 = nb0 + i; nb1 < nbop; nb1 += MAXE)
                    MARKLO(*nb1);

                for (; nb1 < nblim; nb1 += MAXE)
                    MARKLO((*nb1)->prev->prev->prev);
            }
            *numext5 = k;
        }
        else
            *numext5 = 0;
    }
}

/**************************************************************************/

static int
make_dual(void)

/* Store in the rightface field of each edge the number of the face on
   the right hand side of that edge.  Faces are numbered 0,1,....  Also
   store in facestart[i] an example of an edge in the clockwise orientation
   of the face boundary, and the size of the face in facesize[i], for each i.
   Returns the number of faces. */
{
    register int i, nf, sz;
    int nvlim;
    register EDGE *e, *ex, *ef, *efx;

    RESETMARKS;

    nvlim = nv + (missing_vertex >= 0);
    nf = 0;
    for (i = 0; i < nvlim; ++i)
    {
        if (i == missing_vertex)
            continue;

        e = ex = firstedge[i];
        do
        {
            if (!ISMARKEDLO(e))
            {
                facestart[nf] = ef = efx = e;
                sz = 0;
                do
                {
                    ef->rightface = nf;
                    MARKLO(ef);
                    ef = ef->invers->prev;
                    ++sz;
                } while (ef != efx);
                facesize[nf] = sz;
                ++nf;
            }
            e = e->next;
        } while (e != ex);
    }

    return nf;
}

/**************************************************************************/

static void
compute_edgecode(unsigned char code[], int *length, int *headerlength)

/* Computes a code by numbering the edges and
   then listing them in code. Code consists of a header (of varying length
   -- see below) and a sequence of entries coding edge numbers and separators
   of length ne+nv-1. In this program unsigned char will always provide enough 
   room to number the edges.

   We will first describe how the default code works: 
   All entries are unsigned char. The first unsigned char encodes the 
   length of the code that follows (so it is not including the 1 byte for
   the header). The numbers of the edges are 0 to 254
   and the byte 255 is always used as a separator between 2 lists of edges.
   The first segment from entry 2 (so the first non-header-entry) until the 
   first separator contains
   the edges around vertex 1 in clockwise order. The second segment between
   the first separator and the second contains the edges around vertex 2 in
   clockwise order, etc. Every edgenumber occurs exactly twice.

   In case of a given directed starting edge in code_edge, this edge is 
   numbered 0 and starts at the vertex corresponding to the first list.

   In plantri it can't happen (at the moment) that 254 is not enough to 
   encode the edges, but it can happen that 255 is not sufficient to encode
   the length of the following code. In this case the first byte is 0 --
   meaning: interpret the second byte as information about sizes of
   the entries. The first 4 bits encode the number of bytes used to
   encode the codesize and the second 4 (those with lower value) encode 
   the number of bytes used to encode the edge numbers. In plantri it will
   never be necessary to use more than 1 byte for the edgenumbers and 2
   for the codesize. So in case the first byte is 0, the second will
   always be (2<<4)+1. The separator is always one byte with value 255.
 
   A sequence of bytes will always be interpreted in a big-endian way. So
   the first byte is the most significant one. In order to be able to
   recognize separators in cases where more than 1 byte is used to encode 
   edges, we never use numbers for the edges where the most significant
   8 bits are 1. So if n bytes are used for the edges, the largest number 
   used is (1<<n)-1-(1<<(n-1)).
*/
{
    register EDGE *run;
    int i, j, startvertex;
    int edgenumber, limitnv;

    RESETMARKS;

    if (missing_vertex >= 0)
        limitnv = nv + 1;
    else
        limitnv = nv;

    i = nv + ne - 1;

    if (i < 256)
    {
        *code = i;
        code++;
        *length = i + 1;
        *headerlength = 1;
    }
    else
    {
        *code = 0;
        code++;
        *code = (2 << 4) + 1;
        code++;
        *code = i >> 8;
        code++;
        *code = i & 255;
        code++;
        *headerlength = 4;
        *length = i + 4;
    }

    if (code_edge == NULL)
        run = firstedge[0];
    else
    {
        run = code_edge;
    }
    startvertex = run->start;
    //MARK(run);
    MARK(run->invers);
    //run->index=
    run->invers->index = *code = 0;
    code++;
    run = run->next;

    edgenumber = 1;

    for (j = 1; j < degree[startvertex]; j++, run = run->next)
    {
        if (ISMARKED(run))
        {
            *code = run->index;
            code++;
        }
        else
        { //MARK(run);
            MARK(run->invers);
            //run->index=
            run->invers->index = *code = edgenumber;
            code++;
            edgenumber++;
        }
    }
    *code = 255;
    code++;

    for (i = 0; i < limitnv; i++)
        if ((i != startvertex) && (i != missing_vertex))
        {
            for (j = 0, run = firstedge[i]; j < degree[i]; j++, run = run->next)
            {
                if (ISMARKED(run))
                {
                    *code = run->index;
                    code++;
                }
                else
                { //MARK(run);
                    MARK(run->invers);
                    //run->index=
                    run->invers->index = edgenumber;
                    *code = edgenumber;
                    code++;
                    edgenumber++;
                }
            }
            *code = 255;
            code++;
        }
    return;
}

/**************************************************************************/

static void
compute_dual_edgecode(unsigned char code[], int *length, int *headerlength)

/* See compute_edgecode. It directly computes the code of the dual.
   In case code_edge is given, the first list of edges corresponds
   to the vertex representing the outer face.
*/

{
    register EDGE *run, *start;
    int i, j;
    int edgenumber, limitnv;

    RESETMARKS;

    if (missing_vertex >= 0)
        limitnv = nv + 1;
    else
        limitnv = nv;

    i = ne + (ne / 2) - nv + 1;

    if (i < 256)
    {
        *code = i;
        code++;
        *length = i + 1;
        *headerlength = 1;
    }
    else
    {
        *code = 0;
        code++;
        *code = (2 << 4) + 1;
        code++;
        *code = i >> 8;
        code++;
        *code = i & 255;
        code++;
        *headerlength = 4;
        *length = i + 4;
    }

    if (code_edge == NULL)
        start = firstedge[0];
    else
    {
        start = code_edge;
    }
    run = start;
    edgenumber = 0;
    do
    {
        if (ISMARKED(run))
        {
            *code = run->index;
            code++;
        }
        else /* so the other side has not yet been visited */
        {
            MARKLO(run->invers);
            /* numbered but left hand face not yet listed. In case of bridges it can even
	     happen for the first face that the other side is already marked high.*/
            //run->index is never used in the future
            run->invers->index = *code = edgenumber;
            code++;
            edgenumber++;
        }
        MARKHI(run); /* is numbered and face on the left has already been listed */
        run = run->prev->invers;
    } while (run != start);
    *code = 255;
    code++;

    /* that was to make sure that in the case of disc triangulations the right start
       is taken -- now the rest */

    for (i = 0; i < limitnv; i++)
        if (i != missing_vertex)
            for (j = 0, start = firstedge[i]; j < degree[i]; j++, start = start->next)
                if (!ISMARKEDHI(start)) /* a new face to be coded */
                {
                    run = start;
                    do
                    {
                        if (ISMARKED(run))
                        {
                            *code = run->index;
                            code++;
                        }
                        else /* so the other side has not yet been visited */
                        {
                            MARKLO(run->invers);
                            run->invers->index = *code = edgenumber;
                            code++;
                            edgenumber++;
                        }
                        MARKHI(run);
                        run = run->prev->invers;
                    } while (run != start);
                    *code = 255;
                    code++;
                }
    return;
}

/**************************************************************************/

static void
mirror_of_edgecode(unsigned char newcode[], unsigned char oldcode[],
                   int preserve, int totallength, int headerlength)
{
    /* copies oldcode to newcode by reversing the rotational order inside
     the lists. In case "preserve" is not 0, it is made sure that the
     face on the left hand side of edge 1 starting at the vertex corresponding
     to the first list is the same afterwards when interpreting the output
     in clockwise order both times 

     In case of "preserve" the routine relies on the first entry of oldcode
     except the vertexnumber being 1. This is guaranteed by compute_edgecode.

*/

    int i, number[MAXE / 2];
    unsigned char *run, *start, *end, *last;

    last = newcode + totallength;

    for (i = 0; i < headerlength; i++)
        newcode[i] = oldcode[i];

    if (!preserve)
    {
        newcode += headerlength;
        start = end = oldcode + headerlength - 1;
        while (newcode < last)
        {
            for (run = end + 1; *run != 255; run++)
                ;
            end = run;
            for (run--; run != start; run--, newcode++)
                *newcode = *run;
            *newcode = 255;
            newcode++;
            start = end;
        }
        return;
    }

    /* else -- do preserve the face */

    for (i = 0; i < ne / 2; i++)
        number[i] = i;
    if (oldcode[headerlength] != 0)
    {
        fprintf(stderr, "Problem in mirror_of_edgecode -- read function description.\n");
        exit(1);
    }
    for (run = oldcode + headerlength; *run != 255; run++)
        ;
    end = run;
    run--;
    number[0] = *run;
    number[*run] = 0;
    newcode += headerlength;
    for (; run != (oldcode + headerlength - 1); run--)
    {
        *newcode = number[*run];
        newcode++;
    }
    *newcode = 255;
    newcode++;
    start = end;

    while (newcode < last)
    {
        for (run = end + 1; *run != 255; run++)
            ;
        end = run;
        for (run--; run != start; run--, newcode++)
            *newcode = number[*run];
        *newcode = 255;
        newcode++;
        start = end;
    }
    return;
}

/**************************************************************************/

static void
write_edgecode(FILE *f, int doflip)

/* Write in edge_code format.  Always write in next direction,
   and if doflip != 0 also write in prev direction. */
{
    int length, headerlength;
    unsigned char code[MAXN + MAXE + 4];
    unsigned char mirrorcode[MAXN + MAXE + 4];

    if ((ne / 2) > UCHAR_MAX)
    {
        fprintf(stderr,
                ">E %s: Output routine write_edgecode not prepared for ", cmdname);
        fprintf(stderr, "that many edges\n");
        exit(1);
    }

    compute_edgecode(code, &length, &headerlength);

    if (fwrite(code, sizeof(unsigned char), length, f) != length)
    {
        fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
        perror(">E ");
        exit(1);
    }
    if (doflip)
    {
        mirror_of_edgecode(mirrorcode, code, (code_edge != NULL), length, headerlength);
        if (fwrite(mirrorcode, sizeof(unsigned char), length, f) != length)
        {
            fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
            perror(">E ");
            exit(1);
        }
    }
}

static void
write_dual_edgecode(FILE *f, int doflip)

/* Write in edge_code format.  Always write in next direction,
   and if doflip != 0 also write in prev direction. */
{
    int length, headerlength;
    unsigned char code[MAXF + MAXE + 4], mirrorcode[MAXF + MAXE + 4];

    if ((ne / 2) > UCHAR_MAX)
    {
        fprintf(stderr,
                ">E %s: Output routine write_dual_edgecode not prepared for ", cmdname);
        fprintf(stderr, "that many edges\n");
        exit(1);
    }

    compute_dual_edgecode(code, &length, &headerlength);
    if (fwrite(code, sizeof(unsigned char), length, f) != length)
    {
        fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
        perror(">E ");
        exit(1);
    }
    if (doflip)
    {
        mirror_of_edgecode(mirrorcode, code, 0, length, headerlength);
        if (fwrite(mirrorcode, sizeof(unsigned char), length, f) != length)
        {
            fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
            perror(">E ");
            exit(1);
        }
    }
}

/**************************************************************************/

static void
compute_code(unsigned char code[])

/* computes a code by numbering the vertices in a breadth first manner and
   then listing them in code. Code is a sequence of numbers of length ne+nv+1.
   The first entry is the number of vertices.
   Then the numbers of the vertices adjacent to the vertex numbered 1 are
   given -- ended by a 0, and listed in clockwise orientation.
   Then those adjacent to 2, ended by a 0, etc. . In case of no
   double edges, the identification of the corresponding "half edges" leaving 
   each vertex is unique. Nevertheless also for this case the following rules
   apply (not in the definition of the code, but in this routine):

   In case of double edges, the first time a new vertex
   b occurs in the list, say it is in the list of vertex a, must be matched
   with the first occurence of vertex a in the list of b. In this routine
   it will always be the first position in the list of b.

   This spanning tree
   gives a unique matching for the other "half edges" -- provided the fact
   that the ordering comes from an embedding on the sphere. 

   In case of a given starting edge in code_edge, the start of this
   edge is numbered 1 and the end 2.
*/
{
    register EDGE *run;
    register int vertex;
    EDGE *temp;
    EDGE *startedge[MAXN + 1];
    int number[MAXN + 1], i;
    int last_number, actual_number;
    EDGE *givenedge;

    for (i = 0; i < nv; i++)
        number[i] = 0;

    *code = nv;
    code++;
    if (code_edge == NULL)
        givenedge = firstedge[0];
    else
    {
        givenedge = code_edge;
        number[nv] = 0;
    }
    number[givenedge->start] = 1;
    if (givenedge->start != givenedge->end)
    {
        number[givenedge->end] = 2;
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge;

    while (last_number < nv)
    {
        *code = number[temp->end];
        code++;
        for (run = temp->next; run != temp; run = run->next)
        {
            vertex = run->end;
            if (!number[vertex])
            {
                startedge[last_number] = run->invers;
                last_number++;
                number[vertex] = last_number;
                *code = last_number;
            }
            else
                *code = number[vertex];
            code++;
        }
        *code = 0;
        code++;
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nv)
    {
        *code = number[temp->end];
        code++;
        for (run = temp->next; run != temp; run = run->next)
        {
            *code = number[run->end];
            code++;
        }
        *code = 0;
        code++;
        temp = startedge[actual_number];
        actual_number++;
    }
}

/****************************************************************************/

static void
compute_code_mirror(unsigned char code[])

/* In the case of no double edges -- that is when the identifications are
   clear -- there is no problem in just returning the inverse order of
   the previously computed code. Nevertheless in the case where edge 
   identifications must be made via the spanning tree described in the code,
   this is not that easy, so we can as well just compute mirror code just
   like the normal code computed before.

   In case code_edge is not NULL, its start is numbered 1 and its
   end is numbered 0.
*/
{
    register EDGE *run;
    register int vertex;
    EDGE *temp;
    EDGE *startedge[MAXN + 1];
    int number[MAXN + 1], i;
    int last_number, actual_number;
    EDGE *givenedge;

    for (i = 0; i < nv; i++)
        number[i] = 0;

    *code = nv;
    code++;
    if (code_edge == NULL)
        givenedge = firstedge[0];
    else
    {
        givenedge = code_edge->invers;
        number[nv] = 0;
    }
    number[givenedge->start] = 1;
    if (givenedge->start != givenedge->end)
    {
        number[givenedge->end] = 2;
        last_number = 2;
        startedge[1] = givenedge->invers;
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge;

    while (last_number < nv)
    {
        *code = number[temp->end];
        code++;
        for (run = temp->prev; run != temp; run = run->prev)
        {
            vertex = run->end;
            if (!number[vertex])
            {
                startedge[last_number] = run->invers;
                last_number++;
                number[vertex] = last_number;
                *code = last_number;
            }
            else
                *code = number[vertex];
            code++;
        }
        *code = 0;
        code++;
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nv)
    {
        *code = number[temp->end];
        code++;
        for (run = temp->prev; run != temp; run = run->prev)
        {
            *code = number[run->end];
            code++;
        }
        *code = 0;
        code++;
        temp = startedge[actual_number];
        actual_number++;
    }
}

/****************************************************************************/

static void
compute_dual_code(unsigned char code[])

/* works like compute_code -- only for the dual */

{
    register EDGE *run, *run2;
    EDGE *temp;
    EDGE *startedge[MAXF + 1];
    /* int i, number[MAXF+1]; */
    int last_number, actual_number;
    int nf;
    EDGE *givenedge;

    nf = 2 + (ne / 2) - nv;
    *code = nf;
    code++;
    RESETMARKS; /* The face on the right has already been numbered if
		   and only if it is marked. */
    /* for (i = 0; i < nf; i++) number[i] = 0; */

    if (code_edge == NULL)
        givenedge = firstedge[0];
    else
        givenedge = code_edge->invers;

    run = givenedge;
    do
    {
        MARKLO(run);
        run->rf = 1;
        run = run->invers->prev;
    } while (run != givenedge);
    if (!ISMARKED(givenedge->invers)) /* no loop in the dual at this point */
    {
        run2 = run = givenedge->invers;
        do
        {
            MARKLO(run2);
            run2->rf = 2;
            run2 = run2->invers->prev;
        } while (run2 != run);
        last_number = 2;
        startedge[1] = givenedge; /* the startedge has the face it belongs
				     to on the LEFT */
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge->invers;
    while (last_number < nf)
    {
        *code = temp->rf;
        code++;
        for (run = temp->prev->invers; run != temp; run = run->prev->invers)
        /* run also has the face it runs around on the left */
        {
            if (!ISMARKED(run))
            {
                startedge[last_number] = run->invers;
                last_number++;
                run2 = run;
                do
                {
                    MARKLO(run2);
                    run2->rf = last_number;
                    run2 = run2->invers->prev;
                } while (run2 != run);
                *code = last_number;
            }
            else
                *code = run->rf;
            code++;
        }
        *code = 0;
        code++;
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nf)
    {
        *code = temp->rf;
        code++;
        for (run = temp->prev->invers; run != temp; run = run->prev->invers)
        {
            *code = run->rf;
            code++;
        }
        *code = 0;
        code++;
        temp = startedge[actual_number];
        actual_number++;
    }
}

/****************************************************************************/

static void
compute_dual_code_mirror(unsigned char code[])

/* works like compute_code_mirror -- only for the dual */

{
    register EDGE *run, *run2;
    EDGE *temp;
    EDGE *startedge[MAXF + 1];
    /* int i, number[MAXF+1]; */
    int last_number, actual_number;
    int nf;
    EDGE *givenedge;

    nf = 2 + (ne / 2) - nv;
    *code = nf;
    code++;
    RESETMARKS; /* The face on the right has already been numbered
                   if and only if it is marked. */
    /* for (i = 0; i < nf; i++) number[i] = 0; */

    if (code_edge == NULL)
        givenedge = firstedge[0];
    else
        givenedge = code_edge->invers;

    run = givenedge;
    do
    {
        MARKLO(run);
        run->rf = 1;
        run = run->invers->prev;
    } while (run != givenedge);
    if (!ISMARKED(givenedge->invers)) /* no loop in the dual at this point */
    {
        run2 = run = givenedge->invers;
        do
        {
            MARKLO(run2);
            run2->rf = 2;
            run2 = run2->invers->prev;
        } while (run2 != run);
        last_number = 2;
        startedge[1] = givenedge; /* the startedge has the face it
				     belongs to on the LEFT */
    }
    else
        last_number = 1;

    actual_number = 1;
    temp = givenedge->invers;

    while (last_number < nf)
    {
        *code = temp->rf;
        code++;
        for (run = temp->invers->next; run != temp; run = run->invers->next)
        /* run also has the face it runs around on the left */
        {
            if (!ISMARKED(run))
            {
                startedge[last_number] = run->invers;
                last_number++;
                run2 = run;
                do
                {
                    MARKLO(run2);
                    run2->rf = last_number;
                    run2 = run2->invers->prev;
                } while (run2 != run);
                *code = last_number;
            }
            else
                *code = run->rf;
            code++;
        }
        *code = 0;
        code++;
        temp = startedge[actual_number];
        actual_number++;
    }

    while (actual_number <= nf)
    {
        *code = temp->rf;
        code++;
        for (run = temp->invers->next; run != temp; run = run->invers->next)
        {
            *code = run->rf;
            code++;
        }
        *code = 0;
        code++;
        temp = startedge[actual_number];
        actual_number++;
    }
}

/**************************************************************************/

static void
write_planar_code(FILE *f, int doflip)

/* Write in planar_code format.  Always write in next direction,
   and if doflip != 0 also write in prev direction. */
{
    size_t length;
    unsigned char code[MAXN + MAXE + 1];

    length = nv + ne + 1;
    compute_code(code);
    if (fwrite(code, sizeof(unsigned char), length, f) != length)
    {
        fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
        perror(">E ");
        exit(1);
    }
    if (doflip)
    {
        compute_code_mirror(code);
        if (fwrite(code, sizeof(unsigned char), length, f) != length)
        {
            fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
            perror(">E ");
            exit(1);
        }
    }
}

/**************************************************************************/

static void
write_dual_planar_code(FILE *f, int doflip)

/* Write the dual in planar_code format.  Always write in next direction,
   and if doflip != 0 also write in prev direction. */
{
    size_t length;
    unsigned char code[MAXF + MAXE + 1];

    length = 3 + ne + (ne / 2) - nv;
    compute_dual_code(code);
    if (fwrite(code, sizeof(unsigned char), length, f) != length)
    {
        fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
        perror(">E ");
        exit(1);
    }
    if (doflip)
    {
        compute_dual_code_mirror(code);
        if (fwrite(code, sizeof(unsigned char), length, f) != length)
        {
            fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
            perror(">E ");
            exit(1);
        }
    }
}

/**************************************************************************/

static void
write_digits(FILE *f, int doflip)

/* Write in alphabetic format.  Always write in next direction,
   and if doflip != 0 also write in prev direction.  This output
   procedure uses the internal numbering of vertices and is 
   intended for debugging purposes. */
{
    int i, k;
    EDGE *ex, *e;
    unsigned char code[2 * MAXN + 2 * MAXE + 9];
    int nvsize;
    int lastnum, w;
    int nbop, nbtot, nbpart;
    EDGE **nb0, **nb, **nblim;
#define CODE0(x) ((x) < 10 ? '0' + (x) : 'a' + (x)-10)

    if (oneswitch)
    {
        nbop = gotone_nbop;
        nbtot = gotone_nbtot;
        nbpart = (nbop == 0 || nbop == nbtot ? nbtot : nbop);
        fprintf(f, "%d %d %d %d %d\n", nv, ne, (doflip ? 2 : 1), nbpart, nbtot);

        nb0 = (EDGE **)numbering[0];
        nblim = (EDGE **)numbering[doflip ? nbpart : nbtot];

        if (nblim != (EDGE **)numbering[1])
            for (nb = nb0; nb < nblim; nb += MAXE)
            {
                for (i = 0; i < ne; ++i)
                    fprintf(f, " %c%c", CODE0(nb[i]->start), CODE0(nb[i]->end));
                fprintf(f, "\n");
            }
    }

    if (nv >= 10)
    {
        code[0] = '0' + nv / 10;
        code[1] = '0' + nv % 10;
        code[2] = ' ';
        nvsize = k = 3;
    }
    else
    {
        code[0] = '0' + nv;
        code[1] = ' ';
        nvsize = k = 2;
    }

    if (missing_vertex < 0)
        lastnum = nv - 1;
    else
        lastnum = nv;

    for (i = 0; i <= lastnum; ++i)
    {
        if (i != missing_vertex)
        {
            e = ex = firstedge[i];
            do
            {
                w = e->end;
                code[k++] = CODE0(w);
                e = e->next;
            } while (e != ex);
            code[k++] = ',';
        }
    }
    code[k - 1] = '\n';

    if (doflip)
    {
        for (i = 0; i < nvsize; ++i)
            code[k++] = code[i];

        for (i = 0; i <= lastnum; ++i)
        {
            if (i != missing_vertex)
            {
                e = ex = firstedge[i];
                do
                {
                    w = e->end;
                    code[k++] = CODE0(w);
                    e = e->prev;
                } while (e != ex);
                code[k++] = ',';
            }
        }
    }
    code[k - 1] = '\n';

    if (fwrite(code, (size_t)1, (size_t)k, f) != (size_t)k)
    {
        fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
        perror(">E ");
        exit(1);
    }
}

/**************************************************************************/

static void
write_alpha(FILE *f, int doflip)

/* Write in alphabetic format.  Always write in next direction,
   and if doflip != 0 also write in prev direction. */
{
    int i, j, start;
    unsigned char code[MAXN + MAXE + 4];
    unsigned char precode[MAXN + MAXE + 1];
    size_t length;

    length = nv + ne;
    compute_code(precode);

    if (nv >= 10)
    {
        code[0] = '0' + nv / 10;
        code[1] = '0' + nv % 10;
        code[2] = ' ';
        length += 3;
        start = 3;
    }
    else
    {
        code[0] = '0' + nv;
        code[1] = ' ';
        length += 2;
        start = 2;
    }

    for (i = 1, j = start; j < length; ++i, ++j)
        if (precode[i] == 0)
            code[j] = ',';
        else
            code[j] = precode[i] - 1 + 'a';

    code[j - 1] = '\n';
    if (fwrite(code, sizeof(unsigned char), length, f) != length)
    {
        fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
        perror(">E ");
        exit(1);
    }
    if (doflip)
    {
        compute_code_mirror(precode);
        for (i = 1, j = start; j < length; ++i, ++j)
            if (precode[i] == 0)
                code[j] = ',';
            else
                code[j] = precode[i] - 1 + 'a';
        code[j - 1] = '\n';
        if (fwrite(code, sizeof(unsigned char), length, f) != length)
        {
            fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
            perror(">E ");
            exit(1);
        }
    }
}

/**************************************************************************/

static void
write_dual_alpha(FILE *f, int doflip)

/* Write the dual in alphabetic format.  Always write in next direction,
   and if doflip != 0 also write in prev direction. */
{
    int i, j, start;
    unsigned char code[MAXN + MAXE + 4];
    unsigned char precode[MAXN + MAXE + 1];
    size_t length;

    length = 2 + ne + (ne / 2) - nv;
    compute_dual_code(precode);

    if (precode[0] >= 10)
    {
        code[0] = '0' + precode[0] / 10;
        code[1] = '0' + precode[0] % 10;
        code[2] = ' ';
        length += 3;
        start = 3;
    }
    else
    {
        code[0] = '0' + precode[0];
        code[1] = ' ';
        length += 2;
        start = 2;
    }

    for (i = 1, j = start; j < length; ++i, ++j)
        if (precode[i] == 0)
            code[j] = ',';
        else
            code[j] = precode[i] - 1 + 'a';

    code[j - 1] = '\n';
    if (fwrite(code, sizeof(unsigned char), length, f) != length)
    {
        fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
        perror(">E ");
        exit(1);
    }
    if (doflip)
    {
        compute_dual_code_mirror(precode);
        for (i = 1, j = start; j < length; ++i, ++j)
            if (precode[i] == 0)
                code[j] = ',';
            else
                code[j] = precode[i] - 1 + 'a';
        code[j - 1] = '\n';
        if (fwrite(code, sizeof(unsigned char), length, f) != length)
        {
            fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
            perror(">E ");
            exit(1);
        }
    }
}

/**************************************************************************/

static void
write_code_as_sparse6(FILE *f, unsigned char code[])

/* Write a graph represented in planar_code to a file in sparse6 format.
   The imbedding is lost but the vertex numbering is the same.  This
   does not use any global variables and works to 255 vertices. */

{
    register unsigned char *pin, *pout;
    unsigned char s6[20 + 2 * MAXE + 2 * MAXF];
    int n, nb, i, j, lastj, x, k, r, rr, topbit;
    int loopcount;

    pin = code;
    n = *pin++;
    pout = s6;
    *pout++ = ':';

    if (n <= 62)
        *pout++ = 63 + n;
    else
    {
        *pout++ = 63 + 63;
        *pout++ = 63 + 0;
        *pout++ = 63 + (n >> 6);
        *pout++ = 63 + (n & 0x3F);
    }

    for (i = n - 1, nb = 0; i != 0; i >>= 1, ++nb)
    {
    }
    topbit = 1 << (nb - 1);
    k = 6;
    x = 0;

    lastj = 0;
    for (j = 0; j < n; ++j)
    {
        loopcount = 0; /* The input code shows loops once from each end,
                            but we want each loop just once in sparse6. */
        while ((i = *pin++) != 0)
        {
            --i;
            if (i < j || (i == j && ((++loopcount) & 1)))
            {
                if (j == lastj)
                {
                    x <<= 1;
                    if (--k == 0)
                    {
                        *pout++ = 63 + x;
                        k = 6;
                        x = 0;
                    }
                }
                else
                {
                    x = (x << 1) | 1;
                    if (--k == 0)
                    {
                        *pout++ = 63 + x;
                        k = 6;
                        x = 0;
                    }
                    if (j > lastj + 1)
                    {
                        for (r = 0, rr = j; r < nb; ++r, rr <<= 1)
                        {
                            if (rr & topbit)
                                x = (x << 1) | 1;
                            else
                                x <<= 1;
                            if (--k == 0)
                            {
                                *pout++ = 63 + x;
                                k = 6;
                                x = 0;
                            }
                        }
                        x <<= 1;
                        if (--k == 0)
                        {
                            *pout++ = 63 + x;
                            k = 6;
                            x = 0;
                        }
                    }
                    lastj = j;
                }
                for (r = 0, rr = i; r < nb; ++r, rr <<= 1)
                {
                    if (rr & topbit)
                        x = (x << 1) | 1;
                    else
                        x <<= 1;
                    if (--k == 0)
                    {
                        *pout++ = 63 + x;
                        k = 6;
                        x = 0;
                    }
                }
            }
        }
    }

    if (k != 6)
        *pout++ = 63 + ((x << k) | ((1 << k) - 1));

    *pout++ = '\n';
    k = pout - s6;

    if (fwrite(s6, sizeof(unsigned char), (size_t)k, f) != k)
    {
        fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
        perror(">E ");
        exit(1);
    }
}

/**************************************************************************/

static void
write_sparse6(FILE *f, int doflip)

/* Write in sparse6 format.  doflip is ignored. */
{
    unsigned char code[MAXN + MAXE + 1];

    compute_code(code);
    write_code_as_sparse6(f, code);
}

/**************************************************************************/

static void
write_dual_sparse6(FILE *f, int doflip)

/* Write dual cubic graph in sparse6 format.  doflip is ignored. */
{
    unsigned char code[MAXF + MAXE + 1];

    compute_dual_code(code);
    write_code_as_sparse6(f, code);
}

/**************************************************************************/

static void
write_code_as_graph6(FILE *f, unsigned char code[])

/* Write a graph represented in planar_code to a file in graph6 format.
   The imbedding is lost, loops are lost, and multiple edges are changed
   to one edge.  The vertex numbering is the same.  This does not use any
   global variables and works to 255 vertices. */

{
    unsigned char g6[20 + MAXF * (MAXF - 1) / 12];
    register unsigned char *pin, *pout;
    int n, nlen, bodylen, i, j, org;
    static unsigned char g6bit[] = {32, 16, 8, 4, 2, 1};

    pin = code;
    n = *pin++;

    if (n <= 62)
    {
        g6[0] = 63 + n;
        nlen = 1;
    }
    else
    {
        g6[0] = 63 + 63;
        g6[1] = 63 + 0;
        g6[2] = 63 + (n >> 6);
        g6[3] = 63 + (n & 0x3F);
        nlen = 4;
    }

    pout = g6 + nlen;
    bodylen = ((n * (n - 1)) / 2 + 5) / 6;
    for (i = 0; i < bodylen; ++i)
        pout[i] = 0;
    pout[bodylen] = '\n';

    for (i = 0, org = -1; i < n; org += i, ++i)
    {
        while ((j = *pin++) != 0)
        {
            if (j <= i)
            {
                j += org;
                pout[j / 6] |= g6bit[j % 6];
            }
        }
    }

    for (i = 0; i < bodylen; ++i)
        pout[i] += 63;

    j = nlen + bodylen + 1;
    if (fwrite(g6, sizeof(unsigned char), (size_t)j, f) != j)
    {
        fprintf(stderr, ">E %s: fwrite() failed\n", cmdname);
        perror(">E ");
        exit(1);
    }
}

/**************************************************************************/

static void
write_graph6(FILE *f, int doflip)

/* Write in graph6 format.  doflip is ignored. */
{
    unsigned char code[MAXN + MAXE + 1];

    compute_code(code);
    write_code_as_graph6(f, code);
}

/**************************************************************************/

static void
write_dual_graph6(FILE *f, int doflip)

/* Write dual cubic graph in graph6 format.  doflip is ignored. */
{
    unsigned char code[MAXF + MAXE + 1];

    compute_dual_code(code);
    write_code_as_graph6(f, code);
}

/**************************************************************************/

static void
check_it(int code, int triang)

/* Checks these properties:
   1. Degrees are correct.
   2. Faces are triangles (if triang)
   3. start and end fields are correct.
   4. min fields are ok.
   5. vertex numbers are in range.
*/

{
    int i, j;
    EDGE *e;

    for (i = 0; i < nv; ++i)
    {
        /*
        if (degree[i] < 3)
        {
            fprintf(stderr,">E degree error, code=%d\n",code);
            exit(1);
        }
	*/

        e = firstedge[i];
        for (j = 0; j < degree[i]; ++j)
            e = e->next;
        if (e != firstedge[i])
        {
            fprintf(stderr, ">E next error, code=%d\n", code);
            exit(1);
        }

        e = firstedge[i];
        for (j = 0; j < degree[i]; ++j)
            e = e->prev;
        if (e != firstedge[i])
        {
            fprintf(stderr, ">E prev error, code=%d\n", code);
            exit(1);
        }

        e = firstedge[i];
        for (j = 0; j < degree[i]; ++j)
        {
            e = e->next;
            if (e->start != i)
            {
                fprintf(stderr, ">E start error, code=%d\n", code);
                exit(1);
            }
            if (e->end < 0 || e->end >= nv)
            {
                fprintf(stderr, ">E end label error, code=%d\n", code);
                exit(1);
            }
            if (e->end != e->invers->start)
            {
                fprintf(stderr, ">E invers label error, code=%d\n", code);
                exit(1);
            }
            if (e->invers->end != i)
            {
                fprintf(stderr, ">E end error, code=%d\n", code);
                exit(1);
            }
            if (triang)
                if (e->invers->next == e || e->invers->next->invers->next == e || e->invers->next->invers->next->invers->next != e)
                {
                    fprintf(stderr, ">E face error, code=%d\n", code);
                    exit(1);
                }

            if (e->min != e && e->min != e->invers)
            {
                fprintf(stderr, ">E min error 1, code=%d\n", code);
                exit(1);
            }

            if (e->invers->min != e->min)
            {
                fprintf(stderr, ">E min error 2, code=%d\n", code);
                exit(1);
            }
        }
    }
}

/**************************************************************************/

static void
got_one(int nbtot, int nbop, int connec)

/* This is called when a complete output graph is formed.  The main 
   purpose is to write the graph and to collect some stats. */
{
    int doflip, wt;
#ifdef STATS
    int numroot;
#ifdef STATS2
    int num2, i;
#endif
#endif

    if (xswitch && connec != xconnec)
        return;

    doflip = oswitch && (nbop == nbtot || nbop == 0);
    wt = doflip ? 2 : 1;

    if (Vswitch)
    {
        if (nbtot == 1 || (oswitch && nbop == 1))
        {
            ADDBIG(nout_V, wt);
            return;
        }
    }

#ifdef FILTER
    if (!FILTER(nbtot, nbop, doflip))
        return;
#endif

    ADDBIG(nout[connec], 1);
    if (oswitch)
        ADDBIG(nout_op[connec], wt);

    if (pswitch)
    {
        if (oswitch)
            ADDBIG(nout_e_op[ne / 2], wt);
        ADDBIG(nout_e[ne / 2], 1);
    }

    if (polygonsize == 0)
    {
        if (oswitch)
            ADDBIG(nout_p_op[outside_face_size], wt);
        ADDBIG(nout_p[outside_face_size], 1);
    }

#ifdef STATS
    if (polygonsize < 0)
    {
        numroot = wt * numedgeorbits(nbtot, nbop);
        ADDBIG(numrooted, numroot);
        if (pswitch)
            ADDBIG(numrooted_e[ne / 2], numroot);
        if (degree[nv - 1] < 6)
            ADDBIG(nummindeg[degree[nv - 1]], wt);
    }
    else
    {
        numroot = wt * numorbitsonface(nbtot, nbop, code_edge);
        ADDBIG(numrooted, numroot);
        ADDBIG(numbigface[degree[missing_vertex]], numroot);
    }
    if (needgroup && nbtot == 1)
        ADDBIG(ntriv, wt);
#ifdef STATS2
    num2 = 0;
    for (i = 0; i < nv; ++i)
        if (degree[i] == 2)
            ++num2;
    ADDBIG(numtwos[num2], wt);
#endif
#endif

    if (!uswitch)
    {
        gotone_nbop = nbop;
        gotone_nbtot = nbtot;
        if (dswitch)
            (*write_dual_graph)(outfile, doflip);
        else
            (*write_graph)(outfile, doflip);
    }
}

/**************************************************************************/

static void
sortedges(EDGE **ed, int ned)

/* Sort an array of edges according to address.
   Good for short arrays only. */
{
    register int i, j;
    EDGE *edi;

    for (i = 1; i < ned; ++i)
    {
        edi = ed[i];
        for (j = i; ed[j - 1] > edi;)
        {
            ed[j] = ed[j - 1];
            if (--j <= 0)
                break;
        }
        ed[j] = edi;
    }
}

/**************************************************************************/

static int
isminset(EDGE **ed, int ned, int nbtot, int nbop,
         EDGE *old_numbering[][MAXE], EDGE *new_numbering[][MAXE],
         int *xnbtot, int *xnbop)

/* Test if the set ed[0..ned-1] is minimal under the group given by
   old_numbering.  These are assumed to be undirected edges matching
   their min fields.  If it is, *xnbtot and *xnbop are counts for the
   stabiliser.  In the case that the stabiliser is not trivial, it is
   placed in new_numbering. 
   (This represents the group, but not a canonical labelling.) */
{
    EDGE **nb, **nbnew;
    EDGE *image[MAXE];
    register int i, j, jnew;
    int instabiliser[2 * MAXE];

    *xnbtot = 1;
    if (nbop > 0)
        *xnbop = 1;
    else
        *xnbop = 0;

    instabiliser[0] = TRUE;

    nb = (EDGE **)old_numbering[0];
    for (i = 0; i < ne; ++i)
        nb[i]->index = i;

    for (j = 1; j < nbtot; ++j)
    {
        nb = (EDGE **)old_numbering[j];
        for (i = 0; i < ned; ++i)
            image[i] = nb[ed[i]->index]->min;

        sortedges(image, ned);
        for (i = 0; i < ned; ++i)
            if (image[i] != ed[i])
                break;
        if (i == ned)
        {
            if (j < nbop)
                ++*xnbop;
            ++*xnbtot;
            instabiliser[j] = TRUE;
        }
        else if (image[i] < ed[i])
            return FALSE;
        else
            instabiliser[j] = FALSE;
    }

    if (*xnbtot > 1)
    {
        jnew = 0;
        for (j = 0; j < nbtot; ++j)
            if (instabiliser[j])
            {
                nb = (EDGE **)old_numbering[j];
                nbnew = (EDGE **)new_numbering[jnew++];
                for (i = 0; i < ne; ++i)
                    nbnew[i] = nb[i];
            }
    }

    return TRUE;
}

/***************************************************************/

/*
static void
delete_edge(EDGE *e)

/-* deletes edge e. Assumes that none of the endpoints of e has valency 1. 
   It assumes that e has a triangle ON THE LEFT. The values of left_facesize
   are updated according to this assumption.
   Currently unused, so commented out. *-/
{
int newfacesize;
EDGE *run, *end;

    firstedge[e->start] = e->next;
    firstedge[e->end] = e->invers->next;

    e->prev->next=e->next;
    e->next->prev=e->prev;
    (degree[e->start])--;

    e=e->invers;

    e->prev->next=e->next;
    e->next->prev=e->prev;
    (degree[e->start])--;

    ne -= 2;

    end=run=e->prev->invers;
         /-* now the face on the right of e when entering this function
            is on the left of run *-/
    newfacesize=run->left_facesize+1;
    
    do { run->left_facesize=newfacesize; run=run->prev->invers;
       } while (run != end);
}
*/

/***************************************************************/

static void
insert_edge_tri(EDGE *e)

/* inserts the edge previously deleted -- e may not have been modified in
   the meantime and the map must look exactly like it looked before deleting 
   it. On the left hand side of e there must be a triangle after inserting e */
{
    int newfacesize;
    EDGE *run;

    ne += 2;

    e->prev->next = e;
    e->next->prev = e;
    (degree[e->start])++;

    e = e->invers;

    e->prev->next = e;
    e->next->prev = e;
    (degree[e->start])++;

    run = e->prev->invers;
    /* now the face on the right of e when entering this function is
           on the left of run */
    newfacesize = e->left_facesize;

    for (run = e->prev->invers; run != e; run = run->prev->invers)
        run->left_facesize = newfacesize;

    run = e->next;
    run->left_facesize = 3;
    run->invers->next->left_facesize = 3;
}

/************************************************************************/

static void
insert_edge_general(EDGE *e)

/* inserts the edge previously deleted -- e may not have been modified in
   the meantime and the map must look exactly like it looked before deleting
   it. There is no special face size required on the left hand side of e */
{
    int newfacesize;
    EDGE *run;

    ne += 2;

    e->prev->next = e;
    e->next->prev = e;
    (degree[e->start])++;

    e = e->invers;

    e->prev->next = e;
    e->next->prev = e;
    (degree[e->start])++;

    run = e->prev->invers;
    /* now the face on the right of e when entering this function is
           on the left of run */
    newfacesize = e->left_facesize;

    for (run = e->prev->invers; run != e; run = run->prev->invers)
        run->left_facesize = newfacesize;

    e = e->invers; /* back to the old */
    run = e->prev->invers;
    newfacesize = e->left_facesize;
    for (run = e->prev->invers; run != e; run = run->prev->invers)
        run->left_facesize = newfacesize;
}

/************************************************************************/

static int
threeconn(EDGE *e)

/* tests whether the graph obtained by deleting EDGE e is still 3-connected.
   The edge e may have been deleted or not, but the values in e must be
   as before it was (possibly) deleted. The map must have been 3-connected
   before -- so especially there weren't any vertices of degree 2.
   degree[] is not assumed correct for the endvertices of e.

   On the left hand side of e there must be a triangle
   (e->left_facesize==3) and it is assumed that it is checked before
   that the endvertices of e have degree at least 3 after the deletion.

   If there is a 2-cut, e->start and e->end cannot be contained, but they
   must be in different components, so v=e->prev->end MUST be contained.
   It is checked whether v is contained in a face that shares yet another
   vertex with the face formerly on the right hand side of e (the new face
   obtained by deleting e).

   Returns 1 if it is 3-connected after deleting e, 0 else.  */

{
    EDGE *run, *start, *end;

    start = e->prev->invers;
    if (degree[start->start] == 3)
        return 1;

    RESETMARKS_V;

    /* The endvertices of e need not be marked */
    for (run = e->next, end = e->invers->prev->invers;
         run != end; run = run->invers->next)
        MARK_V(run->end);

    end = start->prev->prev; /* stops the running around the vertex before
			      the last face */

    /* The first face and the last face contain also one of the endvertices of e,
   so if they also contain marked vertices, then there already was a 2-cut. */

    start = start->next;

    while (start != end)
    {
        run = start->invers;
        start = start->next;
        for (; run != start; run = run->prev->invers)
            if (ISMARKED_V(run->start))
                return 0;
    }

    return 1;
}

/************************************************************************/

static int
twoconn(EDGE *e)

/* tests whether the graph obtained by deleting EDGE e is still 2-connected.
   The edge e may have been deleted or not, but the values in e must be
   as before it was (possibly) deleted. The map must have been 2-connected
   before.  degree[] is not assumed correct for the endvertices of e.

   On the left hand side of e there must be a triangle (e->left_facesize==3).

   If there is a 1-cut, it cannot be e->start or e->end (otherwise
   it was a 1-cut before), but they must be in different components, (same
   reason), so v=e->prev->end MUST be the cutvertex.
   It is checked whether v is contained in the face on the right hand side
   of e (before deleting). 

   Returns 1 if it is 2-connected after deleting e, 0 else.
*/

{
    EDGE *run, *end;
    int v;

    end = e->next;
    if (end == e->prev)
        return 0;
    end = end->invers;

    v = e->prev->end;
    if (degree[v] == 2)
        return 1;

    for (run = e->invers->prev; run != end; run = run->invers->prev)
        if (run->end == v)
            return 0;

    return 1;
}

/***************************************************************/

#if 0
static int
edge_del_conn(EDGE *e, int connectivity)

/* computes the connectivity of the graph after the removal of edge e.
   The edge e may have been deleted or not, but the values in e must be
   as before it was (possibly) deleted.  degree[] is not assumed correct.
   The argument connectivity gives the largest possible value k in {1,2,3}
   so that the map is k-connected before the removal of e. Larger values
   for the connectivity lead to an error. The value returned is also one
   of 1,2,3.

   If connectivity==3 then the endvertices of e are assumed to have
   degree>3 before removing e. This must be guaranteed before calling
   the function.

   On the left hand side of e there must be a triangle (e->left_facesize==3).
*/

{
  if (connectivity==3) return (2+threeconn(e));
  if (connectivity==2) return (1+twoconn(e));
  return 1;
}
#endif

/************************************************************************/

static void
prune_poly_edgelist(EDGE *old[], int numold, EDGE *newe[], int *numnew)

/* Copy from old[0..numold-1] to newe[0..*numnew-1] each edge e with
   these two properties:
   1. Both ends of e have degree >= minpolydeg+1.
   2. e is contained in a 3-face.
   It is legal that old and newe and &numold and numnew are the same.

   17Aug2005: Changed "new" to "newe" to avoid Codewarrior bug.
*/

{
    int i, counter = 0;
    EDGE *e;

    for (i = 0; i < numold; i++, old++)
    {
        e = *old;
        if (degree[e->start] > minpolydeg && degree[e->end] > minpolydeg && (e->left_facesize == 3 || e->invers->left_facesize == 3))
            newe[counter++] = e;
    }

    *numnew = counter;
}

/***************************************************************************/

static void
find_special_loopmakers(EDGE *loops[], int num_loops,
                        EDGE *special_loop_makers[], int *num_spec_loops)

/* Finds all those loops so that after switching on one side of it there is
   a triangle consisting only of loops and on the other there is a double edge.
   The edges are given in min form.  

   It is assumed that the map handed to this routine does not contain
   vertices of valency smaller than "minimumdegree" and the routine only 
   returns edges that can be switched without producing some.

   Additionally, if tswitch==0 (no -t) it is checked that the double
   edges inside the one of the triangles do not contain a loop on
   one side, since this would give a double edge in the dual.

   Or to be exact: They do not contain a loop that is neighbouring both the
   double edges.

   Note that "other" double edges can occur in the dual in case minimumdegree<3.
*/

{
    int i;
    EDGE *run, *test;

    *num_spec_loops = 0;

    if (num_loops < 2)
        return;

    RESETMARKS;
    RESETMARKS_V;

    for (i = 0; i < num_loops; i++)
    {
        run = loops[i];
        MARKLO(run);
        MARKLO(run->invers);
        if (ISMARKED_V(run->start)) /* already another loop started
				                       at the same vertex */
        /* To determine a switcher, a pair of loops is necessary.
             The switcher is always detected by the second loop of the
             pair that is visited */
        {
            if (ISMARKED(run->prev->prev) && (degree[run->prev->end] > minimumdeg) && (run->prev->start != run->prev->end))
            {
                test = run->prev->invers;
                /* the first edge at the top inside the double edge */
                if (tswitch || (test->next->next->invers != test->prev->prev))
                /* the last test is a bit weird in case degree<4 of the test->start
		   but the result is correct */
                {
                    special_loop_makers[*num_spec_loops] = run->prev->min;
                    (*num_spec_loops)++;
                }
            }
            if (ISMARKED(run->next->next) && (degree[run->next->end] > minimumdeg) && (run->next->start != run->next->end))
            {
                test = run->next->invers;
                if (tswitch || (test->next->next->invers != test->prev->prev))
                {
                    special_loop_makers[*num_spec_loops] = run->next->min;
                    (*num_spec_loops)++;
                }
            }
            run = run->invers;
            if (ISMARKED(run->prev->prev) && (degree[run->prev->end] > minimumdeg) && (run->prev->start != run->prev->end))
            {
                test = run->prev->invers;
                if (tswitch || (test->next->next->invers != test->prev->prev))
                {
                    special_loop_makers[*num_spec_loops] = run->prev->min;
                    (*num_spec_loops)++;
                }
            }
            if (ISMARKED(run->next->next) && (degree[run->next->end] > minimumdeg) && (run->next->start != run->next->end))
            {
                test = run->next->invers;
                if (tswitch || (test->next->next->invers != test->prev->prev))
                {
                    special_loop_makers[*num_spec_loops] = run->next->min;
                    (*num_spec_loops)++;
                }
            }
        }
        else
            MARK_V(run->start);
    }
}

/**************************************************************************/

static void
find_loopmakers(EDGE *doubleedges[], int num_doubleedges,
                EDGE *possible_loops[], int *number_pos_loops)

/* This routine uses nv>3!!

   Computes the lists of edges that can be switched to give a loop.
   For every pair of inverse edges, ONE (the smaller one) is written 
   to list. The total number of edges is written to *number_pos_loops.

   For the computation of the switchers it is useful to know where the
   double edges are.  The list doubleedges[] must be supplied as a
   list of all edges contained in multiple edges (one direction
   only). "num_doubleedges" is its number;

   Some reasoning about degrees in this functions uses the fact that
   so far no loops are present in the graph.

   An edge being contained in a double edge cannot be switched to give a 
   loop.
*/

{
    int i, counter = 0;
    EDGE *run, *buffer;

    RESETMARKS;

    if ((num_doubleedges < 2) ||
        ((minimumdeg >= 3) && (num_doubleedges < 4)))
    {
        *number_pos_loops = 0;
        return;
    }

    for (i = 0; i < num_doubleedges; i++)
    {
        run = doubleedges[i];
        MARKLO(run);
        MARKLO(run->invers);
    }

    /* Now all the edges contained in doubleedges are marked and we can
   start testing. We will first look for edges connecting two sets of
   double edges. */

    if (num_doubleedges >= 4)
        for (i = 0; i < num_doubleedges; i++)
        { /* there must be a neighbouring doubleedge */
            run = doubleedges[i];
            if (ISMARKEDLO(run->next) && (!ISMARKEDHI(run->invers->prev)) && (run->start == run->invers->prev->prev->end))
            {
                buffer = run->invers->prev;
                MARKHI(buffer);
                MARKHI(buffer->invers);
                possible_loops[counter] = buffer->min;
                counter++;
            }
            run = run->invers;
            if (ISMARKEDLO(run->next) && (!ISMARKEDHI(run->invers->prev)) && (run->start == run->invers->prev->prev->end))
            {
                buffer = run->invers->prev;
                MARKHI(buffer);
                MARKHI(buffer->invers);
                possible_loops[counter] = buffer->min;
                counter++;
            }
        }

    /* We will now look for switchers that make degree one vertices. They can 
   be easily found: they are exactly the edges adjacent to degree 2 vertices.
   Note that for n>3 there can never be 2 degree 2 vertices neighbouring each other.
*/

    if (minimumdeg == 1)
        for (i = 0; i < nv; i++)
        {
            if (degree[i] == 2)
            {
                possible_loops[counter] = (firstedge[i])->min;
                counter++;
                possible_loops[counter] = (firstedge[i])->next->min;
                counter++;
            }
        }

    *number_pos_loops = counter;
}

/************************************************************************/

static void
prune_edgelist(EDGE *edge[], int *nedges, int nbtot)

/* Reduce edge[0..*nedges-1] (as undirected edges) according to the group */

{
    int i, oldnum, newnum;
    EDGE **nb0, **nb, **nblim;

    if (nbtot == 1)
        return;

    nb0 = (EDGE **)numbering[0];
    nblim = (EDGE **)numbering[nbtot];
    for (i = 0; i < ne; ++i)
        nb0[i]->index = i;

    RESETMARKS;

    oldnum = *nedges;
    newnum = 0;
    for (i = 0; i < oldnum; ++i)
    {
        nb = nb0 + edge[i]->index;
        if (!ISMARKEDLO(*nb))
        {
            edge[newnum++] = edge[i];
            for (; nb < nblim; nb += MAXE)
                MARKLO((*nb)->min);
        }
    }
    *nedges = newnum;
}

/************************************************************************/

static void
find_start_loops(EDGE *loop[], int nloops, EDGE *start[],
                 EDGE *start_inv[], int *nstarts)

/* loop[0..nloops-1] is a list of all the loops.  A "special" loop is
   one with one face bounded by non-loops and the other face bounded
   by loops.  loop[nloops-1] is known to be special.  If loop[nloops-1]
   does not have the lowest vertex degree of all special loops, return
   with *nstarts=0.  Otherwise, list in start[0..*nstarts-1] all the
   special loops with lowest vertex degree, and in start_inv[0..*nstarts-1]
   their inverses.  The orientations in start[] have a loop in the next
   direction.
*/

{
    int i, nst, mindeg;
    EDGE *e;

    e = loop[nloops - 1];
    if (e->next->start == e->next->end)
    {
        start[0] = e;
        start_inv[0] = e->invers;
    }
    else
    {
        start[0] = e->invers;
        start_inv[0] = e;
    }

    nst = 1;
    mindeg = degree[start[0]->end];

    for (i = nloops - 1; --i >= 0;)
    {
        e = loop[i];
        if ((e->next->start == e->next->end) + (e->prev->start == e->prev->end) == 1)
        {
            if (degree[e->end] < mindeg)
            {
                *nstarts = 0;
                return;
            }
            else if (degree[e->end] == mindeg)
            {
                if (e->next->start == e->next->end)
                {
                    start[nst] = e;
                    start_inv[nst++] = e->invers;
                }
                else
                {
                    start_inv[nst] = e;
                    start[nst++] = e->invers;
                }
            }
        }
    }

    *nstarts = nst;
}

/************************************************************************/

static void
scanspecialloops(EDGE *loop[], int nloops, int nbtot, int nbop)

/* The recursive procedure for adding special loops.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   loops[0..nloops-1] are all the loops, of which there is at least one.
   The loops are all in min form. */
{
    register int i;
    int xnbtot, xnbop, nloopmakers, ngood;
    EDGE *loopmaker[MAXE], *good[(MAXE + 1) / 2], *good_inv[(MAXE + 1) / 2];

    got_one(nbtot, nbop, 1);

#ifdef PRE_FILTER_SPECIALLOOP
    if (!(PRE_FILTER_SPECIALLOOP))
        return;
#endif

    find_special_loopmakers(loop, nloops, loopmaker, &nloopmakers);
    if (nloopmakers == 0)
        return;

    if (nbtot > 1)
        prune_edgelist(loopmaker, &nloopmakers, nbtot);

    for (i = 0; i < nloopmakers; ++i)
    {
        switch_edge(loopmaker[i]);

        loop[nloops] = loopmaker[i];
        find_start_loops(loop, nloops + 1, good, good_inv, &ngood);
        if (ngood > 0)
        {
            if (canon_edge_oriented(good, ngood, 1, good_inv, ngood, 1,
                                    degree, numbering, &xnbtot, &xnbop))
                scanspecialloops(loop, nloops + 1, xnbtot, xnbop);
        }

        switch_edge_back(loopmaker[i]);
    }
}

/************************************************************************/

static void
scanordloops(int nbtot, int nbop, int numdoubles)

/* The code for adding ordinary loops using a grey code.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   numdoubles is the number of undirected edges with a parallel mate.
   There are no loops when this is called. */
{
    register int i, j;
    int xnbtot, xnbop, nloopmakers, nloops;
    EDGE *loopmaker[2 * MAXN], *loop[2 * MAXN], **nb0, **nb1, *e1;
    int isloop[2 * MAXN], partner[2 * MAXN], numpseudo, pj;
    long x, xlim, w;

    /*  Meaning of isloop[i]:
 *  0 = not a loop, possibly available for switching
 *  1 = a pseudo-loop: not a loop but unavailable for switching
 *  2 = a real loop, available for unswitching
 *  numpseudo = number of pseudo-loops at the moment.
 */

    got_one(nbtot, nbop, 2 + (numdoubles == 0));

    // fprintf(stderr,"Check this part of the code -- changed by me:\n");
    if ((numdoubles < 2) ||
        ((minimumdeg >= 3) && (numdoubles < 4)))
        return;

        // was: if (numdoubles < 4) return;

#ifdef PRE_FILTER_ORDLOOP
    if (!(PRE_FILTER_ORDLOOP))
        return;
#endif

    find_loopmakers(doubles, numdoubles, loopmaker, &nloopmakers);
    if (nloopmakers == 0)
        return;

    for (i = 0; i < nloopmakers; ++i)
        isloop[i] = 0;
    numpseudo = 0;

    if (nbtot == 1) /* Case of trivial group */
    {
        for (i = 0; i < nloopmakers; ++i)
            loopmaker[i]->index = i;
        for (i = 0; i < nloopmakers; ++i)
        {
            if (degree[loopmaker[i]->start] == 2)
                partner[i] = loopmaker[i]->next->min->index;
            else if (degree[loopmaker[i]->end] == 2)
                partner[i] = loopmaker[i]->invers->next->min->index;
            else
                partner[i] = -1;
        }

        xlim = 1 << nloopmakers;
        for (x = 1; x < xlim; ++x)
        {
            for (j = 0, w = x; (w & 1) == 0; ++j, w >>= 1)
            {
            }
            // if (isloop[j]) switch_edge_back(loopmaker[j]);
            // else           switch_edge(loopmaker[j]);
            // isloop[j] = !isloop[j];
            if (isloop[j] == 0)
                if (degree[loopmaker[j]->start] == 1 || degree[loopmaker[j]->end] == 1)
                {
                    isloop[j] = 1;
                    ++numpseudo;
                }
                else
                {
                    switch_edge(loopmaker[j]);
                    isloop[j] = 2;
                }
            else if (isloop[j] == 1)
            {
                --numpseudo;
                isloop[j] = 0;
            }
            else /* isloop[j] = 2 */
            {
                switch_edge_back(loopmaker[j]);
                isloop[j] = 0;
                pj = partner[j];
                if (pj >= 0 && isloop[pj] == 1)
                {
                    e1 = loopmaker[pj];
                    if (degree[e1->start] > 1 && degree[e1->end] > 1)
                    {
                        switch_edge(e1);
                        isloop[pj] = 2;
                        --numpseudo;
                    }
                }
            }

            if (numpseudo > 0)
                continue;
            for (j = 0; j < nv; ++j)
                if (degree[j] < minimumdeg)
                    break;
            if (j < nv)
                continue;

            for (i = nloops = 0; i < nloopmakers; ++i)
                if (isloop[i])
                    loop[nloops++] = loopmaker[i];

            if (tswitch)
                scanspecialloops(loop, nloops, 1, 1);
            else
            {
                for (j = 0; j < nloops; ++j)
                {
                    if (loop[j]->next->next->next->invers == loop[j] || loop[j]->prev->prev->prev->invers == loop[j])
                        break;
                }
                if (j == nloops)
                    scanspecialloops(loop, nloops, 1, 1);
            }
        }
        if (isloop[nloopmakers - 1] == 2)
            switch_edge_back(loopmaker[nloopmakers - 1]);
    }
    else /* Case of non-trivial group */
    {
        nb0 = (EDGE **)numbering[0];
        nb1 = (EDGE **)saved_numbering[0];
        for (i = 0; i < nbtot; ++i, nb0 += MAXE, nb1 += MAXE)
            for (j = 0; j < ne; ++j)
                nb1[j] = nb0[j];

        sortedges(loopmaker, nloopmakers);
        for (i = 0; i < nloopmakers; ++i)
            loopmaker[i]->index = i;
        for (i = 0; i < nloopmakers; ++i)
        {
            if (degree[loopmaker[i]->start] == 2)
                partner[i] = loopmaker[i]->next->min->index;
            else if (degree[loopmaker[i]->end] == 2)
                partner[i] = loopmaker[i]->invers->next->min->index;
            else
                partner[i] = -1;
        }

        xlim = 1 << nloopmakers;
        for (x = 1; x < xlim; ++x)
        {
            for (j = 0, w = x; (w & 1) == 0; ++j, w >>= 1)
            {
            }
            // if (isloop[j]) switch_edge_back(loopmaker[j]);
            // else           switch_edge(loopmaker[j]);
            // isloop[j] = !isloop[j];
            if (isloop[j] == 0)
                if (degree[loopmaker[j]->start] == 1 || degree[loopmaker[j]->end] == 1)
                {
                    isloop[j] = 1;
                    ++numpseudo;
                }
                else
                {
                    switch_edge(loopmaker[j]);
                    isloop[j] = 2;
                }
            else if (isloop[j] == 1)
            {
                --numpseudo;
                isloop[j] = 0;
            }
            else /* isloop[j] = 2 */
            {
                switch_edge_back(loopmaker[j]);
                isloop[j] = 0;
                pj = partner[j];
                if (pj >= 0 && isloop[pj] == 1)
                {
                    e1 = loopmaker[pj];
                    if (degree[e1->start] > 1 && degree[e1->end] > 1)
                    {
                        switch_edge(e1);
                        isloop[pj] = 2;
                        --numpseudo;
                    }
                }
            }

            if (numpseudo > 0)
                continue;

            for (i = nloops = 0; i < nloopmakers; ++i)
                if (isloop[i] == 2)
                    loop[nloops++] = loopmaker[i];
            if (isminset(loop, nloops, nbtot, nbop,
                         saved_numbering, numbering, &xnbtot, &xnbop))
            {
                for (j = 0; j < nv; ++j)
                    if (degree[j] < minimumdeg)
                        break;
                if (j < nv)
                    continue;

                if (tswitch)
                    scanspecialloops(loop, nloops, xnbtot, xnbop);
                else
                {
                    for (j = 0; j < nloops; ++j)
                    {
                        if (loop[j]->next->next->next->invers == loop[j] || loop[j]->prev->prev->prev->invers == loop[j])
                            break;
                    }
                    if (j == nloops)
                        scanspecialloops(loop, nloops, xnbtot, xnbop);
                }
            }
        }
        if (isloop[nloopmakers - 1] == 2)
            switch_edge_back(loopmaker[nloopmakers - 1]);
    }
}

/**************************************************************************/

static void
find_double_makers(EDGE *list[], int *number, EDGE *de_list[])

/* Put into list[] the edges that can be flipped to make a new
   doubled edge.  Put in de_list[] an example of an edge which 
   will be in parallel with it after it is flipped.  Put in
   *number the number of such things.  All edges are in min form. */
{
    int i, j, num, degneeded;
    EDGE *run, *dummy;

    degneeded = (minimumdeg == 3 ? 4 : 3);

    num = 0;
    for (i = 0; i < nv; i++)
        if (degree[i] >= degneeded)
        {
            run = firstedge[i];
            for (j = degree[i]; j; j--, run = run->next)
                if (run == run->min && degree[run->end] >= degneeded)
                {
                    if (ISADJ(run->next->end, run->prev->end))
                    {
                        dummy = firstedge[run->next->end];
                        while (dummy->end != run->prev->end)
                            dummy = dummy->next;
                        list[num] = run;
                        de_list[num] = dummy->min;
                        num++;
                    }
                }
        }
    *number = num;
}

/**************************************************************************/

static void
update_double_makers(EDGE *list[], int *number, EDGE *de_list[],
                     EDGE *oldlist[], int oldnumber, EDGE *oldde_list[], EDGE *lastflipped)

/* Add more comments.  All edges in the parameters are in min form. */
{
    int a, b, c, d; /* the 4 vertices affected by the last check */
    int i, j, counter;
    EDGE *run, *dummy;
    int degneeded;

    degneeded = (minimumdeg == 3 ? 4 : 3);

    RESETMARKS_V;

    a = lastflipped->start;
    MARK_V(a);
    b = lastflipped->end;
    MARK_V(b);
    c = lastflipped->prev->end;
    MARK_V(c);
    d = lastflipped->next->end;
    MARK_V(d);

    /* abcd must all be distinct, since with lastflipped before and after the
   flipping all edges of K_4 are present, so there would have been a loop
   before or after -- but so far there are no loops... */

    counter = 0;

    for (i = 0; i < oldnumber; i++)
    {
        run = oldlist[i];
        if (!(ISMARKED_V(run->start) || ISMARKED_V(run->end)))
            /* in this case it will be checked from abcd */
            /* The other thing to check is that the edge to be doubled was not
      switched away */
            if (lastflipped != oldde_list[i])
            {
                list[counter] = run;
                de_list[counter] = oldde_list[i];
                counter++;
            }
        /* if it was switched away, there is NO other edge that would be
       doubled, since this would mean that already the edge switched
       away was in a double edge and edges contained in double edges
       are never switched away, since they cannot double another
       (Jordan Curve Theorem). */
    }

    /* Note: It is not possible that some edge not adjacent to abcd can double
   lastflipped in its new position and is not yet included in the old list:
   Lastflipped was flipped in order to double some edge, so there already
   was some edge with these endpoints to double. */

    if (degree[a] >= degneeded)
    {
        run = firstedge[a];
        for (j = degree[a]; j; j--, run = run->next)
            if ((degree[run->end] >= degneeded) &&
                ((run == run->min) || !ISMARKED_V(run->end)))
            /* edges inside the set are regarded twice, so only one of the
         directions should be worked on, edges leaving the set are
         regarded only once */
            {
                if (ISADJ(run->next->end, run->prev->end))
                {
                    dummy = firstedge[run->next->end];
                    while (dummy->end != run->prev->end)
                        dummy = dummy->next;
                    list[counter] = run->min;
                    de_list[counter] = dummy->min;
                    counter++;
                }
            }
    }

    if (degree[b] >= degneeded)
    {
        run = firstedge[b];
        for (j = degree[b]; j; j--, run = run->next)
            if ((degree[run->end] >= degneeded) &&
                ((run == run->min) || !ISMARKED_V(run->end)))
            {
                if (ISADJ(run->next->end, run->prev->end))
                {
                    dummy = firstedge[run->next->end];
                    while (dummy->end != run->prev->end)
                        dummy = dummy->next;
                    list[counter] = run->min;
                    de_list[counter] = dummy->min;
                    counter++;
                }
            }
    }

    if (degree[c] >= degneeded)
    {
        run = firstedge[c];
        for (j = degree[c]; j; j--, run = run->next)
            if ((degree[run->end] >= degneeded) &&
                ((run == run->min) || !ISMARKED_V(run->end)))
            {
                if (ISADJ(run->next->end, run->prev->end))
                {
                    dummy = firstedge[run->next->end];
                    while (dummy->end != run->prev->end)
                        dummy = dummy->next;
                    list[counter] = run->min;
                    de_list[counter] = dummy->min;
                    counter++;
                }
            }
    }

    if (degree[d] >= degneeded)
    {
        run = firstedge[d];
        for (j = degree[d]; j; j--, run = run->next)
            if ((degree[run->end] >= degneeded) &&
                ((run == run->min) || !ISMARKED_V(run->end)))
            {
                if (ISADJ(run->next->end, run->prev->end))
                {
                    dummy = firstedge[run->next->end];
                    while (dummy->end != run->prev->end)
                        dummy = dummy->next;
                    list[counter] = run->min;
                    de_list[counter] = dummy->min;
                    counter++;
                }
            }
    }

    *number = counter;
}

/************************************************************************/

static void
find_feasible_flips(EDGE *flip[], EDGE *mate[], int count, int feasible[],
                    int nbtot)

/* For i=0..count-1, set feasible[i]=1 if flip[i] is the first in its
   edge orbit in flip[0..count-1], and feasible[i]=0 otherwise.
   Also set feasible[i]=0 if flip[i] will definitely have a worse
   colour than mate[i] after flipping. */

{
    int i;
    EDGE **nb0, **nb, **nblim;
    int flipside1, flipside2, flipcol;
    int mateside1, mateside2, matecol;

    if (nbtot == 1)
        for (i = 0; i < count; ++i)
            feasible[i] = 1;
    else
    {
        nb0 = (EDGE **)numbering[0];
        nblim = (EDGE **)numbering[nbtot];
        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        RESETMARKS;

        for (i = 0; i < count; ++i)
        {
            nb = nb0 + flip[i]->index;
            if (!ISMARKEDLO(*nb))
            {
                feasible[i] = 1;
                for (; nb < nblim; nb += MAXE)
                    MARKLO((*nb)->min);
            }
            else
                feasible[i] = 0;
        }
    }

    for (i = 0; i < count; ++i)
        if (feasible[i])
        {
            mateside1 = mate[i]->next->end;
            mateside2 = mate[i]->prev->end;
            flipside1 = flip[i]->start;
            flipside2 = flip[i]->end;

            flipcol = degree[flipside1] + degree[flipside2] - 2;
            matecol = degree[mateside1] + degree[mateside2];

            if (matecol < flipcol)
                feasible[i] = 0;
            else
            {
                if (mateside1 == flipside1 || mateside1 == flipside2)
                    --matecol;
                if (mateside2 == flipside1 || mateside2 == flipside2)
                    --matecol;

                if (matecol < flipcol)
                    feasible[i] = 0;
            }
        }
}

/****************************************************************************/

static void
make_edge_colours(EDGE *test_edge, EDGE *list[], int numlist,
                  EDGE *good[], int *ngood)

/* list[0..numlist-1] give a list of undirected edges, and
   test_edge is another undirected edge (perhaps included). 
   Both must be in min form.

   Calculate a colour for each orientation of all these edges. 
   If the least colour of an orientation of test_edge is not the
   least of all, return with *ngood == 0.
   Otherwise, put those directed edges with the same least colour
   in good[0..*ngood-1], with test_edge and/or its inverse first.

   It is guaranteed that the edges selected all have the same starting
   and ending degree. 

   Note that the definition of colour is used also in find_feasible_flips. */
{
    EDGE *e;
    int i, num_good;
    int d1, d2;
    long bestcol, col1, col2;

    col1 = col2 = (long)(degree[test_edge->prev->end] + degree[test_edge->next->end]) << 20;
    d1 = degree[test_edge->start];
    d2 = degree[test_edge->end];
    col1 += (long)d1 + ((long)d2 << 10);
    col2 += (long)d2 + ((long)d1 << 10);

    bestcol = col1 < col2 ? col1 : col2;

    num_good = 0;
    if (col1 == bestcol)
        good[num_good++] = test_edge;
    if (col2 == bestcol)
        good[num_good++] = test_edge->invers;

    for (i = numlist; --i >= 0;)
    {
        e = list[i];
        if (e == test_edge)
            continue;

        col1 = col2 = (long)(degree[e->prev->end] + degree[e->next->end]) << 20;
        d1 = degree[e->start];
        d2 = degree[e->end];
        col1 += (long)d1 + ((long)d2 << 10);
        col2 += (long)d2 + ((long)d1 << 10);
        if (col1 < bestcol || col2 < bestcol)
        {
            *ngood = 0;
            return;
        }
        if (col1 == bestcol)
            good[num_good++] = e;
        if (col2 == bestcol)
            good[num_good++] = e->invers;
    }

    *ngood = num_good;
}

/****************************************************************************/

static void
make_am(void)

/* Make the adjacency matrix of the graph */
{
    int i;
    EDGE *e, *ex;
    long ami;

    for (i = 0; i < nv; ++i)
    {
        ami = 0;
        e = ex = firstedge[i];
        do
        {
            ami |= BIT(e->end);
            e = e->next;
        } while (e != ex);
        am[i] = ami;
    }
}

/****************************************************************************/

static void
scandouble(int nbtot, int nbop, int numdoubles,
           EDGE *oldflip[], EDGE *oldmate[], int oldnflip, EDGE *lastflip)

/* The main node of the recursion for creating double edges. 
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   numdoubles is the number of undirected edges with a parallel mate.
   oldflip and oldnflip are the flips for the parent graph, and lastflip
   is what was flipped to make this graph.  The initial call is
   distinguished by oldnflip==0.  There are no loops yet. */
{
    register int i, j;
    int xnbtot, xnbop, nflips, xnumdoubles, ngood;
    EDGE *flip[MAXE / 2], *mate[MAXE / 2], *good[MAXE];
    int feasible[MAXE / 2];
    int a, b, c, d;
    long ama, amb, amc, amd;

    if (minconnec == 2)
        got_one(nbtot, nbop, 2 + (numdoubles == 0));

#ifdef PRE_FILTER_DOUBLE
    if (!(PRE_FILTER_DOUBLE))
        return;
#endif

    if (oldnflip == 0)
    {
        make_am();
        find_double_makers(flip, &nflips, mate);
    }
    else
        update_double_makers(flip, &nflips, mate,
                             oldflip, oldnflip, oldmate, lastflip);

    find_feasible_flips(flip, mate, nflips, feasible, nbtot);

    if (minconnec == 1)
        scanordloops(nbtot, nbop, numdoubles);

    for (i = 0; i < nflips; ++i)
    {
        if (!feasible[i])
            continue;

        a = flip[i]->start;
        ama = am[a];
        b = flip[i]->end;
        amb = am[b];
        c = flip[i]->prev->end;
        amc = am[c];
        d = flip[i]->next->end;
        amd = am[d];
        am[a] = ama & ~BIT(b);
        am[b] = amb & ~BIT(a);
        am[c] = amc | BIT(d);
        am[d] = amd | BIT(c);
        switch_edge(flip[i]);

        doubles[numdoubles] = flip[i];
        for (j = 0; j < numdoubles; ++j)
            if (doubles[j] == mate[i])
                break;
        if (j == numdoubles)
        {
            doubles[numdoubles + 1] = mate[i];
            xnumdoubles = numdoubles + 2;
        }
        else
            xnumdoubles = numdoubles + 1;

        make_edge_colours(flip[i], doubles, xnumdoubles, good, &ngood);

        if (ngood > 0 && canon_edge(good, ngood, degree, numbering, &xnbtot, &xnbop))
            scandouble(xnbtot, xnbop, xnumdoubles, flip, mate, nflips, flip[i]);

        am[a] = ama;
        am[b] = amb;
        am[c] = amc;
        am[d] = amd;
        switch_edge_back(flip[i]);
    }
}

/****************************************************************************/

static int
make_colours(int col[], EDGE *e3)
/* Make better colours for maxdeg=3, supposing that expand3() has been
   performed at position e3 (though it hasn't been yet).
   If the virtual new vertex, nv, is not best, return 0.
   Otherwise, return the number of vertices with the same
   colour as nv (including itself).  Note that for correct
   operation, col[nv-1] must have the smallest value in col[]
   and all colours must be positive. */
{
    register int i, c, c0, nc;
    register EDGE *e;
    register int v1, v2, v3;

    v1 = e3->start;
    v2 = e3->end;
    v3 = e3->next->end;

    c0 = (1 << ((++degree[v1]) & 7)) + (1 << ((++degree[v2]) & 7)) + (1 << ((++degree[v3]) & 7));

    col[nv] = 2;
    nc = 1;

    for (i = nv; --i >= 0;)
    {
        if (degree[i] != 3)
            col[i] = degree[i];
        else
        {
            e = firstedge[i];
            c = (1 << (degree[e->end] & 7)) + (1 << (degree[e->next->end] & 7)) + (1 << (degree[e->next->next->end] & 7));
            if (c > c0)
            {
                --degree[v1];
                --degree[v2];
                --degree[v3];
                return 0;
            }
            else if (c == c0)
            {
                col[i] = 2;
                ++nc;
            }
            else
                col[i] = 3;
        }
    }

    --degree[v1];
    --degree[v2];
    --degree[v3];

    return nc;
}

/**************************************************************************/

static int
valid5edge(EDGE *e)

/* e is an edge leaving a vertex of degree 5.  This function returns
   TRUE if e->end is not adjacent to either e->next->next->end or
   e->next->next->next->end, and FALSE otherwise. */
{
    register EDGE *e1, *ex;
    register int u, v;

    e1 = e->next->next;
    u = e1->end;
    v = e1->next->end;

    ex = e->invers;
    for (e1 = ex->next; e1 != ex; e1 = e1->next)
        if (e1->end == u || e1->end == v)
            return FALSE;

    return TRUE;
}

/*************************************************************************/

static void
mark_edge_orbits(EDGE *edge[], int count, int minimal[], int nbtot)

/* edge[0..count-1] is a list of edges.  Put minimal[i] = 1 if
   edge[i] is the first appearance of its orbit, and  minimal[i] = 0
   if not.  Orbits on undirected edges are considered. */
{
    int i;
    EDGE **nb0, **nb, **nblim;

    if (nbtot == 1)
        for (i = 0; i < count; ++i)
            minimal[i] = 1;
    else
    {
        nb0 = (EDGE **)numbering[0];
        nblim = (EDGE **)numbering[nbtot];
        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        RESETMARKS;

        for (i = 0; i < count; ++i)
        {
            nb = nb0 + edge[i]->index;
            if (!ISMARKEDLO((*nb)->min))
            {
                minimal[i] = 1;
                for (; nb < nblim; nb += MAXE)
                    MARKLO((*nb)->min);
            }
            else
                minimal[i] = 0;
        }
    }
}

/*************************************************************************/

static void
check_am2(int code)
/* Just check if am2[][] is valid.  Debug only. */
{
    int i, j, d;
    EDGE *e, *elast;

    for (i = 0; i < nv; ++i)
    {
        if (am2[i][i] == 0)
        {
            fprintf(stderr, ">E am2 error 0, code %d\n", code);
            exit(1);
        }
    }

    for (i = 0; i < nv; ++i)
    {
        d = 0;
        for (j = 0; j < nv; ++j)
            d += (am2[i][j] != 0);
        if (d != degree[i] + 1)
        {
            fprintf(stderr, ">E am2 error 1, code %d\n", code);
            exit(1);
        }
    }

    for (i = 0; i < nv; ++i)
    {
        e = elast = firstedge[i];
        do
        {
            if (am2[i][e->end] == 0)
            {
                fprintf(stderr, ">E am2 error 2, code %d\n", code);
                exit(1);
            }
            e = e->next;
        } while (e != elast);
    }
}

/*************************************************************************/

static unsigned long int neighbours_c4[MAXE / 2][MAXN];
/* neighbours_c4[e][j] is the set of vertices that share a face with vertex j at the moment
   that there are e edges in the graph. */

static void
init_nb4_triangulation(void)
/* initializes the datastructure neighbours_c4. This routine may only be called for triangulations! 
   Only for triangulations the set of neighbours is equal to the set of vertices a vertex shares a face with.
   In fact it does the same as make_am applied to the neighbours_c4 array, but seems to be faster. */
{

    int i, j, ne_u;
    EDGE *run;
    unsigned long int *bitv;
    ne_u = ne / 2;

    for (i = 0; i < nv; i++)
    {
        run = firstedge[i];
        bitv = neighbours_c4[ne_u] + i;
        *bitv = BIT(run->end);
        for (j = degree[i] - 1; j; j--)
        {
            run = run->next;
            *bitv |= BIT(run->end);
        }
    }

    return;
}

static int
test_for_c4(EDGE *rem)

/* assumes that the graph it is called for is 4-connected and tests whether after removing the edge rem 
   -- that bounds a triangle in prev-direction (left) -- the graph is still 4-connected. If rem=a->b 
   it is tested whether a vertex in the boundary of the face on the right of rem shares a face with a vertex 
   different from a,b that also shares a face with the unique vertex on the left of rem. 

   It is assumed that the value in edge->left_facesize is correct.

   Returns 1 if it will be 4-connected and 0 otherwise.
*/

{

    int j;
    EDGE *run;
    unsigned long int buf, *nb4;

    nb4 = neighbours_c4[ne / 2];

    run = rem->next;
    j = rem->invers->left_facesize - 3;
    buf = nb4[rem->prev->end] & ~(BIT(rem->start) | BIT(rem->end));

    if (buf & nb4[run->end])
        return 0;

    for (; j; j--)
    {
        run = run->invers->next;
        if (buf & nb4[run->end])
            return 0;
    }

    return 1;
}

static void
update_neighbours_c4(EDGE *rem)

/* 
   Prepares the array neighbours_c4[ne/2-1] for the deletion of the edge *rem.

   Assumes that the graph it is called for is 4-connected also after removing the edge rem.
   In prev direction of rem there must be a triangle. 

   It is assumed that the value in edge->left_facesize is correct.

   It computes the data for neighbours_c4 after the edge has been removed, but assumes that the edge
   has not yet been removed.
*/

{

    int j;
    EDGE *run;
    unsigned long int *nb4_new, face, left_v;

    nb4_new = neighbours_c4[ne / 2 - 1];

    memcpy(nb4_new, neighbours_c4[ne / 2], nv * sizeof(unsigned long int));

    run = rem->next;
    j = rem->invers->left_facesize - 3;
    left_v = BIT(rem->prev->end);
    face = BIT(run->end);
    nb4_new[run->end] |= left_v;

    for (; j; j--)
    {
        run = run->invers->next;
        face |= BIT(run->end);
        nb4_new[run->end] |= left_v;
    }
    nb4_new[rem->prev->end] |= face;

    return;
}

/*************************************************************************/

static int
maybe_delete_c4(EDGE *edel, int oldmaxface, int oldmaxlist0, int oldmaxlist1,
                int *newmaxface, int *newmaxlist0, int *newmaxlist1,
                EDGE *good_or[], int *ngood_or, int *ncan_or,
                EDGE *good_inv[], int *ngood_inv, int *ncan_inv)

/* Assumes there is a 3-face on the left of *edel, and that *edel can
   be deleted while keeping degrees >= minpolydeg.  Also, the new face
   created will be a largest face.  oldmaxface is the size of the largest
   face so far, and inmaxface[oldmaxlist0..oldmaxlist1-1] are the edges
   with a face of maximum size on the left.

   This procedure deletes *edel provided the result is 4-connected, and that
   the procedure believes the re-insertion of *edel might be a canonical
   edge insertion.  The latter decision is based on four combinatorial
   invariates: the three vertex degrees at the ends of *edel and on its left,
   and the size of the face to the left of edel->prev.

   In case *edel passes the test and is deleted, the edges which may 
   represent the re-insertion of *edel and optimise the four-part invariant
   mentioned above are put in good_or[0..*ncan_or-1] and
   good_inv[0..*ncan_inv-1].  This will include at least one of the edges
   edel->prev, edel->invers->next and (if there is also a 3-face on the
   right of *edel) edel->next and edel->invers->prev.  Then all other edges
   which might possibly represent canonical edge insertions are put in 
   good_or[*ncan_or..*ngood_or-1] or good_inv[*ncan_inv..*ngood_inv-1].
   The *_or edges are those for which the inserted edge will be in the
   next direction, and the *_inv edges .. the prev direction.

   In addition, if *edel is deleted, inmaxface[*newmaxlist0..*newmaxlist1-1]
   will have all edges with a maximum face on the left (that size being put
   into *newmaxface).  This list may overlap
   inmaxface[oldmaxlist0..oldmaxlist1-1] if the max face size does not
   increase.

   Return values:   0 = ok
                    1 = rejected by threeconn()
		    2 = rejected by colour

   This version is for 4-connected only!  maybe_delete_c3() is for 3-conn
   and maybe_delete() is the more general version that works for connectivity
   1 or more.
*/

{
#define DEGENDC4(ed) (degree[ed->end])
#define REJECTC4      \
    {                 \
        ++degree[v1]; \
        ++degree[v2]; \
        return 2;     \
    }
#define ORTESTC4(e)                                                \
    {                                                              \
        col = DEGENDC4(e);                                         \
        if (col > maxcol)                                          \
            REJECTC4 else if (col == maxcol) good_or[ng_or++] = e; \
    }
#define INVTESTC4(e)                                                 \
    {                                                                \
        col = DEGENDC4(e);                                           \
        if (col > maxcol)                                            \
            REJECTC4 else if (col == maxcol) good_inv[ng_inv++] = e; \
    }
#define ORCOLC4(ed) ((degree[ed->invers->prev->end] << 10) + ed->left_facesize)
#define INVCOLC4(ed) \
    ((degree[ed->invers->next->end] << 10) + ed->invers->left_facesize)

    EDGE *e1, *e2, *e3, *e4, *ee;
    long col, maxcol;
    int k, i, v, ng_or, ng_inv, nc_or, nc_inv;
    int maxface, v1, v2, v3, v4, maxdeg, nml1;

    maxface = *newmaxface = edel->invers->left_facesize + 1;
    if (maxface > oldmaxface)
        oldmaxlist0 = oldmaxlist1;
    *newmaxlist0 = oldmaxlist0;

    *ngood_or = *ngood_inv = 0;

    /* Now old edges that will be on a largest face (if *edel is deleted)
    are in places oldmaxlist0..oldmaxlist1-1.  New edges will be from
    oldmaxlist1 to *newmaxlist1-1, but *newmaxlist1 is not set yet. */

    v1 = edel->start;
    v2 = edel->end;
    maxdeg = (degree[v1] > degree[v2] ? degree[v1] : degree[v2]) - 1;

    e1 = edel->prev;
    v3 = e1->end;
    e4 = edel->next;
    v4 = e4->end;

    if (degree[v3] > maxdeg || degree[v4] > maxdeg)
        return 2;

    --degree[v1];
    --degree[v2];
    e2 = edel->invers->next;
    e3 = edel->invers->prev;

    maxcol = nc_or = nc_inv = 0;

    if (degree[v1] == maxdeg)
    {
        col = DEGENDC4(e1);
        maxcol = col;
        good_or[nc_or++] = e1;

        if (maxface == 4)
        {
            col = DEGENDC4(e4);
            if (col > maxcol)
            {
                nc_or = nc_inv = 0;
                good_inv[nc_inv++] = e4;
                maxcol = col;
            }
            else if (col == maxcol)
                good_inv[nc_inv++] = e4;
        }
    }

    if (degree[v2] == maxdeg)
    {
        col = DEGENDC4(e2);
        if (col > maxcol)
        {
            nc_or = nc_inv = 0;
            good_inv[nc_inv++] = e2;
            maxcol = col;
        }
        else if (col == maxcol)
            good_inv[nc_inv++] = e2;

        if (maxface == 4)
        {
            col = DEGENDC4(e3);
            if (col > maxcol)
            {
                nc_or = nc_inv = 0;
                good_or[nc_or++] = e3;
                maxcol = col;
            }
            else if (col == maxcol)
                good_or[nc_or++] = e3;
        }
    }

    ng_or = nc_or;
    ng_inv = nc_inv;

    if (maxface > 4)
    {
        if (degree[v2] == maxdeg)
            ORTESTC4(e3);
        if (degree[v1] == maxdeg)
            INVTESTC4(e4);
    }

    if (degree[v3] == maxdeg)
    {
        ORTESTC4(e2->invers);
        INVTESTC4(e1->invers);
    }

    nml1 = oldmaxlist1;

    v = e3->end;
    ee = e3->invers;
    for (;;)
    {
        inmaxface[nml1++] = ee;
        if (degree[v] > maxdeg)
        {
            REJECTC4
        }
        else if (degree[v] == maxdeg)
        {
            INVTESTC4(ee);
            ee = ee->prev;
            ORTESTC4(ee);
        }
        else
            ee = ee->prev;

        if (v == v4)
            break;

        v = ee->end;
        ee = ee->invers;
    }

    inmaxface[nml1++] = e2;
    inmaxface[nml1++] = e1->invers;
    inmaxface[nml1++] = e4;

    /* Now test old edges still on max faces */

    for (i = oldmaxlist0; i < oldmaxlist1; ++i)
    {
        ee = inmaxface[i];
        if (degree[ee->start] > maxdeg)
        {
            REJECTC4
        }
        else if (degree[ee->start] == maxdeg)
        {
            INVTESTC4(ee);
            ee = ee->prev;
            ORTESTC4(ee);
        }
    }

    if (!test_for_c4(edel))
    {
        ++degree[v1];
        ++degree[v2];
        return 1;
    }

    /* Now we have complete success!  Delete edel! */

    update_neighbours_c4(edel);

    *newmaxlist1 = nml1;
    *ngood_or = ng_or;
    *ngood_inv = ng_inv;
    *ncan_or = nc_or;
    *ncan_inv = nc_inv;

    for (i = oldmaxlist1; i < nml1; ++i)
        inmaxface[i]->left_facesize = maxface;

    edel->prev->next = edel->next;
    edel->next->prev = edel->prev;
    edel = edel->invers;
    edel->prev->next = edel->next;
    edel->next->prev = edel->prev;
    firstedge[v1] = e1;
    firstedge[v2] = e2;
    ne -= 2;

    if (ng_or + ng_inv == 1)
        return 0;

    maxcol = 0;
    for (i = 0; i < nc_or; ++i)
        if (ORCOLC4(good_or[i]) > maxcol)
            maxcol = ORCOLC4(good_or[i]);
    for (i = 0; i < nc_inv; ++i)
        if (INVCOLC4(good_inv[i]) > maxcol)
            maxcol = INVCOLC4(good_inv[i]);

    for (i = 0, k = 0; i < nc_or; ++i)
        if (ORCOLC4(good_or[i]) == maxcol)
            good_or[k++] = good_or[i];
    *ncan_or = k;
    for (; i < ng_or; ++i)
    {
        col = ORCOLC4(good_or[i]);
        if (col == maxcol)
            good_or[k++] = good_or[i];
        else if (col > maxcol)
        {
            insert_edge_tri(edel->invers);
            *ngood_or = *ngood_inv = 0;
            return 2;
        }
    }
    *ngood_or = k;

    for (i = 0, k = 0; i < nc_inv; ++i)
        if (INVCOLC4(good_inv[i]) == maxcol)
            good_inv[k++] = good_inv[i];
    *ncan_inv = k;
    for (; i < ng_inv; ++i)
    {
        col = INVCOLC4(good_inv[i]);
        if (col == maxcol)
            good_inv[k++] = good_inv[i];
        else if (col > maxcol)
        {
            insert_edge_tri(edel->invers);
            *ngood_or = *ngood_inv = 0;
            return 2;
        }
    }
    *ngood_inv = k;

    return 0;
}

/*************************************************************************/

static void
scanpoly_c4(int nbtot, int nbop, EDGE *oldfeas[], int noldfeas,
            int oldmaxface, int oldmaxlist0, int oldmaxlist1)

/* This is the recursive search procedure for 4-conn polytopes.
   oldfeas[0..noldfeas-1] are the edges which can be removed
   without violating connectivity.  nbtot/nbop represent the
   group, as usual.   oldmaxface is the size of the largest face.
   inmaxface[oldmaxlist0..oldmaxlist1-1] lists the edges whose
   left face has greatest size (unless that is 3).

   This version is for 4-connected only! scanpoly_c3() is for
   3-connected and scanpoly() is the more general version that works
   for connectivity 1 or more.
*/

{
    EDGE *newfeas[MAXE / 2], *good_or[MAXE], *good_inv[MAXE], *e, *esave;
    int i, nnewfeas, minimal[MAXE / 2], newmaxface;
    int code, xnbtot, xnbop;
    int ngood_or, ncan_or, ngood_inv, ncan_inv;
    int newmaxlist0, newmaxlist1;

    if (ne <= edgebound[1])
        got_one(nbtot, nbop, 3);
    if (ne == edgebound[0])
        return;
    if (ne - 2 * noldfeas > edgebound[1])
        return;

#ifdef PRE_FILTER_POLY
    if (!(PRE_FILTER_POLY))
        return;
#endif

    mark_edge_orbits(oldfeas, noldfeas, minimal, nbtot);

    for (i = 0; i < noldfeas; ++i)
    {
        if (!minimal[i])
            continue;

        e = oldfeas[i];
        if (e->left_facesize != 3)
            e = e->invers;
        if (e->invers->left_facesize < oldmaxface - 1 || e->invers->left_facesize == maxfacesize)
            continue;

        code = maybe_delete_c4(e, oldmaxface, oldmaxlist0, oldmaxlist1,
                               &newmaxface, &newmaxlist0, &newmaxlist1,
                               good_or, &ngood_or, &ncan_or,
                               good_inv, &ngood_inv, &ncan_inv);

        if (code == 0)
        {
#ifdef FAST_FILTER_POLY
            if (FAST_FILTER_POLY)
#endif
            {
                if (ngood_or + ngood_inv == 1)
                {
                    esave = oldfeas[i];
                    oldfeas[i] = oldfeas[noldfeas - 1];
                    prune_poly_edgelist(oldfeas, noldfeas - 1, newfeas, &nnewfeas);
                    oldfeas[i] = esave;
                    scanpoly_c4(1, 1, newfeas, nnewfeas,
                                newmaxface, newmaxlist0, newmaxlist1);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ncan_or,
                                             good_inv, ngood_inv, ncan_inv,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    esave = oldfeas[i];
                    oldfeas[i] = oldfeas[noldfeas - 1];
                    prune_poly_edgelist(oldfeas, noldfeas - 1, newfeas, &nnewfeas);
                    oldfeas[i] = esave;
                    scanpoly_c4(xnbtot, xnbop, newfeas, nnewfeas,
                                newmaxface, newmaxlist0, newmaxlist1);
                }
            }
            insert_edge_tri(e);
        }
        else if (code == 1)
        {
            oldfeas[i] = oldfeas[noldfeas - 1];
            minimal[i] = minimal[noldfeas - 1];
            --i;
            --noldfeas;
        }
    }
}

/*************************************************************************/

static int
maybe_delete_c3(EDGE *edel, int oldmaxface, int oldmaxlist0, int oldmaxlist1,
                int *newmaxface, int *newmaxlist0, int *newmaxlist1,
                EDGE *good_or[], int *ngood_or, int *ncan_or,
                EDGE *good_inv[], int *ngood_inv, int *ncan_inv)

/* Assumes there is a 3-face on the left of *edel, and that *edel can
   be deleted while keeping degrees >= 3.  Also, the new face created will
   be a largest face.  oldmaxface is the size of the largest face so far,
   and inmaxface[oldmaxlist0..oldmaxlist1-1] are the edges with a face of
   maximum size on the left.

   This procedure deletes *edel provided the result is 3-connected, and that
   the procedure believes the re-insertion of *edel might be a canonical
   edge insertion.  The latter decision is based on four combinatorial
   invariates: the three vertex degrees at the ends of *edel and on its left,
   and the size of the face to the left of edel->prev.

   In case *edel passes the test and is deleted, the edges which may 
   represent the re-insertion of *edel and optimise the four-part invariant
   mentioned above are put in good_or[0..*ncan_or-1] and
   good_inv[0..*ncan_inv-1].  This will include at least one of the edges
   edel->prev, edel->invers->next and (if there is also a 3-face on the
   right of *edel) edel->next and edel->invers->prev.  Then all other edges
   which might possibly represent canonical edge insertions are put in 
   good_or[*ncan_or..*ngood_or-1] or good_inv[*ncan_inv..*ngood_inv-1].
   The *_or edges are those for which the inserted edge will be in the
   next direction, and the *_inv edges .. the prev direction.

   In addition, if *edel is deleted, inmaxface[*newmaxlist0..*newmaxlist1-1]
   will have all edges with a maximum face on the left (that size being put
   into *newmaxface).  This list may overlap
   inmaxface[oldmaxlist0..oldmaxlist1-1] if the max face size does not
   increase.

   Return values:   0 = ok
                    1 = rejected by threeconn()
		    2 = rejected by colour

   This version is for 3-connected only!  maybe_delete() is the more
   general version that works for connectivity 1 or more.
*/

{
#define DEGENDC3(ed) (degree[ed->end])
#define REJECTC3      \
    {                 \
        ++degree[v1]; \
        ++degree[v2]; \
        return 2;     \
    }
#define ORTESTC3(e)                                                \
    {                                                              \
        col = DEGENDC3(e);                                         \
        if (col > maxcol)                                          \
            REJECTC3 else if (col == maxcol) good_or[ng_or++] = e; \
    }
#define INVTESTC3(e)                                                 \
    {                                                                \
        col = DEGENDC3(e);                                           \
        if (col > maxcol)                                            \
            REJECTC3 else if (col == maxcol) good_inv[ng_inv++] = e; \
    }
#define ORCOLC3(ed) ((degree[ed->invers->prev->end] << 10) + ed->left_facesize)
#define INVCOLC3(ed) \
    ((degree[ed->invers->next->end] << 10) + ed->invers->left_facesize)

    EDGE *e1, *e2, *e3, *e4, *ee;
    long col, maxcol;
    int k, i, v, ng_or, ng_inv, nc_or, nc_inv;
    int maxface, v1, v2, v3, v4, maxdeg, nml1;

    maxface = *newmaxface = edel->invers->left_facesize + 1;
    if (maxface > oldmaxface)
        oldmaxlist0 = oldmaxlist1;
    *newmaxlist0 = oldmaxlist0;

    *ngood_or = *ngood_inv = 0;

    /* Now old edges that will be on a largest face (if *edel is deleted)
    are in places oldmaxlist0..oldmaxlist1-1.  New edges will be from
    oldmaxlist1 to *newmaxlist1-1, but *newmaxlist1 is not set yet. */

    v1 = edel->start;
    v2 = edel->end;
    maxdeg = (degree[v1] > degree[v2] ? degree[v1] : degree[v2]) - 1;

    e1 = edel->prev;
    v3 = e1->end;
    e4 = edel->next;
    v4 = e4->end;

    if (degree[v3] > maxdeg || degree[v4] > maxdeg)
        return 2;

    --degree[v1];
    --degree[v2];
    e2 = edel->invers->next;
    e3 = edel->invers->prev;

    maxcol = nc_or = nc_inv = 0;

    if (degree[v1] == maxdeg)
    {
        col = DEGENDC3(e1);
        maxcol = col;
        good_or[nc_or++] = e1;

        if (maxface == 4)
        {
            col = DEGENDC3(e4);
            if (col > maxcol)
            {
                nc_or = nc_inv = 0;
                good_inv[nc_inv++] = e4;
                maxcol = col;
            }
            else if (col == maxcol)
                good_inv[nc_inv++] = e4;
        }
    }

    if (degree[v2] == maxdeg)
    {
        col = DEGENDC3(e2);
        if (col > maxcol)
        {
            nc_or = nc_inv = 0;
            good_inv[nc_inv++] = e2;
            maxcol = col;
        }
        else if (col == maxcol)
            good_inv[nc_inv++] = e2;

        if (maxface == 4)
        {
            col = DEGENDC3(e3);
            if (col > maxcol)
            {
                nc_or = nc_inv = 0;
                good_or[nc_or++] = e3;
                maxcol = col;
            }
            else if (col == maxcol)
                good_or[nc_or++] = e3;
        }
    }

    ng_or = nc_or;
    ng_inv = nc_inv;

    if (maxface > 4)
    {
        if (degree[v2] == maxdeg)
            ORTESTC3(e3);
        if (degree[v1] == maxdeg)
            INVTESTC3(e4);
    }

    if (degree[v3] == maxdeg)
    {
        ORTESTC3(e2->invers);
        INVTESTC3(e1->invers);
    }

    nml1 = oldmaxlist1;

    v = e3->end;
    ee = e3->invers;
    for (;;)
    {
        inmaxface[nml1++] = ee;
        if (degree[v] > maxdeg)
        {
            REJECTC3
        }
        else if (degree[v] == maxdeg)
        {
            INVTESTC3(ee);
            ee = ee->prev;
            ORTESTC3(ee);
        }
        else
            ee = ee->prev;

        if (v == v4)
            break;

        v = ee->end;
        ee = ee->invers;
    }

    inmaxface[nml1++] = e2;
    inmaxface[nml1++] = e1->invers;
    inmaxface[nml1++] = e4;

    /* Now test old edges still on max faces */

    for (i = oldmaxlist0; i < oldmaxlist1; ++i)
    {
        ee = inmaxface[i];
        if (degree[ee->start] > maxdeg)
        {
            REJECTC3
        }
        else if (degree[ee->start] == maxdeg)
        {
            INVTESTC3(ee);
            ee = ee->prev;
            ORTESTC3(ee);
        }
    }

    if (!threeconn(edel))
    {
        ++degree[v1];
        ++degree[v2];
        return 1;
    }

    /* Now we have complete success!  Delete edel! */

    *newmaxlist1 = nml1;
    *ngood_or = ng_or;
    *ngood_inv = ng_inv;
    *ncan_or = nc_or;
    *ncan_inv = nc_inv;

    for (i = oldmaxlist1; i < nml1; ++i)
        inmaxface[i]->left_facesize = maxface;

    edel->prev->next = edel->next;
    edel->next->prev = edel->prev;
    edel = edel->invers;
    edel->prev->next = edel->next;
    edel->next->prev = edel->prev;
    firstedge[v1] = e1;
    firstedge[v2] = e2;
    ne -= 2;

    if (ng_or + ng_inv == 1)
        return 0;

    maxcol = 0;
    for (i = 0; i < nc_or; ++i)
        if (ORCOLC3(good_or[i]) > maxcol)
            maxcol = ORCOLC3(good_or[i]);
    for (i = 0; i < nc_inv; ++i)
        if (INVCOLC3(good_inv[i]) > maxcol)
            maxcol = INVCOLC3(good_inv[i]);

    for (i = 0, k = 0; i < nc_or; ++i)
        if (ORCOLC3(good_or[i]) == maxcol)
            good_or[k++] = good_or[i];
    *ncan_or = k;
    for (; i < ng_or; ++i)
    {
        col = ORCOLC3(good_or[i]);
        if (col == maxcol)
            good_or[k++] = good_or[i];
        else if (col > maxcol)
        {
            insert_edge_tri(edel->invers);
            *ngood_or = *ngood_inv = 0;
            return 2;
        }
    }
    *ngood_or = k;

    for (i = 0, k = 0; i < nc_inv; ++i)
        if (INVCOLC3(good_inv[i]) == maxcol)
            good_inv[k++] = good_inv[i];
    *ncan_inv = k;
    for (; i < ng_inv; ++i)
    {
        col = INVCOLC3(good_inv[i]);
        if (col == maxcol)
            good_inv[k++] = good_inv[i];
        else if (col > maxcol)
        {
            insert_edge_tri(edel->invers);
            *ngood_or = *ngood_inv = 0;
            return 2;
        }
    }
    *ngood_inv = k;

    return 0;
}

/*************************************************************************/

static void
scanpoly_c3(int nbtot, int nbop, EDGE *oldfeas[], int noldfeas,
            int oldmaxface, int oldmaxlist0, int oldmaxlist1)

/* This is the recursive search procedure for polytopes.
   oldfeas[0..noldfeas-1] are the edges which can be removed
   without violating connectivity.  nbtot/nbop represent the
   group, as usual.   oldmaxface is the size of the largest face.
   inmaxface[oldmaxlist0..oldmaxlist1-1] lists the edges whose
   left face has greatest size (unless that is 3).

   This version is for 3-connected only!  scanpoly() is the more
   general version that works for connectivity 1 or more.
*/

{
    EDGE *newfeas[MAXE / 2], *good_or[MAXE], *good_inv[MAXE], *e, *esave;
    int i, nnewfeas, minimal[MAXE / 2], newmaxface;
    int code, xnbtot, xnbop;
    int ngood_or, ncan_or, ngood_inv, ncan_inv;
    int newmaxlist0, newmaxlist1;

    if (ne <= edgebound[1])
        got_one(nbtot, nbop, 3);
    if (ne == edgebound[0])
        return;
    if (ne - 2 * noldfeas > edgebound[1])
        return;

#ifdef PRE_FILTER_POLY
    if (!(PRE_FILTER_POLY))
        return;
#endif

    mark_edge_orbits(oldfeas, noldfeas, minimal, nbtot);

    for (i = 0; i < noldfeas; ++i)
    {
        if (!minimal[i])
            continue;

        e = oldfeas[i];
        if (e->left_facesize != 3)
            e = e->invers;
        if (e->invers->left_facesize < oldmaxface - 1 || e->invers->left_facesize == maxfacesize)
            continue;

        code = maybe_delete_c3(e, oldmaxface, oldmaxlist0, oldmaxlist1,
                               &newmaxface, &newmaxlist0, &newmaxlist1,
                               good_or, &ngood_or, &ncan_or,
                               good_inv, &ngood_inv, &ncan_inv);

        if (code == 0)
        {
#ifdef FAST_FILTER_POLY
            if (FAST_FILTER_POLY)
#endif
            {
                if (ngood_or + ngood_inv == 1)
                {
                    esave = oldfeas[i];
                    oldfeas[i] = oldfeas[noldfeas - 1];
                    prune_poly_edgelist(oldfeas, noldfeas - 1, newfeas, &nnewfeas);
                    oldfeas[i] = esave;
                    scanpoly_c3(1, 1, newfeas, nnewfeas,
                                newmaxface, newmaxlist0, newmaxlist1);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ncan_or,
                                             good_inv, ngood_inv, ncan_inv,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    esave = oldfeas[i];
                    oldfeas[i] = oldfeas[noldfeas - 1];
                    prune_poly_edgelist(oldfeas, noldfeas - 1, newfeas, &nnewfeas);
                    oldfeas[i] = esave;
                    scanpoly_c3(xnbtot, xnbop, newfeas, nnewfeas,
                                newmaxface, newmaxlist0, newmaxlist1);
                }
            }
            insert_edge_tri(e);
        }
        else if (code == 1)
        {
            oldfeas[i] = oldfeas[noldfeas - 1];
            minimal[i] = minimal[noldfeas - 1];
            --i;
            --noldfeas;
        }
    }
}

/*************************************************************************/

static int
maybe_delete(EDGE *edel, int oldmaxface, int oldmaxlist0, int oldmaxlist1,
             int *newmaxface, int *newmaxlist0, int *newmaxlist1,
             EDGE *good_or[], int *ngood_or, int *ncan_or,
             EDGE *good_inv[], int *ngood_inv, int *ncan_inv, int *connec)

/* Assumes there is a 3-face on the left of *edel, and that *edel can be
   deleted while keeping degrees >= minpolydeg.  Also, the new face created
   will be a largest face.  oldmaxface is the size of the largest face so far,
   and inmaxface[oldmaxlist0..oldmaxlist1-1] are the edges with a face of
   maximum size on the left.  *connec is the current connectivity (or 3,
   whichever is smaller).

   This procedure deletes *edel provided the result is at least as connected
   as minpolyconnec, and that the procedure believes the re-insertion of *edel
   might be a canonical edge insertion.  The latter decision is based on
   four combinatorial invariates: the three vertex degrees at the ends of
   *edel and on its left, and the size of the face to the left of edel->prev.

   In case *edel passes the test and is deleted, the edges which may 
   represent the re-insertion of *edel and optimise the four-part invariant
   mentioned above are put in good_or[0..*ncan_or-1] and
   good_inv[0..*ncan_inv-1].  This will include at least one of the edges
   edel->prev, edel->invers->next and (if there is also a 3-face on the
   right of *edel) edel->next and edel->invers->prev.  Then all other edges
   which might possibly represent canonical edge insertions are put in 
   good_or[*ncan_or..*ngood_or-1] or good_inv[*ncan_inv..*ngood_inv-1].
   The *_or edges are those for which the inserted edge will be in the
   next direction, and the *_inv edges .. the prev direction.

   In addition, if *edel is deleted, inmaxface[*newmaxlist0..*newmaxlist1-1]
   will have all edges with a maximum face on the left (that size being put
   into *newmaxface).  This list may overlap
   inmaxface[oldmaxlist0..oldmaxlist1-1] if the max face size does not
   increase.

   In the case of value 0, *connec is changed to represent the new
   connectivity (or 3, whichever is smaller).

   Return values:   0 = ok
                    1 = rejected as connectivity will be too small
		    2 = rejected by colour
*/

{
#define DEGEND(e) (degree[e->end])
#define OROK(e) ISNEQADJ(e->start, e->invers->prev->end)
#define INVOK(e) ISNEQADJ(e->start, e->invers->next->end)
#define REJECT(x)     \
    {                 \
        ++degree[v1]; \
        ++degree[v2]; \
        return x;     \
    }
#define ORTEST(e)                          \
    {                                      \
        col = DEGEND(e);                   \
        if (col > maxcol)                  \
        {                                  \
            if (OROK(e))                   \
                REJECT(2)                  \
        }                                  \
        else if (col == maxcol && OROK(e)) \
            good_or[ng_or++] = e;          \
    }
#define INVTEST(e)                          \
    {                                       \
        col = DEGEND(e);                    \
        if (col > maxcol)                   \
        {                                   \
            if (INVOK(e))                   \
                REJECT(2)                   \
        }                                   \
        else if (col == maxcol && INVOK(e)) \
            good_inv[ng_inv++] = e;         \
    }
#define ORCOL(e) (((long)degree[e->invers->prev->end] << 10) + e->left_facesize)
#define INVCOL(e) \
    (((long)degree[e->invers->next->end] << 10) + e->invers->left_facesize)

    EDGE *e1, *e2, *e3, *e4, *ee, *ea, *eb;
    long col, maxcol, col1, col2;
    int k, i, ng_or, ng_inv, nc_or, nc_inv;
    int maxface, v1, v2, v3, v4, v5;
    int da, db, mindeg, maxdeg, nml1;
    int newconnec;

    maxface = *newmaxface = edel->invers->left_facesize + 1;
    if (maxface > oldmaxface)
        oldmaxlist0 = oldmaxlist1;
    *newmaxlist0 = oldmaxlist0;

    *ngood_or = *ngood_inv = 0;

    /* Now old edges that will be on a largest face (if *edel is deleted)
    are in places oldmaxlist0..oldmaxlist1-1.  New edges will be from
    oldmaxlist1 to *newmaxlist1-1, but *newmaxlist1 is not set yet. */

    v1 = edel->start;
    v2 = edel->end;
    /* maxdeg = (degree[v1] > degree[v2] ? degree[v1] : degree[v2]) - 1;  BDM 2/5/09 */

    /* mindeg and maxdeg are the degrees of the ends of edel after deletion */
    if (degree[v1] < degree[v2])
    {
        mindeg = degree[v1] - 1;
        maxdeg = degree[v2] - 1;
    }
    else
    {
        mindeg = degree[v2] - 1;
        maxdeg = degree[v1] - 1;
    }

    e1 = edel->prev;
    v3 = e1->end;
    e4 = edel->next;
    v4 = e4->end;
    e3 = edel->invers->prev;

    /* The following is an efficiency short-cut, but it is assumed
      to have been done below. */

    if (maxface == 4)
    {
        if (ISNEQADJ(v3, v4) && (degree[v3] > maxdeg || degree[v4] > maxdeg))
            return 2;
    }
    else if (degree[v3] > maxdeg)
    {
        if (ISNEQADJ(v3, e3->end) || ISNEQADJ(v3, v4))
            return 2;
    }

    e2 = edel->invers->next;
    --degree[v1];
    --degree[v2];

    maxcol = nc_or = nc_inv = 0;

    if (degree[v1] == maxdeg)
    {
        col = DEGEND(e1);
        maxcol = col;
        good_or[nc_or++] = e1;

        if (maxface == 4)
        {
            col = DEGEND(e4);
            if (col > maxcol)
            {
                nc_or = nc_inv = 0;
                good_inv[nc_inv++] = e4;
                maxcol = col;
            }
            else if (col == maxcol)
                good_inv[nc_inv++] = e4;
        }
    }

    if (degree[v2] == maxdeg)
    {
        col = DEGEND(e2);
        if (col > maxcol)
        {
            nc_or = nc_inv = 0;
            good_inv[nc_inv++] = e2;
            maxcol = col;
        }
        else if (col == maxcol)
            good_inv[nc_inv++] = e2;

        if (maxface == 4)
        {
            col = DEGEND(e3);
            if (col > maxcol)
            {
                nc_or = nc_inv = 0;
                good_or[nc_or++] = e3;
                maxcol = col;
            }
            else if (col == maxcol)
                good_or[nc_or++] = e3;
        }
    }

    ng_or = nc_or;
    ng_inv = nc_inv;

    if (maxface == 4)
    {
        /* Recall from above that degree[v3,v4] <= maxdeg */

        if (ISNEQADJ(v3, v4))
        {
            col1 = degree[v1];
            col2 = degree[v2];

            if (degree[v3] == maxdeg)
            {
                if (col1 > maxcol)
                    REJECT(2)
                else if (col1 == maxcol)
                    good_inv[ng_inv++] = e1->invers;
                if (col2 > maxcol)
                    REJECT(2)
                else if (col2 == maxcol)
                    good_or[ng_or++] = e2->invers;
            }

            if (degree[v4] == maxdeg)
            {
                if (col1 > maxcol)
                    REJECT(2)
                else if (col1 == maxcol)
                    good_or[ng_or++] = e4->invers;
                if (col2 > maxcol)
                    REJECT(2)
                else if (col2 == maxcol)
                    good_inv[ng_inv++] = e3->invers;
            }
        }

        nml1 = oldmaxlist1;
        inmaxface[nml1++] = e1->invers;
        inmaxface[nml1++] = e2;
        inmaxface[nml1++] = e3->invers;
        inmaxface[nml1++] = e4;
    }
    else
    {
        v5 = e3->end;

        /* Recall from above that degree[v3] <= maxdeg */

        if (ISNEQADJ(v3, v5))
        {
            if (degree[v5] > maxdeg)
                REJECT(2);
            col = degree[v2];
            if (degree[v3] == maxdeg)
            {
                if (col > maxcol)
                    REJECT(2)
                else if (col == maxcol)
                    good_or[ng_or++] = e2->invers;
            }
            if (degree[v5] == maxdeg)
            {
                if (col > maxcol)
                    REJECT(2)
                else if (col == maxcol)
                    good_inv[ng_inv++] = e3->invers;
            }
        }
        if (ISNEQADJ(v3, v4))
        {
            if (degree[v4] > maxdeg)
                REJECT(2);
            col = degree[v1];
            if (degree[v3] == maxdeg)
            {
                if (col > maxcol)
                    REJECT(2)
                else if (col == maxcol)
                    good_inv[ng_inv++] = e1->invers;
            }
            if (degree[v4] == maxdeg)
            {
                if (col > maxcol)
                    REJECT(2)
                else if (col == maxcol)
                    good_or[ng_or++] = e4->invers;
            }
        }

        nml1 = oldmaxlist1;

        ea = e3->invers;
        eb = ea->prev;
        do
        {
            if (ISNEQADJ(ea->end, eb->end))
            {
                da = DEGEND(ea);
                db = DEGEND(eb);
                if (da > maxdeg || db > maxdeg)
                    REJECT(2);
                col = degree[ea->start];
                if (da == maxdeg)
                {
                    if (col > maxcol)
                        REJECT(2)
                    else if (col == maxcol)
                        good_or[ng_or++] = ea->invers;
                }
                if (db == maxdeg)
                {
                    if (col > maxcol)
                        REJECT(2)
                    else if (col == maxcol)
                        good_inv[ng_inv++] = eb->invers;
                }
            }
            inmaxface[nml1++] = ea;
            ea = eb->invers;
            eb = ea->prev;
        } while (ea != e4);

        inmaxface[nml1++] = e2;
        inmaxface[nml1++] = e1->invers;
        inmaxface[nml1++] = e4;
    }

    /* Now test old edges still on max faces */

    for (i = oldmaxlist0; i < oldmaxlist1; ++i)
    {
        ee = inmaxface[i];
        if (degree[ee->start] > maxdeg)
        {
            if (INVOK(ee))
                REJECT(2);
            ee = ee->prev;
            if (OROK(ee))
                REJECT(2);
        }
        else if (degree[ee->start] == maxdeg)
        {
            INVTEST(ee);
            ee = ee->prev;
            ORTEST(ee);
        }
    }

    if (mindeg < *connec)
        newconnec = mindeg;
    else if (*connec == 3)
        newconnec = 2 + threeconn(edel);
    else if (*connec == 2)
        newconnec = 1 + twoconn(edel);
    else
        newconnec = 1;

    if (newconnec < minpolyconnec)
        REJECT(1);

    /* Now we have complete success!  Just prune the lists a bit and
    complete the deletion of edel. */

    edel->prev->next = edel->next;
    edel->next->prev = edel->prev;
    ee = edel->invers;
    ee->prev->next = ee->next;
    ee->next->prev = ee->prev;

    for (i = oldmaxlist1; i < nml1; ++i)
        inmaxface[i]->left_facesize = maxface;

    firstedge[v1] = e1;
    firstedge[v2] = e2;
    ne -= 2;

    *connec = newconnec;

    *newmaxlist1 = nml1;
    *ngood_or = ng_or;
    *ngood_inv = ng_inv;
    *ncan_or = nc_or;
    *ncan_inv = nc_inv;

    if (ng_or + ng_inv == 1)
        return 0;

    maxcol = 0;
    for (i = 0; i < nc_or; ++i)
        if (ORCOL(good_or[i]) > maxcol)
            maxcol = ORCOL(good_or[i]);
    for (i = 0; i < nc_inv; ++i)
        if (INVCOL(good_inv[i]) > maxcol)
            maxcol = INVCOL(good_inv[i]);

    for (i = 0, k = 0; i < nc_or; ++i)
        if (ORCOL(good_or[i]) == maxcol)
            good_or[k++] = good_or[i];
    *ncan_or = k;
    for (; i < ng_or; ++i)
    {
        col = ORCOL(good_or[i]);
        if (col == maxcol)
            good_or[k++] = good_or[i];
        else if (col > maxcol)
        {
            insert_edge_tri(edel);
            *ngood_or = *ngood_inv = 0;
            return 2;
        }
    }
    *ngood_or = ng_or = k;

    for (i = 0, k = 0; i < nc_inv; ++i)
        if (INVCOL(good_inv[i]) == maxcol)
            good_inv[k++] = good_inv[i];
    *ncan_inv = k;
    for (; i < ng_inv; ++i)
    {
        col = INVCOL(good_inv[i]);
        if (col == maxcol)
            good_inv[k++] = good_inv[i];
        else if (col > maxcol)
        {
            insert_edge_tri(edel);
            *ngood_or = *ngood_inv = 0;
            return 2;
        }
    }
    *ngood_inv = ng_inv = k;

    return 0;
}

/*************************************************************************/

static void
scanpoly(int nbtot, int nbop, EDGE *oldfeas[], int noldfeas,
         int oldmaxface, int oldmaxlist0, int oldmaxlist1, int connec)

/* This is the recursive search procedure for polytopes.
   oldfeas[0..noldfeas-1] are the edges which can be removed without
   violating the degree bound minpolydeg, with some (but not necessarily
   all) missing because they are known to violate the connectivity
   bound minpolyconnec.  nbtot/nbop represent the group, as usual.
   oldmaxface is the size of the largest face.
   inmaxface[oldmaxlist0..oldmaxlist1-1] lists the edges whose
   left face has greatest size (unless that is 3).  connec is
   the actual connectivity, except that values greater than 3
   are given as 3. */
{
    EDGE *newfeas[MAXE / 2], *good_or[MAXE], *good_inv[MAXE], *e, *esave;
    int i, nnewfeas, minimal[MAXE / 2], newmaxface;
    int code, xnbtot, xnbop;
    int ngood_or, ncan_or, ngood_inv, ncan_inv;
    int newmaxlist0, newmaxlist1, newconnec;

    if (ne <= edgebound[1])
        got_one(nbtot, nbop, connec);
    if (ne == edgebound[0])
        return;
    if (ne - 2 * noldfeas > edgebound[1])
        return;

#ifdef PRE_FILTER_POLY
    if (!(PRE_FILTER_POLY))
        return;
#endif

    mark_edge_orbits(oldfeas, noldfeas, minimal, nbtot);

    for (i = 0; i < noldfeas; ++i)
    {
        if (!minimal[i])
            continue;

        e = oldfeas[i];
        if (e->left_facesize != 3)
            e = e->invers;
        if (e->invers->left_facesize < oldmaxface - 1 || e->invers->left_facesize == maxfacesize)
            continue;

        AMDELEDGE(e->start, e->end);

        newconnec = connec;
        code = maybe_delete(e, oldmaxface, oldmaxlist0, oldmaxlist1,
                            &newmaxface, &newmaxlist0, &newmaxlist1,
                            good_or, &ngood_or, &ncan_or,
                            good_inv, &ngood_inv, &ncan_inv, &newconnec);

        if (code == 0)
        {
#ifdef FAST_FILTER_POLY
            if (FAST_FILTER_POLY)
#endif
            {
                if (ngood_or + ngood_inv == 1)
                {
                    esave = oldfeas[i];
                    oldfeas[i] = oldfeas[noldfeas - 1];
                    prune_poly_edgelist(oldfeas, noldfeas - 1, newfeas, &nnewfeas);
                    oldfeas[i] = esave;
                    scanpoly(1, 1, newfeas, nnewfeas,
                             newmaxface, newmaxlist0, newmaxlist1, newconnec);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ncan_or,
                                             good_inv, ngood_inv, ncan_inv,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    /* The following line corrects for the fact that canon*()
                    finds each automorphism twice if the maximum degree is
                    at most 2.  However, it interferes with -o so is disabled.
    
	            if (ne <= 2*nv && maxdegree() <= 2) xnbtot = xnbop;
                 */
                    esave = oldfeas[i];
                    oldfeas[i] = oldfeas[noldfeas - 1];
                    prune_poly_edgelist(oldfeas, noldfeas - 1, newfeas, &nnewfeas);
                    oldfeas[i] = esave;
                    scanpoly(xnbtot, xnbop, newfeas, nnewfeas,
                             newmaxface, newmaxlist0, newmaxlist1, newconnec);
                }
            }
            insert_edge_tri(e);
        }
        else if (code == 1)
        {
            oldfeas[i] = oldfeas[noldfeas - 1];
            minimal[i] = minimal[noldfeas - 1];
            --i;
            --noldfeas;
        }
        AMADDEDGE(e->start, e->end);
    }
}

/**************************************************************************/

static void
startpolyscan(int nbtot, int nbop)

/* This routine begins the scan for general connected planar graphs formed
   by removing edges from triangulations.  The current graph is such a
   triangulation, and the group is known (parameters nbtot,nbop).
*/

{
    EDGE *feasible[MAXE / 2];
    EDGE *e, *ex;
    EDGE **nb0, **nb1;
    int i, j, nfeas;

    /* In the -m5 case, the group must be saved and restored. */

    if (minimumdeg == 5 && nbtot > 1)
    {
        nb0 = (EDGE **)numbering[0];
        nb1 = (EDGE **)saved_numbering[0];
        for (i = 0; i < nbtot; ++i, nb0 += MAXE, nb1 += MAXE)
            for (j = 0; j < ne; ++j)
                nb1[j] = nb0[j];
    }

    if (minpolyconnec < 3)
    {
        for (i = 0; i < nv; ++i)
        {
            for (j = 0; j < nv; ++j)
                am2[i][j] = 0;
            am2[i][i] = 1;
        }
    }

    nfeas = 0;
    for (i = 0; i < nv; ++i)
    {
        e = ex = firstedge[i];
        do
        {
            if (e == e->min && degree[e->start] > minpolydeg && degree[e->end] > minpolydeg)
                feasible[nfeas++] = e;
            e->left_facesize = 3;
            am2[e->start][e->end] = 1;
            e = e->next;
        } while (e != ex);
    }

    prune_poly_edgelist(feasible, nfeas, feasible, &nfeas);

    if (minpolyconnec == 3)
        scanpoly_c3(nbtot, nbop, feasible, nfeas, 3, 0, 0);
    else if (minpolyconnec == 4)
    {
        init_nb4_triangulation();
        scanpoly_c4(nbtot, nbop, feasible, nfeas, 3, 0, 0);
    }
    else
        scanpoly(nbtot, nbop, feasible, nfeas, 3, 0, 0, 3);

    if (minimumdeg == 5 && nbtot > 1)
    {
        nb0 = (EDGE **)saved_numbering[0];
        nb1 = (EDGE **)numbering[0];
        for (i = 0; i < nbtot; ++i, nb0 += MAXE, nb1 += MAXE)
            for (j = 0; j < ne; ++j)
                nb1[j] = nb0[j];
    }
}

/********************************************************************/

static int
disk_threeconn(EDGE *e)

/* Checks whether a triangulation of a disk is 3-connected. This is
   the case if and only if there are no chords (except for K3).
   The edge e must have the triangulation on the right and the outer
   face on the left. 
   Returns TRUE if 3-connected, FALSE otherwise. */
{
    EDGE *run, *run2, *buffer;

    if (nv == 3)
        return FALSE; /* K3 has connectivity 2 */

    RESETMARKS_V;

    /* It is correct to do the marking and the running and checking in one
   wash, since a chord will be detected when the second of the endpoints 
   is reached */

    MARK_V(e->start);
    MARK_V(e->end);

    for (buffer = e->invers, run = buffer->next; run != e;
         buffer = run->invers, run = buffer->next)
    {
        MARK_V(run->end);
        for (run2 = run->next; run2 != buffer; run2 = run2->next)
            if (ISMARKED_V(run2->end))
                return FALSE;
    }

    return TRUE;
}

/******************************************************************/

static EDGE *
remove_vertex(int i)

/* removes vertex i from the graph and returns an edge with the
   new face on the left. Note that afterwards the vertices are
   in general no more numbered 0...nv-1, but maybe e.g. 0...nv
   with some number in the middle missing. 

*/
{
    EDGE *run, *end, *buffer;

    nv--;
    ne -= 2 * degree[i];

    run = end = firstedge[i];

    do
    {
        buffer = run->invers;
        buffer->prev->next = buffer->next;
        buffer->next->prev = buffer->prev;
        (degree[buffer->start])--;
        firstedge[buffer->start] = buffer->next;
        run = run->next;
    } while (run != end);

    missing_vertex = i;
    outside_face_size = degree[i];
    return buffer->next;
}

/******************************************************************/

static void
insert_vertex(int i)

/* inserts the previously removed vertex */
{

    EDGE *run, *end, *buffer;

    nv++;
    ne += 2 * degree[i];

    run = end = firstedge[i];

    do
    {
        buffer = run->invers;
        buffer->prev->next = buffer;
        buffer->next->prev = buffer;
        (degree[buffer->start])++;
        run = run->next;
    } while (run != end);

    missing_vertex = -1;
}

/**************************************************************************/

static void
polygon_triang(int nbtot, int nbop)

/* This routine receives a 3-conn triangulation with one more vertex
   than the output size.  It then makes the polygon triangulations by
   removing inequivalent vertices of the required degree. */
{
    int i, j, j0, j1, k, v, connec;
    register EDGE **e, **nb0, **nb1, **nbnew, **nblim;
    int newnbtot, newnbop;
    int vmark[MAXN];
    EDGE *ev;

    for (v = 0; v < nv; ++v)
        if (polygonsize <= 0 || degree[v] == polygonsize)
            vmark[v] = 1;
        else
            vmark[v] = 0;

    if (minimumdeg == 3 || minconnec == 3)
    {
        for (v = 0; v < nv; ++v)
            if (degree[v] == 3)
            {
                ev = firstedge[v];
                vmark[ev->end] = vmark[ev->next->end] = vmark[ev->prev->end] = 0;
            }
    }

    if (nbtot == 1) /* Case of trivial group */
    {
        for (v = 0; v < nv; ++v)
            if (vmark[v])
            {
#ifdef PRE_FILTER_DISK
                if (!PRE_FILTER_DISK(v))
                    continue;
#endif

                code_edge = remove_vertex(v);

                connec = 2;
                if (degree[v] == 3)
                    connec = 3;
                else if (minconnec == 3 || xswitch)
                    connec += disk_threeconn(code_edge);
                if (connec >= minconnec)
                    got_one(1, 1, connec);
                insert_vertex(v);
                code_edge = NULL;
            }
    }
    else /* Case of non-trivial group */
    {
        nb0 = (EDGE **)numbering[0];
        nb1 = (EDGE **)saved_numbering[0];
        for (i = 0; i < nbtot; ++i, nb0 += MAXE, nb1 += MAXE)
            for (j = 0; j < ne; ++j)
                nb1[j] = nb0[j];

        nbnew = (EDGE **)saved_numbering[0];
        nblim = (EDGE **)saved_numbering[nbtot];
        for (k = 0; k < ne; ++k)
        {
            v = nbnew[k]->start;
            if (!vmark[v])
                continue;

            newnbtot = newnbop = 0;
            for (i = 0, e = nbnew + k; e < nblim; ++i, e += MAXE)
            {
                vmark[(*e)->start] = 0;
                if ((*e)->start == v)
                {
                    nb1 = (EDGE **)saved_numbering[i];
                    nb0 = (EDGE **)numbering[newnbtot];
                    for (j0 = j1 = 0; j1 < ne; ++j1)
                        if (nb1[j1]->start != v && nb1[j1]->end != v)
                            nb0[j0++] = nb1[j1];
                    if (i < nbop)
                        ++newnbop;
                    ++newnbtot;
                }
            }

#ifdef PRE_FILTER_DISK
            if (!PRE_FILTER_DISK(v))
                continue;
#endif

            code_edge = remove_vertex(v);

            connec = 2;
            if (degree[v] == 3 && nv > 3)
                connec = 3;
            else if (minconnec == 3 || xswitch)
                connec += disk_threeconn(code_edge);

            if (connec >= minconnec)
                got_one(newnbtot, newnbop, connec);
            insert_vertex(v);
            code_edge = NULL;
        }
    }
}

/**************************************************************************/

static void
scansimple(int nbtot, int nbop)

/* The main node of the recursion for triangulations without double 
   edges or loops.  As this procedure is entered,
   nv,ne,degree etc are set for some graph, and nbtot/nbop are the
   values returned by canon() for that graph. */
{
    EDGE *ext3[MAXE / 3], *ext4[MAXE / 2], *ext5[MAXE];
    int next3, next4, next5;
    EDGE *save_list[4];
    register int i;
    register EDGE *e1, *e2, **nb, **nblim;
    EDGE *e, *ex;
    int nc, xnbtot, xnbop, v, needed_deg;
    int colour[MAXN];
    EDGE *firstedge_save[MAXE];

    if (nv == maxnv)
    {
        if (pswitch)
            startpolyscan(nbtot, nbop);
        else if (polygonsize >= 0)
            polygon_triang(nbtot, nbop);
        else if (minconnec == 3)
            got_one(nbtot, nbop, 3);
        else
            scandouble(nbtot, nbop, 0, NULL, NULL, 0, NULL);
        return;
    }

    if (nv == splitlevel)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

    /* The following could be improved significantly by avoiding
      extensions that can't lead to success here. */
    if (polygonsize >= 9)
    {
        needed_deg = polygonsize + nv - maxnv;
        for (i = 0; i < nv; ++i)
            if (degree[i] >= needed_deg)
                break;
        if (i == nv)
            return;
    }

#ifdef PRE_FILTER_SIMPLE
    if (!(PRE_FILTER_SIMPLE))
        return;
#endif

#ifndef FIND_EXTENSIONS_SIMPLE
#define FIND_EXTENSIONS_SIMPLE find_extensions
#endif

    FIND_EXTENSIONS_SIMPLE(nbtot, nbop, ext3, &next3, ext4, &next4, ext5, &next5);

    for (i = 0; i < next3; ++i)
    {
        nc = make_colours(colour, ext3[i]);
        if (nc)
        {
            extend3(ext3[i]);
#ifdef FAST_FILTER_SIMPLE
            if (FAST_FILTER_SIMPLE)
#endif
            {
                if (nc == 1 && nv == maxnv && !needgroup)
                    got_one(1, 1, 3);
                else if (canon(colour, numbering, &xnbtot, &xnbop))
                    scansimple(xnbtot, xnbop);
            }
            reduce3(ext3[i]);
        }
    }

    for (i = 0; i < next4; ++i)
    {
        extend4(ext4[i], save_list);
#ifdef FAST_FILTER_SIMPLE
        if (FAST_FILTER_SIMPLE)
#endif
        {
            if (canon(degree, numbering, &xnbtot, &xnbop))
            {
                e = numbering[0][0];
                v = e->next->next->end;
                ex = e->invers;
                for (e = ex->next; e != ex; e = e->next)
                    if (e->end == v)
                        break;

                e1 = ext4[i]->next->invers;
                if (e != ex)
                    e1 = e1->next;

                e2 = e1->next->next;
                nblim = (EDGE **)numbering[xnbtot];
                for (nb = (EDGE **)numbering[0]; nb < nblim; nb += MAXE)
                    if (*nb == e1 || *nb == e2)
                        break;

                if (nb < nblim)
                    scansimple(xnbtot, xnbop);
            }
        }
        reduce4(ext4[i], save_list);
    }

    for (i = 0; i < next5; ++i)
    {
        extend5(ext5[i], save_list);
#ifdef FAST_FILTER_SIMPLE
        if (FAST_FILTER_SIMPLE)
#endif
        {
            if (canon(degree, numbering, &xnbtot, &xnbop))
            {
                e1 = ext5[i]->next->invers;
                e2 = numbering[0][0];
                if (xnbtot == 1)
                {
                    if (!valid5edge(e2))
                    {
                        if (xnbop == 1)
                            if (valid5edge(e2->prev))
                                e2 = e2->prev;
                            else
                                e2 = e2->next;
                        else if (valid5edge(e2->next))
                            e2 = e2->next;
                        else
                            e2 = e2->prev;
                    }
                    if (e2 == e1)
                        scansimple(xnbtot, xnbop);
                }
                else
                {
                    for (nb = (EDGE **)numbering[0]; !valid5edge(*nb); ++nb)
                    {
                    }

                    nblim = (EDGE **)numbering[xnbtot];
                    for (; nb < nblim; nb += MAXE)
                        if (*nb == e1)
                            break;

                    if (nb < nblim)
                        scansimple(xnbtot, xnbop);
                }
            }
        }
        reduce5(ext5[i], save_list);
    }

    if (nv == splitlevel)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/***********************************************************************/

static void
extend_bip_P(EDGE *ref)

/* This routine is the implementation of the P-operation in Batagelj's paper.
   It inserts two new vertices -- nv and nv+1. The reference edge ref is
   the one starting at the vertex to be split that will (always) become a 
   valency 4 vertex neighbouring the one in the center. 


       a
      / \
  ---b---c---e  The edge c-->e is the reference edge
      \ /
       d

The operations can only be understood by drawing a picture containing the edge
numbers as initialized in init_P_op().
*/
{
    EDGE *rp, *rn; /* reference->prev and reference->next */
    EDGE *start, *work, *work2;
    int buffer;

    start = P_op(nv);
    rp = ref->prev;
    rn = ref->next;

    firstedge[ref->start] = rn; /* just in case ref was "firstedge" */
    ref->start = ref->invers->end = nv;
    ref->next = start + 4;
    ref->prev = start + 2;
    degree[nv] = degree[nv + 1] = 4;
    firstedge[nv] = start;
    firstedge[nv + 1] = start + 1;

    buffer = rn->end;
    degree[buffer] += 2;
    work = start + 4;
    work->end = buffer;
    work->prev = ref;
    work2 = rn->invers->next;
    /*work=start+5;*/ work++;
    work->start = buffer;
    work->next = work2;
    work2->prev = work;
    work2 = rn->invers;
    /*work=start+6;*/ work++;
    work->start = buffer;
    work->prev = work2;
    work2->next = work;
    /*(start+7)*/ work++;
    work->end = buffer;

    buffer = rn->start;
    /*work=start+8;*/ work++;
    work->start = buffer;
    work->prev = rp;
    work->next = rn;
    rn->prev = rp->next = work;
    /*(start+9)*/ work++;
    work->end = buffer;

    buffer = rp->end;
    degree[buffer] += 2;
    work2 = rp->invers->prev;
    /*work=start+10;*/ work++;
    work->start = buffer;
    work->next = rp->invers;
    rp->invers->prev = work;
    /*(start+11)*/ work++;
    work->end = buffer;
    work = start + 3;
    work->start = buffer;
    work->prev = work2;
    work2->next = work;
    /*work=start+2;*/ work--;
    work->end = buffer;
    work->next = ref;

    nv += 2;
    ne += 12;
}

/***********************************************************************/

static void
reduce_bip_P(EDGE *ref)

/* This routine is the implementation of the inverse P-operation in Batagelj's 
   paper. It removes the two new vertices -- nv and nv+1. The reference edge 
   ref is c->e and when c and e are removed becomes x->e

        a
       / \
  x---b---c---e  The edge c-->e is the reference edge
       \ /
        d

*/
{
    EDGE *a, *b, *c, *d;
    /* 4 edges forming the square whose inside is removed (except ref) */

    a = ref->invers->next;
    b = ref->invers->prev;
    c = a->invers->next->next->next->invers;
    d = b->invers->prev->prev->prev->invers;

    degree[a->end] -= 2;
    degree[b->end] -= 2;

    ref->start = ref->invers->end = c->start;
    firstedge[ref->start] = ref;
    ref->next = d;
    d->prev = ref;
    ref->prev = c;
    c->next = ref;

    a = a->invers;
    c = c->invers;
    a->next = c;
    c->prev = a;
    firstedge[a->start] = a;

    b = b->invers;
    d = d->invers;
    b->prev = d;
    d->next = b;
    firstedge[b->start] = b;

    nv -= 2;
    ne -= 12;
}

/**************************************************************************/

static void
bip_P_legal(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
            EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref, EDGE *hint)

/* The P-operation with reference edge *ref has just been performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal P-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal P-reductions (mirror-image editions) that
   might be canonical, with the first *ngood_mir_ref of those being ref.
   *ngood_ref and *ngood_mir_ref might each be 0 or 1.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   The "type" used in this procedure needs to match the requirements of
   find_extensions_bip(), so changing it is dangerous.
   If hint!=NULL, it is an edge of the graph that has some chance of
   being a better P-reduction than the one just performed.
*/
{
    int i, j, w, z, ok;
    long degend, deg0, deg1, deg2, deg3, deg4, deg5;
    long thistype, besttype;
    EDGE *e, *e1, *ew, *ewlast;

    degend = degree[ref->end];
    deg0 = degend << 21;
    deg1 = nv - degree[ref->next->next->invers->next->next->end];
    deg2 = degree[ref->next->end];
    deg3 = degree[ref->prev->end];
    deg4 = degree[ref->invers->prev->prev->end];
    deg5 = degree[ref->invers->next->next->end];

    besttype = deg0 + (deg1 << 11) + (deg2 << 2) + (deg3 << 1) + deg4 - deg5;
    thistype = deg0 + (deg1 << 11) + (deg3 << 2) + (deg2 << 1) + deg5 - deg4;
    if (besttype > thistype)
    {
        good_or[0] = ref;
        *ngood_or = *ngood_ref = 1;
        *ngood_mir = *ngood_mir_ref = 0;
    }
    else if (besttype == thistype)
    {
        good_or[0] = good_mir[0] = ref;
        *ngood_or = *ngood_ref = 1;
        *ngood_mir = *ngood_mir_ref = 1;
    }
    else
    {
        good_mir[0] = ref;
        *ngood_or = *ngood_ref = 0;
        *ngood_mir = *ngood_mir_ref = 1;
        besttype = thistype;
    }

    if (hint)
    {
        e = hint;
        w = e->end;
        e1 = e->next->next;
        if (degree[w] >= degend && degree[e->start] == 4 && degree[e->next->end] != 4 && degree[e->prev->end] != 4 && degree[e1->end] == 4 && e != ref)
        {
            z = e1->invers->next->next->end;
            ok = (degree[z] == 4);
            if (!ok)
            {
                ew = e->invers;
                ewlast = ew->prev;
                for (ew = ew->next->next; ew != ewlast; ew = ew->next)
                    if (ew->end == z)
                        break;
                ok = (ew == ewlast);
            }

            if (ok)
            {
                deg0 = ((long)degree[w] << 21) + ((long)(nv - degree[z]) << 11);
                deg2 = degree[e->next->end];
                deg3 = degree[e->prev->end];
                deg4 = degree[e->invers->prev->prev->end];
                deg5 = degree[e->invers->next->next->end];

                thistype = deg0 + (deg2 << 2) + (deg3 << 1) + deg4 - deg5;
                if (thistype > besttype)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }

                thistype = deg0 + (deg3 << 2) + (deg2 << 1) + deg5 - deg4;
                if (thistype > besttype)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
            }
        }
    }

    for (i = 0; i < nv; ++i)
        if (degree[i] == 4)
        {
            e = firstedge[i];
            j = 0;
            if (degree[e->end] == 4)
            {
                e1 = e;
                ++j;
            }
            e = e->next;
            if (degree[e->end] == 4)
            {
                e1 = e;
                ++j;
            }
            e = e->next;
            if (degree[e->end] == 4)
            {
                e1 = e;
                ++j;
            }
            e = e->next;
            if (degree[e->end] == 4)
            {
                e1 = e;
                ++j;
            }
            if (j != 1)
                continue;

            e = e1->next->next;

            w = e->end;
            if (degree[w] < degend)
                continue;
            if (e == ref)
                continue;
            z = e1->invers->next->next->end;

            if (degree[z] != 4)
            {
                ew = e->invers;
                ewlast = ew->prev;
                for (ew = ew->next->next; ew != ewlast; ew = ew->next)
                    if (ew->end == z)
                        break;
                if (ew != ewlast)
                    continue;
            }

            deg0 = ((long)degree[w] << 21) + ((long)(nv - degree[z]) << 11);
            deg2 = degree[e->next->end];
            deg3 = degree[e->prev->end];
            deg4 = degree[e->invers->prev->prev->end];
            deg5 = degree[e->invers->next->next->end];

            thistype = deg0 + (deg2 << 2) + (deg3 << 1) + deg4 - deg5;
            if (thistype > besttype)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else if (thistype == besttype)
                good_or[(*ngood_or)++] = e;

            thistype = deg0 + (deg3 << 2) + (deg2 << 1) + deg5 - deg4;
            if (thistype > besttype)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else if (thistype == besttype)
                good_mir[(*ngood_mir)++] = e;
        }
}

/**************************************************************************/

static int
is_bip_P(EDGE *e)

/* Return 1 if e is the reference edge of a valid P reduction,
   otherwise 0.  It must be that e is an edge of the graph. */
{
    int z;
    EDGE *e1, *ew, *ewlast;

    if (degree[e->start] != 4 || degree[e->end] == 4)
        return 0;
    if (degree[e->next->end] == 4 || degree[e->prev->end] == 4)
        return 0;
    e1 = e->next->next;
    if (degree[e1->end] != 4)
        return 0;
    z = e1->invers->next->next->end;
    if (degree[z] == 4)
        return 1;
    ew = e->invers;
    ewlast = ew->prev;
    for (ew = ew->next->next; ew != ewlast; ew = ew->next)
        if (ew->end == z)
            break;
    if (ew != ewlast)
        return 0;
    else
        return 1;
}

/**************************************************************************/

static EDGE *
has_bip_P(void)

/* If the graph has a legal P-reduction return an example;
   otherwise return NULL. */
{

    int i, j, w, z;
    EDGE *e, *e1, *ez, *ezlast;

    for (i = 0; i < nv; ++i)
        if (degree[i] == 4)
        {
            e = firstedge[i];
            j = 0;
            if (degree[e->end] == 4)
            {
                e1 = e;
                ++j;
            }
            e = e->next;
            if (degree[e->end] == 4)
            {
                e1 = e;
                ++j;
            }
            e = e->next;
            if (degree[e->end] == 4)
            {
                e1 = e;
                ++j;
            }
            e = e->next;
            if (degree[e->end] == 4)
            {
                e1 = e;
                ++j;
            }
            if (j != 1)
                continue;

            e = e1->next->next;

            w = e->end;
            z = e1->invers->next->next->end;

            if (degree[z] != 4)
            {
                ezlast = ez = firstedge[z];
                do
                {
                    if (ez->end == w)
                        break;
                    ez = ez->next;
                } while (ez != ezlast);
                if (ez->end == w)
                    continue;
            }

            return e;
        }
    return NULL;
}

/**************************************************************************/

static void
extend_bip_Q(EDGE *ref)

/* This routine is the implementation of the Q-operation in Batagelj's
   paper.  It inserts one new vertex -- nv. The reference edge ref is
   the one starting at the vertex to be split that will (always) become a 
   valency 4 vertex in the new graph. 

        a
   |\  /   reference edge nv->a
   | \/nv
   | /\
   |/  \

The operations can only be understood by drawing a picture containing the edge
numbers as initialized in init_P_op().
*/
{
    EDGE *a, *b, *c, *d, *x, *start;
    int dummy, dummy2;

    start = Q_op(nv);

    firstedge[nv] = ref;
    x = ref->next;
    b = ref->prev->invers;
    a = b->prev;

    d = x->next->invers;
    c = d->next;

    ref->start = ref->invers->end = x->start = x->invers->end = nv;

    ref->prev = start + 4;

    c->prev = start + 1;
    d->next = start + 2;
    b->prev = start + 3;
    a->next = start + 5;

    dummy = c->start;
    dummy2 = a->start;
    (degree[dummy]) += 2;
    (degree[dummy2]) += 2;
    degree[nv] = 4;
    (degree[b->end]) -= 2;
    start->prev = x;
    x->next = start;
    start->end = dummy;
    start++;
    /*1*/ start->next = c;
    c->prev = start;
    start->start = dummy;
    start++;
    /*2*/ start->prev = d;
    d->next = start;
    start->start = dummy;
    start->end = dummy2;
    start++;
    /*3*/ start->next = b;
    b->prev = start;
    start->start = dummy2;
    start->end = dummy;
    start++;
    /*4*/ start->next = ref;
    ref->prev = start;
    start->end = dummy2;
    start++;
    /*5*/ start->prev = a;
    a->next = start;
    start->start = dummy2;

    b = b->invers;
    d = d->invers;

    firstedge[b->start] = b;
    b->next = d;
    d->prev = b;

    nv++;
    ne += 6;
}

/***********************************************************************/

static void
reduce_bip_Q(EDGE *ref)

/* This routine is the implementation of the inverse Q-operation in
   Batagelj's paper. It removes the new vertex nv. 
*/
{

    EDGE *a, *b, *c, *d, *x;

    x = ref->next;
    a = ref->invers->next->invers;
    b = a->next->next->next;

    c = x->invers->prev->invers;
    d = c->prev->prev->prev;

    firstedge[a->start] = a;
    firstedge[c->start] = c;

    ref->start = ref->invers->end = x->start = x->invers->end = b->end;
    (degree[b->end]) += 2;
    (degree[a->start]) -= 2;
    (degree[c->start]) -= 2;

    b->prev = a;
    a->next = b;
    c->prev = d;
    d->next = c;

    b = b->invers;
    d = d->invers;

    b->next = ref;
    ref->prev = b;
    d->prev = x;
    x->next = d;

    nv--;
    ne -= 6;
}

/**************************************************************************/

static void
bip_Q_legal(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
            EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* The Q-operation with reference edge *ref has just been performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal Q-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal P-reductions (mirror-image editions) that
   might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0 or 1.  If they are  
   both 0, nothing else need be correct.  
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
*/
{
    int i, j, w, z1, z2;
    long thistype, besttype;
    EDGE *e, *e1, *ew, *ewlast;

    besttype = ((long)degree[ref->end] << 10) + degree[ref->next->end] + degree[ref->prev->end];
    good_or[0] = ref;
    *ngood_or = *ngood_ref = 1;

    e = ref->next;
    thistype = ((long)degree[e->end] << 10) + degree[e->next->end] + degree[e->prev->end];
    if (thistype >= besttype)
    {
        good_mir[0] = e;
        *ngood_mir = *ngood_mir_ref = 1;
    }
    else
        *ngood_mir = *ngood_mir_ref = 0;

    if (thistype > besttype)
    {
        *ngood_or = *ngood_ref = 0;
        besttype = thistype;
    }

    for (i = 0; i < nv; ++i)
        if (degree[i] == 4)
        {
            e = firstedge[i];
            e1 = e->next->next;
            for (j = 0; j < 4; ++j, e = e->next, e1 = e1->next)
            {
                if (degree[e->prev->end] < 6 || degree[e1->end] < 6)
                    continue;
                if (e == ref)
                    continue;
                w = e1->invers->prev->prev->end;

                z1 = e->end;
                z2 = e->next->end;
                ew = ewlast = firstedge[w];
                do
                {
                    if (ew->end == z1 || ew->end == z2)
                        break;
                    ew = ew->next;
                } while (ew != ewlast);
                if (ew->end == z1 || ew->end == z2)
                    continue;

                thistype = ((long)degree[z1] << 10) + degree[z2] + degree[e->prev->end];
                if (thistype > besttype)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (thistype == besttype)
                    good_or[(*ngood_or)++] = e;

                thistype = ((long)degree[z2] << 10) + degree[z1] + degree[e1->end];
                if (thistype > besttype)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (thistype == besttype)
                    good_mir[(*ngood_mir)++] = e->next;
            }
        }
}

/**************************************************************************/

static void
find_extensions_bip(int nbtot, int nbop, EDGE *extP[], int *nextP,
                    EDGE *extQ[], int *nextQ, EDGE *Pedges[], int nPedges)

/* nbtot and nbop are the usual group parameters.
   Place in extP{0..nextP-1] the reference edges of possible P_ops, and
   place in extQ{0..nextQ-1] the reference edges of possible Q_ops.
   In both cases, only inequivalent edges are listed.
*/
{
    int Ptot, Qtot;
    EDGE *e, *elast, *ev, *evlast, *ee;
    EDGE **nb, **nb0, **nblim, **nboplim;
    register int i, v, w;
    int weight[MAXN], minweight;
    int oldPwt, Pv1, Pv2;

    Ptot = Qtot = 0;
    for (i = 0; i < nv; ++i)
        weight[i] = 0;
    minweight = 0;
    RESETMARKS;
    for (i = 0; i < nPedges; ++i)
        if (i == nPedges - 1 || is_bip_P(Pedges[i]))
        {
            e = Pedges[i];
            if (ISMARKEDLO(e))
                continue;
            MARKLO(e);
            ++weight[e->start];
            e = e->next->next->invers->next->next;
            ++weight[e->start];
            ++weight[e->end];
            while (degree[e->end] == 4)
                e = e->invers->next->next;
            MARKLO(e);
            ++weight[e->start];
            e = e->prev->prev->invers->prev->prev;
            ++weight[e->start];
            ++weight[e->end];
            minweight += 2;
        }

    if (nv == maxnv - 1)
    {
        if (nbtot == 1) /* Case of trivial group */
        {
            for (i = 0; i < nv; ++i)
                if (degree[i] != 4)
                {
                    e = elast = firstedge[i];
                    do
                    {
                        v = e->prev->end;
                        w = e->next->next->end;
                        if (weight[v] + weight[w] >= minweight)
                        {
                            ev = evlast = e->prev->invers;
                            for (ev = ev->next; ev != evlast; ev = ev->next)
                                if (ev->end == w)
                                    break;
                            if (ev == evlast)
                                extQ[Qtot++] = e;
                        }
                        e = e->next;
                    } while (e != elast);
                }
        }
        else /* Case of nontrivial group */
        {
            nb0 = (EDGE **)numbering[0];
            nblim = (EDGE **)numbering[nbtot];
            nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];
            RESETMARKS;
            for (i = 0; i < ne; ++i, ++nb0)
            {
                e = *nb0;
                if (!ISMARKEDLO(e) && degree[e->start] >= 6)
                {
                    v = e->prev->end;
                    w = e->next->next->end;

                    if (weight[v] + weight[w] >= minweight)
                    {
                        ev = evlast = e->prev->invers;
                        for (ev = ev->next; ev != evlast; ev = ev->next)
                            if (ev->end == w)
                                break;
                        if (ev == evlast)
                            extQ[Qtot++] = e;
                    }

                    nb = nb0 + MAXE;
                    for (; nb < nboplim; nb += MAXE)
                        MARKLO(*nb);
                    for (; nb < nblim; nb += MAXE)
                        MARKLO((*nb)->prev);
                }
            }
        }
    }
    else /* nv <= maxnv-2 */
    {
        if (nPedges > 0)
        {
            e = Pedges[nPedges - 1];
            oldPwt = degree[e->end];
            Pv1 = e->start;
            Pv2 = e->next->next->end;
        }
        else
            oldPwt = 0;

        if (nbtot == 1) /* Case of trivial group */
        {
            for (i = 0; i < nv; ++i)
                if (degree[i] != 4)
                {
                    e = elast = firstedge[i];
                    do
                    {
                        if (degree[i] >= oldPwt ||
                            e->next->end == Pv1 || e->next->end == Pv2 ||
                            e->prev->end == Pv1 || e->prev->end == Pv2)
                        {
                            for (ee = e; degree[ee->end] == 4;
                                 ee = ee->invers->next->next)
                            {
                            }
                            if (degree[i] >= degree[ee->end])
                                extP[Ptot++] = e->invers;
                        }

                        v = e->prev->end;
                        w = e->next->next->end;

                        if (weight[v] + weight[w] >= minweight)
                        {
                            ev = evlast = e->prev->invers;
                            for (ev = ev->next; ev != evlast; ev = ev->next)
                                if (ev->end == w)
                                    break;
                            if (ev == evlast)
                                extQ[Qtot++] = e;
                        }

                        e = e->next;
                    } while (e != elast);
                }
        }
        else /* Case of nontrivial group */
        {
            nb0 = (EDGE **)numbering[0];
            nblim = (EDGE **)numbering[nbtot];
            RESETMARKS;
            for (i = 0; i < ne; ++i, ++nb0)
            {
                if (!ISMARKEDLO(*nb0) && degree[(*nb0)->start] >= 6)
                {
                    e = *nb0;
                    if (degree[e->start] >= oldPwt ||
                        e->next->end == Pv1 || e->next->end == Pv2 ||
                        e->prev->end == Pv1 || e->prev->end == Pv2)
                    {
                        for (ee = e; degree[ee->end] == 4;
                             ee = ee->invers->next->next)
                        {
                        }
                        if (degree[e->start] >= degree[ee->end])
                            extP[Ptot++] = e->invers;
                    }

                    for (nb = nb0; nb < nblim; nb += MAXE)
                        MARKLO(*nb);
                }
            }

            nb0 = (EDGE **)numbering[0];
            nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];
            RESETMARKS;
            for (i = 0; i < ne; ++i, ++nb0)
            {
                e = *nb0;
                if (!ISMARKEDLO(e) && degree[e->start] >= 6)
                {
                    v = e->prev->end;
                    w = e->next->next->end;

                    if (weight[v] + weight[w] >= minweight)
                    {
                        ev = evlast = e->prev->invers;
                        for (ev = ev->next; ev != evlast; ev = ev->next)
                            if (ev->end == w)
                                break;
                        if (ev == evlast)
                            extQ[Qtot++] = e;
                    }

                    nb = nb0 + MAXE;
                    for (; nb < nboplim; nb += MAXE)
                        MARKLO(*nb);
                    for (; nb < nblim; nb += MAXE)
                        MARKLO((*nb)->prev);
                }
            }
        }
    }

    *nextP = Ptot;
    *nextQ = Qtot;
}

/**************************************************************************/

static void
scanbipartite(int nbtot, int nbop, EDGE *wheelrim, int dosplit,
              EDGE *Pedges[], int nPedges)

/* The main node of the recursion for bipartite triangulations
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   If wheelrim != NULL, the input is a double wheel and *wheelrim is
   one of the edges on the rim.
   If dosplit==TRUE, this is the place to do splitting (if any).
   Splitting is a bit more complicated because the P operation adds
   two vertices.
   Pedges[0..nPedges-1] are edges of the graph that were reference
   edges for P-operations in ancestors of this graph.  They may not
   be reference edges for P-reductions now, but at least they are edges.
   However, if nPedges>0, we can say that certainly Pedges[nPedges-1]
   is a P-operation that was just done.
*/
{
    EDGE *firstedge_save[MAXN];
    EDGE *extP[MAXE], *extQ[MAXE];
    EDGE *good_or[MAXE], *good_mir[MAXE];
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int nextP, nextQ, i;
    int xnbtot, xnbop;
    EDGE *hint, *newPedges[MAXN / 2];

    if (nv == maxnv)
    {
        got_one(nbtot, nbop, 3);
        return;
    }

    if (dosplit)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_BIP
    if (!(PRE_FILTER_BIP))
        return;
#endif

#ifndef FIND_EXTENSIONS_BIP
#define FIND_EXTENSIONS_BIP find_extensions_bip
#endif

    FIND_EXTENSIONS_BIP(nbtot, nbop, extP, &nextP, extQ, &nextQ, Pedges, nPedges);

    if (wheelrim && nv <= maxnv - 2)
    {
        extend_bip_P(wheelrim);
#ifdef FAST_FILTER_BIP
        if (FAST_FILTER_BIP)
#endif
        {
            (void)canon(degree, numbering, &xnbtot, &xnbop);
            scanbipartite(xnbtot, xnbop, wheelrim,
                          nv == splitlevel || nv == splitlevel + 1, Pedges, 0);
        }
        reduce_bip_P(wheelrim);
    }

    for (i = 0; i < nextP; ++i)
    {
        extend_bip_P(extP[i]);
#ifdef FAST_FILTER_BIP
        if (FAST_FILTER_BIP)
#endif
        {
            bip_P_legal(extP[i], good_or, &ngood_or, &ngood_ref,
                        good_mir, &ngood_mir, &ngood_mir_ref,
                        nPedges ? Pedges[nPedges - 1] : NULL);
            if (ngood_ref + ngood_mir_ref > 0)
            {
                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref)
                    got_one(1, 1, 3);
                else if (ngood_or + ngood_mir == 1)
                {
                    Pedges[nPedges] = extP[i];
                    scanbipartite(1, 1, NULL,
                                  nv == splitlevel || nv == splitlevel + 1, Pedges, nPedges + 1);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    Pedges[nPedges] = extP[i];
                    scanbipartite(xnbtot, xnbop, NULL,
                                  nv == splitlevel || nv == splitlevel + 1, Pedges, nPedges + 1);
                }
            }
        }
        reduce_bip_P(extP[i]);
    }

    hint = NULL;
    for (i = 0; i < nextQ; ++i)
    {
        extend_bip_Q(extQ[i]);
#ifdef FAST_FILTER_BIP
        if (FAST_FILTER_BIP)
#endif
        {
            if (!hint || !is_bip_P(hint))
                hint = has_bip_P();

            if (!hint)
            {
                bip_Q_legal(extQ[i], good_or, &ngood_or, &ngood_ref,
                            good_mir, &ngood_mir, &ngood_mir_ref);
                if (ngood_ref + ngood_mir_ref > 0 && canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                                                         good_mir, ngood_mir, ngood_mir_ref,
                                                                         degree, numbering, &xnbtot, &xnbop))
                    scanbipartite(xnbtot, xnbop, NULL, nv == splitlevel, newPedges, 0);
            }
        }
        reduce_bip_Q(extQ[i]);
    }

    if (dosplit)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/**************************************************************************/

static void
update_nft_P(triangle nft[], int numnft, EDGE *ref,
             triangle newnft[], int *newnumnft)

/* Make new list of non-facial triangles after a P-extension. */
{
    EDGE *refmin, *e, *elast;
    int i, k, w;

    refmin = ref->min;

    /* Remove triangles that include ref */
    k = 0;
    for (i = 0; i < numnft; ++i)
        if (nft[i].e1 != refmin && nft[i].e2 != refmin && nft[i].e3 != refmin)
            newnft[k++] = nft[i];

    /* Add new nfts formed by a shortcut if present.  There must be at
     least two nfts already for this to be possible. */

    if (k >= 2)
    {
        w = ref->next->end;
        elast = ref->invers->next->invers;
        for (e = elast->next->next->next->next; e != elast; e = e->next)
            if (e->end == w)
                break;
        if (e != elast)
        {
            newnft[k].e1 = e->min;
            newnft[k].e2 = ref->prev->min;
            newnft[k].e3 = ref->next->min;
            newnft[k + 1].e1 = e->min;
            newnft[k + 1].e2 = ref->next->next->invers->prev->min;
            newnft[k + 1].e3 = ref->next->next->invers->next->min;
            k += 2;
        }
    }
    *newnumnft = k;
}

/**************************************************************************/

static void
update_nft_Q(triangle nft[], int numnft, EDGE *ref,
             triangle newnft[], int *newnumnft)

/* Make new list of non-facial triangles after a Q-extension. */
{
    EDGE *refmin1, *refmin2, *e, *elast, *f, *flast;
    int i, k, w;

    refmin1 = ref->min;
    refmin2 = ref->next->min;

    /* Remove triangles that include ref or ref->next */
    k = 0;
    for (i = 0; i < numnft; ++i)
        if (nft[i].e1 != refmin1 && nft[i].e2 != refmin1 && nft[i].e3 != refmin1 && nft[i].e1 != refmin2 && nft[i].e2 != refmin2 && nft[i].e3 != refmin2)
            newnft[k++] = nft[i];

    /* Add new nft through ref if present */

    w = ref->end;
    elast = ref->next->next->invers->prev->prev;
    for (e = elast->next->next->next->next; e != elast; e = e->next)
        if (e->end == w)
            break;
    if (e != elast)
    {
        newnft[k].e1 = e->min;
        newnft[k].e2 = ref->min;
        newnft[k].e3 = ref->next->next->min;
        ++k;
    }

    /* Add new nft through ref->next if present */

    w = ref->next->end;
    elast = ref->invers->next->invers;
    for (e = elast->next->next->next->next; e != elast; e = e->next)
        if (e->end == w)
            break;
    if (e != elast)
    {
        newnft[k].e1 = e->min;
        newnft[k].e2 = ref->next->min;
        newnft[k].e3 = ref->prev->min;
        ++k;
    }

    /* Add all new nft's through the shortcut.  This is the only place
     an nft can be made where there was none before.  This code can
     also add extra nfts through ref or ref->next, since v can be
     ref->end or ref->next->end. */

    w = ref->prev->end;
    elast = ref->next->next->invers->prev->prev;
    for (e = elast->next->next->next; e != elast; e = e->next)
    {
        flast = e->invers;
        for (f = flast->next; f != flast; f = f->next)
            if (f->end == w)
                break;
        if (f != flast)
        {
            newnft[k].e1 = elast->next->min;
            newnft[k].e2 = e->min;
            newnft[k].e3 = f->min;
            ++k;
        }
    }

    *newnumnft = k;
}

/**************************************************************************/

static void
bipnftlaststep(EDGE *extP[], int *nextP, triangle nft[], int numnft)

/* Remove from extP[0..*nextP-1] those extensions which do not
   hit all of nft[0..numnft-1]. */
{
    int i, j, k;

    for (j = 0; j < numnft; ++j)
    {
        RESETMARKS;
        MARKLO(nft[j].e1);
        MARKLO(nft[j].e1->invers);
        MARKLO(nft[j].e2);
        MARKLO(nft[j].e2->invers);
        MARKLO(nft[j].e3);
        MARKLO(nft[j].e3->invers);

        k = 0;
        for (i = 0; i < *nextP; ++i)
            if (ISMARKEDLO(extP[i]))
                extP[k++] = extP[i];
        *nextP = k;
    }
}

/**************************************************************************/

static void
scanbipartite4c(int nbtot, int nbop, EDGE *wheelrim, int dosplit,
                EDGE *Pedges[], int nPedges, triangle nft[], int numnft)

/* The main node of the recursion for bipartite triangulations with
   monitoring of non-facial triangles.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   If wheelrim != NULL, the input is a double wheel and *wheelrim is
   one of the edges on the rim.
   If dosplit==TRUE, this is the place to do splitting (if any).
   Splitting is a bit more complicated because the P operation adds
   two vertices.
   Pedges[0..nPedges-1] are edges of the graph that were reference
   edges for P-operations in ancestors of this graph.  They may not
   be reference edges for P-reductions now, but at least they are edges.
   However, if nPedges>0, we can say that certainly Pedges[nPedges-1]
   is a P-operation that was just done.
   nft[0..numnft-1] is a list of the non-facial triangles.
*/
{
    EDGE *firstedge_save[MAXN];
    EDGE *extP[MAXE], *extQ[MAXE];
    EDGE *good_or[MAXE], *good_mir[MAXE];
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int nextP, nextQ, i;
    int xnbtot, xnbop;
    EDGE *hint, *newPedges[MAXN / 2];
    triangle newnft[MAXN];
    int newnumnft, connec;

    if (nv == maxnv)
    {
        connec = 3 + (numnft == 0);
        if (connec >= minconnec)
            got_one(nbtot, nbop, connec);
        return;
    }

    if (dosplit)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_BIP
    if (!(PRE_FILTER_BIP))
        return;
#endif

#ifndef FIND_EXTENSIONS_BIP
#define FIND_EXTENSIONS_BIP find_extensions_bip
#endif

    FIND_EXTENSIONS_BIP(nbtot, nbop, extP, &nextP, extQ, &nextQ, Pedges, nPedges);

    if (nv == maxnv - 2 && numnft > 0 && minconnec == 4)
        bipnftlaststep(extP, &nextP, nft, numnft);

    if (wheelrim && nv <= maxnv - 2)
    {
        extend_bip_P(wheelrim);
#ifdef FAST_FILTER_BIP
        if (FAST_FILTER_BIP)
#endif
        {
            canon(degree, numbering, &xnbtot, &xnbop);
            scanbipartite4c(xnbtot, xnbop, wheelrim,
                            nv == splitlevel || nv == splitlevel + 1, Pedges, 0, nft, numnft);
        }
        reduce_bip_P(wheelrim);
    }

    for (i = 0; i < nextP; ++i)
    {
        extend_bip_P(extP[i]);
#ifdef FAST_FILTER_BIP
        if (FAST_FILTER_BIP)
#endif
        {
            bip_P_legal(extP[i], good_or, &ngood_or, &ngood_ref,
                        good_mir, &ngood_mir, &ngood_mir_ref,
                        nPedges ? Pedges[nPedges - 1] : NULL);
            if (ngood_ref + ngood_mir_ref > 0)
            {
                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref)
                {
                    update_nft_P(nft, numnft, extP[i], newnft, &newnumnft);
                    connec = 3 + (newnumnft == 0);
                    if (connec >= minconnec)
                        got_one(1, 1, connec);
                }
                else if (ngood_or + ngood_mir == 1)
                {
                    update_nft_P(nft, numnft, extP[i], newnft, &newnumnft);
                    Pedges[nPedges] = extP[i];
                    scanbipartite4c(1, 1, NULL, nv == splitlevel || nv == splitlevel + 1,
                                    Pedges, nPedges + 1, newnft, newnumnft);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    update_nft_P(nft, numnft, extP[i], newnft, &newnumnft);
                    Pedges[nPedges] = extP[i];
                    scanbipartite4c(xnbtot, xnbop, NULL,
                                    nv == splitlevel || nv == splitlevel + 1,
                                    Pedges, nPedges + 1, newnft, newnumnft);
                }
            }
        }
        reduce_bip_P(extP[i]);
    }

    hint = NULL;
    for (i = 0; i < nextQ; ++i)
    {
        extend_bip_Q(extQ[i]);
#ifdef FAST_FILTER_BIP
        if (FAST_FILTER_BIP)
#endif
        {
            if (!hint || !is_bip_P(hint))
                hint = has_bip_P();

            if (!hint)
            {
                bip_Q_legal(extQ[i], good_or, &ngood_or, &ngood_ref,
                            good_mir, &ngood_mir, &ngood_mir_ref);
                if (ngood_ref + ngood_mir_ref > 0 && canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                                                         good_mir, ngood_mir, ngood_mir_ref,
                                                                         degree, numbering, &xnbtot, &xnbop))
                {
                    update_nft_Q(nft, numnft, extQ[i], newnft, &newnumnft);
                    scanbipartite4c(xnbtot, xnbop, NULL, nv == splitlevel,
                                    newPedges, 0, newnft, newnumnft);
                }
            }
        }
        reduce_bip_Q(extQ[i]);
    }

    if (dosplit)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/**************************************************************************/

static void
extend_four(EDGE *ref)

/* This routine is another implementation of the 4-operation
   in Batagelj's paper.
*/
{
    register EDGE *a, *b, *start, *dummy;

    start = four_op(nv);
    b = ref->next->invers;
    a = b->next;

    degree[nv] = 4;
    firstedge[nv] = start;

    dummy = start + 1;
    start->end = dummy->start = a->start;
    (degree[a->start])++;
    a->prev = b->next = dummy;
    dummy->prev = b;
    dummy->next = a;

    b = b->invers;
    a = ref->prev;

    start += 2; /*2*/
    dummy = start + 1;
    start->end = dummy->start = b->start;
    firstedge[b->start] = dummy;
    b->prev = a->next = dummy;
    dummy->prev = a;
    dummy->next = b;

    a = a->invers;
    b = a->prev;
    start += 2; /*4*/
    dummy = start + 1;
    start->end = dummy->start = b->start;
    (degree[b->start])++;
    a->prev = b->next = dummy;
    dummy->prev = b;
    dummy->next = a;

    start->next = (start - 4)->prev = ref;
    ref->next = start - 4;
    ref->prev = start;
    ref->start = ref->invers->end = nv;

    nv++;
    ne += 6;
}

/**************************************************************************/

static int
is_min4_four(EDGE *ref)

/* Test if ref (known to be an edge!) is the reference edge of a
   legal four-reduction in the min4 case. 
   Return 1 if it is, and 0 if it isn't.
*/
{
    int w;
    EDGE *e, *elast;

    if (degree[ref->start] != 4)
        return 0;
    if (degree[ref->prev->end] == 4 || degree[ref->next->end] == 4)
        return 0;

    w = ref->next->next->end;
    if (degree[w] == 4)
        return 1;
    e = ref->invers;
    elast = e->prev;
    for (e = e->next->next; e != elast; e = e->next)
        if (e->end == w)
            return 0;

    return 1;
}

/**************************************************************************/

static void
reduce_four(EDGE *ref)

/* The reverse of extend_four(ref) */
{
    register EDGE *a, *b;

    a = ref->invers->prev->invers;
    b = a->prev->prev;

    a->prev = b;
    b->next = a;
    firstedge[a->start] = a;
    (degree[a->start])--;

    a = b->invers;
    b = a->prev->prev;
    a->prev = b->next = ref;
    ref->next = a;
    ref->prev = b;
    ref->start = ref->invers->end = a->start;
    firstedge[a->start] = a;

    a = b->invers;
    b = a->prev->prev;
    a->prev = b;
    b->next = a;
    firstedge[a->start] = a;
    (degree[a->start])--;

    nv--;
    ne -= 6;
}

/**************************************************************************/

static void
prune_oriented_lists(EDGE *good_or[], int *ngood_or, int *ngood_ref,
                     EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* Try to prune the edge lists (of the form required by
   canon_edge_oriented()) by using the degrees of a couple of
   extra vertices.  The result is returned in the same form.
   As always, if *ngood_ref==*ngood_mir_ref==0 on output
   (which must not be true on input), all else is undefined.
*/
{
    int i, k, kref;
    long code_or[MAXE], code_mir[MAXE], maxcode;
#define PRUNE_OR(e) ((degree[(e)->invers->prev->prev->end] << 10) + degree[(e)->next->invers->prev->end])
#define PRUNE_MIR(e) ((degree[(e)->invers->next->next->end] << 10) + degree[(e)->prev->invers->next->end])

    maxcode = 0;
    for (i = 0; i < *ngood_or; ++i)
    {
        code_or[i] = PRUNE_OR(good_or[i]);
        if (code_or[i] > maxcode)
            maxcode = code_or[i];
    }

    for (i = 0; i < *ngood_mir; ++i)
    {
        code_mir[i] = PRUNE_MIR(good_mir[i]);
        if (code_mir[i] > maxcode)
            maxcode = code_mir[i];
    }

    k = kref = 0;
    for (i = 0; i < *ngood_or; ++i)
        if (code_or[i] == maxcode)
        {
            if (i < *ngood_ref)
                ++kref;
            good_or[k++] = good_or[i];
        }
    *ngood_or = k;
    *ngood_ref = kref;

    k = kref = 0;
    for (i = 0; i < *ngood_mir; ++i)
        if (code_mir[i] == maxcode)
        {
            if (i < *ngood_mir_ref)
                ++kref;
            good_mir[k++] = good_mir[i];
        }
    *ngood_mir = k;
    *ngood_mir_ref = kref;
}

/**************************************************************************/

static void
min4_four_legal(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
                EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* The four-operation with reference edge *ref has just been performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal four-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-2.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   Four-reductions have a priority: (maxdeg, mindeg) where those are
   the two degrees on the subdivided diagonal.  Bigger = better.
*/
{
    EDGE *e, *er;
    long deg1, deg2, deg3, deg4;
#define FOURTYPE(d3, d4) (((d3) << 10) + (d4))
    long besttype, etype1, etype2, ertype1, ertype2, etype, ertype;
    int bestdeg, nextdeg, nor, nmir, i, w;
    EDGE *ei, *eilast;

    e = ref;
    er = ref->next->next;
    deg1 = degree[e->end];
    deg2 = degree[er->end];
    deg3 = degree[e->prev->end];
    deg4 = degree[e->next->end];

    nor = nmir = 0;

    if (deg1 >= deg2)
    {
        bestdeg = deg1;
        nextdeg = deg2;
        etype1 = FOURTYPE(deg3, deg4);
        etype2 = FOURTYPE(deg4, deg3);
        besttype = etype = etype1 > etype2 ? etype1 : etype2;
    }

    if (deg1 <= deg2)
    {
        bestdeg = deg2;
        nextdeg = deg1;
        ertype1 = FOURTYPE(deg4, deg3);
        ertype2 = FOURTYPE(deg3, deg4);
        besttype = ertype = ertype1 > ertype2 ? ertype1 : ertype2;
    }

    if (deg1 == deg2)
        besttype = etype > ertype ? etype : ertype;

    if (deg1 >= deg2)
    {
        if (etype1 == besttype)
            good_or[nor++] = e;
        if (etype2 == besttype)
            good_mir[nmir++] = e;
    }
    if (deg1 <= deg2)
    {
        if (ertype1 == besttype)
            good_or[nor++] = er;
        if (ertype2 == besttype)
            good_mir[nmir++] = er;
    }

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    RESETMARKS;
    MARKLO(e->invers);
    MARKLO(er->invers);

    for (i = 0; i < nv; ++i)
        if (degree[i] > bestdeg)
        {
            ei = eilast = firstedge[i];
            do
            {
                if (degree[ei->end] == 4 && is_min4_four(ei->invers))
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                ei = ei->next;
            } while (ei != eilast);
        }
        else if (degree[i] == bestdeg)
        {
            ei = eilast = firstedge[i];
            do
            {
                if (degree[ei->end] == 4 && !ISMARKEDLO(ei))
                {
                    e = ei->invers;
                    er = e->next->next;
                    w = er->end;
                    deg2 = degree[w];
                    if (deg2 > nextdeg && is_min4_four(e))
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        return;
                    }
                    else if (deg2 == nextdeg && (bestdeg > nextdeg || i < w) && is_min4_four(e))
                    {
                        deg3 = degree[e->prev->end];
                        deg4 = degree[e->next->end];
                        etype1 = FOURTYPE(deg3, deg4);
                        etype2 = FOURTYPE(deg4, deg3);

                        if (etype1 > besttype || etype2 > besttype)
                        {
                            *ngood_ref = *ngood_mir_ref = 0;
                            return;
                        }
                        if (etype1 == besttype)
                            good_or[nor++] = e;
                        if (etype2 == besttype)
                            good_mir[nmir++] = e;

                        if (nextdeg == bestdeg)
                        {
                            ertype1 = FOURTYPE(deg4, deg3);
                            ertype2 = FOURTYPE(deg3, deg4);

                            if (ertype1 > besttype || ertype2 > besttype)
                            {
                                *ngood_ref = *ngood_mir_ref = 0;
                                return;
                            }

                            if (ertype1 == besttype)
                                good_or[nor++] = er;
                            if (ertype2 == besttype)
                                good_mir[nmir++] = er;
                        }
                    }
                }
                ei = ei->next;
            } while (ei != eilast);
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/**************************************************************************/

static int
min4_four_centre(void)

/* If there is a four-reduction, return the central vertex.
   If not, return -1.
*/
{
    int i;
    EDGE *e;

    for (i = 0; i < nv; ++i)
        if (degree[i] == 4)
        {
            e = firstedge[i];
            if ((degree[e->prev->end] >= 5 && degree[e->next->end] >= 5) || (degree[e->end] >= 5 && degree[e->next->next->end] >= 5))
                return i;
        }

    return -1;
}

/*************************************************************************/

static int
is_min4_four_centre(int v)

/* return 1 if v is the centre of a four-reduction, 0 if not.
*/
{
    EDGE *e;

    if (degree[v] != 4)
        return 0;

    e = firstedge[v];
    if ((degree[e->prev->end] >= 5 && degree[e->next->end] >= 5) || (degree[e->end] >= 5 && degree[e->next->next->end] >= 5))
        return 1;
    else
        return 0;
}

/*************************************************************************/

static int
has_3_four_centres(void)

/* Return 1 if there are at least three vertices which are centres
   for a four-reduction (min4 case).  Return 0 otherwise.
*/
{
    EDGE *e;
    int v, count;

    count = 0;
    for (v = nv; --v >= 0;)
        if (degree[v] == 4)
        {
            e = firstedge[v];
            if ((degree[e->prev->end] >= 5 && degree[e->next->end] >= 5) || (degree[e->end] >= 5 && degree[e->next->next->end] >= 5))
            {
                if (++count == 3)
                    return 1;
            }
        }

    return count >= 3;
}

/*************************************************************************/

static int
degree5_vertex(void)

/* Return a vertex of degree 5, -1 if there are none */
{
    int i;

    for (i = 0; i < nv; ++i)
        if (degree[i] == 5)
            return 1;

    return -1;
}

/*************************************************************************/

static void
extend_five(EDGE *ref)

/* This routine is another implementation of the five-operation
   in Batagelj's paper. */
{
    EDGE *a, *b, *start, *dummy;

    start = five_op(nv);
    degree[nv] = 5;
    firstedge[nv] = start;

    b = ref->prev;
    a = ref->next;
    dummy = start + 1;
    b->next = a->prev = dummy;
    dummy->next = a;
    dummy->prev = b;
    dummy->start = start->end = a->start;
    firstedge[a->start] = a;

    a = b->invers;
    b = a->prev;
    start += 2; /*2*/
    dummy = start + 1;
    b->next = a->prev = dummy;
    dummy->next = a;
    dummy->prev = b;
    dummy->start = start->end = a->start;
    (degree[a->start])++;

    a = b->invers;
    b = a->prev->prev->prev;
    dummy = ref->invers;
    b->next = dummy;
    dummy->prev = b;
    firstedge[a->start] = a;
    (degree[a->start])--;

    a = b->invers;
    b = a->prev;
    start += 2; /*4*/
    dummy = start + 1;
    b->next = a->prev = dummy;
    dummy->next = a;
    dummy->prev = b;
    dummy->start = start->end = a->start;
    (degree[a->start])++;

    dummy = b->invers->prev->invers; /* the other remaining edge of the "v" */

    dummy->start = dummy->invers->end = nv;
    dummy->next = start - 4;
    dummy->prev = start;
    start->next = dummy;
    (start - 4)->prev = dummy;

    ref->start = ref->invers->end = nv;
    ref->next = start;
    ref->prev = start - 2;
    start->prev = ref;
    (start - 2)->next = ref;

    nv++;
    ne += 6;
}

/**************************************************************************/

static void
reduce_five(EDGE *ref)

/* The reverse of extend_five(). */
{
    EDGE *a, *b, *dummy;

    a = ref->next->next;
    dummy = ref->invers;
    b = dummy->prev;
    dummy->prev = b->next = a;
    a->next = dummy;
    a->prev = b;
    a->start = a->invers->end = dummy->start;
    (degree[dummy->start])++;

    a = b->invers;
    b = a->prev->prev;
    a->prev = b;
    b->next = a;
    (degree[a->start])--;
    firstedge[a->start] = a;

    a = b->invers->prev->prev->invers;
    b = a->prev->prev;
    a->prev = ref;
    ref->next = a;
    b->next = ref;
    ref->prev = b;
    ref->start = ref->invers->end = a->start;
    firstedge[a->start] = a;

    a = b->invers;
    b = a->prev->prev;
    a->prev = b;
    b->next = a;
    (degree[a->start])--;
    firstedge[a->start] = a;

    nv--;
    ne -= 6;
}

/**************************************************************************/

static void
min4_five_legal(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
                EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* The five-operation with reference edge *ref has just been performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal five-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal five-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref.
   *ngood_ref and *ngood_mir_ref might each be 0 or 1.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
*/
{
    EDGE *e;
    long deg1, deg2, deg3, bestdeg;
#define FIVETYPE(d1, d2, d3) (((d1) << 21) + ((d2) << 11) + (d3))
    long besttype, type1, type2;
    int nor, nmir, i, j, v, w;
    EDGE *ez, *ezlast;

    e = ref;
    bestdeg = degree[e->end];
    deg2 = degree[e->prev->end];
    deg3 = degree[e->next->end];

    type1 = FIVETYPE(bestdeg, deg2, deg3);
    type2 = FIVETYPE(bestdeg, deg3, deg2);
    besttype = type1 > type2 ? type1 : type2;

    nor = nmir = 0;
    if (type1 == besttype)
        good_or[nor++] = e;
    if (type2 == besttype)
        good_mir[nmir++] = e;

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    for (i = 0; i < nv; ++i)
        if (degree[i] == 5)
        {
            for (e = firstedge[i], j = 0; j < 5; ++j, e = e->next)
            {
                if (e == ref)
                    continue;
                deg1 = degree[e->end];
                if (deg1 < bestdeg)
                    continue;
                deg2 = degree[e->prev->end];
                if (deg2 == 4)
                    continue;
                deg3 = degree[e->next->end];
                if (deg3 == 4)
                    continue;

                v = e->next->next->end;
                w = e->next->next->next->end;
                ez = e->invers;
                ezlast = ez->prev;
                for (ez = ez->next->next; ez != ezlast; ez = ez->next)
                    if (ez->end == w || ez->end == v)
                        break;
                if (ez != ezlast)
                    continue;

                if (deg1 > bestdeg)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }

                type1 = FIVETYPE(deg1, deg2, deg3);
                type2 = FIVETYPE(deg1, deg3, deg2);

                if (type1 > besttype || type2 > besttype)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                if (type1 == besttype)
                    good_or[nor++] = e;
                if (type2 == besttype)
                    good_mir[nmir++] = e;
            }
        }

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/**************************************************************************/

static void
extend_S(EDGE *ref)

/* This routine is the implementation of the S-operation in Batagelj's paper.
   It inserts 3 new vertices in triangular form into a triangle on the right
   hand side of ref */

{
    register EDGE *a, *b, *start;
    int dummy;

    start = S_op(nv);

    a = ref->invers->prev;
    b = a->invers->prev;

    degree[nv] = degree[nv + 1] = degree[nv + 2] = 4;

    dummy = ref->start;
    degree[dummy] += 2;
    (start + 10)->start = (start + 11)->end = (start + 8)->start = (start + 9)->end = dummy;

    dummy = ref->end;
    degree[dummy] += 2;
    (start + 12)->start = (start + 13)->end = (start + 14)->start = (start + 15)->end = dummy;

    dummy = a->end;
    degree[dummy] += 2;
    (start + 6)->start = (start + 7)->end = (start + 16)->start = (start + 17)->end = dummy;

    firstedge[nv] = start + 1;
    firstedge[nv + 1] = start;
    firstedge[nv + 2] = start + 2;

    ref->next = start + 10;
    (start + 10)->prev = ref;
    a->next = start + 14;
    (start + 14)->prev = a;
    b->next = start + 6;
    (start + 6)->prev = b;

    ref = ref->invers;
    ref->prev = start + 12;
    (start + 12)->next = ref;
    a = a->invers;
    a->prev = start + 16;
    (start + 16)->next = a;
    b = b->invers;
    b->prev = start + 8;
    (start + 8)->next = b;

    nv += 3;
    ne += 18;
}

/**************************************************************************/

static void
reduce_S(EDGE *ref)

/* This routine is the implementation of the inverse S-operation in
   Batagelj's paper. It removes the triangle. 
*/
{
    register EDGE *a, *b;

    a = ref->invers->prev->prev->prev;
    b = a->invers->prev->prev->prev;

    firstedge[ref->start] = ref;
    degree[ref->start] -= 2;
    firstedge[a->start] = a;
    degree[a->start] -= 2;
    firstedge[b->start] = b;
    degree[b->start] -= 2;

    ref->next = b->invers;
    b->invers->prev = ref;
    a->next = ref->invers;
    ref->invers->prev = a;
    b->next = a->invers;
    a->invers->prev = b;

    nv -= 3;
    ne -= 18;
}

/**************************************************************************/

static void
min4_S_legal(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
             EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* The S-operation with reference edge *ref has just been performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal S-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal S-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those
   being ref.
   *ngood_ref and *ngood_mir_ref might each be 0 or 1.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).

   Hopefully this routine is used rarely, so we are going for simple
   rather than fast.  If the S operation ever becomes a critical part
   of some generation, optimising this routine would be necesary.
*/
{
    EDGE *e, *ee;
    int nor, nmir, i, j;

    RESETMARKS;
    e = ref;

    nor = nmir = 0;
    good_or[nor++] = e;
    good_mir[nmir++] = e->invers;
    MARKLO(e);

    ee = e->invers->prev->prev->prev;
    good_or[nor++] = ee;
    good_mir[nmir++] = ee->invers;
    MARKLO(ee);

    ee = ee->invers->prev->prev->prev;
    good_or[nor++] = ee;
    good_mir[nmir++] = ee->invers;
    MARKLO(ee);

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    for (i = 0; i < nv; ++i)
        if (degree[i] >= 6)
        {
            for (e = firstedge[i], j = degree[i]; --j >= 0; e = e->next)
            {
                if (ISMARKEDLO(e))
                    continue;
                if (degree[e->end] < 6 || degree[e->next->end] != 4 ||
                    degree[e->next->next->end] != 4 ||
                    degree[e->next->next->next->end] < 6)
                    continue;
                if (degree[e->next->invers->next->next->end] != 4)
                    continue;

                good_or[nor++] = e;
                good_mir[nmir++] = e->invers;
                MARKLO(e);

                ee = e->invers->prev->prev->prev;
                good_or[nor++] = ee;
                good_mir[nmir++] = ee->invers;
                MARKLO(ee);

                ee = ee->invers->prev->prev->prev;
                good_or[nor++] = ee;
                good_mir[nmir++] = ee->invers;
                MARKLO(ee);
            }
        }

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/**************************************************************************/

static void
find_extensions_min4_four(int nbtot, EDGE *ext4[], int *next4, EDGE *known)

/* nbtot is the number of automorphisms.  If known!=NULL, it is the
   reference edge of a canonical four-extension just used to make the
   graph.  See min4_four_legal() for important comments about what makes
   a four-extension canonical.  This procedure makes a list in
   ext4[0..*next4-1] of undirected edges whose use in a four-extension
   might possible be canonical.
*/
{
    int deg1, deg2, deg3, dega, degb;
    int i, v, k, kk;
    EDGE *e, *elast, *ez, *ezlim, *e2;
    EDGE **nb, **nb0, **nblim;

    RESETMARKS;
    k = 0;

    if (known)
    {
        deg1 = degree[known->end];
        deg2 = degree[known->next->next->end];
        if (deg1 < deg2)
        {
            i = deg1;
            deg1 = deg2;
            deg2 = i;
            known = known->next->next;
        }

        ez = known->invers;
        ezlim = ez->prev;
        deg3 = 0;
        for (ez = ez->next->next; ez != ezlim; ez = ez->next)
        {
            if (is_min4_four(ez->invers))
            {
                kk = degree[ez->invers->next->next->end];
                if (kk > deg3)
                {
                    deg3 = kk;
                    e2 = ez;
                }
            }
        }

        if (deg3 == 0)
        {
            /* edges around the outside */
            e = known->invers->next;
            ext4[k++] = e;
            MARKLO(e);
            MARKLO(e->invers);
            e = e->invers->next->next;
            ext4[k++] = e;
            MARKLO(e);
            MARKLO(e->invers);
            e = e->invers->next->next;
            ext4[k++] = e;
            MARKLO(e);
            MARKLO(e->invers);
            e = e->invers->next->next;
            ext4[k++] = e;
            MARKLO(e);
            MARKLO(e->invers);

            /* edges in the middle */
            e = known;
            ext4[k++] = e;
            MARKLO(e);
            MARKLO(e->invers);
            e = e->next;
            ext4[k++] = e;
            MARKLO(e);
            MARKLO(e->invers);
            e = e->next;
            if (deg2 == deg1)
            {
                ext4[k++] = e;
                MARKLO(e);
                MARKLO(e->invers);
            }
            e = e->next;
            ext4[k++] = e;
            MARKLO(e);
            MARKLO(e->invers);
        }
        else
        {
            dega = degree[known->prev->end];
            degb = degree[known->next->end];

            /* edges around the outside */
            e = known->invers->next;
            if (dega >= deg3 || e->next == e2)
            {
                ext4[k++] = e;
                MARKLO(e);
                MARKLO(e->invers);
            }

            e = e->invers->next->next;
            if (deg1 == deg2 && dega >= deg3)
            {
                ext4[k++] = e;
                MARKLO(e);
                MARKLO(e->invers);
            }

            e = e->invers->next->next;
            if (deg1 == deg2 && degb >= deg3)
            {
                ext4[k++] = e;
                MARKLO(e);
                MARKLO(e->invers);
            }

            e = e->invers->next->next;
            if (degb >= deg3 || e->invers->prev == e2)
            {
                ext4[k++] = e;
                MARKLO(e);
                MARKLO(e->invers);
            }

            /* edges in the middle */
            e = known;
            if (deg3 == 4)
            {
                ext4[k++] = e;
                MARKLO(e);
                MARKLO(e->invers);
            }

            e = e->next;
            if (degb > deg1 + 1 || (degb == deg1 + 1 && deg3 == 4))
            {
                ext4[k++] = e;
                MARKLO(e);
                MARKLO(e->invers);
            }

            e = e->next;
            if (deg1 == deg2 && deg3 == 4)
            {
                ext4[k++] = e;
                MARKLO(e);
                MARKLO(e->invers);
            }

            e = e->next;
            if (dega > deg1 + 1 || (dega == deg1 + 1 && deg3 == 4))
            {
                ext4[k++] = e;
                MARKLO(e);
                MARKLO(e->invers);
            }
        }
    }
    else
        deg1 = 0;

    for (v = 0; v < nv; ++v)
        if (degree[v] > deg1)
        {
            e = elast = firstedge[v];
            do
            {
                if (!ISMARKEDLO(e))
                {
                    ext4[k++] = e;
                    MARKLO(e);
                    MARKLO(e->invers);
                }
                e = e->next;
            } while (e != elast);
        }
        else if (degree[v] == deg1)
        {
            e = elast = firstedge[v];
            do
            {
                if (!ISMARKEDLO(e) && degree[e->end] >= deg2)
                {
                    ext4[k++] = e;
                    MARKLO(e);
                    MARKLO(e->invers);
                }
                e = e->next;
            } while (e != elast);
        }

    if (nbtot > 1)
    {
        nb0 = (EDGE **)numbering[0];
        nblim = (EDGE **)numbering[nbtot];
        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        kk = 0;
        RESETMARKS;
        for (i = 0; i < k; ++i)
            if (!ISMARKEDLO(ext4[i]))
            {
                ext4[kk++] = ext4[i];
                for (nb = nb0 + ext4[i]->index + MAXE; nb < nblim; nb += MAXE)
                {
                    MARKLO(*nb);
                    MARKLO((*nb)->invers);
                }
            }
        k = kk;
    }

    *next4 = k;
}

/**************************************************************************/

static void
find_extensions_min4(int nbtot, int nbop, EDGE *ext4[], int *next4,
                     EDGE *ext5[], int *next5, EDGE *extS[], int *nextS, EDGE *known)

/* Determine the inequivalent places to make extensions, for the
   ordinary triangulations of minimum degree 4.  The results are
   put in the arrays ext4[0..*next4-1], etc..
   nbtot and nbop are the usual group parameters.

   If known!=NULL, it is the reference edge of a known four-reduction.
*/
{
    register int i, k;
    register EDGE *e, *e1, *elast;
    EDGE **nb, **nb0, **nblim, **nboplim;
    int manycentres;

    find_extensions_min4_four(nbtot, ext4, next4, known);

    manycentres = has_3_four_centres();

    if (nbtot == 1)
    {
        /* five-extensions, trivial group */

        if (manycentres)
            *next5 = 0;
        else if (known)
        {
            k = 0;
            for (i = 0, e = known; i < 4; ++i, e = e->next)
                if (degree[e->end] >= 6)
                {
                    ext5[k++] = e->invers->prev->invers;
                    ext5[k++] = e->invers->next->next->invers;
                }
            *next5 = k;
        }
        else
        {
            k = 0;
            for (i = 0; i < nv; ++i)
                if (degree[i] >= 6)
                {
                    e = elast = firstedge[i];
                    do
                    {
                        ext5[k++] = e->invers;
                        e = e->next;
                    } while (e != elast);
                }
            *next5 = k;
        }

        /* S-extensions, trivial group */

        k = 0;
        if (nv <= maxnv - 3)
        {
            for (i = 0; i < nv; ++i)
            {
                e = elast = firstedge[i];
                do
                {
                    e1 = e->invers->prev;
                    if (e1 > e)
                    {
                        e1 = e1->invers->prev;
                        if (e1 > e)
                            extS[k++] = e;
                    }
                    e = e->next;
                } while (e != elast);
            }
        }
        *nextS = k;
    }
    else
    {
        /* five-extensions, non-trivial group */

        if (manycentres)
            *next5 = 0;
        else
        {
            nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];
            nblim = (EDGE **)numbering[nbtot];

            RESETMARKS;
            k = 0;
            nb0 = (EDGE **)numbering[0];
            for (i = 0; i < ne; ++i, ++nb0)
            {
                e = *nb0;
                if (!ISMARKEDLO(e) && degree[e->start] >= 6)
                {
                    ext5[k++] = e->next->invers;

                    nb = nb0 + MAXE;
                    for (; nb < nboplim; nb += MAXE)
                        MARKLO(*nb);
                    for (; nb < nblim; nb += MAXE)
                        MARKLO((*nb)->prev);
                }
            }
            *next5 = k;
        }

        /* S-extensions, non-trivial group */

        k = 0;
        if (nv <= maxnv - 3)
        {
            nb0 = (EDGE **)numbering[0];
            nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];
            nblim = (EDGE **)numbering[nbtot];
            RESETMARKS;

            for (i = 0; i < ne; ++i)
                nb0[i]->index = i;

            for (i = 0; i < ne; ++i)
            {
                e = nb0[i];
                if (ISMARKEDLO(e))
                    continue;
                extS[k++] = e;

                for (nb = nb0 + i; nb < nboplim; nb += MAXE)
                    MARKLO(*nb);

                for (; nb < nblim; nb += MAXE)
                    MARKLO((*nb)->invers);

                e1 = e->invers->prev;
                for (nb = nb0 + e1->index; nb < nboplim; nb += MAXE)
                    MARKLO(*nb);

                for (; nb < nblim; nb += MAXE)
                    MARKLO((*nb)->invers);

                e1 = e1->invers->prev;
                for (nb = nb0 + e1->index; nb < nboplim; nb += MAXE)
                    MARKLO(*nb);

                for (; nb < nblim; nb += MAXE)
                    MARKLO((*nb)->invers);
            }
        }
        *nextS = k;
    }
}

/**************************************************************************/

static void
update_nft_four(triangle nft[], int numnft, EDGE *ref,
                triangle newnft[], int *newnumnft)

/* Make new list of non-facial triangles after a four-extension. */
{
    EDGE *refmin, *e, *elast;
    int i, k, w;

    refmin = ref->min;

    /* Remove triangles that include ref */
    k = 0;
    for (i = 0; i < numnft; ++i)
        if (nft[i].e1 != refmin && nft[i].e2 != refmin && nft[i].e3 != refmin)
            newnft[k++] = nft[i];

    /* Add a shortcut if there is one (only possible if there are >= 2 others) */
    if (k >= 2)
    {
        w = ref->next->end;
        elast = ref->invers->next->invers;
        for (e = elast->next->next->next; e != elast; e = e->next)
            if (e->end == w)
                break;
        if (e != elast)
        {
            newnft[k].e1 = e->min;
            newnft[k].e2 = ref->prev->min;
            newnft[k].e3 = ref->next->min;
            ++k;
        }
    }
    *newnumnft = k;
}

/**************************************************************************/

static void
update_nft_five(triangle nft[], int numnft, EDGE *ref,
                triangle newnft[], int *newnumnft)

/* Make new list of non-facial triangles after a five-extension. */
{
    EDGE *refmin, *amin, *e, *elast, *ee;
    int i, k, w, j;

    refmin = ref->min;
    amin = ref->next->next->min;

    /* Remove triangles that include either of the former two chords */
    k = 0;
    for (i = 0; i < numnft; ++i)
        if (nft[i].e1 != refmin && nft[i].e2 != refmin && nft[i].e3 != refmin && nft[i].e1 != amin && nft[i].e2 != amin && nft[i].e3 != amin)
            newnft[k++] = nft[i];

    /* Add a shortcut if there is one (only possible if there is another) */

    if (k == 0)
    {
        *newnumnft = 0;
        return;
    }

    for (ee = ref->prev->prev, j = 0; j < 3; ee = ee->next->next, ++j)
    {
        w = ee->next->end;
        elast = ee->invers->next->invers;
        for (e = elast->next->next->next; e != elast; e = e->next)
            if (e->end == w)
                break;
        if (e != elast)
        {
            newnft[k].e1 = e->min;
            newnft[k].e2 = ee->prev->min;
            newnft[k].e3 = ee->next->min;
            ++k;
        }
    }
    *newnumnft = k;
}

/**************************************************************************/

static void
nftlaststep(EDGE *ext4[], int *next4, EDGE *ext5[], int *next5,
            triangle nft[], int numnft)

/* Remove from ext4[0..*next4-1] and ext5[0..*next5-1] those extensions
   for which not all of nft[0..numnft-1] hit some chord. */
{
    int i, j, k;

    for (j = 0; j < numnft; ++j)
    {
        RESETMARKS;
        MARKLO(nft[j].e1);
        MARKLO(nft[j].e1->invers);
        MARKLO(nft[j].e2);
        MARKLO(nft[j].e2->invers);
        MARKLO(nft[j].e3);
        MARKLO(nft[j].e3->invers);

        k = 0;
        for (i = 0; i < *next4; ++i)
            if (ISMARKEDLO(ext4[i]))
                ext4[k++] = ext4[i];
        *next4 = k;

        k = 0;
        for (i = 0; i < *next5; ++i)
            if (ISMARKEDLO(ext5[i]) || ISMARKEDLO(ext5[i]->invers->prev))
                ext5[k++] = ext5[i];
        *next5 = k;
    }
}

/**************************************************************************/

static void
scanmin4c(int nbtot, int nbop, int dosplit, EDGE *lastfour,
          triangle nft[], int numnft)

/* The main node of the recursion for triangulations with minimum
   degree at least 4.  This is the version keeping track of all the
   non-facial triangles.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   If dosplit==TRUE, this is the place to do splitting (if any).
   Splitting is a bit more complicated because the S operation adds
   three vertices.
   If this graph was made with a four-operation, the reference edge of
   that operation is lastfour.  If not, lastfour=NULL.
   nft[0..numnft-1] is a list of all the non-facial triangles.
   Edges in the triangles must be in min form.
*/
{
    EDGE *firstedge_save[MAXN];
    EDGE *ext4[MAXE / 2], *ext5[MAXE], *extS[MAXF];
    EDGE *good_or[MAXE], *good_mir[MAXE], *e;
    triangle newnft[MAXN];
    int newnumnft;
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int next4, next5, nextS, i;
    int xnbtot, xnbop;
    int hint;

    if (nv == maxnv)
    {
        if (numnft == 0)
        {
            if (pswitch)
                startpolyscan(nbtot, nbop);
            else
                got_one(nbtot, nbop, 3 + (numnft == 0));
        }
        return;
    }

    if (dosplit)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_MIN4
    if (!(PRE_FILTER_MIN4))
        return;
#endif

#ifndef FIND_EXTENSIONS_MIN4
#define FIND_EXTENSIONS_MIN4 find_extensions_min4
#endif

    FIND_EXTENSIONS_MIN4(nbtot, nbop, ext4, &next4, ext5, &next5, extS, &nextS,
                         lastfour);

    if (nv == maxnv - 1 && numnft > 0 && minconnec == 4)
        nftlaststep(ext4, &next4, ext5, &next5, nft, numnft);

    for (i = 0; i < next4; ++i)
    {
        extend_four(ext4[i]);
#ifdef FAST_FILTER_MIN4
        if (FAST_FILTER_MIN4)
#endif
        {
            min4_four_legal(ext4[i], good_or, &ngood_or, &ngood_ref,
                            good_mir, &ngood_mir, &ngood_mir_ref);

            if (ngood_ref + ngood_mir_ref > 0)
            {
                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref)
                {
                    update_nft_four(nft, numnft, ext4[i], newnft, &newnumnft);
                    got_one(1, 1, 3 + (newnumnft == 0));
                }
                else if (ngood_or + ngood_mir == 1)
                {
                    update_nft_four(nft, numnft, ext4[i], newnft, &newnumnft);
                    scanmin4c(1, 1, nv == splitlevel, ext4[i], newnft, newnumnft);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    update_nft_four(nft, numnft, ext4[i], newnft, &newnumnft);
                    scanmin4c(xnbtot, xnbop, nv == splitlevel, ext4[i],
                              newnft, newnumnft);
                }
            }
        }
        reduce_four(ext4[i]);
    }

    hint = -1;
    for (i = 0; i < next5; ++i)
    {
        extend_five(ext5[i]);
#ifdef FAST_FILTER_MIN4
        if (FAST_FILTER_MIN4)
#endif
        {
            if (hint < 0 || !is_min4_four_centre(hint))
                hint = min4_four_centre();
            if (hint < 0)
            {
                min4_five_legal(ext5[i], good_or, &ngood_or, &ngood_ref,
                                good_mir, &ngood_mir, &ngood_mir_ref);
                if (ngood_ref + ngood_mir_ref > 0)
                {
                    if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                            good_mir, ngood_mir, ngood_mir_ref,
                                            degree, numbering, &xnbtot, &xnbop))
                    {
                        update_nft_five(nft, numnft, ext5[i], newnft, &newnumnft);
                        scanmin4c(xnbtot, xnbop, nv == splitlevel, NULL,
                                  newnft, newnumnft);
                    }
                }
            }
        }
        reduce_five(ext5[i]);
    }

    for (i = 0; i < nextS; ++i)
    {
        extend_S(extS[i]);
#ifdef FAST_FILTER_MIN4
        if (FAST_FILTER_MIN4)
#endif
        {
            if (degree5_vertex() < 0 && min4_four_centre() < 0)
            {
                min4_S_legal(extS[i], good_or, &ngood_or, &ngood_ref,
                             good_mir, &ngood_mir, &ngood_mir_ref);
                if (ngood_ref + ngood_mir_ref > 0)
                {
                    if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                            good_mir, ngood_mir, ngood_mir_ref,
                                            zero, numbering, &xnbtot, &xnbop))
                    {
                        e = extS[i];
                        nft[numnft].e1 = e->min;
                        e = e->invers->prev->prev->prev;
                        nft[numnft].e2 = e->min;
                        e = e->invers->prev->prev->prev;
                        nft[numnft].e3 = e->min;
                        scanmin4c(xnbtot, xnbop,
                                  nv >= splitlevel && nv <= splitlevel + 2, NULL, nft, numnft + 1);
                    }
                }
            }
        }
        reduce_S(extS[i]);
    }

    if (dosplit)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/**************************************************************************/

static void
scanmin4(int nbtot, int nbop, int dosplit, EDGE *lastfour)

/* The main node of the recursion for triangulations with minimum
   degree at least 4.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   If dosplit==TRUE, this is the place to do splitting (if any).
   Splitting is a bit more complicated because the S operation adds
   three vertices.
   If this graph was made with a four-operation, the reference edge of
   that operation is lastfour.  If not, lastfour=NULL.
*/
{
    EDGE *firstedge_save[MAXN];
    EDGE *ext4[MAXE / 2], *ext5[MAXE], *extS[MAXF];
    EDGE *good_or[MAXE], *good_mir[MAXE];
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int next4, next5, nextS, i;
    int xnbtot, xnbop;
    int hint;

    if (nv == maxnv)
    {
        if (pswitch)
            startpolyscan(nbtot, nbop);
        else
            got_one(nbtot, nbop, 3);
        return;
    }

    if (dosplit)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_MIN4
    if (!(PRE_FILTER_MIN4))
        return;
#endif

#ifndef FIND_EXTENSIONS_MIN4
#define FIND_EXTENSIONS_MIN4 find_extensions_min4
#endif

    FIND_EXTENSIONS_MIN4(nbtot, nbop, ext4, &next4, ext5, &next5, extS, &nextS,
                         lastfour);

    for (i = 0; i < next4; ++i)
    {
        extend_four(ext4[i]);
#ifdef FAST_FILTER_MIN4
        if (FAST_FILTER_MIN4)
#endif
        {
            min4_four_legal(ext4[i], good_or, &ngood_or, &ngood_ref,
                            good_mir, &ngood_mir, &ngood_mir_ref);

            if (ngood_ref + ngood_mir_ref > 0)
            {
                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref)
                    got_one(1, 1, 3);
                else if (ngood_or + ngood_mir == 1)
                    scanmin4(1, 1, nv == splitlevel, ext4[i]);
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                    scanmin4(xnbtot, xnbop, nv == splitlevel, ext4[i]);
            }
        }
        reduce_four(ext4[i]);
    }

    /* hint = lastfour ? lastfour->start : -1; */
    hint = -1;
    for (i = 0; i < next5; ++i)
    {
        extend_five(ext5[i]);
#ifdef FAST_FILTER_MIN4
        if (FAST_FILTER_MIN4)
#endif
        {
            if (hint < 0 || !is_min4_four_centre(hint))
                hint = min4_four_centre();
            if (hint < 0)
            {
                min4_five_legal(ext5[i], good_or, &ngood_or, &ngood_ref,
                                good_mir, &ngood_mir, &ngood_mir_ref);
                if (ngood_ref + ngood_mir_ref > 0)
                {
                    if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                            good_mir, ngood_mir, ngood_mir_ref,
                                            degree, numbering, &xnbtot, &xnbop))
                        scanmin4(xnbtot, xnbop, nv == splitlevel, NULL);
                }
            }
        }
        reduce_five(ext5[i]);
    }

    for (i = 0; i < nextS; ++i)
    {
        extend_S(extS[i]);
#ifdef FAST_FILTER_MIN4
        if (FAST_FILTER_MIN4)
#endif
        {
            if (degree5_vertex() < 0 && min4_four_centre() < 0)
            {
                min4_S_legal(extS[i], good_or, &ngood_or, &ngood_ref,
                             good_mir, &ngood_mir, &ngood_mir_ref);
                if (ngood_ref + ngood_mir_ref > 0)
                {
                    if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                            good_mir, ngood_mir, ngood_mir_ref,
                                            zero, numbering, &xnbtot, &xnbop))
                        scanmin4(xnbtot, xnbop,
                                 nv >= splitlevel && nv <= splitlevel + 2, NULL);
                }
            }
        }
        reduce_S(extS[i]);
    }

    if (dosplit)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/**************************************************************************/

static EDGE *
extend_min5_a(EDGE *e1, EDGE *e2)

/* extends a graph in the way given by the type a extension for
   5-connected triangulations. The edges e1, e2 start at the same
   vertex and must have at least two edges on each of their sides. 

   It returns the edge characterizing this operation.
*/

{
    register EDGE *e3, *e4, *start, *run, *e1i, *e2i, *work1, *work2;
    int end1, end2, center, counter;

    e3 = e1->next;
    e4 = e2->prev;
    e1i = e1->invers;
    e2i = e2->invers;
    work1 = e1i->prev;
    work2 = e2i->next;
    center = e1->start;
    end1 = e1->end;
    end2 = e2->end;

    start = min5_a(nv);
    firstedge[center] = start + 2;
    firstedge[nv] = start + 1;

    counter = 1;
    run = e3;
    run->start = run->invers->end = nv;
    do
    {
        run = run->next;
        run->start = run->invers->end = nv;
        counter++;
    } while (run != e4);

    degree[nv] = counter + 3;
    degree[center] -= (counter - 1);

    start->start = end1;
    start->prev = work1;
    start->next = e1i;
    work1->next = e1i->prev = start;
    (degree[end1])++;

    run = start + 1;
    run->end = end1;
    run->next = e3;
    e3->prev = run;

    run++; /*start+2*/
    run->start = center;
    run->next = e2;
    run->prev = e1;
    e1->next = e2->prev = run;

    run++; /*start+3*/
    run->end = center;

    run++; /*start+4*/
    run->start = end2;
    run->prev = e2i;
    run->next = work2;
    e2i->next = work2->prev = run;
    (degree[end2])++;

    run++; /*start+5*/
    run->end = end2;
    run->prev = e4;
    e4->next = run;

    nv++;
    ne += 6;

    return (start + 2); /* It is the minimum of the two inverse edges */
}

/**************************************************************************/

static void
reduce_min5_a(EDGE *e)

/* reduces the graph previously extended by the type a extension for
   5-connected triangulations if the edge returned by the function is
   given as a parameter.
*/

{
    register EDGE *e1, *e2, *e3, *e4, *e1i, *e2i, *work1, *work2, *run;
    int end1, end2, center, counter;

    e1 = e->prev;
    e2 = e->next;
    e1i = e1->invers;
    e2i = e2->invers;
    work1 = e1i->prev->prev;
    work2 = e2i->next->next;

    e = e->invers;
    e3 = e->next->next;
    e4 = e->prev->prev;
    center = e1->start;
    end1 = e1->end;
    end2 = e2->end;

    firstedge[center] = e1;
    firstedge[end1] = e1i;
    firstedge[end2] = e2i;

    counter = 1;
    run = e3;
    run->start = run->invers->end = center;
    do
    {
        run = run->next;
        run->start = run->invers->end = center;
        counter++;
    } while (run != e4);

    degree[center] += (counter - 1);
    degree[end1]--;
    degree[end2]--;

    e1->next = e3;
    e3->prev = e1;
    e2->prev = e4;
    e4->next = e2;

    e1i->prev = work1;
    work1->next = e1i;
    e2i->next = work2;
    work2->prev = e2i;

    nv--;
    ne -= 6;
}

/**************************************************************************/

static EDGE *
extend_min5_b(EDGE *e, int do_mirror)

/* extends a graph in the way given by the type b extension for
   5-connected triangulations. The edge e must start and end at
   a vertex of degree 5.

   It returns the edge characterizing this operation.

*/

{

    EDGE *ei, *e2, *e2i, *e3, *e3i, *e4, *e5i;
    EDGE *start, *run, *work1, *work2, *work3;
    int end2, center1, center2, start3;

    if (!do_mirror)
    {
        ei = e->invers;
        work2 = e->next;
        work3 = work2->next;
        e3i = work3->next;
        e3 = e3i->invers;
        e5i = e3->next;
        work1 = ei->prev;
        e2 = work1->prev;
        e2i = e2->invers;
        e4 = e2i->prev;

        center1 = e->end;
        center2 = e->start;
        start3 = e3->start;
        end2 = e2->end;

        start = min5_b0(nv);

        work1->start = work1->invers->end = nv;
        firstedge[nv] = work1;
        degree[nv] = 5;

        work2->start = work2->invers->end = work3->start = work3->invers->end = nv + 1;
        firstedge[nv + 1] = work2;
        degree[nv + 1] = 5;

        firstedge[center1] = ei;
        firstedge[center2] = e;

        /* The degree at center1 and center2 remains unchanged */

        start->start = end2;
        start->prev = e4;
        e4->next = start;
        start->next = e2i;
        e2i->prev = start;
        (degree[end2])++;

        run = start + 1;
        run->end = end2;
        run->next = work1;
        work1->prev = run;

        run++; /*2*/
        run->start = (run + 1)->end = center1;
        run->prev = e2;
        e2->next = run;
        run->next = ei;
        ei->prev = run;

        run += 2; /*4*/
        run->start = (run + 1)->end = center2;
        run->prev = e;
        e->next = run;

        run += 2; /*6*/
        run->next = work2;
        work2->prev = run;

        run++; /*7*/
        run->prev = work1;
        work1->next = run;

        run++; /*8*/
        run->start = (run + 1)->end = center2;
        run->next = e3i;
        e3i->prev = run;

        run += 2; /*10*/
        run->start = start3;
        run->next = e5i;
        e5i->prev = run;
        run->prev = e3;
        e3->next = run;

        run++; /*11*/
        run->end = start3;
        run->prev = work3;
        work3->next = run;
        degree[start3]++;

        nv += 2;
        ne += 12;

        return (start + 4); /* is the smaller one */
    }

    else /* do_mirror=1*/
    {
        ei = e->invers;
        work2 = e->prev;
        work3 = work2->prev;
        e3i = work3->prev;
        e3 = e3i->invers;
        e5i = e3->prev;
        work1 = ei->next;
        e2 = work1->next;
        e2i = e2->invers;
        e4 = e2i->next;

        center1 = e->end;
        center2 = e->start;
        start3 = e3->start;
        end2 = e2->end;

        start = min5_b1(nv);

        work1->start = work1->invers->end = nv;
        firstedge[nv] = work1;
        degree[nv] = 5;

        work2->start = work2->invers->end = work3->start = work3->invers->end = nv + 1;
        firstedge[nv + 1] = work2;
        degree[nv + 1] = 5;

        firstedge[center1] = ei;
        firstedge[center2] = e;

        /* The degree at center1 and center2 remains unchanged */

        start->start = end2;
        start->next = e4;
        e4->prev = start;
        start->prev = e2i;
        e2i->next = start;
        (degree[end2])++;

        run = start + 1;
        run->end = end2;
        run->prev = work1;
        work1->next = run;

        run++; /*2*/
        run->start = (run + 1)->end = center1;
        run->next = e2;
        e2->prev = run;
        run->prev = ei;
        ei->next = run;

        run += 2; /*4*/
        run->start = (run + 1)->end = center2;
        run->next = e;
        e->prev = run;

        run += 2; /*6*/
        run->prev = work2;
        work2->next = run;

        run++; /*7*/
        run->next = work1;
        work1->prev = run;

        run++; /*8*/
        run->start = (run + 1)->end = center2;
        run->prev = e3i;
        e3i->next = run;

        run += 2; /*10*/
        run->start = start3;
        run->prev = e5i;
        e5i->next = run;
        run->next = e3;
        e3->prev = run;

        run++; /*11*/
        run->end = start3;
        run->next = work3;
        work3->prev = run;
        degree[start3]++;

        nv += 2;
        ne += 12;

        return (start + 4); /* is the smaller one */
    }
}

/**************************************************************************/

static void
reduce_min5_b(EDGE *ref, int do_mirror)

{
    EDGE *e, *ei, *e2, *e2i, *e4, *work1, *work2, *work3, *e3, *e3i, *e5i;
    int center1, center2, end2, start3;

    if (!do_mirror)
    {
        e = ref->prev;
        ei = e->invers;
        e2 = ei->prev->prev;
        e2i = e2->invers;
        e4 = e2i->prev->prev;
        work1 = e4->next->invers->next;
        e3i = e->prev->prev;
        e3 = e3i->invers;
        e5i = e3->next->next;
        work3 = e5i->prev->invers->prev;
        work2 = work3->prev;

        end2 = e2->end;
        center1 = e->end;
        center2 = e->start;
        start3 = e3->start;

        degree[end2]--;
        degree[start3]--;

        firstedge[end2] = e4;
        firstedge[center1] = ei;
        firstedge[center2] = e;
        firstedge[start3] = e3;

        e4->next = e2i;
        e2i->prev = e4;
        e2->next = work1;
        work1->prev = e2;
        ei->prev = work1;
        work1->next = ei;
        e->next = work2;
        work2->prev = e;
        e3i->prev = work3;
        work3->next = e3i;
        e3->next = e5i;
        e5i->prev = e3;

        work1->start = work1->invers->end = center1;
        work2->start = work2->invers->end = work3->start = work3->invers->end = center2;

        nv -= 2;
        ne -= 12;
    }

    else
    {
        e = ref->next;
        ei = e->invers;
        e2 = ei->next->next;
        e2i = e2->invers;
        e4 = e2i->next->next;
        work1 = e4->prev->invers->prev;
        e3i = e->next->next;
        e3 = e3i->invers;
        e5i = e3->prev->prev;
        work3 = e5i->next->invers->next;
        work2 = work3->next;

        end2 = e2->end;
        center1 = e->end;
        center2 = e->start;
        start3 = e3->start;

        degree[end2]--;
        degree[start3]--;

        firstedge[end2] = e4;
        firstedge[center1] = ei;
        firstedge[center2] = e;
        firstedge[start3] = e3;

        e4->prev = e2i;
        e2i->next = e4;
        e2->prev = work1;
        work1->next = e2;
        ei->next = work1;
        work1->prev = ei;
        e->prev = work2;
        work2->next = e;
        e3i->next = work3;
        work3->prev = e3i;
        e3->prev = e5i;
        e5i->next = e3;

        work1->start = work1->invers->end = center1;
        work2->start = work2->invers->end = work3->start = work3->invers->end = center2;

        nv -= 2;
        ne -= 12;
    }
}

/**************************************************************************/

static void
make_icosahedron(void)

/* Make an icosahedron using the first 60 edges */
{
    int i;
    EDGE *buffer;

    for (i = 0; i <= 11; i++)
    {
        buffer = edges + 5 * i;
        firstedge[i] = buffer;
        degree[i] = 5;
        buffer->next = buffer + 1;
        buffer->prev = buffer + 4;
        buffer->start = i;
        buffer++;
        buffer->next = buffer + 1;
        buffer->prev = buffer - 1;
        buffer->start = i;
        buffer++;
        buffer->next = buffer + 1;
        buffer->prev = buffer - 1;
        buffer->start = i;
        buffer++;
        buffer->next = buffer + 1;
        buffer->prev = buffer - 1;
        buffer->start = i;
        buffer++;
        buffer->next = buffer - 4;
        buffer->prev = buffer - 1;
        buffer->start = i;
    }

    buffer = edges; /* edge number 0 */
    buffer->end = 1;
    buffer->invers = edges + 5;
    buffer->min = buffer;

    buffer++; /* edge number 1 */
    buffer->end = 2;
    buffer->invers = edges + 10;
    buffer->min = buffer;

    buffer++; /* edge number 2 */
    buffer->end = 3;
    buffer->invers = edges + 15;
    buffer->min = buffer;

    buffer++; /* edge number 3 */
    buffer->end = 4;
    buffer->invers = edges + 20;
    buffer->min = buffer;

    buffer++; /* edge number 4 */
    buffer->end = 5;
    buffer->invers = edges + 25;
    buffer->min = buffer;

    buffer++; /* edge number 5 */
    buffer->end = 0;
    buffer->invers = edges;
    buffer->min = buffer->invers;

    buffer++; /* edge number 6 */
    buffer->end = 5;
    buffer->invers = edges + 29;
    buffer->min = buffer;

    buffer++; /* edge number 7 */
    buffer->end = 6;
    buffer->invers = edges + 30;
    buffer->min = buffer;

    buffer++; /* edge number 8 */
    buffer->end = 7;
    buffer->invers = edges + 35;
    buffer->min = buffer;

    buffer++; /* edge number 9 */
    buffer->end = 2;
    buffer->invers = edges + 11;
    buffer->min = buffer;

    buffer++; /* edge number 10 */
    buffer->end = 0;
    buffer->invers = edges + 1;
    buffer->min = buffer->invers;

    buffer++; /* edge number 11 */
    buffer->end = 1;
    buffer->invers = edges + 9;
    buffer->min = buffer->invers;

    buffer++; /* edge number 12 */
    buffer->end = 7;
    buffer->invers = edges + 39;
    buffer->min = buffer;

    buffer++; /* edge number 13 */
    buffer->end = 8;
    buffer->invers = edges + 40;
    buffer->min = buffer;

    buffer++; /* edge number 14 */
    buffer->end = 3;
    buffer->invers = edges + 16;
    buffer->min = buffer;

    buffer++; /* edge number 15 */
    buffer->end = 0;
    buffer->invers = edges + 2;
    buffer->min = buffer->invers;

    buffer++; /* edge number 16 */
    buffer->end = 2;
    buffer->invers = edges + 14;
    buffer->min = buffer->invers;

    buffer++; /* edge number 17 */
    buffer->end = 8;
    buffer->invers = edges + 44;
    buffer->min = buffer;

    buffer++; /* edge number 18 */
    buffer->end = 9;
    buffer->invers = edges + 45;
    buffer->min = buffer;

    buffer++; /* edge number 19  */
    buffer->end = 4;
    buffer->invers = edges + 21;
    buffer->min = buffer;

    buffer++; /* edge number 20 */
    buffer->end = 0;
    buffer->invers = edges + 3;
    buffer->min = buffer->invers;

    buffer++; /* edge number 21 */
    buffer->end = 3;
    buffer->invers = edges + 19;
    buffer->min = buffer->invers;

    buffer++; /* edge number 22 */
    buffer->end = 9;
    buffer->invers = edges + 49;
    buffer->min = buffer;

    buffer++; /* edge number 23 */
    buffer->end = 10;
    buffer->invers = edges + 50;
    buffer->min = buffer;

    buffer++; /* edge number 24 */
    buffer->end = 5;
    buffer->invers = edges + 26;
    buffer->min = buffer;

    buffer++; /* edge number 25 */
    buffer->end = 0;
    buffer->invers = edges + 4;
    buffer->min = buffer->invers;

    buffer++; /* edge number 26 */
    buffer->end = 4;
    buffer->invers = edges + 24;
    buffer->min = buffer->invers;

    buffer++; /* edge number 27 */
    buffer->end = 10;
    buffer->invers = edges + 54;
    buffer->min = buffer;

    buffer++; /* edge number 28 */
    buffer->end = 6;
    buffer->invers = edges + 31;
    buffer->min = buffer;

    buffer++; /* edge number 29  */
    buffer->end = 1;
    buffer->invers = edges + 6;
    buffer->min = buffer->invers;

    buffer++; /* edge number 30 */
    buffer->end = 1;
    buffer->invers = edges + 7;
    buffer->min = buffer->invers;

    buffer++; /* edge number 31 */
    buffer->end = 5;
    buffer->invers = edges + 28;
    buffer->min = buffer->invers;

    buffer++; /* edge number 32 */
    buffer->end = 10;
    buffer->invers = edges + 53;
    buffer->min = buffer;

    buffer++; /* edge number 33 */
    buffer->end = 11;
    buffer->invers = edges + 55;
    buffer->min = buffer;

    buffer++; /* edge number 34 */
    buffer->end = 7;
    buffer->invers = edges + 36;
    buffer->min = buffer;

    buffer++; /* edge number 35 */
    buffer->end = 1;
    buffer->invers = edges + 8;
    buffer->min = buffer->invers;

    buffer++; /* edge number 36 */
    buffer->end = 6;
    buffer->invers = edges + 34;
    buffer->min = buffer->invers;

    buffer++; /* edge number 37 */
    buffer->end = 11;
    buffer->invers = edges + 59;
    buffer->min = buffer;

    buffer++; /* edge number 38 */
    buffer->end = 8;
    buffer->invers = edges + 41;
    buffer->min = buffer;

    buffer++; /* edge number 39  */
    buffer->end = 2;
    buffer->invers = edges + 12;
    buffer->min = buffer->invers;

    buffer++; /* edge number 40 */
    buffer->end = 2;
    buffer->invers = edges + 13;
    buffer->min = buffer->invers;

    buffer++; /* edge number 41 */
    buffer->end = 7;
    buffer->invers = edges + 38;
    buffer->min = buffer->invers;

    buffer++; /* edge number 42 */
    buffer->end = 11;
    buffer->invers = edges + 58;
    buffer->min = buffer;

    buffer++; /* edge number 43 */
    buffer->end = 9;
    buffer->invers = edges + 46;
    buffer->min = buffer;

    buffer++; /* edge number 44 */
    buffer->end = 3;
    buffer->invers = edges + 17;
    buffer->min = buffer->invers;

    buffer++; /* edge number 45 */
    buffer->end = 3;
    buffer->invers = edges + 18;
    buffer->min = buffer->invers;

    buffer++; /* edge number 46 */
    buffer->end = 8;
    buffer->invers = edges + 43;
    buffer->min = buffer->invers;

    buffer++; /* edge number 47 */
    buffer->end = 11;
    buffer->invers = edges + 57;
    buffer->min = buffer;

    buffer++; /* edge number 48 */
    buffer->end = 10;
    buffer->invers = edges + 51;
    buffer->min = buffer;

    buffer++; /* edge number 49  */
    buffer->end = 4;
    buffer->invers = edges + 22;
    buffer->min = buffer->invers;

    buffer++; /* edge number 50 */
    buffer->end = 4;
    buffer->invers = edges + 23;
    buffer->min = buffer->invers;

    buffer++; /* edge number 51 */
    buffer->end = 9;
    buffer->invers = edges + 48;
    buffer->min = buffer->invers;

    buffer++; /* edge number 52 */
    buffer->end = 11;
    buffer->invers = edges + 56;
    buffer->min = buffer;

    buffer++; /* edge number 53 */
    buffer->end = 6;
    buffer->invers = edges + 32;
    buffer->min = buffer->invers;

    buffer++; /* edge number 54 */
    buffer->end = 5;
    buffer->invers = edges + 27;
    buffer->min = buffer->invers;

    buffer++; /* edge number 55 */
    buffer->end = 6;
    buffer->invers = edges + 33;
    buffer->min = buffer->invers;

    buffer++; /* edge number 56 */
    buffer->end = 10;
    buffer->invers = edges + 52;
    buffer->min = buffer->invers;

    buffer++; /* edge number 57 */
    buffer->end = 9;
    buffer->invers = edges + 47;
    buffer->min = buffer->invers;

    buffer++; /* edge number 58 */
    buffer->end = 8;
    buffer->invers = edges + 42;
    buffer->min = buffer->invers;

    buffer++; /* edge number 59  */
    buffer->end = 7;
    buffer->invers = edges + 37;
    buffer->min = buffer->invers;

    nv = 12;
    ne = 60;
}

/**************************************************************************/

static void
initialize_min5(void)

/* initialize edges for minimum degree 5 generation, and make the
   inital icosahedron */
{
    EDGE *run, *start;
    int n, i;

    /* First initialize the edges for operation a.). They look like

       a
    \ / \ /
    ?b---c?   Vertex c is the new point. (a,c),(b,c) and (d,c) are the
    / \ / \   new edges with a-->c taken as min5_a(n) 
       d

a,b and d will be from the old graph -- they cannot be initialised so far.
It is assumed that for 12<=n<MAXN after min5_a(n) there is room for 6 edges.
*/

    for (n = 12; n < MAXN; n++)
    {
        run = start = min5_a(n);
        run->end = n;
        run->min = run;
        run->invers = start + 1;

        run = start + 1;
        run->start = n;
        run->min = run->invers = start;
        run->prev = start + 3;

        run = start + 2;
        run->end = n;
        run->min = run;
        run->invers = start + 3;

        run = start + 3;
        run->start = n;
        run->min = run->invers = start + 2;
        run->next = start + 1;
        run->prev = start + 5;

        run = start + 4;
        run->end = n;
        run->min = run;
        run->invers = start + 5;

        run = start + 5;
        run->start = n;
        run->min = run->invers = start + 4;
        run->next = start + 3;
    }

    /* The edges for operation b.) look like


        a
     \ / \
      b---e-
     /|  /|      The new vertices are e,f, the new edges (a,e),(b,e)(c,e),
      | / |      (c,f),(d,f)(e,f) with a-->e taken as min5_b0(n)
      |/  |/
     -c---f
       \ / \
        d

It is assumed that after min5_b(n) there is room for 12 edges.
*/

    for (n = 12; n < MAXN - 1; n++)
    {
        run = start = min5_b0(n);
        run->end = n;
        run->min = run;
        run->invers = start + 1;

        run = start + 1;
        run->start = n;
        run->min = run->invers = start;
        run->prev = start + 3;

        run = start + 2;
        run->end = n;
        run->min = run;
        run->invers = start + 3;

        run = start + 3;
        run->start = n;
        run->min = run->invers = start + 2;
        run->prev = start + 5;
        run->next = start + 1;

        run = start + 4;
        run->end = n;
        run->min = run;
        run->invers = start + 5;
        run->next = start + 8;

        run = start + 5;
        run->start = n;
        run->min = run->invers = start + 4;
        run->prev = start + 7;
        run->next = start + 3;

        run = start + 6;
        run->start = n + 1;
        run->end = n;
        run->min = run;
        run->invers = start + 7;
        run->prev = start + 9;

        run = start + 7;
        run->start = n;
        run->end = n + 1;
        run->min = run->invers = start + 6;
        run->next = start + 5;

        run = start + 8;
        run->end = n + 1;
        run->min = run;
        run->invers = start + 9;
        run->prev = start + 4;

        run = start + 9;
        run->start = n + 1;
        run->min = run->invers = start + 8;
        run->prev = start + 11;
        run->next = start + 6;

        run = start + 10;
        run->end = n + 1;
        run->min = run;
        run->invers = start + 11;

        run = start + 11;
        run->start = n + 1;
        run->min = run->invers = start + 10;
        run->next = start + 9;
    }

    /* The mirror image operation */

    for (n = 12; n < MAXN - 1; n++)
    {
        run = start = min5_b1(n);
        run->end = n;
        run->min = run;
        run->invers = start + 1;

        run = start + 1;
        run->start = n;
        run->min = run->invers = start;
        run->next = start + 3;

        run = start + 2;
        run->end = n;
        run->min = run;
        run->invers = start + 3;

        run = start + 3;
        run->start = n;
        run->min = run->invers = start + 2;
        run->next = start + 5;
        run->prev = start + 1;

        run = start + 4;
        run->end = n;
        run->min = run;
        run->invers = start + 5;
        run->prev = start + 8;

        run = start + 5;
        run->start = n;
        run->min = run->invers = start + 4;
        run->next = start + 7;
        run->prev = start + 3;

        run = start + 6;
        run->start = n + 1;
        run->end = n;
        run->min = run;
        run->invers = start + 7;
        run->next = start + 9;

        run = start + 7;
        run->start = n;
        run->end = n + 1;
        run->min = run->invers = start + 6;
        run->prev = start + 5;

        run = start + 8;
        run->end = n + 1;
        run->min = run;
        run->invers = start + 9;
        run->next = start + 4;

        run = start + 9;
        run->start = n + 1;
        run->min = run->invers = start + 8;
        run->next = start + 11;
        run->prev = start + 6;

        run = start + 10;
        run->end = n + 1;
        run->min = run;
        run->invers = start + 11;

        run = start + 11;
        run->start = n + 1;
        run->min = run->invers = start + 10;
        run->prev = start + 9;
    }

    /* The last operation is c.) It is much too hard too "draw" this way.
   The new part that has to be inserted is a vertex of valency 5 surrounded
   by 5 vertices of the same valency and the "corona" of them. All this is
   inserted into a pentagon. The edge min5_c(n) is one in the corona that
   has its start at an old vertex and an edge of the pentagon in next direction. */

    for (n = 12; n < MAXN - 5; n++)
    {
        start = min5_c(n);

        /* The rotation and starts around the inner vertices is easy: */

        for (i = 0; i < 4; i++)
        {
            run = start + 10 + 5 * i;
            run->start = n + i;
            run->prev = run + 4;
            run->next = run + 1;
            run++;
            run->start = n + i;
            run->prev = run - 1;
            run->next = run + 1;
            run++;
            run->start = n + i;
            run->prev = run - 1;
            run->next = run + 1;
            run++;
            run->start = n + i;
            run->prev = run - 1;
            run->next = run + 1;
            run++;
            run->start = n + i;
            run->prev = run - 1;
            run->next = run - 4;
        }
        run = start + 10 + 5 * i;
        run->prev = run + 4;
        run->next = run + 1;
        run++;
        run->start = n + i;
        run->prev = run - 1;
        run->next = run + 1;
        run++;
        run->start = n + i;
        run->prev = run - 1;
        run->next = run + 1;
        run++;
        run->start = n + i;
        run->prev = run - 1;
        run->next = run + 1;
        run++;
        run->start = n + i;
        run->prev = run - 1;
        run->next = run - 4;
        i++;
        run = start + 10 + 5 * i;
        run->start = n + i - 1;
        run->prev = run + 4;
        run->next = run + 1;
        run++;
        run->start = n + i - 1;
        run->prev = run - 1;
        run->next = run + 1;
        run++;
        run->start = n + i - 1;
        run->prev = run - 1;
        run->next = run + 1;
        run++;
        run->start = n + i - 1;
        run->prev = run - 1;
        run->next = run + 1;
        run++;
        run->start = n + i - 1;
        run->prev = run - 1;
        run->next = run - 4;

        /* The edges starting at the boundary 5-gon */
        run = start;
        run->prev = run + 1;
        (run + 1)->next = run;
        run += 2;
        run->prev = run + 1;
        (run + 1)->next = run;
        run += 2;
        run->prev = run + 1;
        (run + 1)->next = run;
        run += 2;
        run->prev = run + 1;
        (run + 1)->next = run;
        run += 2;
        run->prev = run + 1;
        (run + 1)->next = run;

        /* Now all the ends, inverses, and mins */

        run = start;
        run->end = n;
        run->min = start;
        run->invers = start + 10;
        run++; /*1*/
        run->end = n + 1;
        run->min = run;
        run->invers = start + 15;
        run++; /*2*/
        run->end = n + 1;
        run->min = run;
        run->invers = start + 16;
        run++; /*3*/
        run->end = n + 2;
        run->min = run;
        run->invers = start + 21;
        run++; /*4*/
        run->end = n + 2;
        run->min = run;
        run->invers = start + 22;
        run++; /*5*/
        run->end = n + 3;
        run->min = run;
        run->invers = start + 26;
        run++; /*6*/
        run->end = n + 3;
        run->min = run;
        run->invers = start + 27;
        run++; /*7*/
        run->min = run;
        run->invers = start + 31;
        run++; /*8*/
        run->min = run;
        run->invers = start + 32;
        run++; /*9*/
        run->end = n;
        run->min = run;
        run->invers = start + 14;
        run++; /*10*/
        run->min = run->invers = start;
        run++; /*11*/
        run->end = n + 1;
        run->min = run;
        run->invers = start + 19;
        run++; /*12*/
        run->end = n + 4;
        run->min = run;
        run->invers = start + 35;
        run++; /*13*/
        run->min = run;
        run->invers = start + 33;
        run++; /*14*/
        run->min = run->invers = start + 9;
        run++; /*15*/
        run->min = run->invers = start + 1;
        run++; /*16*/
        run->min = run->invers = start + 2;
        run++; /*17*/
        run->end = n + 2;
        run->min = run;
        run->invers = start + 20;
        run++; /*18*/
        run->end = n + 4;
        run->min = run;
        run->invers = start + 36;
        run++; /*19*/
        run->end = n;
        run->min = run->invers = start + 11;
        run++; /*20*/
        run->end = n + 1;
        run->min = run->invers = start + 17;
        run++; /*21*/
        run->min = run->invers = start + 3;
        run++; /*22*/
        run->min = run->invers = start + 4;
        run++; /*23*/
        run->end = n + 3;
        run->min = run;
        run->invers = start + 25;
        run++; /*24*/
        run->end = n + 4;
        run->min = run;
        run->invers = start + 37;
        run++; /*25*/
        run->end = n + 2;
        run->min = run->invers = start + 23;
        run++; /*26*/
        run->min = run->invers = start + 5;
        run++; /*27*/
        run->min = run->invers = start + 6;
        run++; /*28*/
        run->min = run;
        run->invers = start + 30;
        run++; /*29*/
        run->end = n + 4;
        run->min = run;
        run->invers = start + 38;
        run++; /*30*/
        run->end = n + 3;
        run->min = run->invers = start + 28;
        run++; /*31*/
        run->min = run->invers = start + 7;
        run++; /*32*/
        run->min = run->invers = start + 8;
        run++; /*33*/
        run->end = n;
        run->min = run->invers = start + 13;
        run++; /*34*/
        run->end = n + 4;
        run->min = run;
        run->invers = start + 39;
        run++; /*35*/
        run->end = n;
        run->min = run->invers = start + 12;
        run++; /*36*/
        run->end = n + 1;
        run->min = run->invers = start + 18;
        run++; /*37*/
        run->end = n + 2;
        run->min = run->invers = start + 24;
        run++; /*38*/
        run->end = n + 3;
        run->min = run->invers = start + 29;
        run++; /*39*/
        run->min = run->invers = start + 34;
    }

    make_icosahedron();
}

/**************************************************************************/

static EDGE *
extend_min5_c(EDGE *e, EDGE **anchor)

{
    /* extends a graph in the way given by the type c extension for
   5-connected triangulations. The edge e must start at
   a vertex of degree 5.

   It returns the edge characterizing this operation. This edge as
   well as the edge pointed to by *anchor must be given to the reduction
   routine.

*/

    EDGE *e1, *e2, *e3, *e4, *e5, *e1i, *e2i, *e3i, *e4i, *e5i, *start, *run;
    int v1, v2, v3, v4, v5, origin;

    *anchor = e;

    e1 = e->invers->next;
    e1i = e1->invers;
    e2 = e1i->next->next;
    e2i = e2->invers;
    e3 = e2i->next->next;
    e3i = e3->invers;
    e4 = e3i->next->next;
    e4i = e4->invers;
    e5 = e4i->next->next;
    e5i = e5->invers;

    origin = e->start;
    v1 = e1->start;
    v2 = e1->end;
    v3 = e3->start;
    v4 = e3->end;
    v5 = e5->start;

    start = min5_c(nv);

    firstedge[v1] = e1;
    degree[v1]++;
    firstedge[v2] = e2;
    degree[v2]++;
    firstedge[v3] = e3;
    degree[v3]++;
    firstedge[v4] = e4;
    degree[v4]++;
    firstedge[v5] = e5;
    degree[v5]++;

    firstedge[nv] = start + 10;
    degree[nv] = 5;
    nv++;
    firstedge[nv] = start + 16;
    degree[nv] = 5;
    nv++;
    firstedge[nv] = start + 23;
    degree[nv] = 5;
    nv++;
    firstedge[nv] = start + 28;
    degree[nv] = 5;
    nv++;
    firstedge[nv] = start + 35;
    degree[nv] = 5;
    nv++;
    firstedge[origin] = start + 32;
    /* degree[nv]=5; is already the case */

    ne += 30;

    e1->prev = start;
    start->next = e1;
    run = start + 1;
    e5i->next = run;
    run->prev = e5i;
    run++;
    e5->prev = run;
    run->next = e5;
    run++;
    e4i->next = run;
    run->prev = e4i;
    run++;
    e4->prev = run;
    run->next = e4;
    run++;
    e3i->next = run;
    run->prev = e3i;
    run++;
    e3->prev = run;
    run->next = e3;
    run++;
    e2i->next = run;
    run->prev = e2i;
    run++;
    e2->prev = run;
    run->next = e2;
    run++;
    e1i->next = run;
    run->prev = e1i;

    start->start = (start + 1)->start = (start + 10)->end = (start + 15)->end = v1;
    (start + 8)->start = (start + 9)->start = (start + 14)->end = (start + 32)->end = v2;
    (start + 7)->start = (start + 6)->start = (start + 27)->end = (start + 31)->end = v3;
    (start + 4)->start = (start + 5)->start = (start + 22)->end = (start + 26)->end = v4;
    (start + 2)->start = (start + 3)->start = (start + 16)->end = (start + 21)->end = v5;
    (start + 8)->end = (start + 13)->end = (start + 39)->end = (start + 28)->end = (start + 7)->end = origin;
    (start + 30)->start = (start + 31)->start = (start + 32)->start = (start + 33)->start =
        (start + 34)->start = origin;

    return (start + 35);
}

/**************************************************************************/

static void
reduce_min5_c(EDGE *e, EDGE *anchor)
{

    /* Like other reduction operations, this is not the reverse operation,
     but it relies on the map being EXACTLY the same as after the application 
     of the corresponding extend operation */

    EDGE *e1, *e2, *e3, *e4, *e5, *e1i, *e2i, *e3i, *e4i, *e5i;
    int v1, v2, v3, v4, v5, origin;

    e1 = e->invers->prev->prev->invers->next;
    e1i = e1->invers;
    e2 = e1i->next->next->next;
    e2i = e2->invers;
    e3 = e2i->next->next->next;
    e3i = e3->invers;
    e4 = e3i->next->next->next;
    e4i = e4->invers;
    e5 = e4i->next->next->next;
    e5i = e5->invers;

    v1 = e1->start;
    v2 = e1->end;
    v3 = e3->start;
    v4 = e3->end;
    v5 = e5->start;
    origin = anchor->start;

    firstedge[v1] = e1;
    degree[v1]--;
    firstedge[v2] = e2;
    degree[v2]--;
    firstedge[v3] = e3;
    degree[v3]--;
    firstedge[v4] = e4;
    degree[v4]--;
    firstedge[v5] = e5;
    degree[v5]--;
    firstedge[origin] = anchor;

    nv -= 5;
    ne -= 30;

    e1->prev = e5i->next = anchor->invers;
    anchor = anchor->prev;
    e2->prev = e1i->next = anchor->invers;
    anchor = anchor->prev;
    e3->prev = e2i->next = anchor->invers;
    anchor = anchor->prev;
    e4->prev = e3i->next = anchor->invers;
    anchor = anchor->prev;
    e5->prev = e4i->next = anchor->invers;
}

/**************************************************************************/

static int
on_nf_5_cycle(EDGE *e)
/* nf means that there are vertices inside both parts of the
   triangulation separated by the cycle. 

   Assumes that there are no nf-4-cycles in the graph. This means that
   at ANY vertex of the cycle there is an edge pointing into EACH of the
   two components. 

   Assumes further that the valency of all vertices involved is at least 5.

   Returns TRUE, if edge e is on an nf-5cycle, FALSE otherwise
*/

{
    EDGE *run, *run1, *last, *last1, *dummy;

    if ((degree[e->next->end] == 5) || (degree[e->prev->end] == 5))
        return TRUE;

    RESETMARKS_V;
    last = e->prev->prev;
    run = e->next->next;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    MARK_V(run1->end);
    run1 = run1->next;
    MARK_V(run1->end);
    while (run1 != last1)
    {
        run1 = run1->next;
        MARK_V(run1->end);
    }
    run = run->next;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    MARK_V(run1->end);
    run1 = run1->next;
    MARK_V(run1->end);
    while (run1 != last1)
    {
        run1 = run1->next;
        MARK_V(run1->end);
    }
    while (run != last)
    {
        run = run->next;
        dummy = run->invers;
        last1 = dummy->prev->prev;
        run1 = dummy->next->next;
        MARK_V(run1->end);
        run1 = run1->next;
        MARK_V(run1->end);
        while (run1 != last1)
        {
            run1 = run1->next;
            MARK_V(run1->end);
        }
    }

    e = e->invers;

    last = e->prev->prev;
    run = e->next->next;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    if (ISMARKED_V(run1->end))
        return TRUE;
    run1 = run1->next;
    if (ISMARKED_V(run1->end))
        return TRUE;
    while (run1 != last1)
    {
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return TRUE;
    }
    run = run->next;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    if (ISMARKED_V(run1->end))
        return TRUE;
    run1 = run1->next;
    if (ISMARKED_V(run1->end))
        return TRUE;
    while (run1 != last1)
    {
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return TRUE;
    }
    while (run != last)
    {
        run = run->next;
        dummy = run->invers;
        last1 = dummy->prev->prev;
        run1 = dummy->next->next;
        if (ISMARKED_V(run1->end))
            return TRUE;
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return TRUE;
        while (run1 != last1)
        {
            run1 = run1->next;
            if (ISMARKED_V(run1->end))
                return TRUE;
        }
    }

    return FALSE;
}

/**************************************************************************/

static void
find_extensions_min5(int nbtot, int nbop, EDGE *extA1[], EDGE *extA2[],
                     int *nextA, EDGE *extB[], int extBmirror[], int *nextB,
                     EDGE *extC[], int *nextC, EDGE *lastA)

/* Determine the inequivalent places to make extensions, for the
   ordinary triangulations of minimum degree 5.  The results are
   put in the arrays extD1[0..*nextD-1], etc..
   nbtot and nbop are the usual group parameters.
   If lastA != NULL, this graph was made with an A-operation and lastA
   is its central edge.  If lastA == NULL, it wasn't made with A.
*/
{
    register int i, k;
    register EDGE *e, *e1, *e2, *elast, *elast1, *elast2;
    EDGE **nb, **nb0, **nblim, **nboplim, **nb1, **nb2;
    int v1, v2, d1, d2, xd1, xd2, oldcola, oldcolb, alpha, cola, colb;

    RESETMARKS_V;
    if (lastA)
    {
        v1 = lastA->start;
        v2 = lastA->end;
        d1 = degree[v1];
        d2 = degree[v2];
        MARK_V(v1);
        MARK_V(v2);
        MARK_V(lastA->prev->end);
        MARK_V(lastA->next->end);
    }

    if (nbtot == 1)
    {
        /* A-extensions, trivial group */

        k = 0;
        for (i = 0; i < nv; ++i)
            if (degree[i] >= 6)
            {
                cola = degree[i] + 4;

                if (ISMARKED_V(i) || !lastA || cola >= d1 + d2 + 2)
                {
                    e1 = elast1 = firstedge[i];
                    do
                    {
                        e2 = e1->next->next->next;
                        elast2 = e1->prev->prev;
                        do
                        {
                            if (e2 > e1)
                            {
                                extA1[k] = e1;
                                extA2[k] = e2;
                                ++k;
                            }
                            e2 = e2->next;
                        } while (e2 != elast2);
                        e1 = e1->next;
                    } while (e1 != elast1);
                }
                else if (cola < d1 + d2)
                    continue;
                else
                {
                    e1 = elast1 = firstedge[i];
                    do
                    {
                        e2 = e1->next->next->next;
                        elast2 = e1->prev->prev;
                        alpha = 2;
                        do
                        {
                            if (e2 > e1)
                            {
                                if (e1->end == v1 || e2->end == v1)
                                    xd1 = d1 + 1;
                                else
                                    xd1 = d1;
                                if (e1->end == v2 || e2->end == v2)
                                    xd2 = d2 + 1;
                                else
                                    xd2 = d2;

                                oldcola = xd1 + xd2;
                                if (cola > oldcola)
                                {
                                    extA1[k] = e1;
                                    extA2[k] = e2;
                                    ++k;
                                }
                                else if (cola == oldcola)
                                {
                                    oldcolb = MIN(xd1, xd2);
                                    colb = 3 + MIN(alpha, degree[i] - alpha - 2);
                                    if (colb >= oldcolb)
                                    {
                                        extA1[k] = e1;
                                        extA2[k] = e2;
                                        ++k;
                                    }
                                }
                            }
                            ++alpha;
                            e2 = e2->next;
                        } while (e2 != elast2);
                        e1 = e1->next;
                    } while (e1 != elast1);
                }
            }

        *nextA = k;

        /* B-extensions, trivial group */

        if (lastA || nv >= maxnv - 1)
            *nextB = 0;
        else
        {
            k = 0;

            for (i = 0; i < nv; ++i)
                if (degree[i] == 5)
                {
                    e = elast = firstedge[i];
                    do
                    {
                        if (degree[e->end] == 5 && e == e->min)
                        {
                            extB[k] = extB[k + 1] = e;
                            extBmirror[k] = FALSE;
                            extBmirror[k + 1] = TRUE;
                            k += 2;
                        }
                        e = e->next;
                    } while (e != elast);
                }
            *nextB = k;
        }

        /* C-extensions, trivial group */

        if (nv >= maxnv - 4)
            *nextC = 0;
        else
        {
            k = 0;
            for (i = 0; i < nv; ++i)
                if (degree[i] == 5)
                    extC[k++] = firstedge[i];
            *nextC = k;
        }
    }
    else
    {
        nb0 = (EDGE **)numbering[0];
        nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];
        nblim = (EDGE **)numbering[nbtot];

        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        /* A-extensions, non-trivial group */

        k = 0;

        for (i = 0; i < nv; ++i)
            if (degree[i] >= 6)
            {
                if (!ISMARKED_V(i) && lastA && degree[i] + 4 < d1 + d2)
                    continue;

                e1 = elast1 = firstedge[i];
                do
                {
                    e2 = e1->next->next->next;
                    elast2 = e1->prev->prev;
                    do
                    {
                        if (e1 < e2)
                        {
                            nb1 = &nb0[e1->index + MAXE];
                            nb2 = &nb0[e2->index + MAXE];
                            for (; nb1 < nblim; nb1 += MAXE, nb2 += MAXE)
                                if (*nb1 < *nb2)
                                {
                                    if (*nb1 < e1 || (*nb1 == e1 && *nb2 < e2))
                                        break;
                                }
                                else
                                {
                                    if (*nb2 < e1 || (*nb2 == e1 && *nb1 < e2))
                                        break;
                                }

                            if (nb1 >= nblim)
                            {
                                extA1[k] = e1;
                                extA2[k] = e2;
                                ++k;
                            }
                        }
                        e2 = e2->next;
                    } while (e2 != elast2);
                    e1 = e1->next;
                } while (e1 != elast1);
            }

        *nextA = k;

        /* B-extensions, non-trivial group */

        if (lastA || nv >= maxnv - 1)
            *nextB = 0;
        else
        {
            k = 0;
            RESETMARKS;

            for (i = 0; i < ne; ++i)
                if (!ISMARKEDLO(nb0[i]) && degree[nb0[i]->start] == 5 && degree[nb0[i]->end] == 5)
                {
                    extB[k] = nb0[i]->min;
                    if (nb0[i] == nb0[i]->min)
                    {
                        extBmirror[k] = TRUE;

                        for (nb = &nb0[i]; nb < nboplim; nb += MAXE)
                            MARKLO((*nb)->min);
                        for (; nb < nblim; nb += MAXE)
                            MARKLO((*nb)->min->invers);
                    }
                    else
                    {
                        extBmirror[k] = FALSE;

                        for (nb = &nb0[i]; nb < nboplim; nb += MAXE)
                            MARKLO((*nb)->min->invers);
                        for (; nb < nblim; nb += MAXE)
                            MARKLO((*nb)->min);
                    }
                    ++k;
                }

            *nextB = k;
        }

        /* C-extensions, non-trivial group */

        if (nv >= maxnv - 4)
            *nextC = 0;
        else
        {
            k = 0;

            RESETMARKS_V;
            for (i = 0; i < nv; ++i)
                if (!ISMARKED_V(i) && degree[i] == 5)
                {
                    extC[k++] = firstedge[i];
                    for (nb = nb0 + firstedge[i]->index; nb < nblim; nb += MAXE)
                        MARK_V((*nb)->start);
                }
            *nextC = k;
        }
    }
}

/**************************************************************************/

static void
min5_a_legal(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
             EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref,
             EDGE **prevA, int nprevA)

/* The A-operation with reference edge *ref has just been performed.
   prevA[0..nprevA-1] are all earlier As since the last B or C.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal A-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-2.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   A-reductions have a priority (colour) based on the degrees of the
   four central vertices.  It cannot be changed without changing
   extensions_min5 too.
*/
{
    EDGE *e;
    int deg1, deg2, deg3, deg4, d1, d2, d3, d4;
    long bestcol1, bestcol2, col1, col2;
    int nor, nmir, i;
    int mind1, mind2, maxdeg12, sumdeg12;
    EDGE *ei, *eilast, *hint;
#define PAIR(x, y) (((long)((x) + (y)) << 10) + (long)(x))
#define UPAIR(x, y) ((x) < (y) ? PAIR(x, y) : PAIR(y, x))

    e = ref;
    deg1 = degree[e->start];
    deg2 = degree[e->end];
    deg3 = degree[e->prev->end];
    deg4 = degree[e->next->end];

    bestcol1 = UPAIR(deg1, deg2);
    bestcol2 = UPAIR(deg3, deg4);

    RESETMARKS;
    MARKLO(e);
    MARKLO(e->invers);

    nor = nmir = 0;

    for (i = nprevA; --i >= 0;)
    {
        hint = prevA[i];
        MARKLO(hint);
        MARKLO(hint->invers);
        if ((d3 = degree[hint->prev->end]) >= 6 && (d4 = degree[hint->next->end]) >= 6)
        {
            /* Theorem: The reference edges of the A-expansions since the
              most recent B- or C-expansion are not on essential 5-cycles. */
            d1 = degree[hint->start];
            d2 = degree[hint->end];
            col1 = UPAIR(d1, d2);
            if (col1 == bestcol1)
            {
                col2 = UPAIR(d3, d4);
                if (col2 > bestcol2)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (col2 == bestcol2)
                {
                    if (nor + nmir == 0)
                    {
                        if (deg1 >= deg2)
                        {
                            if (deg3 >= deg4)
                                good_or[nor++] = e;
                            if (deg3 <= deg4)
                                good_mir[nmir++] = e;
                        }
                        if (deg1 <= deg2)
                        {
                            if (deg3 <= deg4)
                                good_or[nor++] = e->invers;
                            if (deg3 >= deg4)
                                good_mir[nmir++] = e->invers;
                        }
                        *ngood_ref = nor;
                        *ngood_mir_ref = nmir;
                    }

                    if (d1 >= d2)
                    {
                        if (d3 >= d4)
                            good_or[nor++] = hint;
                        if (d3 <= d4)
                            good_mir[nmir++] = hint;
                    }
                    if (d1 <= d2)
                    {
                        if (d3 <= d4)
                            good_or[nor++] = hint->invers;
                        if (d3 >= d4)
                            good_mir[nmir++] = hint->invers;
                    }
                }
            }
            else if (col1 > bestcol1)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
        }
    }

    if (nor + nmir == 0)
    {
        if (deg1 >= deg2)
        {
            if (deg3 >= deg4)
                good_or[nor++] = e;
            if (deg3 <= deg4)
                good_mir[nmir++] = e;
        }
        if (deg1 <= deg2)
        {
            if (deg3 <= deg4)
                good_or[nor++] = e->invers;
            if (deg3 >= deg4)
                good_mir[nmir++] = e->invers;
        }

        *ngood_ref = nor;
        *ngood_mir_ref = nmir;
    }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    if (*ngood_ref + *ngood_mir_ref == 0)
        return;

    sumdeg12 = deg1 + deg2;
    mind1 = (sumdeg12 + 1) / 2;
    maxdeg12 = MAX(deg1, deg2);

    for (i = nv; --i >= 0;)
        if ((d1 = degree[i]) >= mind1)
        {
            if (d1 <= maxdeg12)
                mind2 = sumdeg12 - d1;
            else
                mind2 = sumdeg12 - d1 + 1;

            ei = eilast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(ei) && (d2 = degree[ei->end]) >= mind2 && (d3 = degree[ei->prev->end]) >= 6 && (d4 = degree[ei->next->end]) >= 6)
                {
                    col1 = UPAIR(d1, d2);

                    if (col1 > bestcol1)
                    {
                        if (!on_nf_5_cycle(ei))
                        {
                            *ngood_ref = *ngood_mir_ref = 0;
                            return;
                        }
                    }
                    else
                    {
                        col2 = UPAIR(d3, d4);
                        if (col2 > bestcol2)
                        {
                            if (!on_nf_5_cycle(ei))
                            {
                                *ngood_ref = *ngood_mir_ref = 0;
                                return;
                            }
                        }
                        else if (col2 == bestcol2 && !on_nf_5_cycle(ei))
                        {
                            if (d1 >= d2)
                            {
                                if (d3 >= d4)
                                    good_or[nor++] = ei;
                                if (d3 <= d4)
                                    good_mir[nmir++] = ei;
                            }
                            if (d1 <= d2)
                            {
                                if (d3 <= d4)
                                    good_or[nor++] = ei->invers;
                                if (d3 >= d4)
                                    good_mir[nmir++] = ei->invers;
                            }
                        }
                    }
                }
                MARKLO(ei->invers);
                ei = ei->next;
            } while (ei != eilast);
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/**************************************************************************/

static int
is_valid_min5_b(EDGE *ref, int mirror)

/* Check if the B-reduction (ref,mirror) is valid.  The important
   things are that two vertices have degree >= 6 and there are no
   non-facial 5-cycles that will become non-facial 4-cycles.
   It is assumed that the ends and sides of ref have degree 5.
*/

{
    EDGE *e1, *e2, *e, *refi;

    refi = ref->invers;

    if (!mirror)
    {
        if (degree[ref->next->next->end] < 6 || degree[refi->next->next->end] < 6)
            return FALSE;
        e1 = ref->prev->prev->invers->prev->prev;
        e2 = refi->prev->prev->invers->prev->prev;

        RESETMARKS_V;

        for (e = e1->next->next->next->next; e != e1; e = e->next)
            MARK_V(e->end);
        e1 = e1->invers;
        for (e = e1->prev->prev->prev; e != e1; e = e->prev)
            MARK_V(e->end);

        for (e = e2->next->next->next->next; e != e2; e = e->next)
            if (ISMARKED_V(e->end))
                return FALSE;
        e2 = e2->invers;
        for (e = e2->prev->prev->prev; e != e2; e = e->prev)
            if (ISMARKED_V(e->end))
                return FALSE;
    }
    else
    {
        if (degree[ref->prev->prev->end] < 6 || degree[refi->prev->prev->end] < 6)
            return FALSE;
        e1 = ref->next->next->invers->next->next;
        e2 = refi->next->next->invers->next->next;

        RESETMARKS_V;

        for (e = e1->prev->prev->prev->prev; e != e1; e = e->prev)
            MARK_V(e->end);
        e1 = e1->invers;
        for (e = e1->next->next->next; e != e1; e = e->next)
            MARK_V(e->end);

        for (e = e2->prev->prev->prev->prev; e != e2; e = e->prev)
            if (ISMARKED_V(e->end))
                return FALSE;
        e2 = e2->invers;
        for (e = e2->next->next->next; e != e2; e = e->next)
            if (ISMARKED_V(e->end))
                return FALSE;
    }

    return TRUE;
}

/**************************************************************************/

static int
has_min5_a(void)

/* Test if the graph has an A-reduction */

{
    EDGE *e, *elast;
    int i;

    for (i = 0; i < nv; ++i)
    {
        e = elast = firstedge[i];
        do
        {
            if (e == e->min && degree[e->next->end] >= 6 && degree[e->prev->end] >= 6 && !on_nf_5_cycle(e))
                return TRUE;
            e = e->next;
        } while (e != elast);
    }

    return FALSE;
}

/**************************************************************************/

static int
has_min5_b(void)

/* Test if the graph has a B-reduction */

{
    EDGE *e, *elast;
    int i;

    for (i = 0; i < nv; ++i)
        if (degree[i] == 5)
        {
            e = elast = firstedge[i];
            do
            {
                if (e == e->min && degree[e->end] == 5 && degree[e->prev->end] == 5 && degree[e->next->end] == 5 && (is_valid_min5_b(e, FALSE) || is_valid_min5_b(e, TRUE)))
                    return TRUE;
                e = e->next;
            } while (e != elast);
        }

    return FALSE;
}

/**************************************************************************/

static void
min5_b_legal(EDGE *ref, int mirror, EDGE *good_or[], int *ngood_or,
             int *ngood_ref, EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* The B-operation with reference edge *ref and side mirror has just been
   performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal B-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-2.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   This procedure does NOT determine that there are no A-reductions.
*/
{
    EDGE *e, *elast;
    int nor, nmir, i;

    ref = ref->min;
    nor = nmir = 0;

    if (!mirror)
    {
        good_or[nor++] = ref;
        good_or[nor++] = ref->invers;
    }
    else
    {
        good_mir[nmir++] = ref;
        good_mir[nmir++] = ref->invers;
    }

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    RESETMARKS;
    MARKLO(ref);

    for (i = 0; i < nv; ++i)
        if (degree[i] == 5)
        {
            e = elast = firstedge[i];
            do
            {
                if (e == e->min && !ISMARKEDLO(e) && degree[e->prev->end] == 5 && degree[e->end] == 5 && degree[e->next->end] == 5)
                {
                    if (is_valid_min5_b(e, FALSE))
                    {
                        good_or[nor++] = e;
                        good_or[nor++] = e->invers;
                    }
                    if (is_valid_min5_b(e, TRUE))
                    {
                        good_mir[nmir++] = e;
                        good_mir[nmir++] = e->invers;
                    }
                }
                e = e->next;
            } while (e != elast);
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/**************************************************************************/

static int
is_min5_c_centre(int v)

/* checks whether the configuration centered at vertex v is reducible by
   the c-reduction of the min5 generation.

   It assumes that there is no nf-4-cycle in the graph. It can be
   shown that it is enough to check the valencies of the center and its
   neighbours to be 5 and the second neighbours to be at least 6. In this
   case a 4-cut introduced by the reduction would imply that there was one
   before.
 
*/

{

    EDGE *run;

    if (degree[v] != 5)
        return FALSE;

    run = firstedge[v];
    if (degree[run->end] != 5)
        return FALSE;
    run = run->next;
    if (degree[run->end] != 5)
        return FALSE;
    run = run->next;
    if (degree[run->end] != 5)
        return FALSE;
    run = run->next;
    if (degree[run->end] != 5)
        return FALSE;
    run = run->next;
    if (degree[run->end] != 5)
        return FALSE;

    run = run->invers->prev->prev->invers->next; /* edge 1*/
    if ((degree[run->start] < 6) || (degree[run->end] < 6))
        return FALSE;
    run = run->invers->next->next->next; /* edge 2*/
    if (degree[run->end] < 6)
        return FALSE;
    run = run->invers->next->next->next; /* edge 3*/
    if (degree[run->end] < 6)
        return FALSE;
    run = run->invers->next->next->next; /* edge 4*/
    if (degree[run->end] < 6)
        return FALSE;

    return TRUE;
}

/**************************************************************************/

static void
scanmin5c(int nbtot, int nbop, int dosplit, EDGE **prevA, int nprevA)

/* The main node of the recursion for 5-connected triangulations.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   If dosplit==TRUE, this is the place to do splitting (if any).
   prev[0..nprevA-1] is the list of consecutive A operations leading
   to this graph, given by their central edges.
   If nprevA == 0, this graph wasn't made with A.
*/
{
    EDGE *firstedge_save[MAXN];
    EDGE *extA1[MAXN * MAXN / 4 + 10], *extA2[MAXN * MAXN / 4 + 10],
        *extB[MAXE], *extC[MAXN];
    EDGE *extAred, *extBred, *extCred, *extCanchor;
    int extBmirror[MAXE];
    EDGE *good_or[MAXE], *good_mir[MAXE];
    EDGE *newprevA[MAXN];
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int nextA, nextB, nextC, i, j;
    int xnbtot, xnbop;
    int colour[MAXN];

    if (nv == maxnv)
    {
        got_one(nbtot, nbop, 5);
        return;
    }

    if (dosplit)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_MIN5
    if (!(PRE_FILTER_MIN5))
        return;
#endif

#ifndef FIND_EXTENSIONS_MIN5
#define FIND_EXTENSIONS_MIN5 find_extensions_min5
#endif

    FIND_EXTENSIONS_MIN5(nbtot, nbop, extA1, extA2, &nextA, extB, extBmirror,
                         &nextB, extC, &nextC, (nprevA == 0 ? NULL : prevA[nprevA - 1]));

    if (nextA > MAXN * MAXN / 4)
    {
        fprintf(stderr, ">E Increase the array bounds for extA1 and\n");
        fprintf(stderr, "   extA2 in scanmin5() and scanmin5c().\n");
        exit(1);
    }

    for (i = 0; i < nextA; ++i)
    {
        extAred = extend_min5_a(extA1[i], extA2[i]);
#ifdef FAST_FILTER_MIN5
        if (FAST_FILTER_MIN5)
#endif
        {
            min5_a_legal(extAred, good_or, &ngood_or, &ngood_ref,
                         good_mir, &ngood_mir, &ngood_mir_ref, prevA, nprevA);

            if (ngood_ref + ngood_mir_ref > 0)
            {
                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref)
                {
                    got_one(1, 1, 5);
                }
                else if (ngood_or + ngood_mir == 1)
                {
                    prevA[nprevA] = extAred;
                    scanmin5c(1, 1, nv == splitlevel, prevA, nprevA + 1);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    prevA[nprevA] = extAred;
                    scanmin5c(xnbtot, xnbop, nv == splitlevel, prevA, nprevA + 1);
                }
            }
        }
        reduce_min5_a(extAred);
    }

    for (i = 0; i < nextB; ++i)
    {
        extBred = extend_min5_b(extB[i], extBmirror[i]);
#ifdef FAST_FILTER_MIN5
        if (FAST_FILTER_MIN5)
#endif
        {
            if (!has_min5_a())
            {
                min5_b_legal(extBred, extBmirror[i], good_or, &ngood_or,
                             &ngood_ref, good_mir, &ngood_mir, &ngood_mir_ref);

                if (ngood_ref + ngood_mir_ref > 0)
                {
                    if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                            good_mir, ngood_mir, ngood_mir_ref,
                                            degree, numbering, &xnbtot, &xnbop))
                        scanmin5c(xnbtot, xnbop,
                                  nv == splitlevel || nv == splitlevel + 1, newprevA, 0);
                }
            }
        }
        reduce_min5_b(extBred, extBmirror[i]);
    }

    for (i = 0; i < nextC; ++i)
    {
        extCred = extend_min5_c(extC[i], &extCanchor);
#ifdef FAST_FILTER_MIN5
        if (FAST_FILTER_MIN5)
#endif
        {
            if (!has_min5_a() && !has_min5_b())
            {
                for (j = 0; j < nv - 1; ++j)
                    if (is_min5_c_centre(j))
                        colour[j] = 2;
                    else
                        colour[j] = degree[j];
                colour[nv - 1] = 2;

                if (canon(colour, numbering, &xnbtot, &xnbop))
                    scanmin5c(xnbtot, xnbop,
                              nv >= splitlevel && nv <= splitlevel + 4, newprevA, 0);
            }
        }
        reduce_min5_c(extCred, extCanchor);
    }

    if (dosplit)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/**************************************************************************/

static int
wont_be_on_nf_3_cycle(EDGE *e)

/* returns 1 if after switching e won't be on an nf 3-cycle. */

{
    EDGE *run, *last, *dummy;

    RESETMARKS_V;
    dummy = e->next->invers;
    last = dummy->prev;
    run = dummy->next->next;
    MARK_V(run->end);
    while (run != last)
    {
        run = run->next;
        MARK_V(run->end);
    }

    e = e->prev->invers;
    run = e->next;
    last = e->prev->prev;
    if (ISMARKED_V(run->end))
        return 0;
    while (run != last)
    {
        run = run->next;
        if (ISMARKED_V(run->end))
            return 0;
    }

    return 1;
}

/*************************************************************************/

static int
is_3banglecenter_notdouble(EDGE *e)

/* returns 1 if it is the center of a 3bangle and after the edge is
   switched it is not in a double edge, 0 else */

{
    EDGE *run, *last, *dummy;
    int end;

    RESETMARKS_V;

    dummy = e->next->invers;
    e = e->prev->invers;
    end = e->start;

    last = dummy->prev;
    run = dummy->next->next;
    if (run->end == end)
        return 0;
    MARK_V(run->end);
    while (run != last)
    {
        run = run->next;
        if (run->end == end)
            return 0;
        MARK_V(run->end);
    }

    run = e->next;
    last = e->prev->prev;
    if (ISMARKED_V(run->end))
        return 1;
    while (run != last)
    {
        run = run->next;
        if (ISMARKED_V(run->end))
            return 1;
    }

    return 0;
}

/***********************************************************************/

static void
make_3bangle_list(EDGE *list[], int *listlength, EDGE *nf3cycleedges[],
                  int numnf3cycleedges)

/* returns the list of legal 3-bangles, that is of (undirected) edges
   so that:

   (i) both endvertices have valency >=6
   (ii) it is not on an nf-3-cycle at the moment
   (iii) it is the center of a 3bangle
   (iv) after switching it is not in a double edge
 
   nf3cycleedges[] must be a list of all undirected edges -- that
   is: always containing edge->min lying on nf-3-cycles and
   numnf3cycleedges their number.
*/

{
    int i, counter;
    EDGE *run, *end;

    RESETMARKS;
    while (--numnf3cycleedges >= 0)
        MARKLO(nf3cycleedges[numnf3cycleedges]);

    counter = 0;

    for (i = 0; i < nv; i++)
        if (degree[i] >= 6)
        {
            run = end = firstedge[i];
            do
            {
                if (run == run->min && degree[run->end] >= 6 && !ISMARKEDLO(run) && is_3banglecenter_notdouble(run))
                {
                    list[counter] = run;
                    counter++;
                }
                run = run->next;
            } while (run != end);
        }

    *listlength = counter;
}

/**************************************************************************/

static void
find_extensions_min5c3(int nbtot, int nbop, EDGE **on4, int non4,
                       EDGE **on3, int non3, EDGE **ext5_sw, int *next5_sw)

/* List the inequivalent extensions for the 3-connected phase on mindeg 5.
   If on4!=NULL, it is a list of all edges on nf4-cycles (min form).
   If on3!=NULL, on3[0..non3-1] is a list of all edges on nf-3-cycles
   (min form).  If on3==NULL, there are no nf-3-cycles and non3==0.
   Exactly one of on4 and on3 is NULL.
 
   As a result, ext5_sw[0..*next5_sw-1] is set to all feasible switching
   operations.  Equivalent extensions are removed.
*/

{
    /* Currently on4[] is not used, but we could use it if we wanted. */
    make_3bangle_list(ext5_sw, next5_sw, on3, non3);

    if (nbtot > 1 && *next5_sw > 1)
        prune_edgelist(ext5_sw, next5_sw, nbtot);
}

/**************************************************************************/

static void
min5c3_sw_legal(EDGE *e, EDGE **on3, int non3, EDGE **good, int *ngood)

/* Edge e (min form) has been switched (3-connected phase of mindeg=5).
   on3[0..non3-1] are all the edges in nf-3-cycles.
   Put into good[0..ngood-1] edges as desired for canon_edge().
*/

#define SW53COL(e) (((long)degree[(e)->start] << 10) | (long)degree[(e)->end])
{
    long bestcol, col;
    EDGE *e1, *e2;
    int i, ng;

    bestcol = SW53COL(e);
    col = SW53COL(e->invers);
    if (bestcol > col)
    {
        good[0] = e;
        ng = 1;
    }
    else if (bestcol == col)
    {
        good[0] = e;
        good[1] = e->invers;
        ng = 2;
    }
    else
    {
        good[0] = e->invers;
        ng = 1;
        bestcol = col;
    }

    for (i = 0; i < non3; ++i)
    {
        e1 = on3[i];
        e2 = e1->invers;
        if (degree[e1->start] >= 6 && degree[e1->end] >= 6 && e1 != e && wont_be_on_nf_3_cycle(e1))
        {
            col = SW53COL(e1);
            if (col > bestcol)
            {
                *ngood = 0;
                return;
            }
            else if (col == bestcol)
                good[ng++] = e1;

            col = SW53COL(e2);
            if (col > bestcol)
            {
                *ngood = 0;
                return;
            }
            else if (col == bestcol)
                good[ng++] = e2;
        }
    }

    *ngood = ng;
}

/***********************************************************************/

static void
add_new_nf3_cycles(EDGE *e, EDGE **on3, int *non3)

/* The edge e has just been switched.  Previously it was not on any
   nf-3-cycles and on3[0..non3-1] was a list of all edges on nf-3-cycles.
   Add any new nf-3-cycles to on3[].  All edges are in min form. */

{
    int i, j, k, v1;
    EDGE *e1, *e2, *ee;
    EDGE *e0[MAXN];

    RESETMARKS;
    for (i = *non3; --i >= 0;)
        MARKLO(on3[i]);

    RESETMARKS_V;
    v1 = e->start;
    for (e1 = e->next->next, k = degree[v1] - 3; --k >= 0; e1 = e1->next)
    {
        MARK_V(e1->end);
        e0[e1->end] = e1;
    }

    j = *non3;
    for (e1 = e->invers->next->next, k = degree[e->end] - 3;
         --k >= 0; e1 = e1->next)
        if (ISMARKED_V(e1->end))
        {
            e2 = e0[e1->end];

            ee = e->min;
            if (!ISMARKEDLO(ee))
            {
                on3[j++] = ee;
                MARKLO(ee);
            }
            ee = e1->min;
            if (!ISMARKEDLO(ee))
            {
                on3[j++] = ee;
                MARKLO(ee);
            }
            ee = e2->min;
            if (!ISMARKEDLO(ee))
            {
                on3[j++] = ee;
                MARKLO(ee);
            }
        }
    *non3 = j;
}

/**************************************************************************/

static void
scanmin5c3_1(int nbtot, int nbop, EDGE **on3, int non3)

/* This is the first procedure that creates nf-3-cycles for mindeg=5
   triangulations.  It is called with a 3-connected triangulation and
   a list of the min forms of all the edges which lie on nf-3-cycles.
*/

{
    EDGE *good[MAXE], *ext5_sw[MAXE / 2];
    int i, xnbtot, xnbop, ngood, newnon3, next5_sw;

#ifdef PRE_FILTER_MIN5c3
    if (!(PRE_FILTER_MIN5c3))
        return;
#endif

#ifndef FIND_EXTENSIONS_MIN5c3
#define FIND_EXTENSIONS_MIN5c3 find_extensions_min5c3
#endif

    FIND_EXTENSIONS_MIN5c3(nbtot, nbop, NULL, 0, on3, non3, ext5_sw, &next5_sw);

    if (pswitch)
        startpolyscan(nbtot, nbop);
    else
        got_one(nbtot, nbop, 3);

    for (i = 0; i < next5_sw; ++i)
    {
        switch_edge(ext5_sw[i]);
#ifdef FAST_FILTER_MIN5c3
        if (FAST_FILTER_MIN5c3)
#endif
        {
            newnon3 = non3;
            add_new_nf3_cycles(ext5_sw[i], on3, &newnon3);

            min5c3_sw_legal(ext5_sw[i], on3, newnon3, good, &ngood);
            if (ngood > 0 && canon_edge(good, ngood, degree, numbering, &xnbtot, &xnbop))
                scanmin5c3_1(xnbtot, xnbop, on3, newnon3);
        }
        switch_edge_back(ext5_sw[i]);
    }
}

/**************************************************************************/

static void
scanmin5c3_0(int nbtot, int nbop, EDGE **on4, int non4)

/* This is the first procedure that creates nf-3-cycles for mindeg=5
   triangulations.  It is called with a 4-connected triangulation and
   a list of the min forms of all the edges which lie on nf-4-cycles.
*/

{
    EDGE *good[MAXE], *on3[MAXE / 2];
    EDGE *ext5_sw[MAXE / 2];
    int i, xnbtot, xnbop, ngood, non3, next5_sw;

#ifdef PRE_FILTER_MIN5c3
    if (!(PRE_FILTER_MIN5c3))
        return;
#endif

#ifndef FIND_EXTENSIONS_MIN5c3
#define FIND_EXTENSIONS_MIN5c3 find_extensions_min5c3
#endif

    FIND_EXTENSIONS_MIN5c3(nbtot, nbop, on4, non4, NULL, 0, ext5_sw, &next5_sw);

    for (i = 0; i < next5_sw; ++i)
    {
        switch_edge(ext5_sw[i]);
#ifdef FAST_FILTER_MIN5c3
        if (FAST_FILTER_MIN5c3)
#endif
        {
            non3 = 0;
            add_new_nf3_cycles(ext5_sw[i], on3, &non3);

            min5c3_sw_legal(ext5_sw[i], on3, non3, good, &ngood);
            if (ngood > 0 && canon_edge(good, ngood, degree, numbering, &xnbtot, &xnbop))
                scanmin5c3_1(xnbtot, xnbop, on3, non3);
        }
        switch_edge_back(ext5_sw[i]);
    }
}

/**************************************************************************/

static int
is_in_5_bangle(EDGE *e)

/* Test if e is the central edge of a bangle, 5-connected case. */

{
    EDGE *e1, *e2;
    int k, l;

    RESETMARKS_V;
    for (e1 = e->prev->invers->next->next, k = degree[e->prev->end] - 4;
         --k >= 0; e1 = e1->next)
        MARK_V(e1->end);

    for (e1 = e->next->invers->prev->prev, k = degree[e->next->end] - 4;
         --k >= 0; e1 = e1->prev)
        for (e2 = e1->invers->next->next, l = degree[e1->end] - 3;
             --l >= 0; e2 = e2->next)
            if (ISMARKED_V(e2->end))
                return TRUE;

    return FALSE;
}

/**************************************************************************/

static void
all_5_bangles(EDGE **bang, int *nbang)

/* Set bang[0..nbang-1] to the central edges (min) of all bangles.
   5-connected case. */

{
    int i, nb;
    EDGE *e, *elast;

    nb = 0;
    for (i = 0; i < nv; ++i)
    {
        e = elast = firstedge[i];
        do
        {
            if (e == e->min && is_in_5_bangle(e))
                bang[nb++] = e;
            e = e->next;
        } while (e != elast);
    }

    *nbang = nb;
}

/**************************************************************************/

static int
is_4bangle_centre(EDGE *e)

/* returns TRUE if it is the center of a bangle, FALSE otherwise
   4-connected case of mindeg 5 */

{
    EDGE *run, *run1, *last, *last1, *dummy;

    RESETMARKS_V;

    dummy = e->next->invers;
    last = dummy->prev;
    run = dummy->next->next;
    MARK_V(run->end);
    while (run != last)
    {
        run = run->next;
        MARK_V(run->end);
    }

    e = e->prev->invers;

    run = e->next;
    last = e->prev->prev;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    if (ISMARKED_V(run1->end))
        return 1;
    run1 = run1->next;
    if (ISMARKED_V(run1->end))
        return 1;
    while (run1 != last1)
    {
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 1;
    }
    while (run != last)
    {
        run = run->next;
        dummy = run->invers;
        last1 = dummy->prev->prev;
        run1 = dummy->next->next;
        if (ISMARKED_V(run1->end))
            return 1;
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 1;
        while (run1 != last1)
        {
            run1 = run1->next;
            if (ISMARKED_V(run1->end))
                return 1;
        }
    }

    return 0;
}

/***********************************************************************/

static int
will_be_on_nf_3_cycle(EDGE *e)

/* returns TRUE if after switching e will be on an nf-3-cycle, FALSE else.
   Assumes that there are no nf 3-cycles already and that the mins of all
   edges on nf-4-cycles are marked low. */

{
    EDGE *run, *last, *dummy;

    if ((!ISMARKEDLO(e->next->min)) || (!ISMARKEDLO(e->prev->min)))
        return 0;
    /* If after switching it is on an nf-3-cycle, then they are on an nf-4-cycle
     already */

    RESETMARKS_V;

    dummy = e->next->invers;
    last = dummy->prev;
    run = dummy->next->next;
    MARK_V(run->end);
    while (run != last)
    {
        run = run->next;
        MARK_V(run->end);
    }

    dummy = e->prev->invers;

    run = dummy->next;
    last = dummy->prev->prev;

    if (ISMARKED_V(run->end))
        return 1;
    while (run != last)
    {
        run = run->next;
        if (ISMARKED_V(run->end))
            return 1;
    }

    return 0;
}

/***********************************************************************/

static void
make_4bangle_list(EDGE *list[], int *listlength,
                  EDGE *nf4cycleedges[], int numnf4cycleedges)

/* returns the list of legal 4-bangles, that is of (undirected) edges so that:

     (i) both endvertices have valency >=6
     (ii) it is not on an nf-4-cycle at the moment
     (iii) it is the center of a bangle
     (iv) after switching it is not on an nf-3-cycle

     It is assumed that there are no nf-3-cycles.

     nf4cycleedges[] must be a list of all undirected edges -- that
     is: always containing edge->min lying on nf-4-cycles and
     numnf4cycleedges their number.
*/

{
    int i, counter;
    EDGE *run, *end;

    RESETMARKS;
    while (--numnf4cycleedges >= 0)
        MARKLO(nf4cycleedges[numnf4cycleedges]);

    counter = 0;

    for (i = 0; i < nv; i++)
        if (degree[i] >= 6)
        {
            run = end = firstedge[i];
            do
            {
                if ((run == run->min) && (degree[run->end] >= 6) && (!ISMARKEDLO(run)) && is_4bangle_centre(run) && (!will_be_on_nf_3_cycle(run)))
                {
                    list[counter] = run;
                    counter++;
                }
                run = run->next;
            } while (run != end);
        }

    *listlength = counter;

    return;
}

/***********************************************************************/

static int
wont_be_on_nf_4_cycle(EDGE *e)

/* returns 1 if after switching e won't be on an nf 4-cycle. Assumes that
   there are no nf 3-cycles either before or after the switching. */

/* Alternative version:
{
    EDGE *e1,*e2,*e3;
    int k1,k2,k3;

    RESETMARKS_V;

    for (e1 = e->prev->invers->next,
              k1 = degree[e1->start]-2; --k1 >= 0; e1 = e1->next)
	MARK_V(e1->end);

    for (e2 = e->next->invers->prev,
              k2 = degree[e2->start]-2; --k2 >= 0; e2 = e2->prev)
	for (e3 = e2->invers->next->next,
                  k3 = degree[e3->start]-3; --k3 >= 0; e3 = e3->next)
	    if (ISMARKED_V(e3->end)) return FALSE;

    return TRUE;
}
*/

{
    EDGE *run, *run1, *last, *last1, *dummy;

    RESETMARKS_V;
    last = e->next->invers->prev;
    run = last->next->next->next;
    MARK_V(run->end);
    while (run != last)
    {
        run = run->next;
        MARK_V(run->end);
    }

    e = e->prev->invers;
    run = e->next;
    last = e->prev->prev;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    if (ISMARKED_V(run1->end))
        return 0;
    run1 = run1->next;
    if (ISMARKED_V(run1->end))
        return 0;
    while (run1 != last1)
    {
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 0;
    }
    run = run->next;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    if (ISMARKED_V(run1->end))
        return 0;
    run1 = run1->next;
    if (ISMARKED_V(run1->end))
        return 0;
    while (run1 != last1)
    {
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 0;
    }
    while (run != last)
    {
        run = run->next;
        dummy = run->invers;
        last1 = dummy->prev->prev;
        run1 = dummy->next->next;
        if (ISMARKED_V(run1->end))
            return 0;
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 0;
        while (run1 != last1)
        {
            run1 = run1->next;
            if (ISMARKED_V(run1->end))
                return 0;
        }
    }
    return 1;
}

/***********************************************************************/

static void
add_new_nf4_cycles(EDGE *e, EDGE **on4, int *non4)

/* The edge e has just been switched.  Previously it was not on any
   nf-4-cycles and on4[0..non4-1] was a list of all edges on nf-4-cycles.
   Add any new nf-4-cycles to on4[].  All edges are in min form. */

{
    int i, j, k, l, v1;
    EDGE *e1, *e2, *e3, *ee;
    EDGE *e0[MAXN];

    RESETMARKS;
    for (i = *non4; --i >= 0;)
        MARKLO(on4[i]);

    RESETMARKS_V;
    v1 = e->start;
    for (e1 = e->next->next, k = degree[v1] - 3; --k >= 0; e1 = e1->next)
    {
        MARK_V(e1->end);
        e0[e1->end] = e1;
    }

    j = *non4;
    for (e1 = e->invers->next->next, k = degree[e->end] - 3;
         --k >= 0; e1 = e1->next)
        for (e2 = e1->invers->next->next, l = degree[e1->end] - 3;
             --l >= 0; e2 = e2->next)
            if (ISMARKED_V(e2->end))
            {
                e3 = e0[e2->end];

                ee = e->min;
                if (!ISMARKEDLO(ee))
                {
                    on4[j++] = ee;
                    MARKLO(ee);
                }
                ee = e1->min;
                if (!ISMARKEDLO(ee))
                {
                    on4[j++] = ee;
                    MARKLO(ee);
                }
                ee = e2->min;
                if (!ISMARKEDLO(ee))
                {
                    on4[j++] = ee;
                    MARKLO(ee);
                }
                ee = e3->min;
                if (!ISMARKEDLO(ee))
                {
                    on4[j++] = ee;
                    MARKLO(ee);
                }
            }
    *non4 = j;
}

/**************************************************************************/

static int
common_5_endpoint(EDGE *e, EDGE *e1)

/* returns 1, if the endpoints of e and e1 have a common neighbour
   with valency 5, different from their start and different from
   e->prev->end, e->next->end, e1->prev->end, e1->next->end, 0 else.
   It is assumed that the starting points of e, e1 are the same, and that

*/

/*  Alternate version:
{
    EDGE *ee;
    int k;

    RESETMARKS_V;

    ee = e->invers->next->next;
    for (k = degree[ee->start]-3; --k >= 0; ee = ee->next)
	if (degree[ee->end] == 5) MARK_V(ee->end);

    ee = e1->invers->next->next;
    for (k = degree[ee->start]-3; --k >= 0; ee = ee->next) 
        if (ISMARKED_V(ee->end)) return TRUE;

    return FALSE;
}
*/

{
    EDGE *run, *last;

    RESETMARKS_V;

    e = e->invers;
    e1 = e1->invers;

    run = e->next->next;
    if (degree[run->end] == 5)
        MARK_V(run->end);
    run = run->next;
    if (degree[run->end] == 5)
        MARK_V(run->end);
    last = e->prev->prev;
    while (run != last)
    {
        run = run->next;
        if (degree[run->end] == 5)
            MARK_V(run->end);
    }

    run = e1->next->next;
    if (ISMARKED_V(run->end))
        return 1;
    run = run->next;
    if (ISMARKED_V(run->end))
        return 1;
    last = e1->prev->prev;
    while (run != last)
    {
        run = run->next;
        if (ISMARKED_V(run->end))
            return 1;
    }
    return 0;
}

/**************************************************************************/

static void
make_5exp_list(EDGE *list1[], EDGE *list2[], int *listlength,
               EDGE *nf4cycleedges[], int numnf4cycleedges)

/* returns the list of legal 5-expansions for the mindeg5 4-connectivity
   case, that is of (undirected) pairs of edges so that:

   (i) both edges start at the same point of valency >=6
   (ii) in between them there are (on one side) exactly two edges and
        these are not on an nf-4-cycle
   (iii) their endpoints have a common neighbour of valency 5 (so
         especially both edges must be on an nf-4-cycle)

   The list comes in pairs of two, that is: for 0<=i<*listlength
   list1[i] and list2[i] belong together.

   It is assumed that there are no nf-3-cycles.

   nf4cycleedges[] must be a list of all undirected edges -- that
   is: always containing edge->min lying on nf-4-cycles and
   numnf4cycleedges their number.
*/

{
    int i, counter;
    EDGE *run, *run1, *end;

    RESETMARKS;
    for (i = numnf4cycleedges; --i >= 0;)
    {
        MARKLO(nf4cycleedges[i]);
        MARKLO(nf4cycleedges[i]->invers);
    }

    counter = 0;

    for (i = 0; i < nv; i++)
        if (degree[i] >= 6)
        {
            run = firstedge[i];
            if (degree[i] == 6)
            /* This case is special, since for opposite edges, the "same" expansion
           would be done, but different edges would be ckecked to judge whether
           it is legal. If deg>6 there is a 1-1 correspondence between the two
           edges in between and the expansion edgepair */
            {
                end = run->next->next->next;
                do
                {
                    if (ISMARKEDLO(run))
                    {
                        run1 = run->next->next->next;
                        /* is done inside the loop and not as a second run variable,
                 since most likely the loop is entered not too often, so
                 that in those rare cases where it is entered, it pays off
                 to have three "nexts". */
                        if (ISMARKEDLO(run1) &&
                            ((!ISMARKEDLO(run->next) && !ISMARKEDLO(run1->prev)) ||
                             (!ISMARKEDLO(run1->next) && !ISMARKEDLO(run->prev))))
                            if (common_5_endpoint(run, run1))
                            {
                                list1[counter] = run;
                                list2[counter] = run1;
                                counter++;
                            }
                    }
                    run = run->next;
                } while (run != end);
            }

            else /* degree > 6 */
            {
                end = run;
                do
                {
                    if (ISMARKEDLO(run))
                    {
                        run1 = run->next->next->next;
                        if (ISMARKEDLO(run1) &&
                            (!ISMARKEDLO(run->next) && !ISMARKEDLO(run1->prev)))
                            if (common_5_endpoint(run, run1))
                            {
                                list1[counter] = run;
                                list2[counter] = run1;
                                counter++;
                            }
                    }
                    run = run->next;
                } while (run != end);
            } /*else deg>6 */
        }     /* end deg>=6 */

    *listlength = counter;

    return;
}

/**************************************************************************/

static void
find_extensions_min5c4(int nbtot, int nbop, EDGE **bang, int nbang,
                       EDGE **on4, int non4, EDGE **ext5_sw, int *next5_sw,
                       EDGE **ext5_51, EDGE **ext5_52, int *next5_5)

/* List the inequivalent extensions for the 4-connected phase on mindeg 5.
   If bang!=NULL, it is a list of all bangles perhaps with some of 
   insufficient degree.  If on4!=NULL, on4[0..non4-1] is a list of all edges
   on nf-4-cycles (min form).  If on4==NULL, there are no nf-4-cycles and
   non4=0.  Exactly one of bang and on4 is NULL.

   As a result, ext5_sw[0..*next5_sw-1] is set to all feasible switching
   operations, and (ext5_51,ext5_52)[0..*next5_5-1] is set to all feasible
   5-expansions as pairs of edges.  Equivalent extensions are removed.
*/

{
    int i, k;
    EDGE *e1, *e2, **nb0, **nblim, **nb1, **nb2;

    k = 0;
    if (bang)
    {
        for (i = 0; i < nbang; ++i)
            if (degree[bang[i]->start] >= 6 && degree[bang[i]->end] >= 6)
                ext5_sw[k++] = bang[i];
    }
    else
        make_4bangle_list(ext5_sw, &k, on4, non4);

    if (nbtot > 1 && k > 1)
        prune_edgelist(ext5_sw, &k, nbtot);

    *next5_sw = k;

    if (nv < maxnv && on4 && non4 >= 6)
    {
        make_5exp_list(ext5_51, ext5_52, next5_5, on4, non4);

        if (nbtot == 1 || *next5_5 <= 1)
            return;

        nb0 = (EDGE **)numbering[0];
        nblim = (EDGE **)numbering[nbtot];

        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        k = 0;
        for (i = 0; i < *next5_5; ++i)
        {
            if (ext5_51[i] < ext5_52[i])
            {
                e1 = ext5_51[i];
                e2 = ext5_52[i];
            }
            else
            {
                e1 = ext5_52[i];
                e2 = ext5_51[i];
            }

            nb1 = &nb0[e1->index + MAXE];
            nb2 = &nb0[e2->index + MAXE];
            for (; nb1 < nblim; nb1 += MAXE, nb2 += MAXE)
                if (*nb1 < *nb2)
                {
                    if (*nb1 < e1 || (*nb1 == e1 && *nb2 < e2))
                        break;
                }
                else
                {
                    if (*nb2 < e1 || (*nb2 == e1 && *nb1 < e2))
                        break;
                }

            if (nb1 >= nblim)
            {
                ext5_51[k] = e1;
                ext5_52[k] = e2;
                ++k;
            }
        }
        *next5_5 = k;
    }
    else
        *next5_5 = 0;
}

/**************************************************************************/

static void
min5c4_sw_legal(EDGE *e, EDGE **on4, int non4, EDGE **good, int *ngood)

/* Edge e (min form) has been switched (4-connected phase of mindeg=5).
   on4[0..non4-1] are all the edges in nf-4-cycles.
   Put into good[0..ngood-1] edges as desired for canon_edge().
*/

#define BANGCOL(e) (((long)degree[(e)->start] << 10) | (long)degree[(e)->end])
#define BANGCOL2(e) (degree[(e)->next->end] + degree[(e)->prev->end])
{
    long bestcol, col;
    int bestcol2, col2;
    EDGE *e1, *e2;
    int i, ng;

    bestcol = BANGCOL(e);
    col = BANGCOL(e->invers);
    bestcol2 = BANGCOL2(e);

    if (bestcol > col)
    {
        good[0] = e;
        ng = 1;
    }
    else if (bestcol == col)
    {
        good[0] = e;
        good[1] = e->invers;
        ng = 2;
    }
    else
    {
        good[0] = e->invers;
        ng = 1;
        bestcol = col;
    }

    for (i = 0; i < non4; ++i)
    {
        e1 = on4[i];
        e2 = e1->invers;
        if (degree[e1->start] >= 6 && degree[e1->end] >= 6 && e1 != e && wont_be_on_nf_4_cycle(e1))
        {
            col2 = BANGCOL2(e1);

            col = BANGCOL(e1);
            if (col > bestcol)
            {
                *ngood = 0;
                return;
            }
            else if (col == bestcol)
            {
                if (col2 > bestcol2)
                {
                    *ngood = 0;
                    return;
                }
                else if (col2 == bestcol2)
                    good[ng++] = e1;
            }

            col = BANGCOL(e2);
            if (col > bestcol)
            {
                *ngood = 0;
                return;
            }
            else if (col == bestcol)
            {
                if (col2 > bestcol2)
                {
                    *ngood = 0;
                    return;
                }
                else if (col2 == bestcol2)
                    good[ng++] = e2;
            }
        }
    }

    *ngood = ng;
}

/**************************************************************************/

static int
has_min5c4_sw(EDGE **on4, int non4)

/* on4[0..non4-1] is a complete list of all (min) edges in nf-4-cycles.
   Return TRUE if there is a valid switch-reduction.  Assume no nf-3-cycles.
*/

{
    EDGE *e;
    int i;

    for (i = 0; i < non4; ++i)
    {
        e = on4[i];

        if (degree[e->start] >= 6 && degree[e->end] >= 6 && wont_be_on_nf_4_cycle(e))
            return TRUE;
    }

    return FALSE;
}

/**************************************************************************/

static int
will_be_on_nf4_5red(EDGE *e)

/* Checks whether performing a 5-reduction at e (e starting at the
   vertex with valency 5) will produce a configuration with 
   one of the diagonals being on an nf-4-cycle. It is assumed
   that it is already assured that a 5-reduction here is possible
   (e.g. degree[e->start]=5).

   It somehow simulates the situation after the switch. This is
   a bit ugly, since after the switch on ONE side there will be
   an additional edge and on the other there won't.
*/

{
    EDGE *run, *run1, *last, *last1, *dummy, *e1, *e2;

    /* It is important for the correctness, that we go ONE step from e and
     two from e1, resp e2 */

    e1 = e->prev->prev->invers;
    e2 = e->next->next->invers;
    e = e->invers;

    RESETMARKS_V;
    last = e->prev; /* there will be an edge in between */
    run = e->next->next;
    MARK_V(run->end);
    while (run != last)
    {
        run = run->next;
        MARK_V(run->end);
    }

    last = e1->prev->prev; /* I cannot reach the edges that will be
			  missing after the reduction in two steps, so
			  here I can proceed "as usual" */
    run = e1->next->next;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    if (ISMARKED_V(run1->end))
        return 1;
    run1 = run1->next;
    if (ISMARKED_V(run1->end))
        return 1;
    while (run1 != last1)
    {
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 1;
    }
    run = run->next;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    if (ISMARKED_V(run1->end))
        return 1;
    run1 = run1->next;
    if (ISMARKED_V(run1->end))
        return 1;
    while (run1 != last1)
    {
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 1;
    }
    while (run != last)
    {
        run = run->next;
        dummy = run->invers;
        last1 = dummy->prev->prev;
        run1 = dummy->next->next;
        if (ISMARKED_V(run1->end))
            return 1;
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 1;
        while (run1 != last1)
        {
            run1 = run1->next;
            if (ISMARKED_V(run1->end))
                return 1;
        }
    }

    RESETMARKS_V;
    last = e->prev->prev;
    run = e->next; /* there will be an edge in between */
    MARK_V(run->end);
    while (run != last)
    {
        run = run->next;
        MARK_V(run->end);
    }

    last = e2->prev->prev; /* I cannot reach the edges that will be
                          missing after the reduction in two steps, 
			  so here I can proceed "as usual" */
    run = e2->next->next;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    if (ISMARKED_V(run1->end))
        return 1;
    run1 = run1->next;
    if (ISMARKED_V(run1->end))
        return 1;
    while (run1 != last1)
    {
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 1;
    }
    run = run->next;
    dummy = run->invers;
    last1 = dummy->prev->prev;
    run1 = dummy->next->next;
    if (ISMARKED_V(run1->end))
        return 1;
    run1 = run1->next;
    if (ISMARKED_V(run1->end))
        return 1;
    while (run1 != last1)
    {
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 1;
    }
    while (run != last)
    {
        run = run->next;
        dummy = run->invers;
        last1 = dummy->prev->prev;
        run1 = dummy->next->next;
        if (ISMARKED_V(run1->end))
            return 1;
        run1 = run1->next;
        if (ISMARKED_V(run1->end))
            return 1;
        while (run1 != last1)
        {
            run1 = run1->next;
            if (ISMARKED_V(run1->end))
                return 1;
        }
    }

    return 0;
}

/***********************************************************************/

static int
legal_5_min5_reduction(EDGE *e, EDGE *nf4cycleedges[], int numnf4cycleedges)

/* Checks whether the edge given is a legal reference edge for a 5-reduction
   in the minimum valency 5 connectivity 4 case, that is:

   (i) e->start has degree 5 (note that this way in case of both
        endpoints valency 5 the routine has to be called for e and
        e->invers due to the asymmetric behaviour of (iii)) 
   (ii) The two endpoints of e->next, e->prev have valency at least 6
   (iii) The two endpoints of e->next, e->prev have a common neighbour with
         valency 5 different from e->start, e->end, so especially
         e->next, e->prev, e->invers->next, e->invers->prev all are on
         nf-4-cycles.  
  (iv) after doing the 5-reduction e->next->next and e->prev->prev 
       will not be on 4-cycles

   Returns 1 in case it is a legal reduction, 0 otherwise. Assumes the
   non-existence of nf-3-cycles.  nf4cycleedges[0..numnf4cycleedges-1] 
   are the min forms of all edges on nf-4-cycles.
*/

{
    EDGE *dummy;

    if (degree[e->start] != 5)
        return 0;

    RESETMARKS;
    for (numnf4cycleedges--; numnf4cycleedges >= 0; numnf4cycleedges--)
        MARKLO(nf4cycleedges[numnf4cycleedges]);

    if (!ISMARKEDLO(e->next->min) || !ISMARKEDLO(e->prev->min))
        return 0;
    dummy = e->invers;
    if (!ISMARKEDLO(dummy->next->min) || !ISMARKEDLO(dummy->prev->min))
        return 0;
    if (!common_5_endpoint(e->next, e->prev))
        return 0;
    if (will_be_on_nf4_5red(e))
        return 0;

    return 1;
}

/**************************************************************************/

static void
min5c4_5_legal(EDGE *ref, EDGE **on4, int non4, EDGE **good, int *ngood)

/* e is the reference edge of a min5-5-expansion that has just been done.
   on4[0..non4-1] are the min forms of all edges on nf-4-cycles.
   There are no nf-3-cycles.
   Create in good[0..*ngood-1] a list of directed edges in the form
   required by canon_edge().
*/

{
    long bestdeg;
    EDGE *e, *elast;
    int i, ng;

    ng = 0;
    if (legal_5_min5_reduction(ref, on4, non4))
        good[ng++] = ref;
    if (legal_5_min5_reduction(ref->invers, on4, non4))
        good[ng++] = ref->invers;

    bestdeg = MAX(degree[ref->start], degree[ref->end]);

    for (i = 0; i < nv; ++i)
        if (degree[i] == 5)
        {
            e = elast = firstedge[i];
            do
            {
                if (degree[e->end] >= bestdeg && e != ref && e != ref->invers && legal_5_min5_reduction(e, on4, non4))
                {
                    if (degree[e->end] > bestdeg)
                    {
                        *ngood = 0;
                        return;
                    }
                    else
                        good[ng++] = e;
                }
                e = e->next;
            } while (e != elast);
        }

    *ngood = ng;
}

/**************************************************************************/

static void
scanmin5c4_1(int nbtot, int nbop, EDGE **on4, int non4)

/* This is the recursive procedure that creates nf-4-cycles for mindeg=5
   triangulations.  The first call is with a 4-connected triangulation
   made by a single switching from a 5-connected triangulation.
   on4[0..non4-1] are all edges on nf-4-cycles (min form).
*/

{
    EDGE *good[MAXE], *extAred;
    EDGE *ext5_sw[MAXE / 2], *ext5_51[MAXE], *ext5_52[MAXE];
    int next5_sw, next5_5;
    int newnon4, i, xnbtot, xnbop, ngood;

#ifdef PRE_FILTER_MIN5c4
    if (!(PRE_FILTER_MIN5c4))
        return;
#endif

#ifndef FIND_EXTENSIONS_MIN5c4
#define FIND_EXTENSIONS_MIN5c4 find_extensions_min5c4
#endif

    FIND_EXTENSIONS_MIN5c4(nbtot, nbop, NULL, 0, on4, non4,
                           ext5_sw, &next5_sw, ext5_51, ext5_52, &next5_5);

    if (nv == maxnv)
    {
        if (pswitch)
            startpolyscan(nbtot, nbop); /* Saves the group! */
        else
            got_one(nbtot, nbop, 4);

        if (minconnec < 4 && non4 >= 6)
            scanmin5c3_0(nbtot, nbop, on4, non4);
    }

    for (i = 0; i < next5_sw; ++i)
    {
        switch_edge(ext5_sw[i]);
#ifdef FAST_FILTER_MIN5c4
        if (FAST_FILTER_MIN5c4)
#endif
        {
            newnon4 = non4;
            add_new_nf4_cycles(ext5_sw[i], on4, &newnon4);

            min5c4_sw_legal(ext5_sw[i], on4, newnon4, good, &ngood);
            if (ngood > 0 && canon_edge(good, ngood, degree, numbering, &xnbtot, &xnbop))
                scanmin5c4_1(xnbtot, xnbop, on4, newnon4);
        }
        switch_edge_back(ext5_sw[i]);
    }

    for (i = 0; i < next5_5; ++i)
    {
        extAred = extend_min5_a(ext5_51[i], ext5_52[i]);
#ifdef FAST_FILTER_MIN5c4
        if (FAST_FILTER_MIN5c4)
#endif
        {
            if (extAred->start == nv - 1)
            {
                on4[non4] = extAred->next->min;
                on4[non4 + 1] = extAred->prev->min;
                newnon4 = non4 + 2;
            }
            else
            {
                on4[non4] = extAred->invers->next->min;
                on4[non4 + 1] = extAred->invers->prev->min;
                newnon4 = non4 + 2;
            }

            if (!has_min5c4_sw(on4, newnon4))
            {
                min5c4_5_legal(extAred, on4, newnon4, good, &ngood);
                if (ngood > 0 && canon_edge(good, ngood, degree, numbering, &xnbtot, &xnbop))
                    scanmin5c4_1(xnbtot, xnbop, on4, newnon4);
            }
        }
        reduce_min5_a(extAred);
    }
}

/**************************************************************************/

static void
scanmin5c4_0(int nbtot, int nbop, EDGE **bang, int nbang)

/* This is the first procedure that creates nf-4-cycles for mindeg=5
   triangulations.  It is called with a 5-connected triangulation.
   bang[0..nbang-1] are all proper bangles and possibly some improper
   bangles (degree 5 at one or both ends).  For this first step, only
   a switching operation is possible.
*/

{
    EDGE *good[MAXE], *on4[MAXE / 2];
    EDGE *ext5_sw[MAXE / 2], *ext5_51[1], *ext5_52[1]; /* 5-expansion impossible */
    int next5_sw, next5_5;
    int i, xnbtot, xnbop, ngood, non4;
    EDGE *firstedge_save[MAXN];

    if (nv < splitlevel && res > 0)
        return;

    if (splitlevel > 0)
        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];

#ifdef PRE_FILTER_MIN5c4
    if (!(PRE_FILTER_MIN5c4))
        return;
#endif

#ifndef FIND_EXTENSIONS_MIN5c4
#define FIND_EXTENSIONS_MIN5c4 find_extensions_min5c4
#endif

    FIND_EXTENSIONS_MIN5c4(nbtot, nbop, bang, nbang, NULL, 0,
                           ext5_sw, &next5_sw, ext5_51, ext5_52, &next5_5);

    for (i = 0; i < next5_sw; ++i)
    {
        switch_edge(ext5_sw[i]);
#ifdef FAST_FILTER_MIN5c4
        if (FAST_FILTER_MIN5c4)
#endif
        {
            non4 = 0;
            add_new_nf4_cycles(ext5_sw[i], on4, &non4);

            min5c4_sw_legal(ext5_sw[i], on4, non4, good, &ngood);
            if (ngood > 0 && canon_edge(good, ngood, degree, numbering, &xnbtot, &xnbop))
                scanmin5c4_1(xnbtot, xnbop, on4, non4);
        }
        switch_edge_back(ext5_sw[i]);
    }

    if (splitlevel > 0)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/**************************************************************************/

static void
scanmin5(int nbtot, int nbop, int dosplit, EDGE **prevA, int nprevA,
         EDGE **bangle, int nbangles)

/* The main node of the recursion for triangulations with minimum
   degree 5, connectivity 3 or 4.  This part of the recursion makes
   5-connected triangulations.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   If dosplit==TRUE, this is the place to do splitting (if any).
   prev[0..nprevA-1] is the list of consecutive A operations leading
   to this graph, given by their central edges.
   If nprevA == 0, this graph wasn't made with A.
   bangle[0..nbangles-1] contains the edges which are central
   edges of a bangle.
*/

{
    EDGE *firstedge_save[MAXN];
    EDGE *extA1[MAXN * MAXN / 4 + 10], *extA2[MAXN * MAXN / 4 + 10],
        *extB[MAXE], *extC[MAXN];
    EDGE *extAred, *extBred, *extCred, *extCanchor;
    int extBmirror[MAXE];
    EDGE *good_or[MAXE], *good_mir[MAXE];
    EDGE *newprevA[MAXN];
    EDGE *newbang[MAXE / 2];
    int newnbang;
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int nextA, nextB, nextC, i, j, k;
    int xnbtot, xnbop;
    int colour[MAXN];

    if (nv == maxnv)
    {
        if (pswitch)
            startpolyscan(nbtot, nbop); /* Saves the group! */
        else
            got_one(nbtot, nbop, 5);
        if (nbangles > 0)
            scanmin5c4_0(nbtot, nbop, bangle, nbangles);
        return;
    }

    if (dosplit)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_MIN5
    if (!(PRE_FILTER_MIN5))
        return;
#endif

#ifndef FIND_EXTENSIONS_MIN5
#define FIND_EXTENSIONS_MIN5 find_extensions_min5
#endif

    FIND_EXTENSIONS_MIN5(nbtot, nbop, extA1, extA2, &nextA, extB, extBmirror,
                         &nextB, extC, &nextC, (nprevA == 0 ? NULL : prevA[nprevA - 1]));

    if (nbangles > 0)
        scanmin5c4_0(nbtot, nbop, bangle, nbangles);

    for (i = 0; i < nextA; ++i)
    {
        extAred = extend_min5_a(extA1[i], extA2[i]);
#ifdef FAST_FILTER_MIN5
        if (FAST_FILTER_MIN5)
#endif
        {
            min5_a_legal(extAred, good_or, &ngood_or, &ngood_ref,
                         good_mir, &ngood_mir, &ngood_mir_ref, prevA, nprevA);

            if (ngood_ref + ngood_mir_ref > 0)
            {
                newnbang = 0;
                for (j = 0; j < nbangles; ++j)
                    if (is_in_5_bangle(bangle[j]))
                        newbang[newnbang++] = bangle[j];
                if (is_in_5_bangle(extAred))
                    newbang[newnbang++] = extAred;

                if (nv == maxnv)
                {
                    k = 0;
                    for (j = 0; j < newnbang; ++j)
                        if (degree[newbang[j]->start] >= 6 && degree[newbang[j]->end] >= 6)
                            newbang[k++] = newbang[j];
                    newnbang = k;
                }

                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref && ((newnbang == 0 && minconnec == 4) || minconnec == 5))
                {
                    got_one(1, 1, 5); /* Note: -p implies -G */
                }
                else if (ngood_or + ngood_mir == 1)
                {
                    prevA[nprevA] = extAred;
                    scanmin5(1, 1, nv == splitlevel, prevA, nprevA + 1,
                             newbang, newnbang);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    prevA[nprevA] = extAred;
                    scanmin5(xnbtot, xnbop, nv == splitlevel,
                             prevA, nprevA + 1, newbang, newnbang);
                }
            }
        }
        reduce_min5_a(extAred);
    }

    for (i = 0; i < nextB; ++i)
    {
        extBred = extend_min5_b(extB[i], extBmirror[i]);
#ifdef FAST_FILTER_MIN5
        if (FAST_FILTER_MIN5)
#endif
        {
            if (!has_min5_a())
            {
                min5_b_legal(extBred, extBmirror[i], good_or, &ngood_or,
                             &ngood_ref, good_mir, &ngood_mir, &ngood_mir_ref);

                if (ngood_ref + ngood_mir_ref > 0)
                {
                    if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                            good_mir, ngood_mir, ngood_mir_ref,
                                            degree, numbering, &xnbtot, &xnbop))
                    {
                        all_5_bangles(newbang, &newnbang);
                        scanmin5(xnbtot, xnbop, nv == splitlevel || nv == splitlevel + 1,
                                 newprevA, 0, newbang, newnbang);
                    }
                }
            }
        }
        reduce_min5_b(extBred, extBmirror[i]);
    }

    for (i = 0; i < nextC; ++i)
    {
        extCred = extend_min5_c(extC[i], &extCanchor);
#ifdef FAST_FILTER_MIN5
        if (FAST_FILTER_MIN5)
#endif
        {
            if (!has_min5_a() && !has_min5_b())
            {
                for (j = 0; j < nv - 1; ++j)
                    if (is_min5_c_centre(j))
                        colour[j] = 2;
                    else
                        colour[j] = degree[j];
                colour[nv - 1] = 2;

                if (canon(colour, numbering, &xnbtot, &xnbop))
                {
                    all_5_bangles(newbang, &newnbang);
                    scanmin5(xnbtot, xnbop, nv >= splitlevel && nv <= splitlevel + 4,
                             newprevA, 0, newbang, newnbang);
                }
            }
        }
        reduce_min5_c(extCred, extCanchor);
    }

    if (dosplit)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/****************************************************************************/

static void
make_cube(void)

/* Make a cube using the first 24 edges */
{
    int i;
    EDGE *buffer;

    for (i = 0; i < 8; i++)
    {
        buffer = edges + 3 * i;
        firstedge[i] = buffer;
        degree[i] = 3;
        buffer->next = buffer + 1;
        buffer->prev = buffer + 2;
        buffer->start = i;
        buffer++;
        buffer->next = buffer + 1;
        buffer->prev = buffer - 1;
        buffer->start = i;
        buffer++;
        buffer->next = buffer - 2;
        buffer->prev = buffer - 1;
        buffer->start = i;
    }

    buffer = edges; /* edge number 0 */
    buffer->end = 4;
    buffer->invers = edges + 12;
    buffer->min = buffer;

    buffer++; /* edge number 1 */
    buffer->end = 3;
    buffer->invers = edges + 11;
    buffer->min = buffer;

    buffer++; /* edge number 2 */
    buffer->end = 1;
    buffer->invers = edges + 4;
    buffer->min = buffer;

    buffer++; /* edge number 3 */
    buffer->end = 5;
    buffer->invers = edges + 15;
    buffer->min = buffer;

    buffer++; /* edge number 4 */
    buffer->end = 0;
    buffer->invers = edges + 2;
    buffer->min = buffer->invers;

    buffer++; /* edge number 5 */
    buffer->end = 2;
    buffer->invers = edges + 7;
    buffer->min = buffer;

    buffer++; /* edge number 6 */
    buffer->end = 6;
    buffer->invers = edges + 18;
    buffer->min = buffer;

    buffer++; /* edge number 7 */
    buffer->end = 1;
    buffer->invers = edges + 5;
    buffer->min = buffer->invers;

    buffer++; /* edge number 8 */
    buffer->end = 3;
    buffer->invers = edges + 10;
    buffer->min = buffer;

    buffer++; /* edge number 9 */
    buffer->end = 7;
    buffer->invers = edges + 21;
    buffer->min = buffer;

    buffer++; /* edge number 10 */
    buffer->end = 2;
    buffer->invers = edges + 8;
    buffer->min = buffer->invers;

    buffer++; /* edge number 11 */
    buffer->end = 0;
    buffer->invers = edges + 1;
    buffer->min = buffer->invers;

    buffer++; /* edge number 12 */
    buffer->end = 0;
    buffer->invers = edges;
    buffer->min = buffer->invers;

    buffer++; /* edge number 13 */
    buffer->end = 5;
    buffer->invers = edges + 17;
    buffer->min = buffer;

    buffer++; /* edge number 14 */
    buffer->end = 7;
    buffer->invers = edges + 22;
    buffer->min = buffer;

    buffer++; /* edge number 15 */
    buffer->end = 1;
    buffer->invers = edges + 3;
    buffer->min = buffer->invers;

    buffer++; /* edge number 16 */
    buffer->end = 6;
    buffer->invers = edges + 20;
    buffer->min = buffer;

    buffer++; /* edge number 17 */
    buffer->end = 4;
    buffer->invers = edges + 13;
    buffer->min = buffer->invers;

    buffer++; /* edge number 18 */
    buffer->end = 2;
    buffer->invers = edges + 6;
    buffer->min = buffer->invers;

    buffer++; /* edge number 19  */
    buffer->end = 7;
    buffer->invers = edges + 23;
    buffer->min = buffer;

    buffer++; /* edge number 20 */
    buffer->end = 5;
    buffer->invers = edges + 16;
    buffer->min = buffer->invers;

    buffer++; /* edge number 21 */
    buffer->end = 3;
    buffer->invers = edges + 9;
    buffer->min = buffer->invers;

    buffer++; /* edge number 22 */
    buffer->end = 4;
    buffer->invers = edges + 14;
    buffer->min = buffer->invers;

    buffer++; /* edge number 23 */
    buffer->end = 6;
    buffer->invers = edges + 19;
    buffer->min = buffer->invers;

    nv = 8;
    ne = 24;
}

/************************************************************************/

static int
threeconn_quad(EDGE *e)

/* Difference to "threeconn": On the left hand side of e there must be a
   quadrangle instead of a triangle.

   tests whether the graph obtained by deleting EDGE e is still 3-connected.
   The edge e may have been deleted or not, but the values in e must be
   as before it was (possibly) deleted. The map must have been 3-connected
   before -- so especially there weren't any vertices of degree 2.
   degree[] is not assumed correct for the endvertices of e.

   On the left hand side of e there must be a quadrangle.
   (e->left_facesize==4) and it is assumed that it is checked before
   that the endvertices adjacent to e have degree at least 3 after the
   deletion.

   The way it works: If there is a 2-cut, e->start and e->end cannot
   be contained, but they must be in different components after
   removing e, so both faces neighbouring e must contain a
   cutvertex. Because on the left hand side there is a quadrangle this
   means that v=e->prev->end or w=e->invers->next->end MUST be
   contained.  It is checked whether v or w is contained in a face that
   shares yet another vertex with the face formerly on the right hand
   side of e (the new face obtained by deleting e).

   Note that this face cannot be the one v shares with e->start or
   w shares with e->end because that would have meant that a 2-cut
   already existed in the graph.

   Returns 1 if it is 3-connected after deleting e, 0 else.  */

{
    EDGE *run, *start, *end;

    RESETMARKS_V;

    /* The endvertices of e need not be marked */
    for (run = e->next, end = e->invers->prev->invers;
         run != end; run = run->invers->next)
        MARK_V(run->end);

    /* OK -- now test v. */

    start = e->prev->invers;

    end = start->prev;

    /* the face on the right hand side of start contains e->start so 
       need not be tested: */

    start = start->next;

    while (start != end)
    {
        run = start->invers;
        start = start->next;
        for (; run != start; run = run->prev->invers)
            if (ISMARKED_V(run->start))
                return 0;
    }

    /* OK -- now test w. The face that also contains v was already tested */

    if (degree[end->end] == 3)
        return 1;

    start = end->invers->next;
    end = end->invers->prev->prev;

    while (start != end)
    {
        run = start->invers;
        start = start->next;
        for (; run != start; run = run->prev->invers)
            if (ISMARKED_V(run->start))
                return 0;
    }

    return 1;
}

/************************************************************************/

static int
twoconn_quad(EDGE *e)

/* tests whether the graph obtained by deleting EDGE e is still 2-connected.
   The edge e may have been deleted or not, but the values in e must be
   as before it was (possibly) deleted. The map must have been 2-connected
   before.  degree[] is not assumed correct for the endvertices of e.

   On the left hand side of e there must be a quadrangle (e->left_facesize==3).

   If there is a 1-cut, it cannot be e->start or e->end (otherwise
   it was a 1-cut before), but they must be in different components, (same
   reason), so v=e->prev->end or w=e->invers->next->end MUST be the cutvertex.
   It is checked whether v or w are contained in the face on the right hand side
   of e (before deleting). 

   Returns 1 if it is 2-connected after deleting e, 0 else.
*/

{
    EDGE *run, *end;

    RESETMARKS_V;

    MARK_V(e->prev->end);
    MARK_V(e->invers->next->end);

    end = e->next->invers;

    for (run = e->invers->prev; run != end; run = run->invers->prev)
        if (ISMARKED_V(run->end))
            return 0;

    return 1;
}

/***************************************************************/

#if 0
static int
edge_del_conn_quad(EDGE *e, int connectivity)

/* computes the connectivity of the graph after the removal of edge e.

   The edge e may have been deleted or not, but the values in e must be
   as before it was (possibly) deleted.  degree[] is not assumed correct
   for the endvertices of e.
   The variable connectivity gives the largest possible value k in {1,2,3}
   so that the map is k-connected before the removal of e. Larger values
   for the connectivity lead to an error. The value returned is also one
   of 1,2,3.

   On the left hand side of e there must be a quadrangle (e->left_facesize==4).
*/

{
  if (connectivity==3) return (2+threeconn_quad(e));
  if (connectivity==2) return (1+twoconn_quad(e));
  return 1;
}
#endif

/************************************************************************/

static void
prune_bip_edgelist(EDGE *old[], int numold, EDGE *newe[], int *numnew)

/* Copy from old[0..numold-1] to newe[0..*numnew-1] each edge e with
 *    these two properties:
 *       1. Both ends of e have degree >= minpolydeg+1.
 *          2. e is contained in a 4-face.
 *            It is legal that old and newe and &numold and numnew are the same.
 */

{
    int i, counter = 0;
    EDGE *e;

    for (i = 0; i < numold; i++, old++)
    {
        e = *old;
        if (degree[e->start] > minpolydeg && degree[e->end] > minpolydeg && (e->left_facesize == 4 || e->invers->left_facesize == 4))
            newe[counter++] = e;
    }

    *numnew = counter;
}

/*************************************************************************/

static int
maybe_delete_bip(EDGE *edel, int oldmaxface, int oldmaxlist0, int oldmaxlist1,
                 int *newmaxface, int *newmaxlist0, int *newmaxlist1,
                 EDGE *good_or[], int *ngood_or, int *ncan_or,
                 EDGE *good_inv[], int *ngood_inv, int *ncan_inv, int *connec)

/* Assumes there is a 4-face on the left of *edel, and that *edel can be
   deleted while keeping degrees >= minpolydeg.  Also, the new face created
   will be a largest face.  oldmaxface is the size of the largest face so far,
   and inmaxface[oldmaxlist0..oldmaxlist1-1] are the edges with a face of
   maximum size on the left.  *connec is the current connectivity.

   This procedure deletes *edel provided the result is at least as connected
   as minpolyconnec, and that the procedure believes the re-insertion of *edel
   might be a canonical edge insertion.  The latter decision is based on
   four combinatorial invariates: the three vertex degrees at the ends of
   *edel and on its left, and the size of the face to the left of edel->prev.

   In case *edel passes the test and is deleted, the edges which may
   represent the re-insertion of *edel and optimise the four-part invariant
   mentioned above are put in good_or[0..*ncan_or-1] and
   good_inv[0..*ncan_inv-1].  This will include at least one of the edges
   edel->prev, edel->invers->next and (if there is also a 4-face on the
   right of *edel) edel->next and edel->invers->prev.  Then all other edges
   which might possibly represent canonical edge insertions are put in
   good_or[*ncan_or..*ngood_or-1] or good_inv[*ncan_inv..*ngood_inv-1].
   The *_or edges are those for which the inserted edge will be in the
   next direction, and the *_inv edges .. the prev direction.

   In addition, if *edel is deleted, inmaxface[*newmaxlist0..*newmaxlist1-1]
   will have all edges with a maximum face on the left (that size being put
   into *newmaxface).  This list may overlap
   inmaxface[oldmaxlist0..oldmaxlist1-1] if the max face size does not
   increase.

   In the case of value 0, *connec is changed to represent the new
   connectivity.
   Return values:   0 = ok
                    1 = rejected as connectivity will be too small
                    2 = rejected by colour
*/
{

#define DEGENDB(e) (degree[e->end])
#define OROKB(e) ISNEQADJ(e->start, e->invers->prev->invers->prev->end)
#define INVOKB(e) ISNEQADJ(e->start, e->invers->next->invers->next->end)
#define REJECTB(x)    \
    {                 \
        ++degree[v1]; \
        ++degree[v2]; \
        return x;     \
    }
#define ORTESTB(e)                          \
    {                                       \
        col = DEGENDB(e);                   \
        if (col > maxcol)                   \
        {                                   \
            if (OROKB(e))                   \
                REJECTB(2)                  \
        }                                   \
        else if (col == maxcol && OROKB(e)) \
            good_or[ng_or++] = e;           \
    }
#define INVTESTB(e)                          \
    {                                        \
        col = DEGENDB(e);                    \
        if (col > maxcol)                    \
        {                                    \
            if (INVOKB(e))                   \
                REJECTB(2)                   \
        }                                    \
        else if (col == maxcol && INVOKB(e)) \
            good_inv[ng_inv++] = e;          \
    }
#define ORCOLB(e) (((long)degree[e->invers->prev->end] << 10) + e->left_facesize)
#define INVCOLB(e) \
    (((long)degree[e->invers->next->end] << 10) + e->invers->left_facesize)

    EDGE *e1, *e2, *e3, *e4, *e5, *e6, *ee, *ea, *eb;
    long col, maxcol;
    int k, i, ng_or, ng_inv, nc_or, nc_inv;
    int maxface, v1, v2, v3, v4, v5, v6;
    int da, db, mindeg, maxdeg, nml1;
    int newconnec;

    maxface = *newmaxface = edel->invers->left_facesize + 2;
    if (maxface > oldmaxface)
        oldmaxlist0 = oldmaxlist1;
    *newmaxlist0 = oldmaxlist0;

    *ngood_or = *ngood_inv = 0;

    /* Now old edges that will be on a largest face (if *edel is deleted)
    are in places oldmaxlist0..oldmaxlist1-1.  New edges will be from
    oldmaxlist1 to *newmaxlist1-1, but *newmaxlist1 is not set yet. */

    v1 = edel->start;
    v2 = edel->end;

    /* maxdeg = (degree[v1] > degree[v2] ? degree[v1] : degree[v2]) - 1; */
    if (degree[v1] < degree[v2])
    {
        mindeg = degree[v1] - 1;
        maxdeg = degree[v2] - 1;
    }
    else
    {
        mindeg = degree[v2] - 1;
        maxdeg = degree[v1] - 1;
    }

    e1 = edel->prev;
    v3 = e1->end;
    e4 = edel->next;
    v4 = e4->end;
    e3 = edel->invers->prev;
    v6 = e3->end;
    e2 = edel->invers->next;
    v5 = e2->end;

    /* The following is an efficiency short-cut, but it is assumed
      to have been done below. */

    if (ISNEQADJ(v3, v6) && (degree[v3] > maxdeg || degree[v6] > maxdeg))
        return 2;
    if (ISNEQADJ(v4, v5) && (degree[v4] > maxdeg || degree[v5] > maxdeg))
        return 2;

    --degree[v1];
    --degree[v2];

    maxcol = nc_or = nc_inv = 0;

    if (degree[v1] == maxdeg)
    {
        col = DEGENDB(e1);
        maxcol = col;
        good_or[nc_or++] = e1;

        if (maxface == 6)
        {
            col = DEGENDB(e4);
            if (col > maxcol)
            {
                nc_or = nc_inv = 0;
                good_inv[nc_inv++] = e4;
                maxcol = col;
            }
            else if (col == maxcol)
                good_inv[nc_inv++] = e4;
        }
    }

    if (degree[v2] == maxdeg)
    {
        col = DEGENDB(e2);
        if (col > maxcol)
        {
            nc_or = nc_inv = 0;
            good_inv[nc_inv++] = e2;
            maxcol = col;
        }
        else if (col == maxcol)
            good_inv[nc_inv++] = e2;

        if (maxface == 6)
        {
            col = DEGENDB(e3);
            if (col > maxcol)
            {
                nc_or = nc_inv = 0;
                good_or[nc_or++] = e3;
                maxcol = col;
            }
            else if (col == maxcol)
                good_or[nc_or++] = e3;
        }
    }

    ng_or = nc_or;
    ng_inv = nc_inv;

    if (maxface == 6)
    {
        /* Recall from above that all degrees are <= maxdeg whenever
        edges are possible. */

        e5 = e1->invers->prev;
        e6 = e3->invers->prev;

        if (ISNEQADJ(v3, v6))
        {
            if (degree[v3] == maxdeg)
            {
                if (degree[v1] > maxcol)
                    REJECTB(2)
                else if (degree[v1] == maxcol)
                    good_inv[ng_inv++] = e1->invers;
                if (degree[v5] > maxcol)
                    REJECTB(2)
                else if (degree[v5] == maxcol)
                    good_or[ng_or++] = e5;
            }

            if (degree[v6] == maxdeg)
            {
                if (degree[v4] > maxcol)
                    REJECTB(2)
                else if (degree[v4] == maxcol)
                    good_or[ng_or++] = e6;
                if (degree[v2] > maxcol)
                    REJECTB(2)
                else if (degree[v2] == maxcol)
                    good_inv[ng_inv++] = e3->invers;
            }
        }

        if (ISNEQADJ(v4, v5))
        {
            if (degree[v4] == maxdeg)
            {
                if (degree[v6] > maxcol)
                    REJECTB(2)
                else if (degree[v6] == maxcol)
                    good_inv[ng_inv++] = e6->invers;
                if (degree[v1] > maxcol)
                    REJECTB(2)
                else if (degree[v1] == maxcol)
                    good_or[ng_or++] = e4->invers;
            }

            if (degree[v5] == maxdeg)
            {
                if (degree[v2] > maxcol)
                    REJECTB(2)
                else if (degree[v2] == maxcol)
                    good_or[ng_or++] = e2->invers;
                if (degree[v3] > maxcol)
                    REJECTB(2)
                else if (degree[v3] == maxcol)
                    good_inv[ng_inv++] = e5->invers;
            }
        }

        nml1 = oldmaxlist1;
        inmaxface[nml1++] = e1->invers;
        inmaxface[nml1++] = e2;
        inmaxface[nml1++] = e3->invers;
        inmaxface[nml1++] = e4;
        inmaxface[nml1++] = e5->invers;
        inmaxface[nml1++] = e6->invers;
    }
    else
    {
        /* Recall from above that degree[v3,v6] <= maxdeg if v3 notadj v6
                              and degree[v4,v5] <= maxdeg if v4 notadj v5 */

        e5 = e1->invers->prev;

        if (ISNEQADJ(v3, v6))
        {
            if (degree[v3] == maxdeg)
            {
                if (degree[v5] > maxcol)
                    REJECTB(2)
                else if (degree[v5] == maxcol)
                    good_or[ng_or++] = e5;
            }
            if (degree[v6] == maxdeg)
            {
                if (degree[v2] > maxcol)
                    REJECTB(2)
                else if (degree[v2] == maxcol)
                    good_inv[ng_inv++] = e3->invers;
            }
        }
        if (ISNEQADJ(v4, v5))
        {
            if (degree[v5] == maxdeg)
            {
                if (degree[v3] > maxcol)
                    REJECTB(2)
                else if (degree[v3] == maxcol)
                    good_inv[ng_inv++] = e5->invers;
            }
            if (degree[v4] == maxdeg)
            {
                if (degree[v1] > maxcol)
                    REJECTB(2)
                else if (degree[v1] == maxcol)
                    good_or[ng_or++] = e4->invers;
            }
        }

        nml1 = oldmaxlist1;

        ea = e2;
        eb = e3->invers->prev;
        do
        {
            if (ISNEQADJ(ea->end, eb->end))
            {
                da = DEGENDB(ea);
                db = DEGENDB(eb);
                if (da > maxdeg || db > maxdeg)
                    REJECTB(2);

                if (da == maxdeg)
                {
                    if (degree[ea->start] > maxcol)
                        REJECTB(2)
                    else if (degree[ea->start] == maxcol)
                        good_or[ng_or++] = ea->invers;
                }
                if (db == maxdeg)
                {
                    if (degree[eb->start] > maxcol)
                        REJECTB(2)
                    else if (degree[eb->start] == maxcol)
                        good_inv[ng_inv++] = eb->invers;
                }
            }
            inmaxface[nml1++] = ea;
            ea = eb->next;
            eb = eb->invers->prev;
            if (eb == edel)
                eb = e1;
        } while (eb != e5);

        inmaxface[nml1++] = e5->invers;
        inmaxface[nml1++] = e1->invers;
        inmaxface[nml1++] = e4;
    }

    /* Now test old edges still on max faces */

    for (i = oldmaxlist0; i < oldmaxlist1; ++i)
    {
        ee = inmaxface[i];
        if (degree[ee->start] > maxdeg)
        {
            if (INVOKB(ee))
                REJECTB(2);
            ee = ee->prev;
            if (OROKB(ee))
                REJECTB(2);
        }
        else if (degree[ee->start] == maxdeg)
        {
            INVTESTB(ee);
            ee = ee->prev;
            ORTESTB(ee);
        }
    }

    if (mindeg < *connec)
        newconnec = mindeg;
    else if (*connec == 3)
        newconnec = 2 + threeconn_quad(edel);
    else if (*connec == 2)
        newconnec = 1 + twoconn_quad(edel);
    else
        newconnec = 1;

    if (newconnec < minpolyconnec)
        REJECTB(1);

    /* Now we have complete success!  Just prune the lists a bit and
    complete the deletion of edel. */

    edel->prev->next = edel->next;
    edel->next->prev = edel->prev;
    ee = edel->invers;
    ee->prev->next = ee->next;
    ee->next->prev = ee->prev;

    for (i = oldmaxlist1; i < nml1; ++i)
        inmaxface[i]->left_facesize = maxface;

    firstedge[v1] = e1;
    firstedge[v2] = e2;
    ne -= 2;

    *connec = newconnec;

    *newmaxlist1 = nml1;
    *ngood_or = ng_or;
    *ngood_inv = ng_inv;
    *ncan_or = nc_or;
    *ncan_inv = nc_inv;

    if (ng_or + ng_inv == 1)
        return 0;

    maxcol = 0;
    for (i = 0; i < nc_or; ++i)
        if (ORCOLB(good_or[i]) > maxcol)
            maxcol = ORCOLB(good_or[i]);
    for (i = 0; i < nc_inv; ++i)
        if (INVCOLB(good_inv[i]) > maxcol)
            maxcol = INVCOLB(good_inv[i]);

    for (i = 0, k = 0; i < nc_or; ++i)
        if (ORCOLB(good_or[i]) == maxcol)
            good_or[k++] = good_or[i];
    *ncan_or = k;
    for (; i < ng_or; ++i)
    {
        col = ORCOLB(good_or[i]);
        if (col == maxcol)
            good_or[k++] = good_or[i];
        else if (col > maxcol)
        {
            insert_edge_general(edel);
            *ngood_or = *ngood_inv = 0;
            return 2;
        }
    }
    *ngood_or = ng_or = k;

    for (i = 0, k = 0; i < nc_inv; ++i)
        if (INVCOLB(good_inv[i]) == maxcol)
            good_inv[k++] = good_inv[i];
    *ncan_inv = k;
    for (; i < ng_inv; ++i)
    {
        col = INVCOLB(good_inv[i]);
        if (col == maxcol)
            good_inv[k++] = good_inv[i];
        else if (col > maxcol)
        {
            insert_edge_general(edel);
            *ngood_or = *ngood_inv = 0;
            return 2;
        }
    }
    *ngood_inv = ng_inv = k;

    return 0;
}

/*************************************************************************/

static void
scanbip(int nbtot, int nbop, EDGE *oldfeas[], int noldfeas,
        int oldmaxface, int oldmaxlist0, int oldmaxlist1, int connec)

/* This is the recursive search procedure for bipartite graphs.
 * oldfeas[0..noldfeas-1] are the edges which can be removed without
 * violating the degree bound minpolydeg, with some (but not necessarily
 * all) missing because they are known to violate the connectivity
 * bound minpolyconnec.  nbtot/nbop represent the group, as usual.
 * oldmaxface is the size of the largest face.
 * inmaxface[oldmaxlist0..oldmaxlist1-1] lists the edges whose
 * left face has greatest size (unless that is 4).  connec is
 * the actual connectivity. */
{
    EDGE *newfeas[MAXE / 2], *good_or[MAXE], *good_inv[MAXE], *e, *esave;
    int i, nnewfeas, minimal[MAXE / 2], newmaxface;
    int code, xnbtot, xnbop;
    int ngood_or, ncan_or, ngood_inv, ncan_inv;
    int newmaxlist0, newmaxlist1, newconnec;

    if (ne <= edgebound[1])
        got_one(nbtot, nbop, connec);
    if (ne == edgebound[0])
        return;
    if (ne - 2 * noldfeas > edgebound[1])
        return;

#ifdef PRE_FILTER_BIPPOLY
    if (!(PRE_FILTER_BIPPOLY))
        return;
#endif

    mark_edge_orbits(oldfeas, noldfeas, minimal, nbtot);

    for (i = 0; i < noldfeas; ++i)
    {
        if (!minimal[i])
            continue;

        e = oldfeas[i];
        if (e->left_facesize != 4)
            e = e->invers;
        if (e->invers->left_facesize < oldmaxface - 2 || e->invers->left_facesize == maxfacesize)
            continue;

        AMDELEDGE(e->start, e->end);

        newconnec = connec;
        code = maybe_delete_bip(e, oldmaxface, oldmaxlist0, oldmaxlist1,
                                &newmaxface, &newmaxlist0, &newmaxlist1,
                                good_or, &ngood_or, &ncan_or,
                                good_inv, &ngood_inv, &ncan_inv, &newconnec);

        if (code == 0)
        {
#ifdef FAST_FILTER_BIPPOLY
            if (FAST_FILTER_BIPPOLY)
#endif
            {
                if (ngood_or + ngood_inv == 1)
                {
                    esave = oldfeas[i];
                    oldfeas[i] = oldfeas[noldfeas - 1];
                    prune_bip_edgelist(oldfeas, noldfeas - 1, newfeas, &nnewfeas);
                    oldfeas[i] = esave;
                    scanbip(1, 1, newfeas, nnewfeas,
                            newmaxface, newmaxlist0, newmaxlist1, newconnec);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ncan_or,
                                             good_inv, ngood_inv, ncan_inv,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    /* The following line corrects for the fact that canon*()
                    finds each automorphism twice if the maximum degree is
                    at most 2.  However, it interferes with -o so is disabled.
		    CHECK THIS 

                    if (ne <= 2*nv && maxdegree() <= 2) xnbtot = xnbop; */

                    esave = oldfeas[i];
                    oldfeas[i] = oldfeas[noldfeas - 1];
                    prune_bip_edgelist(oldfeas, noldfeas - 1, newfeas, &nnewfeas);
                    oldfeas[i] = esave;
                    scanbip(xnbtot, xnbop, newfeas, nnewfeas,
                            newmaxface, newmaxlist0, newmaxlist1, newconnec);
                }
            }
            insert_edge_general(e);
        }
        else if (code == 1)
        {
            oldfeas[i] = oldfeas[noldfeas - 1];
            minimal[i] = minimal[noldfeas - 1];
            --i;
            --noldfeas;
        }
        AMADDEDGE(e->start, e->end);
    }
}

/*************************************************************************/

static int
con_quad(void)

/* tests and returns the connectivity of a simple quadrangulation.
   Possible values are 2 and 3 */
{

    int i, othervertex;
    EDGE *start, *run, *end, *runend, *buffer;
    static EDGE *lastprob = NULL;
    static int lastdeg = -1;
    /* the last two remember edges or vertices where the last time there
     was a problem -- test these first */

    if (lastdeg >= 0)
    {
        if (degree[lastdeg] == 2)
            return 2;
    }

    RESETMARKS;

    if ((lastprob != NULL) && (degree[lastprob->start] > 3))
    {
        MARK(lastprob);
        buffer = lastprob->invers->prev;
        othervertex = buffer->end;
        if (degree[othervertex] > 3)
        {
            MARK(buffer->invers->prev);
            runend = lastprob->prev;
            run = lastprob->next->next;
            while (run != runend)
            {
                if (run->invers->prev->end == othervertex)
                    return 2;
                run = run->next;
            }
        }
    }

    lastdeg = -1;
    lastprob = NULL;

    for (i = 0; i < nv; i++)
        if (degree[i] == 2)
        {
            lastdeg = i;
            return 2;
        }

    /* Note: edges on the other side of degree 3 vertices in a 
     quadrangle can be marked as non-starts. but this makes it
     much slower (doing it in the loop or doing it before. 
     Don't ask why... */

    for (i = 0; i < nv - 1; i++) /* the faces around nv are all tested from
			  the other side */
    {
        if (degree[i] > 3)
        {
            start = end = firstedge[i]; /* checking face on the right */
            do
            {
                if (!ISMARKED(start))
                {
                    MARK(start);
                    buffer = start->invers->prev;
                    othervertex = buffer->end;
                    if (degree[othervertex] > 3)
                    {
                        MARK(buffer->invers->prev);
                        runend = start->prev;
                        run = start->next->next;
                        while (run != runend)
                        {
                            if (run->invers->prev->end == othervertex)
                            {
                                lastprob = start;
                                return 2;
                            }
                            run = run->next;
                        }
                    }
                    /* Makes it slower... -- also outside the edge-loop
	      if (degree[i]==4) 
		{ MARK(start->next->next);
		MARK(start->prev->invers->next->invers);
		}
	      */
                }
                start = start->next;
            } while (start != end);
        }
    }

    return 3;
}

/**************************************************************************/

static void
startbipscan(int nbtot, int nbop, int conn)

/* This routine begins the scan for general connected bipartite planar graphs
 * formed by removing edges from quadrangulations.  The current graph is
 * a quadrangulation, and the group is known (parameters nbtot,nbop).
 * conn is the connectivity (2 or 3, must be correct).
 */

{
    EDGE *feasible[MAXE / 2];
    EDGE *e, *ex;
    int i, j, nfeas;

    for (i = 0; i < nv; ++i)
    {
        for (j = 0; j < nv; ++j)
            am2[i][j] = 0;
        am2[i][i] = 1;
    }

    nfeas = 0;
    for (i = 0; i < nv; ++i)
    {
        e = ex = firstedge[i];
        do
        {
            if (e == e->min && degree[e->start] > minpolydeg && degree[e->end] > minpolydeg)
                feasible[nfeas++] = e;
            e->left_facesize = 4;
            am2[e->start][e->end] = 1;
            e = e->next;
        } while (e != ex);
    }

    prune_bip_edgelist(feasible, nfeas, feasible, &nfeas);

    scanbip(nbtot, nbop, feasible, nfeas, 4, 0, 0, conn);
}

/**************************************************************************/

static void
make_me_a_star(int n)

/* Makes a star on n vertices -- so one vertex of degree n-1
   and n-1 vertices of degree 1 */
{
    int i;
    EDGE *buffer, *buffer2;

    if (n == 1)
    {
        nv = 1;
        ne = 0;
        firstedge[0] = NULL;
        return;
    }

    firstedge[0] = edges;
    degree[0] = n - 1;
    for (i = 1, buffer = edges, buffer2 = edges + n - 1;
         i <= n - 1; i++, buffer++, buffer2++)
    {
        buffer->start = buffer2->end = 0;
        buffer->end = buffer2->start = i;
        buffer->invers = buffer2;
        buffer2->invers = buffer;
        buffer->min = buffer2->min = buffer;
        buffer2->prev = buffer2->next = buffer2;
        degree[i] = 1;
        firstedge[i] = buffer2;
    }

    buffer = edges; /* buffer leading to 1 */
    if (n > 2)
        buffer->next = buffer + 1;
    else
        buffer->next = buffer;
    buffer->prev = buffer + n - 2;
    for (i = 2, buffer++; i < n - 1; i++, buffer++) /* buffer leading to i */
    {
        buffer->prev = buffer - 1;
        buffer->next = buffer + 1;
    }
    if (n > 2) /* buffer leading to n-1 */
    {
        buffer->prev = buffer - 1;
        buffer->next = edges;
    }

    nv = n;
    ne = 2 * (n - 1);
}

/**************************************************************************/

static void
make_cycle(int n)

/* Makes a cycle on n vertices and uses the first 2n edges of the
   vector edges[] for it. Interpretation: a 1-cycle is a loop,
   a 2-cycle a double-edge. */

{
    int i, end;
    EDGE *buffer, *bufferb;

    /* edges+2*i always leads from i to i+1 (mod n) and edges+2*i+1
      leads back. */

    for (i = 0; i <= n - 1; i++)
    {
        end = (i + 1) % n;
        degree[i] = 2;
        buffer = edges + (2 * i);
        firstedge[i] = buffer;
        bufferb = buffer + 1;
        buffer->invers = bufferb;
        bufferb->invers = buffer;
        buffer->min = bufferb->min = buffer;
        buffer->start = bufferb->end = i;
        bufferb->start = buffer->end = end;
        if (i > 0)
            buffer->prev = buffer->next = buffer - 1;
        else
            buffer->prev = buffer->next = edges + 2 * n - 1;
        if (i < n - 1)
            bufferb->prev = bufferb->next = bufferb + 1;
        else
            bufferb->prev = bufferb->next = edges;
    }

    nv = n;
    ne = 2 * n;

    return;
}

/**************************************************************************/

static void
make_gyro(void)
/* Make a loop with a vertex of degree 1 inside and outside. */
{

    make_cycle(3);
    switch_edge(firstedge[0]);
}

/**************************************************************************/

static void
initialize_min3_quadrangulations(void)

/* initialize edges for the 3-connected  and min3 quadrangulation
   generation, and make the inital cube */

{
    EDGE *run, *start;
    int n, i;

    /* First initialize the edges for operation P1. They look like

       a
    \ / \ /
    ?b   c?   Vertex c is the new point. (a,c) and (d,c) are the
    / \ / \   new edges with a-->c taken as quadr_P1(n) 
       d

It is assumed that for 8<=n<MAXN after quadr_P1(n) there is room for 4 edges.
*/

    for (n = 8; n < MAXN; n++)
    {
        run = start = quadr_P1(n);
        run->end = n;
        run->min = run;
        run->invers = start + 1;

        run = start + 1;
        run->start = n;
        run->min = run->invers = start;
        run->prev = start + 3;

        run = start + 2;
        run->end = n;
        run->min = run;
        run->invers = start + 3;

        run = start + 3;
        run->start = n;
        run->min = run->invers = start + 2;
        run->next = start + 1;
    }

    /* The edges for operation P2 can't be "drawn" -- sorry 

    It is assumed that after quadr_P2(n) there is room for 14 edges.
    */

    for (n = 8; n < MAXN - 2; n++)
    {
        start = quadr_P2(n);

        for (i = 0; i < 4; i++)
        {
            run = start + (2 * i);
            run->invers = run + 1;
            run->min = run;
            (run + 1)->invers = (run + 1)->min = run;
        }

        run = start;
        run->start = n;
        run->prev = start + 7;

        run = start + 1;
        run->end = n;

        run = start + 2;
        run->start = n + 1;
        run->prev = start + 4;
        run->next = start + 6;

        run = start + 3;
        run->end = n + 1;

        run = start + 4;
        run->start = n + 1;
        run->prev = start + 6;
        run->next = start + 2;

        run = start + 5;
        run->end = n + 1;

        run = start + 6;
        run->start = n + 1;
        run->end = n;
        run->prev = start + 2;
        run->next = start + 4;

        run = start + 7;
        run->start = n;
        run->end = n + 1;
        run->next = start;
    }

    /* The edges for operation P3.

    It is assumed that after quadr_P3(n) there is room for 16 edges.
    */

    for (n = 8; n < MAXN - 4; n++)
    {
        start = quadr_P3(n);

        for (i = 0; i < 4; i++)
        {
            run = start + 3 * i;
            run->next = run + 1;
            run->prev = run + 2;
            run->start = n + i;
            run++;
            run->next = run + 1;
            run->prev = run - 1;
            run->start = n + i;
            run++;
            run->next = run - 2;
            run->prev = run - 1;
            run->start = n + i;
        }

        run = start;
        run->invers = start + 12;
        run->min = run;
        run = start + 1;
        run->invers = start + 3;
        run->min = run;
        run->end = n + 1;
        run = start + 2;
        run->invers = start + 11;
        run->min = run;
        run->end = n + 3;
        run = start + 3;
        run->invers = start + 1;
        run->min = run->invers;
        run->end = n;
        run = start + 4;
        run->invers = start + 13;
        run->min = run;
        run = start + 5;
        run->invers = start + 6;
        run->min = run;
        run->end = n + 2;
        run = start + 6;
        run->invers = start + 5;
        run->min = run->invers;
        run->end = n + 1;
        run = start + 7;
        run->invers = start + 14;
        run->min = run;
        run = start + 8;
        run->invers = start + 9;
        run->min = run;
        run->end = n + 3;
        run = start + 9;
        run->invers = start + 8;
        run->min = run->invers;
        run->end = n + 2;
        run = start + 10;
        run->invers = start + 15;
        run->min = run;
        run = start + 11;
        run->invers = start + 2;
        run->min = run->invers;
        run->end = n;
        run = start + 12;
        run->invers = start;
        run->min = run->invers;
        run->end = n;
        run = start + 13;
        run->invers = start + 4;
        run->min = run->invers;
        run->end = n + 1;
        run = start + 14;
        run->invers = start + 7;
        run->min = run->invers;
        run->end = n + 2;
        run = start + 15;
        run->invers = start + 10;
        run->min = run->invers;
        run->end = n + 3;
    }

    make_cube();
}

/****************************************************************************/

static void
make_P3(void)

/* Make the path P3 */
{
    EDGE *buffer;

    buffer = edges; /* edge number 0 */
    buffer->start = 0;
    buffer->end = 1;
    buffer->next = buffer;
    buffer->prev = buffer;
    buffer->invers = edges + 1;
    buffer->min = buffer;

    buffer++; /* edge number 1 */
    buffer->start = 1;
    buffer->end = 0;
    buffer->next = edges + 2;
    buffer->prev = edges + 2;
    buffer->invers = edges;
    buffer->min = edges;

    buffer++; /* edge number 2 */
    buffer->start = 1;
    buffer->end = 2;
    buffer->next = edges + 1;
    buffer->prev = edges + 1;
    buffer->invers = edges + 3;
    buffer->min = buffer;

    buffer++; /* edge number 3 */
    buffer->start = 2;
    buffer->end = 1;
    buffer->next = buffer;
    buffer->prev = buffer;
    buffer->invers = edges + 2;
    buffer->min = edges + 2;

    firstedge[0] = edges;
    firstedge[1] = edges + 1;
    firstedge[2] = edges + 3;

    degree[0] = degree[2] = 1;
    degree[1] = 2;

    nv = 3;
    ne = 4;
}

/**************************************************************************/

static void
initialize_quadrangulations(void)

/* initialize edges for the generation of all simple quadrangulations
   and make the initial path P3 */

{
    EDGE *run, *start;
    int n;

    /* Initialize the edges for operation P0. They look like

       a
      / \
    ?b   c    Vertex c is the new point. (a,c) and (d,c) are the
      \ /     new edges with a-->c taken as quadr_P0(n) 
       d

It is assumed that for 3<=n<MAXN after quadr_P0(n) there is room for 4 edges.
*/

    for (n = 3; n < MAXN; n++)
    {
        run = start = quadr_P0(n);
        run->end = n;
        run->min = run;
        run->invers = start + 1;

        run = start + 1;
        run->start = n;
        run->prev = run->next = start + 3;
        run->min = run->invers = start;

        run = start + 2;
        run->end = n;
        run->min = run;
        run->invers = start + 3;

        run = start + 3;
        run->start = n;
        run->min = run->invers = start + 2;
        run->prev = run->next = start + 1;
    }

    /* Then initialize the edges for operation P1. They look like

       a
    ? / \ 
   --b   c--  Vertex c is the new point. (a,c) and (d,c) are the
    ? \ /     new edges with a-->c taken as quadr_P1(n) 
       d

It is assumed that for 5<=n<MAXN after quadr_P1(n) there is room for 4 edges.
*/

    for (n = 5; n < MAXN; n++)
    {
        run = start = quadr_P1(n);
        run->end = n;
        run->min = run;
        run->invers = start + 1;

        run = start + 1;
        run->start = n;
        run->min = run->invers = start;
        run->prev = start + 3;

        run = start + 2;
        run->end = n;
        run->min = run;
        run->invers = start + 3;

        run = start + 3;
        run->start = n;
        run->min = run->invers = start + 2;
        run->next = start + 1;
    }

    make_P3();
}

/*******************************************************************/

static EDGE
    *
    extend_quadr_P0(EDGE *e1)

/* extends a graph in the way given by the type P0 extension for
   quadrangulations. 

   The new path is inserted on the left of e1. 

   It returns the directed edge starting at the new vertex with the
   new face on its left.

   In the picture: e1=b->a, the edge c->a is returned and
   vertex c is the new point nv.

       ?
       a
      / \
    ?b   c?    
      \ /    
       d
       ?
*/

{
    register EDGE *start, *dummy, *dummy2;
    int buffer;

    start = quadr_P0(nv);

    degree[nv] = 2;

    buffer = e1->end;
    dummy = e1->invers;
    dummy2 = dummy->prev;
    start->start = buffer;
    start->next = dummy;
    dummy->prev = start;
    start->prev = dummy2;
    dummy2->next = start;
    degree[buffer]++;

    start++;
    firstedge[nv] = start;
    start->end = buffer;

    e1 = e1->next;
    start++;
    buffer = e1->end;
    dummy = e1->invers;
    dummy2 = dummy->next;
    start->start = buffer;
    start->next = dummy2;
    dummy2->prev = start;
    start->prev = dummy;
    dummy->next = start;
    degree[buffer]++;

    (start + 1)->end = buffer;

    nv++;
    ne += 4;

    return (start - 1);
}

/**************************************************************************/

static void
reduce_quadr_P0(EDGE *e)

/* reduces a graph previously extended by the P0 extension for
   quadrangulations. The edge e must be the reference edge
   returned by the expansion routine.
*/

{
    register EDGE *dummy, *dummy2;
    int buffer;

    nv--;
    ne -= 4;

    dummy = e->invers;
    dummy2 = dummy->next;
    dummy = dummy->prev;

    dummy->next = dummy2;
    dummy2->prev = dummy;
    buffer = dummy->start;
    firstedge[buffer] = dummy;
    degree[buffer]--;

    dummy = e->prev->invers;
    dummy2 = dummy->next;
    dummy = dummy->prev;

    dummy->next = dummy2;
    dummy2->prev = dummy;
    buffer = dummy->start;
    firstedge[buffer] = dummy;
    degree[buffer]--;
}

/*******************************************************************/

static EDGE
    *
    extend_quadr_P1(EDGE *e)

/* extends a graph in the way given by the type P1 extension for
   3-connected quadrangulations. 

   It returns the directed edge characterizing this operation.
*/

{
    register EDGE *e1, *e1i, *e2, *e3, *e3i, *e4, *start, *dummy;
    int end1, end2, center;

    center = e->start;
    e1 = e->prev;
    e1i = e1->invers;
    e2 = e1i->prev;
    end1 = e2->start;

    e3 = e->next;
    e3i = e3->invers;
    e4 = e3i->next;
    end2 = e4->start;

    e1->next = e3;
    e3->prev = e1;
    degree[center]--;
    firstedge[center] = e1;

    start = quadr_P1(nv);
    dummy = start + 1;
    start->start = dummy->end = end1;
    degree[end1]++;
    start->next = e1i;
    e1i->prev = start;
    start->prev = e2;
    e2->next = start;

    dummy->next = e;
    e->prev = dummy;

    start += 2;
    dummy = start + 1;
    start->start = dummy->end = end2;
    degree[end2]++;
    e3i->next = start;
    start->prev = e3i;
    e4->prev = start;
    start->next = e4;

    e->next = dummy;
    dummy->prev = e;

    degree[nv] = 3;
    e->start = e->invers->end = nv;
    firstedge[nv] = e;
    nv++;
    ne += 4;

    return (e);
}

/**************************************************************************/

static void
reduce_quadr_P1(EDGE *e)

/* reduces a graph previously extended by the type P1 extension for
   3-connected quadrangulations. The edge e must be the reference edge
*/

{
    register EDGE *e1, *e1i, *e2, *e3, *e3i, *e4;
    int end1, end2, center;

    nv--;
    ne -= 4;

    e2 = e->prev->invers->prev;
    end1 = e2->start;
    e1i = e2->next->next;
    e1 = e1i->invers;
    center = e1->start;
    e3 = e1->next;
    e3i = e3->invers;
    e4 = e3i->next->next;
    end2 = e4->start;

    e2->next = e1i;
    e1i->prev = e2;
    firstedge[end1] = e2;
    degree[end1]--;
    e1->next = e;
    e->prev = e1;
    e->next = e3;
    e3->prev = e;
    e->start = e->invers->end = center;
    degree[center]++;
    e3i->next = e4;
    e4->prev = e3i;
    firstedge[end2] = e4;
    degree[end2]--;
}

/*******************************************************************/

static EDGE
    *
    extend_quadr_P2(EDGE *e)

/* extends a graph in the way given by the type P2 extension for
   3-connected quadrangulations. 

   It returns the directed edge characterizing this operation.
*/

{
    register EDGE *e1, *e2, *e3, *e4, *e5, *e5i, *e6i, *start, *dummy;
    int end1, end2, end3;

    e = e->next;
    end2 = e->end;
    e1 = e->invers;
    e4 = e1->next;
    e5 = e1->prev;
    e5i = e5->invers;
    e6i = e5i->prev;
    end3 = e5i->start;
    e3 = e4->invers->next->invers;
    e2 = e3->next;
    end1 = e3->start;

    start = quadr_P2(nv);
    dummy = start + 1;
    start->end = dummy->start = end3;
    degree[end3]++;
    e6i->next = e5i->prev = dummy;
    dummy->prev = e6i;
    dummy->next = e5i;

    dummy = start + 3;
    dummy->start = (dummy - 1)->end = end2;
    firstedge[end2] = dummy;
    e5->next = e4->prev = dummy;
    dummy->next = e4;
    dummy->prev = e5;

    dummy = start + 5;
    dummy->start = (dummy - 1)->end = end1;
    degree[end1]++;
    e3->next = e2->prev = dummy;
    dummy->next = e2;
    dummy->prev = e3;

    dummy = start + 7;
    e->end = e1->start = nv;
    start->next = dummy->prev = e1;
    e1->next = dummy;
    e1->prev = start;

    degree[nv] = degree[nv + 1] = 3;
    firstedge[nv] = start;
    firstedge[nv + 1] = start + 2;

    nv += 2;
    ne += 8;

    return start;
}

/*******************************************************************/

static void
reduce_quadr_P2(EDGE *e)

/* reduces a P2 configuration formerly expanded by extend_quadr_P2() */

{
    register EDGE *e1, *e2, *e3, *e4, *e5, *e5i, *e6i;
    int end1, end2, end3;

    nv -= 2;
    ne -= 8;

    e1 = e->next;
    e = e->invers;
    end3 = e->start;
    e6i = e->prev;
    e5i = e->next;
    e5 = e5i->invers;
    end2 = e5->start;
    e4 = e5->next->next;
    e3 = e4->invers->next->invers;
    end1 = e3->start;
    e2 = e3->next->next;
    e = e1->invers;

    e6i->next = e5i;
    e5i->prev = e6i;
    degree[end3]--;
    firstedge[end3] = e5i;

    e5->next = e4->prev = e1;
    e1->next = e4;
    e1->prev = e5;
    e1->start = e->end = end2;
    firstedge[end2] = e1;

    e3->next = e2;
    e2->prev = e3;
    degree[end1]--;
    firstedge[end1] = e2;
}

/*******************************************************************/

static EDGE
    *
    extend_quadr_P3(EDGE *e)

/* extends a graph in the way given by the type P3 extension for
   3-connected quadrangulations. That is: It inserts a square on the
   right hand side of e.

   It returns the directed edge characterizing this operation.
*/

{
    register EDGE *run, *start, *dummy;
    int vertex;

    start = quadr_P3(nv);

    run = e->next;
    vertex = e->start;
    dummy = start + 12;
    start->end = dummy->start = vertex;
    degree[vertex]++;
    e->next = run->prev = dummy;
    dummy->next = run;
    dummy->prev = e;

    e = run->invers;
    run = e->next;
    vertex = e->start;
    dummy = start + 15;
    (start + 10)->end = dummy->start = vertex;
    degree[vertex]++;
    e->next = run->prev = dummy;
    dummy->next = run;
    dummy->prev = e;

    e = run->invers;
    run = e->next;
    vertex = e->start;
    dummy--;
    (start + 7)->end = dummy->start = vertex;
    degree[vertex]++;
    e->next = run->prev = dummy;
    dummy->next = run;
    dummy->prev = e;

    e = run->invers;
    run = e->next;
    vertex = e->start;
    dummy--;
    (start + 4)->end = dummy->start = vertex;
    degree[vertex]++;
    e->next = run->prev = dummy;
    dummy->next = run;
    dummy->prev = e;

    firstedge[nv] = start;
    degree[nv] = 3;
    firstedge[nv + 1] = start + 3;
    degree[nv + 1] = 3;
    firstedge[nv + 2] = start + 6;
    degree[nv + 2] = 3;
    firstedge[nv + 3] = start + 9;
    degree[nv + 3] = 3;

    nv += 4;
    ne += 16;

    return (run->invers);
}

/*******************************************************************/

static void
reduce_quadr_P3(EDGE *e)

/* Reduces the graph formerly extended by the type P3 extension for
   3-connected quadrangulations. That is: It removes a square on the
   right hand side of e.
*/

{
    register EDGE *dummy;
    int start;

    nv -= 4;
    ne -= 16;

    dummy = e->next->next;
    start = e->start;
    degree[start]--;
    firstedge[start] = e;
    e->next = dummy;
    dummy->prev = e;

    e = dummy->invers;
    dummy = e->next->next;
    start = e->start;
    degree[start]--;
    firstedge[start] = e;
    e->next = dummy;
    dummy->prev = e;

    e = dummy->invers;
    dummy = e->next->next;
    start = e->start;
    degree[start]--;
    firstedge[start] = e;
    e->next = dummy;
    dummy->prev = e;

    e = dummy->invers;
    dummy = e->next->next;
    start = e->start;
    degree[start]--;
    firstedge[start] = e;
    e->next = dummy;
    dummy->prev = e;
}

/*******************************************************************/

static int
will_be_3_connected(EDGE *e)

/* returns 1 if after performing a P1 expansion for edge e, the graph
   will still be 3-connected, 0 else 

   Uses the fact that there are no 3-cycles.
*/

{
    int end1, end2;
    EDGE *run, *last;

    end1 = e->prev->end;
    end2 = e->next->end;

    if (degree[end1] < degree[end2])
    {
        e = e->prev->invers;
        run = e->next;
        last = e->prev;
        /* end2 cannot be in the face left of run -- would be a double edge 
       and for the same reason not in the face right of last */
        while (run != last)
        {
            if (run->invers->prev->end == end2)
                return 0;
            run = run->next;
        }
    }
    else
    {
        e = e->next->invers;
        run = e->next;
        last = e->prev;
        while (run != last)
        {
            if (run->invers->prev->end == end1)
                return 0;
            run = run->next;
        }
    }

    return 1;
}

/*******************************************************************/

static int
legal_P1_reduction(EDGE *e)

/* checks whether the edge e characterizes a legal P1-reduction.
   Returns 1 if yes, 0 otherwise.

   It is assumed that edge->start has degree 3, and that both the side
   vertices edge->next->end and edge->prev->end have degree at least 4.
*/

{
    EDGE *run, *last;
    int w, w1, w2, buffer;

    w = e->end;
    run = e->next->invers->prev->invers;
    last = run->prev;
    run = run->next;

    do
    {
        if (run->end == w)
            return 0;
        run = run->next;
    } while (run != last);

    e = e->invers;
    w1 = e->next->end;
    w2 = e->prev->end;

    /* OK -- then some serious tests have to be done... */

    run = last->next;
    last = last->prev;

    if (run->invers->prev->end == w1)
        return 0;
    /* cannot be w2 */
    for (run = run->next; run != last; run = run->next)
    {
        buffer = run->invers->prev->end;
        if (buffer == w1)
            return 0;
        if (buffer == w2)
            return 0;
    }

    /* the last one cannot be w1 */
    if (run->invers->prev->end == w2)
        return 0;

    /* All tests successful -- no 2-cut will occur: */

    return 1;
}

/***********************************************************************/

static int
legal_P1_reduction_all(EDGE *e)

/* checks whether the edge e characterizes a legal P1-reduction.
   General quadrangulations version.
   Returns TRUE if legal, FALSE otherwise.

   It is assumed that edge->start has degree 3, and that there are
   no vertices of degree 2.
*/

{
    EDGE *run, *last;
    int w;

    w = e->end;
    run = e->next->invers->prev->invers;
    last = run->prev;
    run = run->next;

    do
    {
        if (run->end == w)
            return FALSE;
        run = run->next;
    } while (run != last);

    return TRUE;
}

/***********************************************************************/

static int
legal_P1_reduction_min3(EDGE *e)

/* checks whether the edge e characterizes a legal P1-reduction.
   mindeg 3 version
   Returns TRUE if yes, FALSE otherwise.

   It is assumed that edge->start has degree 3, and that both the side
   vertices edge->next->end and edge->prev->end have degree at least 4.
*/

{
    EDGE *run, *last;
    int w;

    w = e->end;
    run = e->next->invers->prev->invers;
    last = run->prev;
    run = run->next;

    do
    {
        if (run->end == w)
            return FALSE;
        run = run->next;
    } while (run != last);

    return TRUE;
}

/***********************************************************************/

static int
legal_P1_reduction_nf4(EDGE *e)

/* checks whether the edge e characterizes a legal P1-reduction.
   Version for 3-connected quadrangulations without non-facial 4-cycles.
   Returns 1 if yes, 0 otherwise.

   It is assumed that edge->start has degree 3, and that both the side
   vertices edge->next->end and edge->prev->end have degree at least 4.
*/

{
    EDGE *e1, *e1last, *e2, *e2last;

    if (degree[e->end] == 3)
        return TRUE;

    RESETMARKS_V;

    e1 = e->invers;
    e1last = e1->prev;
    e1 = e1->next->next;
    do
    {
        MARK_V(e1->end);
        e1 = e1->next;
    } while (e1 != e1last);

    e1 = e->next->invers->prev->invers;
    e1last = e1->prev;
    e1 = e1->next;
    do
    {
        e2last = e1->invers;
        e2 = e2last->next;
        do
        {
            if (ISMARKED_V(e2->end))
                return FALSE;
            e2 = e2->next;
        } while (e2 != e2last);

        e1 = e1->next;
    } while (e1 != e1last);

    return TRUE;
}

/**********************************************************************/

static int
legal_P3_reduction(EDGE *e)

/* checks whether the edge corresponds to a legal P3 reduction.
   Returns 1 if it is a legal reduction, 0 else. 

   Again it is assumed (necessary or not) that P1 has higher priority
   -- the nonexistence of a P1 reduction forces some subconfiguration.

   Furthermore it is assumed that the graph inspected is not the cube.
*/

{
    EDGE *run, *last;
    int v1, v2;

    if (degree[e->next->end] != 3)
        return 0;
    run = e->invers->prev;
    if (degree[run->end] != 3)
        return 0;
    run = run->prev->invers->prev;
    if (degree[run->end] != 3)
        return 0;
    v1 = run->start;
    run = run->prev->invers->prev;
    if (degree[run->end] != 3)
        return 0;
    v2 = run->start;

    /* OK -- we have an "inserted square" on the right hand side */

    /* Test whether opposite vertices share a face */

    last = e->prev;
    run = e->next->next->next;
    while (run != last)
    {
        if (run->invers->prev->end == v1)
            return 0;
        run = run->next;
    }

    e = e->invers;
    last = e->prev->prev->prev;
    run = e->next;
    while (run != last)
    {
        if (run->invers->prev->end == v2)
            return 0;
        run = run->next;
    }

    return 1;
}

/*******************************************************************/

static int
legal_P3_reduction_min3(EDGE *e)

/* checks whether the edge corresponds to a legal P3 reduction.
   Returns 1 if it is a legal reduction, 0 else. 
   mindeg 3 version

   Again it is assumed (necessary or not) that P1 has higher priority
   -- the nonexistence of a P1 reduction forces some subconfiguration.

   Furthermore it is assumed that the graph inspected is not the cube.
*/

{
    EDGE *run;

    if (degree[e->next->end] != 3)
        return 0;
    run = e->invers->prev;
    if (degree[run->end] != 3)
        return 0;
    run = run->prev->invers->prev;
    if (degree[run->end] != 3)
        return 0;
    run = run->prev->invers->prev;
    if (degree[run->end] != 3)
        return 0;

    return 1;
}

/****************************************************************************/

static void
find_extensions_quad(int nbtot, int nbop, EDGE *extP1[], int *nextP1,
                     EDGE *extP3[], int *nextP3, EDGE *lastP1)

/* Determine the inequivalent places to make extensions, for the
   3-connected quadrangulations.  The results are put in the arrays
   extP1[0..*nextP1-1], etc..
   nbtot and nbop are the usual group parameters.
   If lastA != NULL, this graph was made with an P1-operation and lastP1
   is its reference edge.  If lastP1 == NULL, it wasn't made with P1.
*/

{
    EDGE *e, *ee, *elast;
    EDGE **nb, **nb0, **nblim, **nboplim;
    int i, k;
    int maxdeg, vx;

    if (nbtot == 1)
    {
        /* P1 extension for trivial group */

        RESETMARKS_V;
        if (lastP1 != NULL)
        {
            maxdeg = degree[lastP1->end];
            MARK_V(lastP1->start);
            MARK_V(lastP1->next->invers->prev->end);
            vx = lastP1->end;
        }
        else
        {
            vx = -1;
            maxdeg = 0;
        }

        k = 0;
        for (i = 0; i < nv; ++i)
            if (degree[i] >= 4)
            {
                e = elast = firstedge[i];
                if (i == vx)
                    do
                    {
                        if (will_be_3_connected(e))
                            extP1[k++] = e;
                        e = e->next;
                    } while (e != elast);
                else
                    do
                    {
                        if (ISMARKED_V(e->prev->end) || ISMARKED_V(e->next->end) || degree[e->end] >= maxdeg)
                        {
                            if (will_be_3_connected(e))
                                extP1[k++] = e;
                        }
                        e = e->next;
                    } while (e != elast);
            }

        *nextP1 = k;

        /* P3 extension for trivial group */

        if (nv <= maxnv - 4)
        {
            k = 0;
            RESETMARKS;

            for (i = 0; i < nv; ++i)
            {
                e = elast = firstedge[i];
                do
                {
                    if (!ISMARKEDLO(e))
                    {
                        extP3[k++] = e;
                        MARKLO(e);
                        ee = e->invers->prev;
                        MARKLO(ee);
                        ee = ee->invers->prev;
                        MARKLO(ee);
                        ee = ee->invers->prev;
                        MARKLO(ee);
                    }
                    e = e->next;
                } while (e != elast);
            }
            *nextP3 = k;
        }
        else
            *nextP3 = 0;
    }
    else
    {
        nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];
        nblim = (EDGE **)numbering[nbtot];
        nb0 = (EDGE **)numbering[0];

        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        /* P1 extensions for non-trivial group */
        k = 0;
        RESETMARKS;

        for (i = 0; i < nv; ++i)
            if (degree[i] >= 4)
            {
                e = elast = firstedge[i];
                do
                {
                    if (!ISMARKEDLO(e) && will_be_3_connected(e))
                    {
                        extP1[k++] = e;
                        for (nb = nb0 + e->index + MAXE; nb < nblim; nb += MAXE)
                            MARKLO(*nb);
                    }
                    e = e->next;
                } while (e != elast);
            }
        *nextP1 = k;

        /* P3 extensions for non-trivial group */

        if (nv <= maxnv - 4)
        {
            RESETMARKS;
            k = 0;
            for (i = 0; i < nv; ++i)
            {
                e = elast = firstedge[i];
                do
                {
                    if (!ISMARKEDLO(e))
                    {
                        extP3[k++] = e;
                        ee = e;
                        do
                        {
                            for (nb = nb0 + ee->index; nb < nboplim; nb += MAXE)
                                MARKLO(*nb);
                            for (; nb < nblim; nb += MAXE)
                                MARKLO((*nb)->invers);
                            ee = ee->invers->prev;
                        } while (ee != e);
                    }
                    e = e->next;
                } while (e != elast);
            }
            *nextP3 = k;
        }
        else
            *nextP3 = 0;
    }
}

/****************************************************************************/

static void
find_extensions_quad_all(int nbtot, int nbop, EDGE *extP0[], int *nextP0,
                         EDGE *extP1[], int *nextP1)

/* Determine the inequivalent places to make extensions, for general
   quadrangulations.  The results are put in the arrays
   extP0[0..*nextP0-1] and extP1[0..*nextP1-1].
   nbtot and nbop are the usual group parameters.
*/

{
    EDGE *e, *elast;
    EDGE **nb, **nb0, **nblim, **nboplim;
    int i, j, k, l, x, y;
    int deg2;
#define VCOLP0(i, j) (degree[i] < degree[j] ? (degree[j] << 10) + degree[i] : (degree[i] << 10) + degree[j])

    if (degree[nv - 1] == 2)
    {
        x = firstedge[nv - 1]->end;
        y = firstedge[nv - 1]->next->end;
    }
    else
        x = -1;

    deg2 = 0;
    for (i = nv; --i >= 0 && deg2 < 3;)
        if (degree[i] == 2)
            ++deg2;

    if (nbtot == 1)
    {
        /* P0 extension for trivial group */

        RESETMARKS;
        k = 0;
        for (l = 0; l < nv; ++l)
        {
            e = elast = firstedge[l];
            do
            {
                if (!ISMARKEDLO(e))
                {
                    i = e->end;
                    j = e->next->end;
                    if (x < 0 || i == nv - 1 || j == nv - 1)
                        extP0[k++] = e;
                    else
                    {
                        ++degree[i];
                        ++degree[j];
                        if (VCOLP0(i, j) >= VCOLP0(x, y))
                            extP0[k++] = e;
                        --degree[i];
                        --degree[j];
                    }
                    MARKLO(e->next->invers->next->invers);
                }
                e = e->next;
            } while (e != elast);
        }

        *nextP0 = k;

        /* P1 extension for trivial group */

        if (deg2 > 2)
            *nextP1 = 0;
        else
        {
            k = 0;
            for (i = 0; i < nv; ++i)
                if (degree[i] >= 4)
                {
                    e = elast = firstedge[i];
                    do
                    {
                        if ((degree[e->prev->end] == 2) + (degree[e->next->end] == 2) == deg2)
                            extP1[k++] = e;
                        e = e->next;
                    } while (e != elast);
                }

            *nextP1 = k;
        }
    }
    else
    {
        nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];
        nblim = (EDGE **)numbering[nbtot];
        nb0 = (EDGE **)numbering[0];

        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        /* P0 extensions for non-trivial group */

        k = 0;
        RESETMARKS;

        for (l = 0; l < ne; ++l)
            if (!ISMARKED(nb0[l]))
            {
                e = nb0[l];
                i = e->end;
                j = e->next->end;
                if (x < 0 || i == nv - 1 || j == nv - 1)
                    extP0[k++] = e;
                else
                {
                    ++degree[i];
                    ++degree[j];
                    if (VCOLP0(i, j) >= VCOLP0(x, y))
                        extP0[k++] = e;
                    --degree[i];
                    --degree[j];
                }
                for (nb = nb0 + l + MAXE; nb < nboplim; nb += MAXE)
                    MARKLO(*nb);
                for (; nb < nblim; nb += MAXE)
                    MARKLO((*nb)->invers->next->invers);
                for (nb = nb0 + (nb0[l]->next->invers->next->invers->index);
                     nb < nboplim; nb += MAXE)
                    MARKLO(*nb);
                for (; nb < nblim; nb += MAXE)
                    MARKLO((*nb)->invers->next->invers);
            }

        *nextP0 = k;

        /* P1 extensions for non-trivial group */

        if (deg2 > 2)
            *nextP1 = 0;
        else
        {
            k = 0;
            RESETMARKS;

            for (i = 0; i < nv; ++i)
                if (degree[i] >= 4)
                {
                    e = elast = firstedge[i];
                    do
                    {
                        if (!ISMARKEDLO(e))
                        {
                            if ((degree[e->prev->end] == 2) + (degree[e->next->end] == 2) == deg2)
                                extP1[k++] = e;
                            for (nb = nb0 + e->index + MAXE; nb < nblim; nb += MAXE)
                                MARKLO(*nb);
                        }
                        e = e->next;
                    } while (e != elast);
                }

            *nextP1 = k;
        }
    }
}

/****************************************************************************/

static void
find_extensions_quad_min3(int nbtot, int nbop, EDGE *extP1[], int *nextP1,
                          EDGE *extP3[], int *nextP3, EDGE *lastP1)

/* Determine the inequivalent places to make extensions, for the
   quadrangulations with mindeg 3.  The results are put in the arrays
   extP1[0..*nextP1-1], etc..
   nbtot and nbop are the usual group parameters.
   If lastA != NULL, this graph was made with an P1-operation and lastP1
   is its reference edge.  If lastP1 == NULL, it wasn't made with P1.
*/

{
    EDGE *e, *ee, *elast;
    EDGE **nb, **nb0, **nblim, **nboplim;
    int i, k;
    int maxdeg, vx;

    if (nbtot == 1)
    {
        /* P1 extension for trivial group */

        RESETMARKS_V;
        if (lastP1 != NULL)
        {
            maxdeg = degree[lastP1->end];
            MARK_V(lastP1->start);
            MARK_V(lastP1->next->invers->prev->end);
            vx = lastP1->end;
        }
        else
        {
            vx = -1;
            maxdeg = 0;
        }

        k = 0;
        for (i = 0; i < nv; ++i)
            if (degree[i] >= 4)
            {
                e = elast = firstedge[i];
                if (i == vx)
                    do
                    {
                        extP1[k++] = e;
                        e = e->next;
                    } while (e != elast);
                else
                    do
                    {
                        if (ISMARKED_V(e->prev->end) || ISMARKED_V(e->next->end) || degree[e->end] >= maxdeg)
                        {
                            extP1[k++] = e;
                        }
                        e = e->next;
                    } while (e != elast);
            }

        *nextP1 = k;

        /* P3 extension for trivial group */

        if (nv <= maxnv - 4)
        {
            k = 0;
            RESETMARKS;

            for (i = 0; i < nv; ++i)
            {
                e = elast = firstedge[i];
                do
                {
                    if (!ISMARKEDLO(e))
                    {
                        extP3[k++] = e;
                        MARKLO(e);
                        ee = e->invers->prev;
                        MARKLO(ee);
                        ee = ee->invers->prev;
                        MARKLO(ee);
                        ee = ee->invers->prev;
                        MARKLO(ee);
                    }
                    e = e->next;
                } while (e != elast);
            }
            *nextP3 = k;
        }
        else
            *nextP3 = 0;
    }
    else
    {
        nboplim = (EDGE **)numbering[nbop == 0 ? nbtot : nbop];
        nblim = (EDGE **)numbering[nbtot];
        nb0 = (EDGE **)numbering[0];

        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        /* P1 extensions for non-trivial group */
        k = 0;
        RESETMARKS;

        for (i = 0; i < nv; ++i)
            if (degree[i] >= 4)
            {
                e = elast = firstedge[i];
                do
                {
                    if (!ISMARKEDLO(e))
                    {
                        extP1[k++] = e;
                        for (nb = nb0 + e->index + MAXE; nb < nblim; nb += MAXE)
                            MARKLO(*nb);
                    }
                    e = e->next;
                } while (e != elast);
            }
        *nextP1 = k;

        /* P3 extensions for non-trivial group */

        if (nv <= maxnv - 4)
        {
            RESETMARKS;
            k = 0;
            for (i = 0; i < nv; ++i)
            {
                e = elast = firstedge[i];
                do
                {
                    if (!ISMARKEDLO(e))
                    {
                        extP3[k++] = e;
                        ee = e;
                        do
                        {
                            for (nb = nb0 + ee->index; nb < nboplim; nb += MAXE)
                                MARKLO(*nb);
                            for (; nb < nblim; nb += MAXE)
                                MARKLO((*nb)->invers);
                            ee = ee->invers->prev;
                        } while (ee != e);
                    }
                    e = e->next;
                } while (e != elast);
            }
            *nextP3 = k;
        }
        else
            *nextP3 = 0;
    }
}

/****************************************************************************/

static void
find_extensions_quad_nf4(int nbtot, int nbop,
                         EDGE *extP1[], int *nextP1, EDGE *lastP1)

/* Determine the inequivalent places to make extensions, for the
   3-connected quadrangulations without non-facial 4-cycles.
   The results are put in the arrays extP1[0..*nextP1-1], etc..
   nbtot and nbop are the usual group parameters.
   If lastA != NULL, this graph was made with an P1-operation and lastP1
   is its reference edge.  If lastP1 == NULL, it wasn't made with P1.
*/

{
    EDGE *e, *elast;
    EDGE **nb, **nb0, **nblim;
    int i, k;
    int maxdeg, vx;

    if (nbtot == 1)
    {
        /* P1 extension for trivial group */

        RESETMARKS_V;
        if (lastP1 != NULL)
        {
            maxdeg = degree[lastP1->end];
            MARK_V(lastP1->start);
            MARK_V(lastP1->next->invers->prev->end);
            vx = lastP1->end;
        }
        else
        {
            vx = -1;
            maxdeg = 0;
        }

        k = 0;
        for (i = 0; i < nv; ++i)
            if (degree[i] >= 4)
            {
                e = elast = firstedge[i];
                if (i == vx)
                    do
                    {
                        extP1[k++] = e;
                        e = e->next;
                    } while (e != elast);
                else
                    do
                    {
                        if (ISMARKED_V(e->prev->end) || ISMARKED_V(e->next->end) || degree[e->end] >= maxdeg)
                        {
                            extP1[k++] = e;
                        }
                        e = e->next;
                    } while (e != elast);
            }

        *nextP1 = k;
    }
    else
    {
        nblim = (EDGE **)numbering[nbtot];
        nb0 = (EDGE **)numbering[0];

        for (i = 0; i < ne; ++i)
            nb0[i]->index = i;

        /* P1 extensions for non-trivial group */
        k = 0;
        RESETMARKS;

        for (i = 0; i < nv; ++i)
            if (degree[i] >= 4)
            {
                e = elast = firstedge[i];
                do
                {
                    if (!ISMARKEDLO(e))
                    {
                        extP1[k++] = e;
                        for (nb = nb0 + e->index + MAXE; nb < nblim; nb += MAXE)
                            MARKLO(*nb);
                    }
                    e = e->next;
                } while (e != elast);
            }
        *nextP1 = k;
    }
}

/****************************************************************************/

static int
has_quadr_P0(void)

/* Test whether there is a legal P1 reduction */

{
    int i;

    for (i = nv; --i >= 0;)
        if (degree[i] == 2)
            return TRUE;

    return FALSE;
}

/****************************************************************************/

static int
has_quadr_P1(void)

/* Test whether there is a legal P1 reduction */

{
    int i;
    EDGE *e, *elast;

    for (i = 0; i < nv; ++i)
        if (degree[i] == 3)
        {
            e = elast = firstedge[i];
            do
            {
                if (degree[e->next->end] >= 4 && degree[e->prev->end] >= 4 && legal_P1_reduction(e))
                    return TRUE;
                e = e->next;
            } while (e != elast);
        }

    return FALSE;
}

/****************************************************************************/

static int
has_quadr_P1_min3(void)

/* Test whether there is a legal P1 reduction, mindeg3 version.
   It is enough that there is a vertex of degree 3 with at least
   two neighbours of degree at least 4.
*/

{
    int i, n3;
    EDGE *e;

    for (i = 0; i < nv; ++i)
        if (degree[i] == 3)
        {
            e = firstedge[i];
            n3 = 0;
            if (degree[e->end] == 3)
                ++n3;
            e = e->next;
            if (degree[e->end] == 3)
                ++n3;
            e = e->next;
            if (degree[e->end] == 3)
                ++n3;

            if (n3 <= 1)
                return TRUE;
        }

    return FALSE;
}

/****************************************************************************/

static void
quadr_P1_legal(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
               EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref,
               EDGE *prevP1[], int nprevP1, EDGE **hint)

/* The P1-operation with reference edge *ref has just been performed.
   prevP1[0..nprevP1-1] are all earlier P1s since the last P2 or P3.
   hint (unless it is NULL) is a suggestion for a P1-reduction that
   might be better than ref.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal P1-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-1.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   P1-reductions have a priority (colour) based on the degrees of the
   end vertex and two side vertices.  It cannot be changed without
   changing find_extensions_quad too.
*/

{
    EDGE *e, *ee, *elast;
    int maxdeg;
    int col, maxcol;
    int i, nor, nmir;

#define QORCOL(e) (((long)degree[e->prev->end] << 10) + (long)degree[e->next->end])
#define QMIRCOL(e) (((long)degree[e->next->end] << 10) + (long)degree[e->prev->end])

    RESETMARKS;
    nor = nmir = 0;

    maxdeg = degree[ref->end];
    maxcol = QORCOL(ref);
    col = QMIRCOL(ref);
    if (col < maxcol)
        good_or[nor++] = ref;
    else if (col == maxcol)
    {
        good_or[nor++] = ref;
        good_mir[nmir++] = ref;
    }
    else
    {
        maxcol = col;
        good_mir[nmir++] = ref;
    }

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    MARKLO(ref->invers);

    e = *hint;
    if (e && !ISMARKEDLO(e->invers) && degree[e->start] == 3 && degree[e->end] >= maxdeg && degree[e->next->end] >= 4 && degree[e->prev->end] >= 4 && legal_P1_reduction(e))
    {
        if (degree[e->end] > maxdeg)
        {
            *ngood_ref = *ngood_mir_ref = 0;
            return;
        }
        else
        {
            col = QORCOL(e);
            if (col > maxcol)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else if (col == maxcol)
                good_or[nor++] = e;

            col = QMIRCOL(e);
            if (col > maxcol)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else if (col == maxcol)
                good_mir[nmir++] = e;
        }
        MARKLO(e->invers);
    }

    for (i = nprevP1; --i >= 0;)
    {
        e = prevP1[i];
        if (!ISMARKEDLO(e->invers) && degree[e->end] >= maxdeg && degree[e->start] == 3 && degree[e->next->end] >= 4 && degree[e->prev->end] >= 4 && legal_P1_reduction(e))
        {
            if (degree[e->end] > maxdeg)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else
            {
                col = QORCOL(e);
                if (col > maxcol)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (col == maxcol)
                    good_or[nor++] = e;

                col = QMIRCOL(e);
                if (col > maxcol)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (col == maxcol)
                    good_mir[nmir++] = e;
            }
        }
        MARKLO(e->invers);
    }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    if (*ngood_ref == 0 && *ngood_mir_ref == 0)
        return;

    for (i = 0; i < nv; ++i)
        if (degree[i] > maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e) && degree[e->end] == 3)
                {
                    ee = e->invers;
                    if (degree[ee->next->end] >= 4 && degree[ee->prev->end] >= 4 && legal_P1_reduction(ee))
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        *hint = e;
                        return;
                    }
                }
                e = e->next;
            } while (e != elast);
        }
        else if (degree[i] == maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                ee = e->invers;
                if (degree[e->end] == 3 && !ISMARKEDLO(e) && degree[ee->next->end] >= 4 && degree[ee->prev->end] >= 4 && legal_P1_reduction(ee))
                {
                    col = QORCOL(e->invers);
                    if (col > maxcol)
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        *hint = e;
                        return;
                    }
                    else if (col == maxcol)
                        good_or[nor++] = e->invers;

                    col = QMIRCOL(e->invers);
                    if (col > maxcol)
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        *hint = e;
                        return;
                    }
                    else if (col == maxcol)
                        good_mir[nmir++] = e->invers;
                }
                e = e->next;
            } while (e != elast);
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/****************************************************************************/

static void
quadr_P1_legal_min3(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
                    EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref,
                    EDGE *prevP1[], int nprevP1, EDGE **hint)

/* The P1-operation with reference edge *ref has just been performed.
   prevP1[0..nprevP1-1] are all earlier P1s since the last P2 or P3.
   hint (unless it is NULL) is a suggestion for a P1-reduction that
   might be better than ref.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal P1-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-1.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   P1-reductions have a priority (colour) based on the degrees of the
   end vertex and two side vertices.  It cannot be changed without
   changing find_extensions_quad too.

   mindeg 3 version
*/

{
    EDGE *e, *ee, *elast;
    int maxdeg;
    int col, maxcol;
    int i, nor, nmir;

#define QORCOL(e) (((long)degree[e->prev->end] << 10) + (long)degree[e->next->end])
#define QMIRCOL(e) (((long)degree[e->next->end] << 10) + (long)degree[e->prev->end])

    RESETMARKS;
    nor = nmir = 0;

    maxdeg = degree[ref->end];
    maxcol = QORCOL(ref);
    col = QMIRCOL(ref);
    if (col < maxcol)
        good_or[nor++] = ref;
    else if (col == maxcol)
    {
        good_or[nor++] = ref;
        good_mir[nmir++] = ref;
    }
    else
    {
        maxcol = col;
        good_mir[nmir++] = ref;
    }

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    MARKLO(ref->invers);

    e = *hint;
    if (e && !ISMARKEDLO(e->invers) && degree[e->start] == 3 && degree[e->end] > maxdeg && degree[e->next->end] >= 4 && degree[e->prev->end] >= 4 && legal_P1_reduction_min3(e))
    {
        if (degree[e->end] > maxdeg)
        {
            *ngood_ref = *ngood_mir_ref = 0;
            return;
        }
        else
        {
            col = QORCOL(e);
            if (col > maxcol)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else if (col == maxcol)
                good_or[nor++] = e;

            col = QMIRCOL(e);
            if (col > maxcol)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else if (col == maxcol)
                good_mir[nmir++] = e;
        }
        MARKLO(e->invers);
    }

    for (i = nprevP1; --i >= 0;)
    {
        e = prevP1[i];
        if (!ISMARKEDLO(e->invers) && degree[e->end] >= maxdeg && degree[e->start] == 3 && degree[e->next->end] >= 4 && degree[e->prev->end] >= 4 && legal_P1_reduction_min3(e))
        {
            if (degree[e->end] > maxdeg)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else
            {
                col = QORCOL(e);
                if (col > maxcol)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (col == maxcol)
                    good_or[nor++] = e;

                col = QMIRCOL(e);
                if (col > maxcol)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (col == maxcol)
                    good_mir[nmir++] = e;
            }
        }
        MARKLO(e->invers);
    }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    if (*ngood_ref == 0 && *ngood_mir_ref == 0)
        return;

    for (i = 0; i < nv; ++i)
        if (degree[i] > maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e) && degree[e->end] == 3)
                {
                    ee = e->invers;
                    if (degree[ee->next->end] >= 4 && degree[ee->prev->end] >= 4 && legal_P1_reduction_min3(ee))
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        *hint = e;
                        return;
                    }
                }
                e = e->next;
            } while (e != elast);
        }
        else if (degree[i] == maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                ee = e->invers;
                if (degree[e->end] == 3 && !ISMARKEDLO(e) && degree[ee->next->end] >= 4 && degree[ee->prev->end] >= 4 && legal_P1_reduction_min3(ee))
                {
                    col = QORCOL(e->invers);
                    if (col > maxcol)
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        *hint = e;
                        return;
                    }
                    else if (col == maxcol)
                        good_or[nor++] = e->invers;

                    col = QMIRCOL(e->invers);
                    if (col > maxcol)
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        *hint = e;
                        return;
                    }
                    else if (col == maxcol)
                        good_mir[nmir++] = e->invers;
                }
                e = e->next;
            } while (e != elast);
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/****************************************************************************/

static void
quadr_P0_legal_all(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
                   EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* The P0-operation with reference edge *ref has just been performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal P1-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-1.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   P1-reductions have a priority (colour) based on the degrees of the
   end vertex and two side vertices.  It cannot be changed without
   changing find_extensions_quad too.

   version for general quadrangulations
*/

{
    EDGE *e;
    int col, col2, maxcol, maxcol2;
    int i, nor, nmir;
    int d1, d2, d3, d4;

#define VCOLPD(di, dj) (di < dj ? (dj << 10) + di : (di << 10) + dj)

    nor = nmir = 0;

    d1 = degree[ref->end];
    d2 = degree[ref->next->end];
    d3 = degree[ref->invers->next->end];
    d4 = degree[ref->invers->prev->end];

    maxcol = VCOLPD(d1, d2);
    maxcol2 = VCOLPD(d3, d4);

    if (d1 >= d2)
    {
        if (d3 >= d4)
            good_or[nor++] = ref;
        if (d4 >= d3)
            good_mir[nmir++] = ref;
    }
    if (d2 >= d1)
    {
        if (d4 >= d3)
            good_or[nor++] = ref->next;
        if (d3 >= d4)
            good_mir[nmir++] = ref->next;
    }

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    for (i = nv - 1; --i >= 0;)
        if (degree[i] == 2)
        {
            e = firstedge[i];
            d1 = degree[e->end];
            d2 = degree[e->next->end];
            col = VCOLPD(d1, d2);
            if (col > maxcol)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else if (col == maxcol)
            {
                d3 = degree[e->invers->next->end];
                d4 = degree[e->invers->prev->end];
                col2 = VCOLPD(d3, d4);

                if (col2 > maxcol2)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (col2 == maxcol2)
                {
                    if (d1 >= d2)
                    {
                        if (d3 >= d4)
                            good_or[nor++] = e;
                        if (d4 >= d3)
                            good_mir[nmir++] = e;
                    }
                    if (d2 >= d1)
                    {
                        if (d4 >= d3)
                            good_or[nor++] = e->next;
                        if (d3 >= d4)
                            good_mir[nmir++] = e->next;
                    }
                }
            }
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/****************************************************************************/

static void
quadr_P1_legal_all(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
                   EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* The P1-operation with reference edge *ref has just been performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal P1-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-1.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   P1-reductions have a priority (colour) based on the degrees of the
   end vertex and two side vertices.  It cannot be changed without
   changing find_extensions_quad too.

   version for general quadrangulations
   assumes no vertices of degree 2
*/

{
    EDGE *e, *ee, *elast;
    int maxdeg;
    int col, maxcol;
    int i, nor, nmir;

#define QORCOL(e) (((long)degree[e->prev->end] << 10) + (long)degree[e->next->end])
#define QMIRCOL(e) (((long)degree[e->next->end] << 10) + (long)degree[e->prev->end])

    RESETMARKS;
    nor = nmir = 0;

    maxdeg = degree[ref->end];
    maxcol = QORCOL(ref);
    col = QMIRCOL(ref);
    if (col < maxcol)
        good_or[nor++] = ref;
    else if (col == maxcol)
    {
        good_or[nor++] = ref;
        good_mir[nmir++] = ref;
    }
    else
    {
        maxcol = col;
        good_mir[nmir++] = ref;
    }

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    MARKLO(ref->invers);

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    if (*ngood_ref == 0 && *ngood_mir_ref == 0)
        return;

    for (i = 0; i < nv; ++i)
        if (degree[i] > maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e) && degree[e->end] == 3)
                {
                    ee = e->invers;
                    if (legal_P1_reduction_all(ee))
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        return;
                    }
                }
                e = e->next;
            } while (e != elast);
        }
        else if (degree[i] == maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                ee = e->invers;
                if (degree[e->end] == 3 && !ISMARKEDLO(e) && legal_P1_reduction_all(ee))
                {
                    col = QORCOL(e->invers);
                    if (col > maxcol)
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        return;
                    }
                    else if (col == maxcol)
                        good_or[nor++] = e->invers;

                    col = QMIRCOL(e->invers);
                    if (col > maxcol)
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        return;
                    }
                    else if (col == maxcol)
                        good_mir[nmir++] = e->invers;
                }
                e = e->next;
            } while (e != elast);
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/****************************************************************************/

static void
quadr_P1_legal_nf4(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
                   EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref,
                   EDGE *prevP1[], int nprevP1, EDGE **hint)

/* The P1-operation with reference edge *ref has just been performed.
   prevP1[0..nprevP1-1] are all earlier P1s since the last P2 or P3.
   hint (unless it is NULL) is a suggestion for a P1-reduction that
   might be better than ref.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal P1-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-1.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   P1-reductions have a priority (colour) based on the degrees of the
   end vertex and two side vertices.  It cannot be changed without
   changing find_extensions_quad too.

   Version for 3-connected quadrangulations without non-facial 4-cycles.
*/

{
    EDGE *e, *ee, *elast;
    int maxdeg;
    int col, maxcol;
    int i, nor, nmir;

#define QORCOL(e) (((long)degree[e->prev->end] << 10) + (long)degree[e->next->end])
#define QMIRCOL(e) (((long)degree[e->next->end] << 10) + (long)degree[e->prev->end])

    RESETMARKS;
    nor = nmir = 0;

    maxdeg = degree[ref->end];
    maxcol = QORCOL(ref);
    col = QMIRCOL(ref);
    if (col < maxcol)
        good_or[nor++] = ref;
    else if (col == maxcol)
    {
        good_or[nor++] = ref;
        good_mir[nmir++] = ref;
    }
    else
    {
        maxcol = col;
        good_mir[nmir++] = ref;
    }

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    MARKLO(ref->invers);

    e = *hint;
    if (e && !ISMARKEDLO(e->invers) && degree[e->start] == 3 && degree[e->end] > maxdeg && degree[e->next->end] >= 4 && degree[e->prev->end] >= 4 && legal_P1_reduction_nf4(e))
    {
        if (degree[e->end] > maxdeg)
        {
            *ngood_ref = *ngood_mir_ref = 0;
            return;
        }
        else
        {
            col = QORCOL(e);
            if (col > maxcol)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else if (col == maxcol)
                good_or[nor++] = e;

            col = QMIRCOL(e);
            if (col > maxcol)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else if (col == maxcol)
                good_mir[nmir++] = e;
        }
        MARKLO(e->invers);
    }

    for (i = nprevP1; --i >= 0;)
    {
        e = prevP1[i];
        if (!ISMARKEDLO(e->invers) && degree[e->end] >= maxdeg && degree[e->start] == 3 && degree[e->next->end] >= 4 && degree[e->prev->end] >= 4 && legal_P1_reduction_nf4(e))
        {
            if (degree[e->end] > maxdeg)
            {
                *ngood_ref = *ngood_mir_ref = 0;
                return;
            }
            else
            {
                col = QORCOL(e);
                if (col > maxcol)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (col == maxcol)
                    good_or[nor++] = e;

                col = QMIRCOL(e);
                if (col > maxcol)
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                else if (col == maxcol)
                    good_mir[nmir++] = e;
            }
        }
        MARKLO(e->invers);
    }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    if (*ngood_ref == 0 && *ngood_mir_ref == 0)
        return;

    for (i = 0; i < nv; ++i)
        if (degree[i] > maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e) && degree[e->end] == 3)
                {
                    ee = e->invers;
                    if (degree[ee->next->end] >= 4 && degree[ee->prev->end] >= 4 && legal_P1_reduction_nf4(ee))
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        *hint = e;
                        return;
                    }
                }
                e = e->next;
            } while (e != elast);
        }
        else if (degree[i] == maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                ee = e->invers;
                if (degree[e->end] == 3 && !ISMARKEDLO(e) && degree[ee->next->end] >= 4 && degree[ee->prev->end] >= 4 && legal_P1_reduction_nf4(ee))
                {
                    col = QORCOL(e->invers);
                    if (col > maxcol)
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        *hint = e;
                        return;
                    }
                    else if (col == maxcol)
                        good_or[nor++] = e->invers;

                    col = QMIRCOL(e->invers);
                    if (col > maxcol)
                    {
                        *ngood_ref = *ngood_mir_ref = 0;
                        *hint = e;
                        return;
                    }
                    else if (col == maxcol)
                        good_mir[nmir++] = e->invers;
                }
                e = e->next;
            } while (e != elast);
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/****************************************************************************/

static void
quadr_P3_legal(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
               EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* The P3-operation with reference edge *ref has just been performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal P3-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-4.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   P3-reductions have a priority (colour) based on the degrees of the
   end vertex and two side vertices.  It cannot be changed without
   changing find_extensions_quad too.
*/

{
    EDGE *e, *elast, *e1;
    int maxdeg;
    int col, col1, col2, maxcol;
    int i, j, nor, nmir;

#define QORCOL3(e) \
    (((long)degree[e->next->end] << 10) + (long)degree[e->prev->end])
#define QMIRCOL3(e) \
    (((long)degree[e->prev->end] << 10) + (long)degree[e->next->end])

    RESETMARKS;

    maxdeg = 0;
    e1 = ref->next;

    for (j = 0; j < 4; ++j)
    {
        if (degree[e1->start] > maxdeg)
        {
            maxdeg = degree[e1->start];
            maxcol = QORCOL3(e1);
            nor = nmir = 0;
            good_or[nor++] = e1;

            col = QMIRCOL3(e1);
            if (col > maxcol)
            {
                nor = nmir = 0;
                good_mir[nmir++] = e1;
                maxcol = col;
            }
            else if (col == maxcol)
                good_mir[nmir++] = e1;
        }
        else if (degree[e1->start] == maxdeg)
        {
            col = QORCOL3(e1);
            if (col > maxcol)
            {
                nor = nmir = 0;
                good_or[nor++] = e1;
                maxcol = col;
            }
            else if (col == maxcol)
                good_or[nor++] = e1;

            col = QMIRCOL3(e1);
            if (col > maxcol)
            {
                nor = nmir = 0;
                good_mir[nmir++] = e1;
                maxcol = col;
            }
            else if (col == maxcol)
                good_mir[nmir++] = e1;
        }

        MARKLO(e1);
        e1 = e1->prev->invers->prev;
    }

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    for (i = 0; i < nv; ++i)
        if (degree[i] > maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e) && legal_P3_reduction(e->prev))
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                e = e->next;
            } while (e != elast);
        }
        else if (degree[i] == maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e))
                {
                    col1 = QORCOL3(e);
                    col2 = QMIRCOL3(e);
                    if (col1 > maxcol || col2 > maxcol)
                    {
                        if (legal_P3_reduction(e->prev))
                        {
                            *ngood_ref = *ngood_mir_ref = 0;
                            return;
                        }
                    }
                    else if ((col1 == maxcol || col2 == maxcol) && legal_P3_reduction(e->prev))
                    {
                        if (col1 == maxcol)
                            good_or[nor++] = e;
                        if (col2 == maxcol)
                            good_mir[nmir++] = e;
                    }
                }
                e = e->next;
            } while (e != elast);
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/****************************************************************************/

static void
quadr_P3_legal_min3(EDGE *ref, EDGE *good_or[], int *ngood_or, int *ngood_ref,
                    EDGE *good_mir[], int *ngood_mir, int *ngood_mir_ref)

/* The P3-operation with reference edge *ref has just been performed.
   Make a list in good_or[0..*ngood_or-1] of the reference edges of
   legal P3-reductions (oriented editions) that might be canonical,
   with the first *ngood_ref of those being ref.
   Make a list in good_mir[0..*ngood_mir-1] of the
   reference edges of legal four-reductions (mirror-image editions)
   that might be canonical, with the first *ngood_mir_ref of those being
   ref->next.
   *ngood_ref and *ngood_mir_ref might each be 0-4.  If they are
   both 0, nothing else need be correct.
   All the edges in good_or[] and good_mir[] must start with the same
   vertex degree and end with the same vertex degree (actually, colour
   as passed to canon_edge_oriented).
   P3-reductions have a priority (colour) based on the degrees of the
   end vertex and two side vertices.  It cannot be changed without
   changing find_extensions_quad too.

   mindeg 3 version
*/

{
    EDGE *e, *elast, *e1;
    int maxdeg;
    int col, col1, col2, maxcol;
    int i, j, nor, nmir;

#define QORCOL3(e) \
    (((long)degree[e->next->end] << 10) + (long)degree[e->prev->end])
#define QMIRCOL3(e) \
    (((long)degree[e->prev->end] << 10) + (long)degree[e->next->end])

    RESETMARKS;

    maxdeg = 0;
    e1 = ref->next;

    for (j = 0; j < 4; ++j)
    {
        if (degree[e1->start] > maxdeg)
        {
            maxdeg = degree[e1->start];
            maxcol = QORCOL3(e1);
            nor = nmir = 0;
            good_or[nor++] = e1;

            col = QMIRCOL3(e1);
            if (col > maxcol)
            {
                nor = nmir = 0;
                good_mir[nmir++] = e1;
                maxcol = col;
            }
            else if (col == maxcol)
                good_mir[nmir++] = e1;
        }
        else if (degree[e1->start] == maxdeg)
        {
            col = QORCOL3(e1);
            if (col > maxcol)
            {
                nor = nmir = 0;
                good_or[nor++] = e1;
                maxcol = col;
            }
            else if (col == maxcol)
                good_or[nor++] = e1;

            col = QMIRCOL3(e1);
            if (col > maxcol)
            {
                nor = nmir = 0;
                good_mir[nmir++] = e1;
                maxcol = col;
            }
            else if (col == maxcol)
                good_mir[nmir++] = e1;
        }

        MARKLO(e1);
        e1 = e1->prev->invers->prev;
    }

    *ngood_ref = nor;
    *ngood_mir_ref = nmir;

    for (i = 0; i < nv; ++i)
        if (degree[i] > maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e) && legal_P3_reduction_min3(e->prev))
                {
                    *ngood_ref = *ngood_mir_ref = 0;
                    return;
                }
                e = e->next;
            } while (e != elast);
        }
        else if (degree[i] == maxdeg)
        {
            e = elast = firstedge[i];
            do
            {
                if (!ISMARKEDLO(e))
                {
                    col1 = QORCOL3(e);
                    col2 = QMIRCOL3(e);
                    if (col1 > maxcol || col2 > maxcol)
                    {
                        if (legal_P3_reduction_min3(e->prev))
                        {
                            *ngood_ref = *ngood_mir_ref = 0;
                            return;
                        }
                    }
                    else if ((col1 == maxcol || col2 == maxcol) && legal_P3_reduction_min3(e->prev))
                    {
                        if (col1 == maxcol)
                            good_or[nor++] = e;
                        if (col2 == maxcol)
                            good_mir[nmir++] = e;
                    }
                }
                e = e->next;
            } while (e != elast);
        }

    if (nor > *ngood_ref || nmir > *ngood_mir_ref)
        prune_oriented_lists(good_or, &nor, ngood_ref,
                             good_mir, &nmir, ngood_mir_ref);

    *ngood_or = nor;
    *ngood_mir = nmir;
}

/****************************************************************************/

static void
scanquadrangulations(int nbtot, int nbop, EDGE *spoke, int dosplit,
                     EDGE *P1edge[], int nP1edges)

/* The main node of the recursion for 3-connected quadrangulations.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   If spoke!=NULL the input is a pseudo-double wheel and this is a
   spoke from the rim towards the hub.
   If dosplit==TRUE, this is the place to do splitting (if any).
   Splitting is a bit more complicated because the P operation adds
   two vertices.
   P1edge[0..nP1edges-1] are edges of the graph that were reference
   edges for P1-operations in ancestors of this graph.  They may not
   be reference edges for P1-reductions now, but at least they are edges.
   However, if nP1edges>0, we can say that certainly P1edge[nP1edges-1]
   is a P1-operation that was just done.
*/

{
    EDGE *firstedge_save[MAXN];
    EDGE *extP1[MAXE], *extP3[MAXE];
    EDGE *good_or[MAXE], *good_mir[MAXE];
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int nextP1, nextP3, i;
    int xnbtot, xnbop;
    EDGE *newP1edge[MAXN], *rededge;
    EDGE *hint;

    if (nv == maxnv)
    {
        if (pswitch)
            startbipscan(nbtot, nbop, 3);
        else
            got_one(nbtot, nbop, 3);
        return;
    }

    if (dosplit)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_QUAD
    if (!(PRE_FILTER_QUAD))
        return;
#endif

#ifndef FIND_EXTENSIONS_QUAD
#define FIND_EXTENSIONS_QUAD find_extensions_quad
#endif

    FIND_EXTENSIONS_QUAD(nbtot, nbop, extP1, &nextP1, extP3, &nextP3,
                         (nP1edges == 0 ? NULL : P1edge[nP1edges - 1]));

    if (spoke && nv <= maxnv - 2)
    {
        rededge = extend_quadr_P2(spoke);
#ifdef FAST_FILTER_QUAD
        if (FAST_FILTER_QUAD)
#endif
        {
            (void)canon(degree, numbering, &xnbtot, &xnbop);
            scanquadrangulations(xnbtot, xnbop, spoke,
                                 nv == splitlevel || nv == splitlevel + 1, newP1edge, 0);
        }
        reduce_quadr_P2(rededge);
    }

    hint = NULL;
    for (i = 0; i < nextP1; ++i)
    {
        rededge = extend_quadr_P1(extP1[i]);
#ifdef FAST_FILTER_QUAD
        if (FAST_FILTER_QUAD)
#endif
        {
            quadr_P1_legal(rededge, good_or, &ngood_or, &ngood_ref, good_mir,
                           &ngood_mir, &ngood_mir_ref, P1edge, nP1edges, &hint);
            if (ngood_ref + ngood_mir_ref > 0)
            {
                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref)
                    got_one(1, 1, 3);
                else if (ngood_or + ngood_mir == 1)
                {
                    P1edge[nP1edges] = rededge;
                    scanquadrangulations(1, 1, NULL, nv == splitlevel,
                                         P1edge, nP1edges + 1);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    P1edge[nP1edges] = rededge;
                    scanquadrangulations(xnbtot, xnbop, NULL, nv == splitlevel,
                                         P1edge, nP1edges + 1);
                }
            }
        }
        reduce_quadr_P1(rededge);
    }

    for (i = 0; i < nextP3; ++i)
    {
        rededge = extend_quadr_P3(extP3[i]);
#ifdef FAST_FILTER_QUAD
        if (FAST_FILTER_QUAD)
#endif
        {
            if (!has_quadr_P1())
            {
                quadr_P3_legal(rededge, good_or, &ngood_or, &ngood_ref,
                               good_mir, &ngood_mir, &ngood_mir_ref);
                if (ngood_ref + ngood_mir_ref > 0 && canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                                                         good_mir, ngood_mir, ngood_mir_ref,
                                                                         degree, numbering, &xnbtot, &xnbop))
                    scanquadrangulations(xnbtot, xnbop, NULL,
                                         nv >= splitlevel && nv <= splitlevel + 3, newP1edge, 0);
            }
        }
        reduce_quadr_P3(rededge);
    }

    if (dosplit)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/****************************************************************************/

static void
scanquadrangulations_min3(int nbtot, int nbop, EDGE *spoke, int dosplit,
                          EDGE *P1edge[], int nP1edges)

/* The main node of the recursion for quadrangulations of mindeg 3.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   If spoke!=NULL the input is a pseudo-double wheel and this is a
   spoke from the rim towards the hub.
   If dosplit==TRUE, this is the place to do splitting (if any).
   Splitting is a bit more complicated because the P operation adds
   two vertices.
   P1edge[0..nP1edges-1] are edges of the graph that were reference
   edges for P1-operations in ancestors of this graph.  They may not
   be reference edges for P1-reductions now, but at least they are edges.
   However, if nP1edges>0, we can say that certainly P1edge[nP1edges-1]
   is a P1-operation that was just done.
*/

{
    EDGE *firstedge_save[MAXN];
    EDGE *extP1[MAXE], *extP3[MAXE];
    EDGE *good_or[MAXE], *good_mir[MAXE];
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int nextP1, nextP3, i;
    int xnbtot, xnbop, conn;
    EDGE *newP1edge[MAXN], *rededge;
    EDGE *hint;

    if (nv == maxnv)
    {
        if (pswitch || xswitch)
            conn = con_quad();
        else
            conn = 2; /* really 2 or 3 */

        if (pswitch)
            startbipscan(nbtot, nbop, conn);
        else
            got_one(nbtot, nbop, conn);
        return;
    }

    if (dosplit)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_QUAD_MIN3
    if (!(PRE_FILTER_QUAD_MIN3))
        return;
#endif

#ifndef FIND_EXTENSIONS_QUAD_MIN3
#define FIND_EXTENSIONS_QUAD_MIN3 find_extensions_quad_min3
#endif

    FIND_EXTENSIONS_QUAD_MIN3(nbtot, nbop, extP1, &nextP1, extP3, &nextP3,
                              (nP1edges == 0 ? NULL : P1edge[nP1edges - 1]));

    if (spoke && nv <= maxnv - 2)
    {
        rededge = extend_quadr_P2(spoke);
#ifdef FAST_FILTER_QUAD_MIN3
        if (FAST_FILTER_QUAD_MIN3)
#endif
        {
            (void)canon(degree, numbering, &xnbtot, &xnbop);
            scanquadrangulations_min3(xnbtot, xnbop, spoke,
                                      nv == splitlevel || nv == splitlevel + 1, newP1edge, 0);
        }
        reduce_quadr_P2(rededge);
    }

    hint = NULL;
    for (i = 0; i < nextP1; ++i)
    {
        rededge = extend_quadr_P1(extP1[i]);
#ifdef FAST_FILTER_QUAD_MIN3
        if (FAST_FILTER_QUAD_MIN3)
#endif
        {
            quadr_P1_legal_min3(rededge, good_or, &ngood_or, &ngood_ref, good_mir,
                                &ngood_mir, &ngood_mir_ref, P1edge, nP1edges, &hint);
            if (ngood_ref + ngood_mir_ref > 0)
            {
                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref)
                    got_one(1, 1, 3);
                else if (ngood_or + ngood_mir == 1)
                {
                    P1edge[nP1edges] = rededge;
                    scanquadrangulations_min3(1, 1, NULL, nv == splitlevel,
                                              P1edge, nP1edges + 1);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    P1edge[nP1edges] = rededge;
                    scanquadrangulations_min3(xnbtot, xnbop, NULL, nv == splitlevel,
                                              P1edge, nP1edges + 1);
                }
            }
        }
        reduce_quadr_P1(rededge);
    }

    for (i = 0; i < nextP3; ++i)
    {
        rededge = extend_quadr_P3(extP3[i]);
#ifdef FAST_FILTER_QUAD_MIN3
        if (FAST_FILTER_QUAD_MIN3)
#endif
        {
            if (!has_quadr_P1_min3())
            {
                quadr_P3_legal_min3(rededge, good_or, &ngood_or, &ngood_ref,
                                    good_mir, &ngood_mir, &ngood_mir_ref);
                if (ngood_ref + ngood_mir_ref > 0 && canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                                                         good_mir, ngood_mir, ngood_mir_ref,
                                                                         degree, numbering, &xnbtot, &xnbop))
                    scanquadrangulations_min3(xnbtot, xnbop, NULL,
                                              nv >= splitlevel && nv <= splitlevel + 3, newP1edge, 0);
            }
        }
        reduce_quadr_P3(rededge);
    }

    if (dosplit)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/****************************************************************************/

static void
scanquadrangulations_nf4(int nbtot, int nbop, EDGE *spoke, int dosplit,
                         EDGE *P1edge[], int nP1edges)

/* The main node of the recursion for 3-connected quadrangulations
   without non-facial 4-cycles.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
   If spoke!=NULL the input is a pseudo-double wheel and this is a
   spoke from the rim towards the hub.
   If dosplit==TRUE, this is the place to do splitting (if any).
   Splitting is a bit more complicated because the P operation adds
   two vertices.
   P1edge[0..nP1edges-1] are edges of the graph that were reference
   edges for P1-operations in ancestors of this graph.  They may not
   be reference edges for P1-reductions now, but at least they are edges.
   However, if nP1edges>0, we can say that certainly P1edge[nP1edges-1]
   is a P1-operation that was just done.
*/

{
    EDGE *firstedge_save[MAXN];
    EDGE *extP1[MAXE];
    EDGE *good_or[MAXE], *good_mir[MAXE];
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int nextP1, i;
    int xnbtot, xnbop;
    EDGE *newP1edge[MAXN], *rededge;
    EDGE *hint;

    if (nv == maxnv)
    {
        got_one(nbtot, nbop, 4); /* Note connectivity is really 3 */
        return;
    }

    if (dosplit)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_QUAD_NF4
    if (!(PRE_FILTER_QUAD_NF4))
        return;
#endif

#ifndef FIND_EXTENSIONS_QUAD_NF4
#define FIND_EXTENSIONS_QUAD_NF4 find_extensions_quad_nf4
#endif

    FIND_EXTENSIONS_QUAD_NF4(nbtot, nbop, extP1, &nextP1,
                             (nP1edges == 0 ? NULL : P1edge[nP1edges - 1]));

    if (spoke && nv <= maxnv - 2)
    {
        rededge = extend_quadr_P2(spoke);
#ifdef FAST_FILTER_QUAD_NF4
        if (FAST_FILTER_QUAD_NF4)
#endif
        {
            (void)canon(degree, numbering, &xnbtot, &xnbop);
            scanquadrangulations_nf4(xnbtot, xnbop, spoke,
                                     nv == splitlevel || nv == splitlevel + 1, newP1edge, 0);
        }
        reduce_quadr_P2(rededge);
    }

    hint = NULL;
    for (i = 0; i < nextP1; ++i)
    {
        rededge = extend_quadr_P1(extP1[i]);
#ifdef FAST_FILTER_QUAD_NF4
        if (FAST_FILTER_QUAD_NF4)
#endif
        {
            quadr_P1_legal_nf4(rededge, good_or, &ngood_or, &ngood_ref, good_mir,
                               &ngood_mir, &ngood_mir_ref, P1edge, nP1edges, &hint);
            if (ngood_ref + ngood_mir_ref > 0)
            {
                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref)
                    got_one(1, 1, 4);
                else if (ngood_or + ngood_mir == 1)
                {
                    P1edge[nP1edges] = rededge;
                    scanquadrangulations_nf4(1, 1, NULL, nv == splitlevel,
                                             P1edge, nP1edges + 1);
                }
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                {
                    P1edge[nP1edges] = rededge;
                    scanquadrangulations_nf4(xnbtot, xnbop, NULL, nv == splitlevel,
                                             P1edge, nP1edges + 1);
                }
            }
        }
        reduce_quadr_P1(rededge);
    }

    if (dosplit)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/****************************************************************************/

static void
scanquadrangulations_all(int nbtot, int nbop)

/* The main node of the recursion for general simple quadrangulations.
   As this procedure is entered, nv,ne,degree etc are set for some graph,
   and nbtot/nbop are the values returned by canon() for that graph.
*/

{
    EDGE *firstedge_save[MAXN];
    EDGE *extP0[MAXE], *extP1[MAXE];
    EDGE *good_or[MAXE], *good_mir[MAXE];
    int ngood_or, ngood_mir, ngood_ref, ngood_mir_ref;
    int nextP0, nextP1, i;
    int xnbtot, xnbop, conn;
    EDGE *rededge;

    if (nv == maxnv)
    {
        if (pswitch || xswitch)
            conn = con_quad();
        else
            conn = 2; /* really 2 or 3 */

        if (pswitch)
            startbipscan(nbtot, nbop, conn);
        else
            got_one(nbtot, nbop, conn);
        return;
    }

    if (nv == splitlevel)
    {
#ifdef SPLITTEST
        ADDBIG(splitcases, 1);
        return;
#endif
        if (splitcount-- != 0)
            return;
        splitcount = mod - 1;

        for (i = 0; i < nv; ++i)
            firstedge_save[i] = firstedge[i];
    }

#ifdef PRE_FILTER_QUAD_ALL
    if (!(PRE_FILTER_QUAD_ALL))
        return;
#endif

#ifndef FIND_EXTENSIONS_QUAD_ALL
#define FIND_EXTENSIONS_QUAD_ALL find_extensions_quad_all
#endif

    FIND_EXTENSIONS_QUAD_ALL(nbtot, nbop, extP0, &nextP0, extP1, &nextP1);

    for (i = 0; i < nextP0; ++i)
    {
        rededge = extend_quadr_P0(extP0[i]);
#ifdef FAST_FILTER_QUAD_ALL
        if (FAST_FILTER_QUAD_ALL)
#endif
        {
            quadr_P0_legal_all(rededge, good_or, &ngood_or, &ngood_ref, good_mir,
                               &ngood_mir, &ngood_mir_ref);
            if (ngood_ref + ngood_mir_ref > 0)
            {
                if (nv == maxnv && !needgroup && ngood_or == ngood_ref && ngood_mir == ngood_mir_ref)
                    got_one(1, 1, 2);
                else if (ngood_or + ngood_mir == 1)
                    scanquadrangulations_all(1, 1);
                else if (canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                             good_mir, ngood_mir, ngood_mir_ref,
                                             degree, numbering, &xnbtot, &xnbop))
                    scanquadrangulations_all(xnbtot, xnbop);
            }
        }
        reduce_quadr_P0(rededge);
    }

    for (i = 0; i < nextP1; ++i)
    {
        rededge = extend_quadr_P1(extP1[i]);
#ifdef FAST_FILTER_QUAD_ALL
        if (FAST_FILTER_QUAD_ALL)
#endif
        {
            if (!has_quadr_P0())
            {
                quadr_P1_legal_all(rededge, good_or, &ngood_or, &ngood_ref,
                                   good_mir, &ngood_mir, &ngood_mir_ref);
                if (ngood_ref + ngood_mir_ref > 0 && canon_edge_oriented(good_or, ngood_or, ngood_ref,
                                                                         good_mir, ngood_mir, ngood_mir_ref,
                                                                         degree, numbering, &xnbtot, &xnbop))
                    scanquadrangulations_all(xnbtot, xnbop);
            }
        }
        reduce_quadr_P1(rededge);
    }

    if (nv == splitlevel)
        for (i = 0; i < nv; ++i)
            firstedge[i] = firstedge_save[i];
}

/****************************************************************************/

static int
getswitchvalue(char *arg, int *pj)

/* Find integer value for switch. 
   arg is a pointer to a command-line argument.
   pj is an index into arg, which is updated.
   The value of the switch is the function return value.
   For example, if arg="-xyz1432q" and *pj=3 (pointing at "z"),
       the value 1432 is returned and *pj=7 (pointing at "2").
   An absent value is equivalent to 0.
*/

{
    int j, ans;

    ans = 0;
    for (j = *pj; arg[j + 1] >= '0' && arg[j + 1] <= '9'; ++j)
        ans = ans * 10 + (arg[j + 1] - '0');

    *pj = j;
    return ans;
}

/****************************************************************************/

static void
getswitchvaluelist(char *arg, int *pj, int list[], char delim[],
                   int limit, int *count, char *sep)

/* Decode an integer-list argument for a switch.
   arg is a pointer to a command-line argument.
   *pj is the index of the switch name
     Following the switch name is a list of up to limit non-negative
     integers separated by characters from the string *sep.  They are
     found and put into list[0...] and the number of them into *count.
     The character before each number is put into delim[0..].
     The final value of *pj is the last digit of the last value.
     Empty values are taken as 0.
   For example, if arg = "az12:45-98q" and *pj=2 (at the 'z'), then
   the result will be list[0]=12, list[1]=45, list[2]=98,
                      delim[0]='z', delim[1]=':', delim[2]='-',
   *count=3, and *pj=10 (at the 'q').
*/
{
    int j, val;
    int go;

    *count = 0;
    j = *pj + 1;

    go = TRUE;
    delim[0] = arg[*pj];

    while (go)
    {
        if (*count >= limit)
        {
            fprintf(stderr,
                    ">E %s: too many values for -%c\n", cmdname, arg[*pj]);
            exit(1);
        }

        val = 0;
        while (arg[j] >= '0' && arg[j] <= '9')
        {
            val = val * 10 + (arg[j] - '0');
            ++j;
        }
        list[(*count)++] = val;

        if (arg[j] != '\0' && strchr(sep, arg[j]))
            delim[*count] = arg[j++];
        else
            go = FALSE;
    }

    *pj = j - 1;
}

/****************************************************************************/

static void
check_switch(char sw, char *ok_switches)

/* If ok_switches[sw] is zero, write an error message and exit. */

{
    if (!OK_SWITCHES(sw))
    {
        fprintf(stderr, ">E %s:  -%c is not permitted\n", cmdname, sw);
        exit(1);
    }
}

/****************************************************************************/

static void
decode_command_line(int argc, char *argv[])

/* Decode the command line, setting the global variables which
   give the switch values.  Some basic checking is done too, but
   the most detailed checking is done later.  If an error is
   found, this procedure never returns.

   The values for numerical parameters (minconnec, minimumdeg,
   edgebound[0..1], maxfacesize, polygonsize are set as -1 if the
   parameter is not mentioned, 0 if it appears without an integer
   following, and the given integer value if there is one.  Negative
   values are not currently allowed.
*/

{
    int i, j, ares, amod;
    char *arg, delims[2], *as;
    int badargs, argsgot;
    int numbounds;
    char ok_switches[256];

    for (i = 0; i < argc; ++i)
        fprintf(stderr, "%s ", argv[i]);
    fprintf(stderr, "\n");

    cmdname = argv[0];

    for (i = 0; i < 256; ++i)
        OK_SWITCHES(i) = 0;
    for (as = SWITCHES; *as != '\0'; ++as)
        OK_SWITCHES(*as) = 1;
    OK_SWITCHES('[') = OK_SWITCHES(']') = OK_SWITCHES(' ') = 0;
    OK_SWITCHES(':') = OK_SWITCHES('-') = OK_SWITCHES('#') = 0;
    for (as = SECRET_SWITCHES; *as != '\0'; ++as)
        OK_SWITCHES(*as) = 1;

    argsgot = 0;
    badargs = FALSE;
    outfilename = NULL;
    aswitch = FALSE;
    gswitch = FALSE;
    sswitch = FALSE;
    Eswitch = FALSE;
    Gswitch = FALSE;
    hswitch = FALSE;
    oswitch = FALSE;
    dswitch = FALSE;
    tswitch = FALSE;
    uswitch = FALSE;
    vswitch = FALSE;
    xswitch = FALSE;
    pswitch = FALSE;
    qswitch = FALSE;
    Aswitch = FALSE;
    zeroswitch = FALSE;
    oneswitch = FALSE;
    twoswitch = FALSE;
    minconnec = -1;
    edgebound[0] = edgebound[1] = -1;
    maxfacesize = -1;
    polygonsize = -1;
    minimumdeg = -1;
    res = 0;
    mod = 1;

    for (i = 1; !badargs && i < argc; ++i)
    {
        arg = argv[i];
        if (arg[0] == '-' && arg[1] != '\0')
        {
            for (j = 1; arg[j] != '\0'; ++j)
                if (arg[j] == '\0')
                {
                }
            BOOLSWITCH('o', oswitch)
            BOOLSWITCH('d', dswitch)
            BOOLSWITCH('G', Gswitch)
            BOOLSWITCH('V', Vswitch)
            BOOLSWITCH('h', hswitch)
            BOOLSWITCH('a', aswitch)
            BOOLSWITCH('g', gswitch)
            BOOLSWITCH('s', sswitch)
            BOOLSWITCH('E', Eswitch)
            BOOLSWITCH('u', uswitch)
            BOOLSWITCH('v', vswitch)
            BOOLSWITCH('x', xswitch)
            BOOLSWITCH('t', tswitch)
            BOOLSWITCH('p', pswitch)
            BOOLSWITCH('b', bswitch)
            BOOLSWITCH('q', qswitch)
            BOOLSWITCH('A', Aswitch)
            BOOLSWITCH('0', zeroswitch)
            BOOLSWITCH('1', oneswitch)
            BOOLSWITCH('2', twoswitch)
            INTSWITCH('f', maxfacesize)
            INTSWITCH('c', minconnec)
            INTSWITCH('P', polygonsize)
            INTSWITCH('m', minimumdeg)
            else if (arg[j] == 'e')
            {
                CHECKSWITCH('e');
                getswitchvaluelist(arg, &j, edgebound, delims, 2, &numbounds, ":-");
                if (numbounds == 1)
                    edgebound[1] = edgebound[0];
                if (edgebound[1] == 0)
                    edgebound[1] = MAXE / 2;
            }
#ifdef PLUGIN_SWITCHES
            PLUGIN_SWITCHES
#endif
            else
            {
                CHECKSWITCH(arg[j]);
                badargs = TRUE;
            }
        }
        else if (argsgot >= 3)
            badargs = TRUE;
        else if (argsgot == 0)
        {
            j = -1;
            maxnv = getswitchvalue(arg, &j);
            if (arg[j + 1] == 'd' && arg[j + 2] == '\0')
                if (maxnv & 1)
                {
                    fprintf(stderr, ">E %s: n with 'd' must be even\n", cmdname);
                    exit(1);
                }
                else
                    maxnv = maxnv / 2 + 2;
            else if (arg[j + 1] != '\0')
                badargs = TRUE;
            ++argsgot;
        }
        else
        {
            if (arg[0] == '-')
            {
                if (argsgot == 0)
                    badargs = TRUE;
            }
            else if (sscanf(arg, "%d/%d", &ares, &amod) == 2)
            {
                res = ares;
                mod = amod;
            }
            else
                outfilename = arg;
            ++argsgot;
        }
    }

    if (argsgot == 0)
        badargs = TRUE;

    if (badargs)
    {
        fprintf(stderr,
                ">E Usage: %s %s n [res/mod] [outfile]\n", cmdname, SWITCHES);
        exit(1);
    }

    if (res < 0 || res >= mod)
    {
        fprintf(stderr, ">E %s: must have 0 <= res < mod\n", cmdname);
        exit(1);
    }

    if (oswitch || Vswitch || oneswitch)
        Gswitch = TRUE;
    if (oneswitch)
        zeroswitch = TRUE;
}

/****************************************************************************/

static void
initialize_splitting(int minlevel, int hint, int maxlevel)

/* Set splitlevel and splitcount.  minlevel and maxlevel are bounds
   on its value.  It must be that both minlevel and maxlevel are at
   least equal to the largest starting order (nv for external calls
   to scansimple() or similar routines), and at most equal to the
   smallest parent of a parent of an internal-output graph (call
   from scansimple() or similar to got_one() or similar).  The size
   of internal-output graphs is maxnv-1 for planar triangulations
   and maxnv for other classes.

   hint is a desirable value, which can be anything as the actual
   value used is forced between minlevel and maxlevel.  For plugins,
   the value of splithint is used instead if it is >= 0.

   In case there is no way to use splitting within those limits,
   it is turned off by setting splitlevel=0.  In that case only
   subcase 0 should produce output.

   Splitting occurs at the first level where nv >= splitlevel.
   If an operation can add k vertices, it must be that
   splitlevel <= maxnv - k.
*/
{
    splitlevel = (twoswitch ? hint + 1 : hint);
#ifdef PLUGIN
    if (splithint >= 0)
        splitlevel = splithint;
#endif

    if (splitlevel > maxlevel)
        splitlevel = maxlevel;

    if (splitlevel < minlevel && splitlevel > 0)
    {
        if (minlevel <= maxlevel)
            splitlevel = minlevel;
        else
            splitlevel = 0;
    }
    if (mod == 1)
        splitlevel = 0;

    splitcount = res;
}

/****************************************************************************/

static void
open_output_file(void)

/* Open the output file, and write a header if one is called for.
   All the needed information is in global vars.  Also check if
   maxn is too large for this format, and set the global procedure
   variables write_graph() and write_dual_graph().
*/
{
    int nvf;

    if (aswitch + gswitch + sswitch + uswitch + Eswitch >= 2)
    {
        fprintf(stderr, ">E %s: -a, -g, -s, -u, -E are incompatible\n", cmdname);
        exit(1);
    }

    if (!uswitch) /*UPDATE for -E and reconconsider */
    {
        nvf = dswitch ? 2 * (maxnv - (polygonsize >= 0)) - 4 : maxnv - (polygonsize >= 0);
        if ((aswitch && nvf > 99) ||
            (gswitch && nvf > 255) ||
            (sswitch && nvf > 255) ||
            (!aswitch && !gswitch && !sswitch && nvf > 255))
        {
            fprintf(stderr, ">E %s: n is too large for that output format\n",
                    cmdname);
            exit(1);
        }
    }

    msgfile = stderr;
    if (outfilename == NULL)
    {
        outfilename = "stdout";
        outfile = stdout;
    }
    else if ((outfile = fopen(outfilename,
                              zeroswitch || aswitch || gswitch || sswitch ? "w" : "wb")) == NULL)
    {
        fprintf(stderr,
                ">E %s: can't open %s for writing\n", cmdname, outfilename);
        perror(">E ");
        exit(1);
    }

    if (zeroswitch) /* implied by oneswitch */
        write_graph = write_dual_graph = write_digits;
    else if (aswitch)
    {
        write_graph = write_alpha;
        write_dual_graph = write_dual_alpha;
    }
    else if (gswitch)
    {
        write_graph = write_graph6;
        write_dual_graph = write_dual_graph6;
    }
    else if (sswitch)
    {
        write_graph = write_sparse6;
        write_dual_graph = write_dual_sparse6;
    }
    else if (Eswitch)
    {
        write_graph = write_edgecode;
        write_dual_graph = write_dual_edgecode;
    }
    else
    {
        write_graph = write_planar_code;
        write_dual_graph = write_dual_planar_code;
    }

    if (!uswitch && !aswitch)
    {
        if ((!zeroswitch && !hswitch && !gswitch && !sswitch && !Eswitch &&
             fwrite(PCODE, (size_t)1, PCODELEN, outfile) != PCODELEN) ||
            (!hswitch && Eswitch &&
             fwrite(ECODE, (size_t)1, ECODELEN, outfile) != ECODELEN) ||
            (hswitch && gswitch &&
             fwrite(G6CODE, (size_t)1, G6CODELEN, outfile) != G6CODELEN) ||
            (hswitch && sswitch &&
             fwrite(S6CODE, (size_t)1, S6CODELEN, outfile) != S6CODELEN))
        {
            fprintf(stderr, ">E %s: error writing header\n", cmdname);
            perror(">E ");
            exit(1);
        }
    }
}

/****************************************************************************/

static void
simple_dispatch(void)

/* All the cases not handled in the other dispatch routines. */
{
    int startingsize, nbtot, nbop, i, hint;

    if (minimumdeg <= 0)
        minimumdeg = 3;
    if (minconnec <= 0)
        minconnec = minimumdeg;
    startingsize = 4;

    CHECKRANGE(maxnv, "n", 3, MAXN);
    CHECKRANGE(minconnec, "-c", 1, 3);
    CHECKRANGE(minimumdeg, "-m", 1, 3);

    INCOMPAT(edgebound[0] >= 0, "without -p", "-e");
    INCOMPAT(maxfacesize >= 0, "without -p", "-f");
    INCOMPAT(minconnec == 3 && xswitch && minimumdeg == 3, "-c3", "-x");
    INCOMPAT(Aswitch && (minimumdeg < 3 || minconnec < 3),
             "-A", "-c1/2 or -m1/2");

    if (minconnec < 3 && maxnv > 8 * sizeof(long))
    {
        fprintf(stderr, ">E %s: connectivity < 3 is restricted to n < %d\n",
                cmdname, (int)(8 * sizeof(long)));
        exit(1);
    }

    if (dswitch)
        strcpy(outtypename, "cubic graphs");
    else
        strcpy(outtypename, "triangulations");

    open_output_file();

    needgroup = Gswitch || minconnec < 3;

    hint = MIN(maxnv <= 13 ? maxnv - 2 : maxnv - 3, 14);
    initialize_splitting(startingsize, hint, maxnv - 1);
    if (splitlevel == 0 && res > 0)
        return;

    xconnec = minconnec;

    if (maxnv >= startingsize)
    {
        initialize_triang();
        canon(degree, numbering, &nbtot, &nbop);

#ifdef FAST_FILTER_SIMPLE
        if (FAST_FILTER_SIMPLE)
#endif
            scansimple(nbtot, nbop);
    }
    else if (maxnv == 3 && !Aswitch)
    {
        if (minconnec <= 2 && minimumdeg <= 2)
        {
            make_cycle(3);
            canon(degree, numbering, &nbtot, &nbop);
#ifdef FAST_FILTER_SIMPLE
            if (FAST_FILTER_SIMPLE)
#endif
                got_one(nbtot, nbop, 2);
        }
        if (minconnec == 1 && minimumdeg == 1 && !Aswitch)
        {
            make_gyro();
            canon(degree, numbering, &nbtot, &nbop);
#ifdef FAST_FILTER_SIMPLE
            if (FAST_FILTER_SIMPLE)
#endif
                got_one(nbtot, nbop, 1);
        }
    }

#ifdef STATS
    fprintf(msgfile, "Counts by min degree: ");
    for (i = minimumdeg; i <= 5; ++i)
    {
        PRINTBIG(msgfile, nummindeg[i]);
        if (i != 5)
            fprintf(msgfile, " ");
        else
            fprintf(msgfile, "\n");
    }
#endif

    if (vswitch && minconnec < 3 && !xswitch)
    {
        fprintf(msgfile, "By connectivity: ");
        for (i = minconnec; i <= 3; ++i)
        {
            if (i > minconnec)
                fprintf(msgfile, " ");
            PRINTBIG(msgfile, nout[i]);
            if (i == 3)
                fprintf(msgfile, " (3-5)-conn");
            else
                fprintf(msgfile, " %d-conn", i);
            if (i < 3)
                fprintf(msgfile, ";");
        }
        fprintf(msgfile, "\n");

        if (oswitch)
        {
            fprintf(msgfile, "By connectivity (O-P): ");
            for (i = minconnec; i <= 3; ++i)
            {
                if (i > minconnec)
                    fprintf(msgfile, " ");
                PRINTBIG(msgfile, nout_op[i]);
                if (i == 3)
                    fprintf(msgfile, " (3-5)-conn");
                else
                    fprintf(msgfile, " %d-conn", i);
                if (i < 3)
                    fprintf(msgfile, ";");
            }
            fprintf(msgfile, "\n");
        }
    }
}

/****************************************************************************/

static void
polygon_dispatch(void)

/* Triangulations of a polygon.  This works by making a triangulation
   one size bigger, then deleting a vertex.  maxnv is set one size
   larger to achieve this, but put back before this procedure returns. */
{
    int i, startingsize, nbtot, nbop, hint;

    if (minconnec <= 0)
        minconnec = 3;
    if (minimumdeg <= 0)
        minimumdeg = 3;
    startingsize = 4;

    CHECKRANGE(maxnv, "n", startingsize - 1, MAXN - 1);
    ++maxnv;
    CHECKRANGE(minconnec, "-c", 2, 3);
    CHECKRANGE(minimumdeg, "-m", 2, 3);
    PERROR(polygonsize == 1 || polygonsize == 2 || polygonsize >= maxnv,
           "value of -P must be empty or 3..n-1\n");

    INCOMPAT(Aswitch, "-P", "-A");
    INCOMPAT(pswitch, "-P", "-p");
    INCOMPAT(bswitch, "-P", "-b");
    INCOMPAT(tswitch, "-P", "-t");
    INCOMPAT(qswitch, "-P", "-q");
    INCOMPAT(edgebound[0] >= 0, "-P", "-e");
    INCOMPAT(maxfacesize >= 0, "-P", "-f");

    if (minimumdeg < minconnec)
        minimumdeg = minconnec;

    if (dswitch)
        strcpy(outtypename, "duals of disk triangulations");
    else
        strcpy(outtypename, "disk triangulations");

    open_output_file();

    for (i = 0; i <= MAXN; ++i)
    {
        ZEROBIG(nout_p[i]);
        ZEROBIG(nout_p_op[i]);
    }

    needgroup = TRUE;

    hint = MIN(maxnv <= 12 ? maxnv - 1 : maxnv - 2, 14);
    initialize_splitting(startingsize, hint, maxnv - 1);
    if (splitlevel == 0 && res > 0)
    {
        --maxnv;
        return;
    }

    xconnec = minconnec;

    initialize_triang();
    canon(degree, numbering, &nbtot, &nbop);
    scansimple(nbtot, nbop);

    --maxnv;

    if (vswitch && polygonsize == 0)
    {
        for (i = 0; i <= MAXN; ++i)
            if (!ISZEROBIG(nout_p[i]))
            {
                fprintf(msgfile, " With %2d-gon: ", i);
                if (oswitch)
                {
                    PRINTBIG(msgfile, nout_p_op[i]);
                    fprintf(msgfile, " (");
                    PRINTBIG(msgfile, nout_p[i]);
                    fprintf(msgfile, " classes)\n");
                }
                else
                {
                    PRINTBIG(msgfile, nout_p[i]);
                    fprintf(msgfile, "\n");
                }
            }
    }
}

/****************************************************************************/

static void
min4_dispatch(void)

/* Case of minimum degree >= 4, except for polygons and polytopes. */
{
    int startingsize, nbtot, nbop, hint;
    triangle nft[MAXN];

    if (minimumdeg <= 0)
        minimumdeg = 4;
    if (minconnec <= 0)
        minconnec = 3;
    startingsize = 6;

    CHECKRANGE(maxnv, "n", startingsize, MAXN);
    CHECKRANGE(minconnec, "-c", 3, 4);
    CHECKRANGE(minimumdeg, "-m", 4, 4);

    INCOMPAT(tswitch, "-m4 or -c4", "-t");
    INCOMPAT(qswitch, "-m4 or -c4", "-q");
    INCOMPAT(Aswitch, "-m4 or -c4", "-A");
    INCOMPAT(edgebound[0] >= 0, "-m4 without -p", "-e");
    INCOMPAT(maxfacesize >= 0, "-m4 without -p", "-f");

    if (dswitch)
        strcpy(outtypename, "cubic graphs");
    else
        strcpy(outtypename, "triangulations");

    open_output_file();

    needgroup = Gswitch;
    if (minconnec == 4)
        xswitch = TRUE;

    xconnec = minconnec;

    hint = MIN(maxnv <= 19 ? maxnv - 4 : maxnv - 5, 17);
    initialize_splitting(startingsize, hint, maxnv - 3);
    if (splitlevel == 0 && res > 0)
        return;

    initialize_min4();
    canon(degree, numbering, &nbtot, &nbop);

#ifdef FAST_FILTER_MIN4
    if (FAST_FILTER_MIN4)
#endif
    {
        if (xswitch || minconnec == 4)
            scanmin4c(nbtot, nbop, splitlevel == 6, NULL, nft, 0);
        else
            scanmin4(nbtot, nbop, splitlevel == 6, NULL);
    }
}

/****************************************************************************/

static void
min5_dispatch(void)

/* Case of minimum degree == 5, except for polygons and polytopes. */
{
    int i, startingsize, nbtot, nbop, hint, nbangles;
    EDGE *prevA[MAXN], *bangle[MAXE / 2];

    if (minimumdeg <= 0)
        minimumdeg = 5;
    if (minconnec <= 0)
        minconnec = 3;
    startingsize = 12;

    CHECKRANGE(maxnv, "n", startingsize, MAXN);
    CHECKRANGE(minconnec, "-c", 3, 5);
    CHECKRANGE(minimumdeg, "-m", 5, 5);

    INCOMPAT(tswitch, "-m5 or -c5", "-t");
    INCOMPAT(qswitch, "-m5 or -c5", "-q");
    INCOMPAT(Aswitch, "-m5 or -c5", "-A");
    INCOMPAT(edgebound[0] >= 0, "-m5 without -p", "-e");
    INCOMPAT(maxfacesize >= 0, "-m5 without -p", "-f");

    if (dswitch)
        strcpy(outtypename, "cubic graphs");
    else
        strcpy(outtypename, "triangulations");

    open_output_file();

    needgroup = Gswitch;

    hint = MIN(maxnv - 5, 27);
    if (maxnv >= 35)
        ++hint;
    if (maxnv >= 38)
        ++hint;
    initialize_splitting(startingsize, hint, maxnv - 5);
    if (splitlevel == 0 && res > 0)
        return;

    xconnec = minconnec;

    initialize_min5();
    canon(degree, numbering, &nbtot, &nbop);

    if (minconnec < 5)
    {
        all_5_bangles(bangle, &nbangles);
#ifdef FAST_FILTER_MIN5
        if (FAST_FILTER_MIN5)
#endif
            scanmin5(nbtot, nbop, splitlevel == 12, prevA, 0, bangle, nbangles);
        if (vswitch && !xswitch)
        {
            fprintf(msgfile, "By connectivity: ");
            for (i = minconnec; i <= 5; ++i)
            {
                if (i > minconnec)
                    fprintf(msgfile, " ");
                PRINTBIG(msgfile, nout[i]);
                fprintf(msgfile, " %d-conn", i);
                if (i < 5)
                    fprintf(msgfile, ";");
            }
            fprintf(msgfile, "\n");

            if (oswitch)
            {
                fprintf(msgfile, "By connectivity (O-P): ");
                for (i = minconnec; i <= 5; ++i)
                {
                    if (i > minconnec)
                        fprintf(msgfile, " ");
                    PRINTBIG(msgfile, nout_op[i]);
                    fprintf(msgfile, " %d-conn", i);
                    if (i < 5)
                        fprintf(msgfile, ";");
                }
                fprintf(msgfile, "\n");
            }
        }
    }
    else
#ifdef FAST_FILTER_MIN5
        if (FAST_FILTER_MIN5)
#endif
        scanmin5c(nbtot, nbop, splitlevel == 12, prevA, 0);
}

/****************************************************************************/

static void
polytope_dispatch(void)

/* Polytopes.  Main options are -m4, -m5 and neither. */
{
    int startingsize, nbtot, nbop, i, hint, nbangles, maxundir;
    EDGE *prevA[MAXN], *bangle[MAXE / 2];

    /* Polytopes are made by first making 3-connected triangulations,
     then deleting edges in a second phase.  minconn and minimumdeg
     are used in the first phase; minpolyconn and minpolydeg in the
     second phase.  Since simple triangulations are 3-connected and
     have minimum degree at least 3, minconn and minimumdeg are at
     least 3.  However, minpolyconn and minpolydeg can be anything
     from 1 to minconn and minimumdeg. */

    if (minconnec <= 0)
        minconnec = 3;
    if (minconnec < 3)
    {
        minpolyconnec = minconnec;
        minconnec = 3;
    }
    else
        minpolyconnec = minconnec;

    if (minimumdeg <= 0)
    {
        minimumdeg = minconnec;
        minpolydeg = minpolyconnec;
    }
    else
    {
        minpolydeg = minimumdeg;
        minimumdeg = MAX(minimumdeg, 3);
    }

    if (minconnec > minimumdeg)
        minimumdeg = minconnec;
    if (minpolyconnec > minpolydeg)
        minpolydeg = minpolyconnec;

    startingsize = (minimumdeg == 4 ? 6 : (minimumdeg == 5 ? 12 : 4));

    CHECKRANGE(maxnv, "n", 2, MAXN);
    CHECKRANGE(maxnv, "n", 2, 64);
    CHECKRANGE(minpolyconnec, "-c", 1, 3);
    CHECKRANGE(minpolydeg, "-m", 1, 5);

    INCOMPAT(polygonsize >= 0, "-p", "-P");
    INCOMPAT(bswitch, "-p", "-b");
    INCOMPAT(qswitch, "-p", "-q");
    INCOMPAT(tswitch, "-p", "-t");
    INCOMPAT(Aswitch, "-p", "-A");
    /* INCOMPAT(minconnec == 3 && xswitch,"-c3","-x");  changed 19/2/08 */
    INCOMPAT(minpolyconnec == 3 && xswitch, "-c3", "-x");

    maxundir = (maxnv == 2 ? 1 : 3 * maxnv - 6);
    if (edgebound[0] < 0)
        edgebound[0] = 0;
    if (edgebound[1] < 0)
        edgebound[1] = maxundir;
    if (edgebound[1] > maxundir)
        edgebound[1] = maxundir;
    if (maxfacesize <= 0)
        maxfacesize = MAXE;

    CHECKRANGE(edgebound[0], "-e", 0, maxundir);
    CHECKRANGE(edgebound[1], "-e", 0, maxundir);
    PERROR(edgebound[0] > edgebound[1],
           "The first value of -e can't be greater than the second");
    PERROR(maxnv * minpolydeg > 2 * edgebound[1],
           "The upper bound for -e is impossibly low");
    CHECKRANGE(maxfacesize, "-f", 3, MAXE);

    xconnec = minpolyconnec;

    if (maxnv >= 4 && (edgebound[0] == maxundir || maxfacesize == 3))
    {
        pswitch = FALSE;
        edgebound[0] = edgebound[1] = maxfacesize = -1;
        if (minimumdeg == 4)
            min4_dispatch();
        else if (minimumdeg == 5)
            min5_dispatch();
        else
            simple_dispatch();
        return;
    }

    edgebound[0] *= 2;
    edgebound[1] *= 2;

    strcpy(outtypename, "polytopes");

    open_output_file();

    for (i = 0; i <= maxundir; ++i)
    {
        ZEROBIG(nout_e[i]);
        ZEROBIG(nout_e_op[i]);
#ifdef STATS
        ZEROBIG(numrooted_e[i]);
#endif
    }

    needgroup = TRUE;

    if (minimumdeg == 5)
    {
        hint = MIN(maxnv - 5, 27);
        initialize_splitting(startingsize, hint, maxnv - 5);
        if (splitlevel == 0 && res > 0)
            return;
        initialize_min5();
        canon(degree, numbering, &nbtot, &nbop);
        all_5_bangles(bangle, &nbangles);
        scanmin5(nbtot, nbop, splitlevel == 12, prevA, 0, bangle, nbangles);
    }
    else if (minimumdeg == 4)
    {
        hint = MIN(maxnv <= 19 ? maxnv - 3 : maxnv - 4, 17);
        initialize_splitting(startingsize, hint, maxnv - 3);
        if (splitlevel == 0 && res > 0)
            return;
        initialize_min4();
        canon(degree, numbering, &nbtot, &nbop);
        scanmin4(nbtot, nbop, splitlevel == 6, NULL);
    }
    else if (maxnv >= 4)
    {
        hint = MIN(maxnv <= 13 ? maxnv - 1 : maxnv - 2, 14);
        initialize_splitting(startingsize, hint, maxnv - 1);
        if (splitlevel == 0 && res > 0)
            return;
        initialize_triang();
        canon(degree, numbering, &nbtot, &nbop);
        scansimple(nbtot, nbop);
    }
    else
    {
        if (maxnv <= 3 && minpolydeg == 1 && minpolyconnec == 1 && edgebound[0] <= 2 * maxnv - 2 && edgebound[1] >= 2 * maxnv - 2 && maxfacesize >= 2 * maxnv - 2)
        {
            make_me_a_star(maxnv);
            canon(degree, numbering, &nbtot, &nbop);
            xconnec = minconnec;
            got_one(nbtot, nbop, 1);
        }
        if (maxnv == 3 && minpolydeg <= 2 && minpolyconnec <= 2 && edgebound[0] <= 6 && edgebound[1] >= 6)
        {
            make_cycle(maxnv);
            canon(degree, numbering, &nbtot, &nbop);
            xconnec = minconnec;
            got_one(nbtot, nbop, 2);
        }
    }

    if (vswitch)
    {
        for (i = 0; i <= maxundir; ++i)
            if (!ISZEROBIG(nout_e[i]))
            {
                fprintf(msgfile, " With %2d edges and %2d faces: ", i, 2 + i - maxnv);
                if (oswitch)
                {
                    PRINTBIG(msgfile, nout_e_op[i]);
                    fprintf(msgfile, " (");
                    PRINTBIG(msgfile, nout_e[i]);
                    fprintf(msgfile, " classes)");
#ifdef STATS
                    fprintf(msgfile, " ");
                    PRINTBIG(msgfile, numrooted_e[i]);
                    fprintf(msgfile, " rooted");
#endif
                    fprintf(msgfile, "\n");
                }
                else
                {
                    PRINTBIG(msgfile, nout_e[i]);
                    fprintf(msgfile, "\n");
                }
            }
        if (!xswitch && minpolyconnec < 3)
        {
            fprintf(msgfile, "By connectivity: ");
            for (i = minpolyconnec; i <= 3; ++i)
            {
                if (i > minpolyconnec)
                    fprintf(msgfile, " ");
                PRINTBIG(msgfile, nout[i]);
                if (i == 3)
                    fprintf(msgfile, " (3-5)-conn");
                else
                    fprintf(msgfile, " %d-conn", i);
                if (i < 3)
                    fprintf(msgfile, ";");
            }
            fprintf(msgfile, "\n");

            if (oswitch)
            {
                fprintf(msgfile, "By connectivity (O-P): ");
                for (i = minpolyconnec; i <= 3; ++i)
                {
                    if (i > minpolyconnec)
                        fprintf(msgfile, " ");
                    PRINTBIG(msgfile, nout_op[i]);
                    if (i == 3)
                        fprintf(msgfile, " (3-5)-conn");
                    else
                        fprintf(msgfile, " %d-conn", i);
                    if (i < 3)
                        fprintf(msgfile, ";");
                }
                fprintf(msgfile, "\n");
            }
        }
    }
}

/****************************************************************************/

static void
polytope_c4_dispatch(void)

/* 4-connected polytopes. */
{
    int startingsize, nbtot, nbop, i, hint, nbangles, maxundir;
    EDGE *prevA[MAXN], *bangle[MAXE / 2];
    triangle nft[MAXN];

    /* Polytopes are made by first making 4-connected triangulations,
     then deleting edges in a second phase.  minconn and minimumdeg
     are used in the first phase; minpolyconn and minpolydeg in the
     second phase. */

    minpolyconnec = minconnec;

    if (minimumdeg <= 0)
    {
        minimumdeg = minconnec;
        minpolydeg = minpolyconnec;
    }
    else
    {
        minpolydeg = minimumdeg;
        minimumdeg = MAX(minimumdeg, 4);
    }

    if (minconnec > minimumdeg)
        minimumdeg = minconnec;
    if (minpolyconnec > minpolydeg)
        minpolydeg = minpolyconnec;

    //    startingsize = (minimumdeg == 4 ? 6 : (minimumdeg == 5 ? 12 : 4));

    //    CHECKRANGE(maxnv,"n",2,MAXN);
    //    CHECKRANGE(maxnv,"n",2,64);
    CHECKRANGE(minpolyconnec, "-c", 4, 4);
    CHECKRANGE(minpolydeg, "-m", 4, 5);

    INCOMPAT(polygonsize >= 0, "-p", "-P");
    INCOMPAT(bswitch, "-p", "-b");
    INCOMPAT(qswitch, "-p", "-q");
    INCOMPAT(tswitch, "-p", "-t");
    INCOMPAT(Aswitch, "-p", "-A");
    INCOMPAT(xswitch, "-pc4", "-x");

    maxundir = (maxnv == 2 ? 1 : 3 * maxnv - 6);
    if (edgebound[0] < 0)
        edgebound[0] = 0;
    if (edgebound[1] < 0)
        edgebound[1] = maxundir;
    if (edgebound[1] > maxundir)
        edgebound[1] = maxundir;
    if (maxfacesize <= 0)
        maxfacesize = MAXE;

    CHECKRANGE(edgebound[0], "-e", 0, maxundir);
    CHECKRANGE(edgebound[1], "-e", 0, maxundir);
    PERROR(edgebound[0] > edgebound[1],
           "The first value of -e can't be greater than the second");
    PERROR(maxnv * minpolydeg > 2 * edgebound[1],
           "The upper bound for -e is impossibly low");
    CHECKRANGE(maxfacesize, "-f", 3, MAXE);

    xconnec = minpolyconnec;

    edgebound[0] *= 2;
    edgebound[1] *= 2;

    strcpy(outtypename, "polytopes");

    open_output_file();

    for (i = 0; i <= maxundir; ++i)
    {
        ZEROBIG(nout_e[i]);
        ZEROBIG(nout_e_op[i]);
#ifdef STATS
        ZEROBIG(numrooted_e[i]);
#endif
    }

    needgroup = TRUE;

    if (minimumdeg == 5)
    {
        startingsize = 12;
        CHECKRANGE(maxnv, "n", startingsize, MAXN);
        CHECKRANGE(maxnv, "n", startingsize, 8 * (int)sizeof(unsigned long));

        hint = MIN(maxnv - 5, 27);
        if (maxnv >= 35)
            ++hint;
        if (maxnv >= 38)
            ++hint;

        initialize_splitting(startingsize, hint, maxnv - 5);
        if (splitlevel == 0 && res > 0)
            return;
        initialize_min5();
        canon(degree, numbering, &nbtot, &nbop);
        all_5_bangles(bangle, &nbangles);
        scanmin5(nbtot, nbop, splitlevel == 12, prevA, 0, bangle, nbangles);
    }
    else /* minimumdeg == 4 */
    {
        startingsize = 6;
        CHECKRANGE(maxnv, "n", startingsize, MAXN);
        CHECKRANGE(maxnv, "n", startingsize, 8 * (int)sizeof(unsigned long));

        hint = MIN(maxnv <= 19 ? maxnv - 3 : maxnv - 4, 17);
        initialize_splitting(startingsize, hint, maxnv - 3);
        if (splitlevel == 0 && res > 0)
            return;
        initialize_min4();
        canon(degree, numbering, &nbtot, &nbop);
        scanmin4c(nbtot, nbop, splitlevel == 6, NULL, nft, 0);
    }

    if (vswitch)
    {
        for (i = 0; i <= maxundir; ++i)
            if (!ISZEROBIG(nout_e[i]))
            {
                fprintf(msgfile, " With %2d edges and %2d faces: ", i, 2 + i - maxnv);
                if (oswitch)
                {
                    PRINTBIG(msgfile, nout_e_op[i]);
                    fprintf(msgfile, " (");
                    PRINTBIG(msgfile, nout_e[i]);
                    fprintf(msgfile, " classes)");
#ifdef STATS
                    fprintf(msgfile, " ");
                    PRINTBIG(msgfile, numrooted_e[i]);
                    fprintf(msgfile, " rooted");
#endif
                    fprintf(msgfile, "\n");
                }
                else
                {
                    PRINTBIG(msgfile, nout_e[i]);
                    fprintf(msgfile, "\n");
                }
            }
    }
}

/****************************************************************************/

static void
eulerian_dispatch(void)

/* Eulerian triangulations. */
{
    int startingsize, nbtot, nbop, hint;
    EDGE *Pedges[MAXN / 2 + 1];
    triangle nft[MAXN];

    if (minimumdeg <= 0)
        minimumdeg = 4;
    if (minconnec <= 0)
        minconnec = 3;
    startingsize = 6;

    CHECKRANGE(maxnv, "n", startingsize, MAXN);
    CHECKRANGE(minconnec, "-c", 3, 4);
    CHECKRANGE(minimumdeg, "-m", 4, 4);

    INCOMPAT(pswitch, "-b", "-p");
    INCOMPAT(qswitch, "-b", "-q");
    INCOMPAT(Aswitch, "-b", "-A");
    INCOMPAT(polygonsize >= 0, "-b", "-P");
    INCOMPAT(tswitch, "-b", "-t");
    INCOMPAT(edgebound[0] >= 0, "-b", "-e");
    INCOMPAT(maxfacesize >= 0, "-b", "-f");

    if (dswitch)
        strcpy(outtypename, "bipartite cubic graphs");
    else
        strcpy(outtypename, "eulerian triangulations");

    open_output_file();

    needgroup = Gswitch;

    hint = MIN(maxnv <= 22 ? maxnv - 5 : maxnv - 6, 21);
    initialize_splitting(startingsize, hint, maxnv - 2);
    if (splitlevel == 0 && res > 0)
        return;

    initialize_bip();
    xconnec = minconnec;
    canon(degree, numbering, &nbtot, &nbop);
#ifdef FAST_FILTER_BIP
    if (FAST_FILTER_BIP)
#endif
    {
        if (xswitch || minconnec == 4)
            scanbipartite4c(nbtot, nbop, firstedge[0], splitlevel == 6, Pedges, 0, nft, 0);
        else
            scanbipartite(nbtot, nbop, firstedge[0], splitlevel == 6, Pedges, 0);
    }
}

/****************************************************************************/

static void
quadrangulation_dispatch(void)

/* Simple quadrangulations. */
{
    int startingsize, nbtot, nbop, hint;
    EDGE *P1edges[MAXN];

    if (minimumdeg <= 0)
        minimumdeg = 3;
    if (minconnec <= 0)
        minconnec = 3;
    if (minimumdeg == 2 && minconnec >= 3)
        minimumdeg = 3;
    startingsize = (minimumdeg == 2 ? 4 : 8);

    CHECKRANGE(maxnv, "n", startingsize, MAXN);
    CHECKRANGE(minconnec, "-c", 2, 4);
    CHECKRANGE(minimumdeg, "-m", 2, 3);

    INCOMPAT(pswitch, "-q", "-p");
    INCOMPAT(bswitch, "-q", "-b");
    INCOMPAT(Aswitch, "-q", "-A");
    INCOMPAT(polygonsize >= 0, "-q", "-P");
    INCOMPAT(tswitch, "-q", "-t");
    INCOMPAT(edgebound[0] >= 0, "-q", "-e");
    INCOMPAT(maxfacesize >= 0, "-q", "-f");

    if (dswitch)
        strcpy(outtypename, "quartic graphs");
    else
        strcpy(outtypename, "quadrangulations");

    open_output_file();

    needgroup = Gswitch;

    if (minimumdeg == 2)
    {
        hint = MIN(maxnv <= 16 ? maxnv - 5 : maxnv - 6, maxnv < 25 ? 17 : 18);
        initialize_splitting(startingsize, hint, maxnv - 1);
        if (splitlevel == 0 && res > 0)
            return;
        initialize_quadrangulations();
        extend_quadr_P0(firstedge[1]); /* make square */
        xconnec = minconnec;
        canon(degree, numbering, &nbtot, &nbop);
        scanquadrangulations_all(nbtot, nbop);
#ifdef STATS
        fprintf(msgfile, "Counts by min degree: ");
        PRINTBIG(msgfile, nummindeg[2]);
        fprintf(msgfile, " ");
        PRINTBIG(msgfile, nummindeg[3]);
        fprintf(msgfile, "\n");
#endif
    }
    else
    {
        hint = MIN(maxnv <= 23 ? maxnv - 5 : maxnv - 6, maxnv < 30 ? 23 : 24);
        initialize_splitting(startingsize, hint, maxnv - 2);
        if (splitlevel == 0 && res > 0)
            return;
        initialize_min3_quadrangulations();
        xconnec = minconnec;
        canon(degree, numbering, &nbtot, &nbop);
        if (minconnec == 3)
            scanquadrangulations(nbtot, nbop, firstedge[0],
                                 splitlevel == 8, P1edges, 0);
        else if (minconnec == 4)
            scanquadrangulations_nf4(nbtot, nbop, firstedge[0],
                                     splitlevel == 8, P1edges, 0);
        else
            scanquadrangulations_min3(nbtot, nbop, firstedge[0],
                                      splitlevel == 8, P1edges, 0);
    }
}

/****************************************************************************/

static void
bipartite_dispatch(void)

/* General bipartite graphs.  Main options are -m# -c# for #=1,2,3.  */
{
    int startingsize, nbtot, nbop, i, hint, maxundir;
    EDGE *P1edges[MAXN];

    /* Bipartite graphs are made by first making quadrangulations,
     then deleting edges in a second phase.  minconn and minimumdeg
     are used in the first phase; minpolyconn and minpolydeg in the
     second phase. */

    if (minconnec <= 0)
        minconnec = 3;
    if (minconnec < 3)
    {
        minpolyconnec = minconnec;
        minconnec = 2;
    }
    else
        minpolyconnec = minconnec;

    if (minimumdeg <= 0)
    {
        minimumdeg = minconnec;
        minpolydeg = minpolyconnec;
    }
    else
    {
        minpolydeg = minimumdeg;
        minimumdeg = MAX(minimumdeg, 2);
    }

    if (minconnec > minimumdeg)
        minimumdeg = minconnec;
    if (minpolyconnec > minpolydeg)
        minpolydeg = minpolyconnec;

    startingsize = (minimumdeg == 2 ? 4 : 8);

    CHECKRANGE(maxnv, "n", (minpolydeg == 1 ? 2 : startingsize), MAXN);
    CHECKRANGE(maxnv, "n", 2, 64);
    CHECKRANGE(minpolyconnec, "-c", 1, 3);
    CHECKRANGE(minpolydeg, "-m", 1, 3);

    INCOMPAT(polygonsize >= 0, "-pb", "-P");
    INCOMPAT(qswitch, "-pb", "-q");
    INCOMPAT(tswitch, "-pb", "-t");
    INCOMPAT(Aswitch, "-pb", "-A");
    INCOMPAT(minpolyconnec == 3 && xswitch, "-c3", "-x");

    maxundir = (maxnv == 2 ? 1 : 2 * maxnv - 4);
    if (edgebound[0] < 0)
        edgebound[0] = 0;
    if (edgebound[1] < 0)
        edgebound[1] = maxundir;
    if (edgebound[1] > 2 * maxnv - 4)
        edgebound[1] = maxundir;
    if (maxfacesize <= 0)
        maxfacesize = MAXE;
    maxfacesize &= ~1; /* Must be even */

    CHECKRANGE(edgebound[0], "-e", 0, maxundir);
    CHECKRANGE(edgebound[1], "-e", 0, maxundir);
    PERROR(edgebound[0] > edgebound[1],
           "The first value of -e can't be greater than the second");
    CHECKRANGE(maxfacesize, "-f", 4, MAXE);

    xconnec = minpolyconnec;

    if (maxnv >= startingsize &&
        (edgebound[0] == maxundir || maxfacesize == 4))
    {
        pswitch = bswitch = FALSE;
        edgebound[0] = edgebound[1] = maxfacesize = -1;
        quadrangulation_dispatch();
        return;
    }

    edgebound[0] *= 2;
    edgebound[1] *= 2;

    if (dswitch)
        strcpy(outtypename, "eulerian graphs");
    else
        strcpy(outtypename, "bipartite graphs");

    open_output_file();

    for (i = 0; i <= maxundir; ++i)
    {
        ZEROBIG(nout_e[i]);
        ZEROBIG(nout_e_op[i]);
    }

    needgroup = TRUE;

    if (minimumdeg == 2)
    {
        hint = MIN(maxnv <= 16 ? maxnv - 5 : maxnv - 6, maxnv < 25 ? 17 : 18);
        initialize_splitting(startingsize, hint, maxnv - 1);
        if (splitlevel == 0 && res > 0)
            return;
        if (maxnv >= 4)
        {
            initialize_quadrangulations();
            extend_quadr_P0(firstedge[1]); /* make square */
            xconnec = minconnec;
            canon(degree, numbering, &nbtot, &nbop);
#ifdef FAST_FILTER_QUAD
            if (FAST_FILTER_QUAD)
#endif
                scanquadrangulations_all(nbtot, nbop);
        }
        if (minpolydeg == 1 && edgebound[0] <= 2 * maxnv - 2 && edgebound[1] >= 2 * maxnv - 2 && maxfacesize >= 2 * maxnv - 2 && res == 0)
        {
            make_me_a_star(maxnv);
            canon(degree, numbering, &nbtot, &nbop);
            xconnec = minconnec;
#ifdef FAST_FILTER_QUAD
            if (FAST_FILTER_QUAD)
#endif
                got_one(nbtot, nbop, 1);
        }
    }
    else
    {
        hint = MIN(maxnv <= 23 ? maxnv - 5 : maxnv - 6, maxnv < 30 ? 23 : 24);
        initialize_splitting(startingsize, hint, maxnv - 2);
        if (splitlevel == 0 && res > 0)
            return;
        initialize_min3_quadrangulations();
        xconnec = minconnec;
        canon(degree, numbering, &nbtot, &nbop);
#ifdef FAST_FILTER_QUAD
        if (FAST_FILTER_QUAD)
#endif
        {
            if (minconnec == 3)
                scanquadrangulations(nbtot, nbop, firstedge[0],
                                     splitlevel == 8, P1edges, 0);
            else
                scanquadrangulations_min3(nbtot, nbop, firstedge[0],
                                          splitlevel == 8, P1edges, 0);
        }
    }

    if (vswitch)
    {
        for (i = 0; i <= maxundir; ++i)
            if (!ISZEROBIG(nout_e[i]))
            {
                fprintf(msgfile, " With %2d edges and %2d faces: ", i, 2 + i - maxnv);
                if (oswitch)
                {
                    PRINTBIG(msgfile, nout_e_op[i]);
                    fprintf(msgfile, " (");
                    PRINTBIG(msgfile, nout_e[i]);
                    fprintf(msgfile, " classes)");
#ifdef STATS
                    fprintf(msgfile, " ");
                    PRINTBIG(msgfile, numrooted_e[i]);
                    fprintf(msgfile, " rooted");
#endif
                    fprintf(msgfile, "\n");
                }
                else
                {
                    PRINTBIG(msgfile, nout_e[i]);
                    fprintf(msgfile, "\n");
                }
            }
        if (!xswitch && minpolyconnec < 3)
        {
            fprintf(msgfile, "By connectivity: ");
            for (i = minpolyconnec; i <= 3; ++i)
            {
                if (i > minpolyconnec)
                    fprintf(msgfile, " ");
                PRINTBIG(msgfile, nout[i]);
                if (i == 3)
                    fprintf(msgfile, " (3-5)-conn");
                else
                    fprintf(msgfile, " %d-conn", i);
                if (i < 3)
                    fprintf(msgfile, ";");
            }
            fprintf(msgfile, "\n");

            if (oswitch)
            {
                fprintf(msgfile, "By connectivity (O-P): ");
                for (i = minpolyconnec; i <= 3; ++i)
                {
                    if (i > minpolyconnec)
                        fprintf(msgfile, " ");
                    PRINTBIG(msgfile, nout_op[i]);
                    if (i == 3)
                        fprintf(msgfile, " (3-5)-conn");
                    else
                        fprintf(msgfile, " %d-conn", i);
                    if (i < 3)
                        fprintf(msgfile, ";");
                }
                fprintf(msgfile, "\n");
            }
        }
    }
}

/****************************************************************************/

static void
unused_functions(void)

/* Don't call this, it is just to avoid warning messages about
 * functions defined but not used. */
{
    (void)maxdegree();
    (void)non_facial_triangles();
    (void)has_non_facial_triangle();
    (void)numedgeorbits(0, 0);
    (void)numfaceorbits(0, 0);
    (void)numopfaceorbits(0, 0);
    (void)numorbits(0, 0);
    (void)numoporbits(0, 0);
    (void)numorbitsonface(0, 0, NULL);
    (void)make_dual();
    (void)show_group(NULL, 0, 0);
    (void)connectivity();
    check_it(0, 0);
    check_am2(0);

    unused_functions();
}

/****************************************************************************/

int main(int argc, char *argv[])
{
    int i;
#if CPUTIME
    struct tms timestruct0, timestruct1;

    times(&timestruct0);
#endif

    if (argc > 1 && (strcmp(argv[1], "-help") == 0 || (strcmp(argv[1], "--help") == 0)))
    {
        fprintf(stderr, "Plantri version %s\n", VERSION);
        fprintf(stderr,
                "Usage: %s %s n [res/mod] [outfile]\n", argv[0], SWITCHES);
#ifdef HELPMESSAGE
        HELPMESSAGE;
#endif
        fprintf(stderr, "See plantri-guide.txt for more information.\n");
        return 0;
    }

    decode_command_line(argc, argv);

#ifdef SPLITTEST
    if (mod == 1)
        mod = 2;
    uswitch = TRUE;
    aswitch = gswitch = sswitch = Eswitch = FALSE;
#endif

    if (minconnec < 0 && (tswitch || xswitch))
    {
        fprintf(stderr,
                ">E %s: -t and -x can only be used in conjunction with -c\n", cmdname);
        exit(1);
    }

    for (i = 0; i < 6; ++i)
    {
        ZEROBIG(nout[i]);
        ZEROBIG(nout_op[i]);
    }
    ZEROBIG(nout_V);

#ifdef STATS
    ZEROBIG(ntriv);
    ZEROBIG(numrooted);
    ZEROBIG(nummindeg[1]);
    ZEROBIG(nummindeg[2]);
    ZEROBIG(nummindeg[3]);
    ZEROBIG(nummindeg[4]);
    ZEROBIG(nummindeg[5]);
#endif

#ifdef SPLITTEST
    ZEROBIG(splitcases);
#endif

#ifdef PLUGIN_INIT
    PLUGIN_INIT;
#endif

    minpolydeg = -1;
    minpolyconnec = -1;

    if (pswitch && bswitch)
        bipartite_dispatch();
    else if (pswitch && minconnec >= 4)
        polytope_c4_dispatch();
    else if (pswitch && minconnec < 4)
        polytope_dispatch();
    else if (polygonsize >= 0)
        polygon_dispatch();
    else if (bswitch)
        eulerian_dispatch();
    else if (qswitch)
        quadrangulation_dispatch();
    else if (minconnec >= 5 || minimumdeg >= 5)
        min5_dispatch();
    else if (minconnec >= 4 || minimumdeg >= 4)
        min4_dispatch();
    else
        simple_dispatch();

#if CPUTIME
    times(&timestruct1);
#endif

    ZEROBIG(totalout);
    ZEROBIG(totalout_op);
    for (i = 0; i < 6; ++i)
    {
        SUMBIGS(totalout, nout[i]);
        if (oswitch)
            SUMBIGS(totalout_op, nout_op[i]);
    }

    dosummary = 1;
#ifdef SUMMARY
    nv = maxnv;
    SUMMARY();
#endif

#ifdef SPLITTEST
    PRINTBIG(msgfile, splitcases);
    fprintf(msgfile, " splitting cases at level=%d", splitlevel);
#if CPUTIME
    fprintf(msgfile, "; cpu=%.2f sec\n",
            (double)(timestruct1.tms_utime + timestruct1.tms_stime - timestruct0.tms_utime - timestruct0.tms_stime) / (double)CLK_TCK);
#else
    fprintf(msgfile, "\n");
#endif
    return 0;
#endif

    if (!dosummary)
        return 0;

    if (oswitch && vswitch)
    {
        PRINTBIG(msgfile, totalout);
        fprintf(msgfile, " isomorphism classes\n");
    }

    PRINTBIG(msgfile, (oswitch ? totalout_op : totalout));
    fprintf(msgfile, " %s", outtypename);
    if (uswitch)
        fprintf(msgfile, " generated");
    else
        fprintf(msgfile, " written to %s", outfilename);
#if CPUTIME
    fprintf(msgfile, "; cpu=%.2f sec\n",
            (double)(timestruct1.tms_utime + timestruct1.tms_stime - timestruct0.tms_utime + timestruct0.tms_stime) / (double)CLK_TCK);
#else
    fprintf(msgfile, "\n");
#endif
    if (Vswitch)
    {
        fprintf(msgfile, "Suppressed ");
        PRINTBIG(msgfile, nout_V);
        fprintf(msgfile, " with trivial group.\n");
    }

#ifdef STATS
    if (Gswitch)
    {
        PRINTBIG(msgfile, numrooted);
        fprintf(msgfile, " rooted maps\n");
        fprintf(msgfile, "Number with trivial group: ");
        PRINTBIG(msgfile, ntriv);
        fprintf(msgfile, "\n");
    }
    else if (polygonsize == 0)
    {
        fprintf(msgfile, "Rooted counts by outside face:\n");
        for (i = 3; i < maxnv; ++i)
            if (!ISZEROBIG(numbigface[i]))
            {
                fprintf(msgfile, "%2d: ", i);
                PRINTBIG(msgfile, numbigface[i]);
                fprintf(msgfile, "\n");
            }
    }
#ifdef STATS2
    fprintf(msgfile, "Counts by number of twos:");
    for (i = 0; i < maxnv; ++i)
        if (!ISZEROBIG(numtwos[i]))
        {
            fprintf(msgfile, " %d:", i);
            PRINTBIG(msgfile, numtwos[i]);
        }
    fprintf(msgfile, "\n");
#endif
#endif

    return 0;
}
