/* PLUGIN file to use with plantri.c

   To use this, compile plantri.c using 
       cc -o plantri_maxd -O4 '-DPLUGIN="maxdeg.c"' plantri.c

   This plug-in deletes those triangulations whose maximum
   degree is greater than maxdeg, which is normally 6 but can
   be changed by using the -D switch, for example

      plantri_maxd -D7 14

   makes all triangulations with 14 vertices and maximum degree <= 7.

   This plugin only works for 3-connected planar triangulations
   and all varieties of quadrangulations.

   For triangulations of maximum degree 6 there is a far more
   sophisticated program available from the authors.
*/

static int maxdeg = 6;

#define FILTER maxdeg_filter
#define PRE_FILTER_SIMPLE maxdeg_prune()
#define FIND_EXTENSIONS_QUAD find_extensions_quad_D
#define FIND_EXTENSIONS_QUAD_ALL find_extensions_quad_all_D
#define FIND_EXTENSIONS_QUAD_MIN3 find_extensions_quad_min3_D
#define FIND_EXTENSIONS_QUAD_NF4 find_extensions_quad_nf4_D

/*******************************************************************/ 

/* The following adds the switch D to those normally present.
   and specifies a subset of the switches as permitted. */

#define PLUGIN_SWITCHES  INTSWITCH('D',maxdeg)

#undef SWITCHES
#define SWITCHES "[-D# -qcm -uagsh -odG -v]"
#define HELPMESSAGE \
  fprintf(stderr,"Specify the allowed maximum degree with -D#.\n")
#define PLUGIN_INIT \
  if ((minconnec != 3 && minconnec >= 0 \
       || minimumdeg != 3 && minimumdeg >= 0)  && !qswitch) \
  { \
     fprintf(stderr,">E -c is only allowed with -q\n"); \
     exit(1); \
  }

/*********************************************************************/

static int
maxdeg_filter(int nbtot, int nbop, int doflip)
{
	register int i;

	for (i = 0; i < nv; ++i)
	   if (degree[i] > maxdeg) return FALSE;
	
	return TRUE;
}

/*********************************************************************
The following is used to prune the search tree at levels below maxnv.
Consider the expansion operations E3, E4, E5.  The basic ideas are:
(1) Only E5 can reduce the degree of a vertex, then only by 1.
(2) If there are 3 or more vertices of degree 3, E5 will never be used.
(3) Similarly if there are 2 vertices of degree 3 but they don't have
	two common neighbours.
(4) The quantity (2 * #degree-3 + #degree-4) is reduced by at most one
    by E3 and E4.  E5 can reduce it by 2 as long as it becomes 0. */

static int
commonedge(int a, int b)
/* Test that vertices a,b of degree 3 are at the opposite
   points of two adjacent faces */
{
	EDGE *e;

	e = firstedge[a];
	if (e->invers->next->next->end == b) return TRUE;
	e = e->next;
	if (e->invers->next->next->end == b) return TRUE;
	e = e->next;
	if (e->invers->next->next->end == b) return TRUE;
	return FALSE;
}

static int
maxdeg_prune()
{
	register int i,levs,excess,d3,d4;
	int d3a,d3b;

	levs = maxnv - nv;    /* Number of expansions yet to perform */
	excess = d3 = d4 = 0;

	for (i = 0; i < nv; ++i)
	{
	    if (degree[i] == 3)
	    {
		++d3;
		d3a = d3b;
		d3b = i;
	    }
	    else if (degree[i] == 4)
		++d4;
	    else if (degree[i] > maxdeg)
		excess += degree[i] - maxdeg;
	}

	if (excess == 0) return TRUE;

	if (d3 > 2) return FALSE;
	if (d3 == 2 && !commonedge(d3a,d3b)) return FALSE;
	if (d3 > 0 && excess >= levs) return FALSE;
	
	i = d3 + d3 + d4;
	if (i > 0 && excess > levs - i + 2) return FALSE;

	return TRUE;
}

/*************************************************************************/

static void
find_extensions_quad(int,int,EDGE**,int*,EDGE**,int*,EDGE*);

static void
find_extensions_quad_D(int nbtot, int nbop, EDGE *extP1[], int *nextP1,
   EDGE *extP3[], int *nextP3, EDGE *lastP1)
{
    int i,excess,newP1,newP3;
    EDGE *e;

    find_extensions_quad(nbtot,nbop,extP1,nextP1,extP3,nextP3,lastP1);

    excess = 0;
    for (i = 0; i < nv; ++i)
	if (degree[i] > maxdeg) excess += degree[i] - maxdeg;

    if (excess > maxnv-nv)
    {
	*nextP1 = *nextP3 = 0;
	return ;
    }

    if (excess == maxnv-nv) *nextP3 = 0;

    newP1 = 0;
    for (i = 0; i < *nextP1; ++i)
    {
	e = extP1[i];
	if (excess - (degree[e->start]>maxdeg) 
	     + (degree[e->prev->end]>=maxdeg)
	     + (degree[e->next->end]>=maxdeg) <= maxnv-nv-1)
	    extP1[newP1++] = e;
    }
    *nextP1 = newP1;

    newP3 = 0;
    for (i = 0; i < *nextP3; ++i)
    {
	e = extP3[i];
	if (excess + (degree[e->start]>=maxdeg)
	           + (degree[e->end]>=maxdeg)
	           + (degree[e->next->end]>=maxdeg)
	           + (degree[e->invers->prev->end]>=maxdeg) <= maxnv-nv-1)
	    extP3[newP3++] = e;
    }
    *nextP3 = newP3;
}

static void
find_extensions_quad_all(int,int,EDGE**,int*,EDGE**,int*);

static void
find_extensions_quad_all_D(int nbtot, int nbop, EDGE *extP0[], int *nextP0,
   EDGE *extP1[], int *nextP1)
{
    int i,excess,newP0,newP1;
    EDGE *e;

    find_extensions_quad_all(nbtot,nbop,extP0,nextP0,extP1,nextP1);

    excess = 0;
    for (i = 0; i < nv; ++i)
        if (degree[i] > maxdeg) excess += degree[i] - maxdeg;

    if (excess > maxnv-nv)
    {
        *nextP0 = *nextP1 = 0;
        return ;
    }
    
    if (excess == maxnv-nv) *nextP0 = 0;

    newP1 = 0;
    for (i = 0; i < *nextP1; ++i)
    {
	e = extP1[i];
	if (excess - (degree[e->start]>maxdeg) 
	     + (degree[e->prev->end]>=maxdeg)
	     + (degree[e->next->end]>=maxdeg) <= maxnv-nv-1)
	    extP1[newP1++] = e;
    }
    *nextP1 = newP1;

    newP0 = 0;
    for (i = 0; i < *nextP0; ++i)
    {
	e = extP0[i];
	if (excess + (degree[e->end]>=maxdeg)
	     + (degree[e->next->end]>=maxdeg) <= maxnv-nv-1)
	    extP0[newP0++] = e;
    }
    *nextP0 = newP0;
}

static void
find_extensions_quad_min3(int,int,EDGE**,int*,EDGE**,int*,EDGE*);

static void
find_extensions_quad_min3_D(int nbtot, int nbop, EDGE *extP1[], int *nextP1,
   EDGE *extP3[], int *nextP3, EDGE *lastP1)
{
    int i,excess,newP1,newP3;
    EDGE *e;

    find_extensions_quad_min3(nbtot,nbop,extP1,nextP1,extP3,nextP3,lastP1);

    excess = 0;
    for (i = 0; i < nv; ++i)
	if (degree[i] > maxdeg) excess += degree[i] - maxdeg;

    if (excess > maxnv-nv)
    {
	*nextP1 = *nextP3 = 0;
	return ;
    }

    if (excess == maxnv-nv) *nextP3 = 0;

    newP1 = 0;
    for (i = 0; i < *nextP1; ++i)
    {
	e = extP1[i];
	if (excess - (degree[e->start]>maxdeg) 
	     + (degree[e->prev->end]>=maxdeg)
	     + (degree[e->next->end]>=maxdeg) <= maxnv-nv-1)
	    extP1[newP1++] = e;
    }
    *nextP1 = newP1;

    newP3 = 0;
    for (i = 0; i < *nextP3; ++i)
    {
	e = extP3[i];
	if (excess + (degree[e->start]>=maxdeg)
	           + (degree[e->end]>=maxdeg)
	           + (degree[e->next->end]>=maxdeg)
	           + (degree[e->invers->prev->end]>=maxdeg) <= maxnv-nv-1)
	    extP3[newP3++] = e;
    }
    *nextP3 = newP3;
}

static void
find_extensions_quad_nf4(int,int,EDGE**,int*,EDGE*);

static void
find_extensions_quad_nf4_D(int nbtot, int nbop, EDGE *extP1[], int *nextP1,
   EDGE *lastP1)
{
    int i,excess,newP1;
    EDGE *e;

    find_extensions_quad_nf4(nbtot,nbop,extP1,nextP1,lastP1);

    excess = 0;
    for (i = 0; i < nv; ++i)
	if (degree[i] > maxdeg) excess += degree[i] - maxdeg;

    if (excess > maxnv-nv)
    {
	*nextP1 = 0;
	return ;
    }

    newP1 = 0;
    for (i = 0; i < *nextP1; ++i)
    {
	e = extP1[i];
	if (excess - (degree[e->start]>maxdeg) 
	     + (degree[e->prev->end]>=maxdeg)
	     + (degree[e->next->end]>=maxdeg) <= maxnv-nv-1)
	    extP1[newP1++] = e;
    }
    *nextP1 = newP1;
}

