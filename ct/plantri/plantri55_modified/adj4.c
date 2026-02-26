/* PLUGIN file to use with plantri.c 

   To use this, compile plantri.c using 
       cc -o plantri_adj4 -O4 '-DPLUGIN="adj4.c"' plantri.c

   This plug-in filters out those triangulations having a
   vertex of degree 4 adjacent to at least two other vertices
   of degree 4.  It doesn't try to be at all smart.
*/

#define FILTER adj4_filter

static int
adj4_filter(int nbtot, int nbop, int doflip)
{
    int i,n4;
    EDGE *e;

    for (i = 0; i < nv + (missing_vertex >= 0); ++i)
    if (degree[i] == 4 && i != missing_vertex)
    {
	n4 = 0;
	e = firstedge[i];
	if (degree[e->end] == 4) ++n4;
	e = e->next;
	if (degree[e->end] == 4) ++n4;
        e = e->next;
        if (degree[e->end] == 4) ++n4;
        e = e->next;
	if (degree[e->end] == 4) ++n4;
	if (n4 >= 2) return FALSE;
    }

    return TRUE;
}
