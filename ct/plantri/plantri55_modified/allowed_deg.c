/* PLUGIN file to use with plantri.c 

   To use this, compile plantri.c using 
   cc -o plantri_ad -O '-DPLUGIN="allowed_deg.c"' plantri.c

   This plug-in deletes those triangulations 
   with vertex degrees which are not allowed. 
   Allowed degrees may be defined by using the -F switch, for example

   plantri_ad -F7F5 14

   makes all triangulations with 14 vertices and degrees 5 or 7.

   authors: Gunnar Brinkmann and Ulrike von Nathusius,
   contains parts of maxdeg.c by Brendan McKay.

   The upper and lower limits for the number of faces to be used
   can be given like e.g. plantri_ad -F7_1^3F5F6 14 forcing between
   one and 3 vertices with valency 7. At the moment this is only 
   implemented as a filter at the end. It could be used for better 
   bounding criteria -- should be implemented once...

   The nonstandard (but common) long long type is required.
   (Warning: some versions of the Sun "cc" compiler give incorrect
   results with programs using long long.)
*/

#include <ctype.h>

#define FAST_FILTER_SIMPLE ((nv<maxnv) || ad_filter())
#define FIND_EXTENSIONS_SIMPLE find_extensions_ad

/************************** Switches ********************************/

/* The following adds the switch f to those normally present.
   arg is the address of the command-line argument, and j is the
   index where 'F' might be.  The value of j must be left on the
   last digit of the switch value. */

#undef SWITCHES
#define SWITCHES "[-F#[_#^#] -uagsh -odG -v]"

#define PLUGIN_SWITCHES else if (arg[j]=='F') list_of_allowed_degrees(arg, &j); 

#define PLUGIN_INIT if (minconnec >= 0 || polygonsize >= 0 \
   || minimumdeg >= 0 || pswitch || xswitch || tswitch) \
  {fprintf(stderr,">E Usage: %s %s n [res/mod] [outfile]\n",cmdname,SWITCHES);\
   exit(1);}

/********************************************************************/

#define INFTY_AD (3*MAXN)

static int maxdeg = 0; /* the maximum allowed degree */
static unsigned long long int LISTE=0; /* a binary representation of the allowed degrees */
static unsigned long long int mask[MAXN];
static int error_up[MAXN];
static int error_down[MAXN];
static int error_of_degree[MAXN];
static int maxnumber[MAXN],minnumber[MAXN];
static int degreelist[MAXN]; /* a list of allowed degrees ended by 0 */
static int grenzen=0;
static int x_error=0;

int error_1[MAXN]; /* the error for the special case x=1 */
int doextra_x;

/********************************* Filter **************************/

static int 
ad_filter(void) 
{
  int i, run, anzahl[MAXN];

for(i=0;i<nv ; i++) if (error_of_degree[degree[i]]) return(0);

if (grenzen)
  { 
    for (run=0; degreelist[run]; run++) anzahl[degreelist[run]]=0;
    for(i=0;i<nv ; i++) (anzahl[degree[i]])++; 
    for (run=0; degreelist[run]; run++) 
      if ((anzahl[degreelist[run]]<minnumber[degreelist[run]]) || 
	  (anzahl[degreelist[run]]>maxnumber[degreelist[run]])) return(0);
  }

return(1);

}


/*******************  nur_noch_E3  *******************************/

int
nur_noch_E3(void)
{
  register EDGE *e;
  unsigned long long int vmask;
  int a,b,i,ident,deg3;
  
  /* This function may only be used, if there are exactly two vertices of 
     degree 3. Two vertices of degree three that do not have two common 
     neighbours can only disappear (get a higher degree) by inserting 
     at least two new such vertices with the same property, so only E3
     can be used from now on:
     The distance between two such vertices can not decrease with E3, 
     and if E3 is applied to one of them, the new 3-vertex will have
     (at least) the same distances from the remaining old one.

     The function will return TRUE, if they have no common neighbours 
     so that only E3 can be used further, otherwise FALSE. 
   */

  for (i = deg3 = 0; i < nv ; ++i)
          if (degree[i] == 3)
	    {  
	      if (deg3 == 0) {a = i;deg3=1;}
	      else           {b = i;i=nv;}
	    }
	e = firstedge[a];
	vmask=mask[e->end]; /* vmask will be the set of neighbours of a */
	vmask|=mask[e->prev->end];
	vmask|=mask[e->next->end];

	
	e = firstedge[b]; /* Test if two of the neighbours of b are in vmask*/
	if (mask[e->end] & vmask) 
	  { if ((mask[e->prev->end] & vmask) || (mask[e->next->end] & vmask)) return FALSE; }
	else
	  { if ((mask[e->prev->end] & vmask) && (mask[e->next->end] & vmask)) return FALSE; }

	return TRUE;
}

/************************** list_of_allowed_degrees ***********************/

/* The allowed degrees taken from the F-Switch LISTE are described as bits 
   of the binary representation of an integer.
   The definition of the error_of_degree is explained in the text below. 
   */

void
list_of_allowed_degrees(char arg[], int *pj )
{  
  static int init=1;
  int i,n,j,x,run,maxdegree, newi, newj, numlargesizes; 
  if (init) {
    init=0;
    maxdegree=8*sizeof(unsigned long long)-1;
    mask[0]=1;
    for(i=1;(i<=maxdegree) && (i<MAXN);i++) mask[i]=mask[i-1]<<1;
    for(i=0;i<MAXN;i++)
       error_up[i]=error_down[i]=error_of_degree[i]=error_1[i]=INFTY_AD;
    for(i=0;i<MAXN;i++) degreelist[i]=0;
  }
  j=*pj;
  if  (!isdigit(arg[j+1]))
    {fprintf(stderr,"No degrees given! Problem: %s\n",arg+j);exit(0);} 
  else 
    {  /* get the switch values of option -F */
      n = atoi (arg+j+1);
      if (n>=MAXN) {fprintf(stderr,"Maximum n is %d!\n",MAXN);exit(0);}
      if (n>maxdegree) {fprintf(stderr,"Maximum degree is %d!\n",maxdegree);exit(0);}
      LISTE |= mask[n];
      maxnumber[n]=MAXN; minnumber[n]=0;
      for (run=0; degreelist[run]; run++); degreelist[run]=n;
      if(n>maxdeg) maxdeg = n;
      for (i=3; i<=n; i++){
	if ( error_up[i] > (n-i)) error_up[i]=n-i;
      }
      if(n>=5){
	for(i=n;i<MAXN;i++){
	  if(error_down[i]> (i-n)){ 
	    error_down[i]=i-n;
	  }
	}
      }
      if(error_up[3]&&error_up[5]) x=error_up[5] - 1;
      else x=error_up[5];
     for(i=3;i<MAXN;i++)
       { if (2*error_down[i]<error_up[i])
                    error_1[i]=2*error_down[i];
       else error_1[i]=error_up[i];
       }

      for(i=3;i<MAXN;i++){
	if ((1+x)*error_down[i]<error_up[i]){
	  error_of_degree[i]=(1+x)*error_down[i]; }
	else {
	  error_of_degree[i]=error_up[i];
	}
      }
      j++; 
      while ((arg[j]>='0') && (arg[j]<='9')) j++; 
      j--;
      /* Two times the same to  be independent of the order */
      if (arg[j+1]=='_') { grenzen=1; j+=2;
			 minnumber[n]=atoi(arg+j);
			 while ((arg[j]>='0') && (arg[j]<='9')) j++; j--; }
      if (arg[j+1]=='^') { grenzen=1; j+=2;
			 maxnumber[n]=atoi(arg+j);
			 while ((arg[j]>='0') && (arg[j]<='9')) j++; j--; }
      if (arg[j+1]=='_') { grenzen=1; j+=2;
			 minnumber[n]=atoi(arg+j);
			 while ((arg[j]>='0') && (arg[j]<='9')) j++; j--; }
      if (arg[j+1]=='^') { grenzen=1; j+=2;
			 maxnumber[n]=atoi(arg+j);
			 while ((arg[j]>='0') && (arg[j]<='9')) j++; j--; }
      *pj = j;
    }

  if (error_of_degree[3] && error_of_degree[5]) x_error= error_of_degree[5]-1;
  else x_error= error_of_degree[5];

  for (i=6,numlargesizes=0;i<=maxdeg;i++) if (error_of_degree[i]==0) numlargesizes++;
  
  if ((numlargesizes<=2) && (error_of_degree[5]==0))
    doextra_x=1; else doextra_x=0;

} 



/**************************************************************************/

static void
find_extensions_ad(int numb_total, int numb_pres,
                EDGE *ext3[], int *numext3, 
                EDGE *ext4[], int *numext4,
                EDGE *ext5[], int *numext5)

/* Find all nonequivalent places for extension.
   These are listed in ext# according to the degree of the future new vertex.  
   The number of cases is returned in numext# (#=3,4,5). 

   For explanations of WHY this is correct, see plantri_ad paper.

*/
{
    int d3,d4;
    register EDGE *e,*e1,*e2,*ex, *start;
    EDGE **nb0,**nb1,**nbop,**nblim;

    register int i,i1,i2,i3,k,levs,excess;
    unsigned long long int vmask=0;
    int a,b,j,x,eintraege,error,ierror,nur_E3,nur_E5,do_E3,do_E4,do_E5,newi,newj;
    int eckenliste[MAXN];
    int d[MAXN]; /* number of vertices with degree [i] */
    int maxd, minimprove, improvebuffer, improvebuffer2;
    int errors1;


    if (nv==4) { *numext3=*numext4=1; *numext5=0;
                 ext3[0]=ext4[0]=firstedge[0];
                 return; }

    *numext3=*numext4=*numext5=0;
    do_E3=do_E4=do_E5=1;
	levs = maxnv - nv;          /* remaining number of steps */
	excess = 0;

	for (i = 3; i < nv; ++i) d[i]=0;
	for (i = 0; i < nv; ++i) (d[degree[i]])++;
	for (maxd=nv-1;d[maxd]==0;maxd--);
	for (i=maxd;i>maxdeg;i--) excess+= (d[i]*(i-maxdeg));


	d3=d[3]; d4=d[4];
	nur_E3 = ((d3>2) || ((d3==2) && nur_noch_E3()));
	if (error_of_degree[3] && nur_E3) { return; }

	i = d3 + d3 + d[4]; /* By (4): */ 

	if (excess) 
	  {
	    if (nur_E3 || (excess > levs)) { return; }
	    if (d3 > 0 && (excess >= levs)) { return; }
	    
	    if ((i > 0) && (excess > levs - i + 2)) { return; }
	  }

	if (error_of_degree[3]&&error_of_degree[4]&&(i>levs+1)) { return; }
	
	if (!nur_E3)
	  { 
	    /* In this case it is not possible to exclude any of the three
	       operations. */
	    for (i=3,error=0;i<=maxd;i++) error += (error_of_degree[i]*d[i]);
	    
	    if (error_up[3]&&error_up[5])
	      {
		// if (error>2*levs) return; extensions chosen so that this cannot happen
		minimprove=error-(2*(levs-1));
	      }
	    else { 
	      // if (error>3*levs) return;  extensions chosen so that this cannot happen
		   minimprove=error-(3*(levs-1));
	         }
		do_E3=((minimprove+error_of_degree[3])<=3);
		do_E4=((minimprove+error_of_degree[4])<=2);
		do_E5=((minimprove+error_of_degree[5])<=3+x_error);


		if (doextra_x)
		  {
		    for (i=3,errors1=0;i<=maxd;i++)
		      { errors1 += (error_1[i]*d[i]); }
		    if (errors1 >  (4*levs)) { return; }
		    /* only done if error(5)=0, so m(S)=4 for x=1 */
		  }


	  } /* end: all operations possible */

	else {
	  /* Only Operation E3 can be used from now on, so that "error_of_degree" may be 
	     substituted by "error_up". */
  
	  do_E4=do_E5=0;

	  for (i=4,error=0;i<=maxd;i++) /* error_of_degree[3]=0 -- otherwise the routine 
					   would already have returned */
	    { error += (error_up[i]*d[i]); }
	    if (error >  (3*levs)) { return; }
	    minimprove=error-(3*(levs-1));

	    if (error>levs)
	      { /* We try to find a set of independent vertices.  E3
                   can decrease the error of only one vertex of the
                   set.  So the number of remaining steps cannot be
                   less than the sum of errors of this vertex-set.  In
                   order to get an effective condition one starts the
                   computation of neighbours with vertices which have
                   a large error.  */



	  /* First rank the vertices with respect to the error of 
	     their degrees */


	    for (i=eintraege=0; i<nv; i++){	
	      if (error=error_up[degree[i]])
               {
		for (j=eintraege-1;(j>=0) && ((error_up[degree[eckenliste[j]]]) < error); j--)
    		                                eckenliste[j+1]=eckenliste[j];
		for ( ;(j>=0) && 
		       (error_up[degree[eckenliste[j]]] == error) && (degree[eckenliste[j]]>degree[i]); j--)
		  eckenliste[j+1]=eckenliste[j];

		eckenliste[j+1]=i; 
		eintraege++;
	      }
	      }
		  
	  for(i=ierror=vmask=0;i<eintraege; i++) 
	    {
	      a = eckenliste[i];          /* computation of the neighbours */
	      if (!(vmask & mask[a]))
		{
		  start = e = firstedge[a];
		  vmask|=mask[e->end]; /* vmask: set of forbidden vertices */
		  while((e=e->next) != start){
		    vmask|=mask[e->end];
		  }
		  ierror += error_up[degree[a]];
		  /* error: minimum number of necessary steps */ 
		  if (ierror>levs) { return; } 
		}
	    }
	      }/* end error>levs -- worth trying to find such an independent set */

	}


	nur_E5= (excess==levs);
	if (nur_E5) { do_E3=do_E4=0;}

	if ((excess>0) && (excess==levs-1)) do_E3=0;

	if (d3 || (d[4] > 2)) do_E5=0;


     /* code for trivial group */

	//find_extensions(numb_total, numb_pres,ext3, numext3, ext4, numext4,ext5, numext5); return;


    if (numb_total == 1)
    {
        
      if (do_E3)
	{ improvebuffer=minimprove+error_of_degree[3];
	  k = 0;
	  for (i = 0; i < nv; ++i)
	    { 
	      if (nur_E3) improvebuffer2=(error_up[degree[i]]-error_up[degree[i]+1]);
	      else improvebuffer2=(error_of_degree[degree[i]]-error_of_degree[degree[i]+1]);
	    if (improvebuffer-improvebuffer2<=2)
	    {
            e = ex = firstedge[i];
            do
	      {
		i2=degree[e->end]; i3=degree[e->next->end];
		if ( (nur_E3 &&
		      (improvebuffer<=improvebuffer2+ 
		       (error_up[i2]-error_up[i2+1]) +(error_up[i3]-error_up[i3+1])))

		     ||
		     (!nur_E3 && (improvebuffer<=improvebuffer2+
				  (error_of_degree[i2]-error_of_degree[i2+1])
				  +(error_of_degree[i3]-error_of_degree[i3+1]))))
		  {
		    e1 = e->invers->prev;
		    if (e1 > e)
		      {
			e1 = e1->invers->prev;
			if (e1 > e) ext3[k++] = e;
		      }
		  }
                e = e->next;
	      } while (e != ex);
	    }
	    }/* end of for() */
	  *numext3 = k;
	}

        if (do_E4)
        {   improvebuffer=minimprove+error_of_degree[4];
            k = 0;
            for (i = 0; i < nv; ++i)
            {
                if (degree[i] == 3) continue;
                e = ex = firstedge[i];
                do
                {
		i2=degree[e->end]; i3=degree[e->next->next->end];
		if (improvebuffer<=
		    (error_of_degree[i2]-error_of_degree[i2+1])
		    +(error_of_degree[i3]-error_of_degree[i3+1]))
		  {
                    e1 = e->next;
                    if (e1->invers > e1)
                    {
                        e2 = e1->invers->prev;
                        if ((degree[e->end] == 3) 
                                + (degree[e2->end] == 3) == d3)
                            ext4[k++] = e;
                    }
		  }
		e = e->next;
                } while (e != ex);
            }
            *numext4 = k;
        }
 
        if (do_E5)
        {   improvebuffer=minimprove+error_of_degree[5];
            k = 0;
            for (i = 0; i < nv; ++i)
            {
                if (degree[i] < 6) continue;
                if (nur_E5 && (degree[i]<=maxdeg)) continue;
		improvebuffer2=(error_of_degree[degree[i]]-error_of_degree[degree[i]-1]);
		if (improvebuffer-improvebuffer2<=2)
		  {
		    e = ex = firstedge[i];
		    do
		      {  i2=degree[e->end]; i3=degree[e->next->next->next->end];
		      if (improvebuffer<=improvebuffer2+
			  (error_of_degree[i2]-error_of_degree[i2+1])
			  +(error_of_degree[i3]-error_of_degree[i3+1]))
			{
			  e1 = e->next->next->next;
			  if ((degree[e->end] == 4)
			      + (degree[e1->end] == 4) == d4) 
			    ext5[k++] = e;
			}
		      e = e->next; 
		      } while (e != ex);
		  }
	    }
            *numext5 = k;
        }
    }




  /* code for nontrivial group */

    else
    {
        nb0 = (EDGE**)numbering[0];
        nbop = (EDGE**)numbering[numb_pres == 0 ? numb_total : numb_pres];
        nblim = (EDGE**)numbering[numb_total];

        for (i = 0; i < ne; ++i) nb0[i]->index = i;

	if (do_E3)
	  {
	    RESETMARKS;
	    improvebuffer=minimprove+error_of_degree[3];
	    k = 0;
	    for (i = 0; i < ne; ++i)
	      {
		e = nb0[i];
		if (ISMARKEDLO(e)) continue;
		i1=degree[e->start]; i2=degree[e->end]; i3=degree[e->next->end];
		if (( !nur_E3 && (improvebuffer<=
				  (error_of_degree[i1]-error_of_degree[i1+1])
				  +(error_of_degree[i2]-error_of_degree[i2+1])
				  +(error_of_degree[i3]-error_of_degree[i3+1]))) ||
		      ( nur_E3 && (improvebuffer<=
				  (error_up[i1]-error_up[i1+1])
				  +(error_up[i2]-error_up[i2+1])
				   +(error_up[i3]-error_up[i3+1]))))
		  ext3[k++] = e;
		
		for (nb1 = nb0 + i; nb1 < nbop; nb1 += MAXE) MARKLO(*nb1);
		
		for (; nb1 < nblim; nb1 += MAXE) MARKLO((*nb1)->invers);
		
		e1 = e->invers->prev;
		for (nb1 = nb0 + e1->index; nb1 < nbop; nb1 += MAXE) MARKLO(*nb1);
		
		for (; nb1 < nblim; nb1 += MAXE) MARKLO((*nb1)->invers);
		
		e1 = e1->invers->prev;
		for (nb1 = nb0 + e1->index; nb1 < nbop; nb1 += MAXE) MARKLO(*nb1);
		
		for (; nb1 < nblim; nb1 += MAXE) MARKLO((*nb1)->invers);
	      }
	    *numext3 = k;
	  }

        if (do_E4)
        {
            RESETMARKS;
	    improvebuffer=minimprove+error_of_degree[4];
            k = 0;
            for (i = 0; i < ne; ++i)
            {
                e = nb0[i];
                if (ISMARKEDLO(e)) continue;
                e1 = e->next->invers->prev;
                if ((degree[e->end] == 3) + (degree[e1->end] == 3) != d3)
                    continue;
		i2=degree[e->end]; i3=degree[e->next->next->end];
		if (improvebuffer<=
		    (error_of_degree[i2]-error_of_degree[i2+1])
		    +(error_of_degree[i3]-error_of_degree[i3+1]))
		  ext4[k++] = e;

                for (nb1 = nb0 + i; nb1 < nbop; nb1 += MAXE) MARKLO(*nb1);

                for (; nb1 < nblim; nb1 += MAXE) MARKLO((*nb1)->prev->prev);

                for (nb1 = nb0 + e1->index; nb1 < nbop; nb1 += MAXE)
                    MARKLO(*nb1);
 
                for (; nb1 < nblim; nb1 += MAXE) MARKLO((*nb1)->prev->prev);
            }
            *numext4 = k;
        }

        if (do_E5)
        {
            RESETMARKS;
	    improvebuffer=minimprove+error_of_degree[5];
            k = 0;
            for (i = 0; i < ne; ++i)
            {
                e = nb0[i];
                if (ISMARKEDLO(e) || degree[e->start] < 6) continue;

                if ((degree[e->end] == 4) 
                       + (degree[e->next->next->next->end] == 4) != d4)
                    continue;
		if (nur_E5 && (degree[e->start]<=maxdeg)) continue;
		i1=degree[e->start]; i2=degree[e->end]; i3=degree[e->next->next->next->end];
		     if (improvebuffer<=
			 (error_of_degree[i1]-error_of_degree[i1-1])
			 +(error_of_degree[i2]-error_of_degree[i2+1])
			 +(error_of_degree[i3]-error_of_degree[i3+1]))
		       ext5[k++] = e;
 
                for (nb1 = nb0 + i; nb1 < nbop; nb1 += MAXE) MARKLO(*nb1);
 
                for (; nb1 < nblim; nb1 += MAXE) 
                    MARKLO((*nb1)->prev->prev->prev); 
            } 
            *numext5 = k;
        }

    }
}


