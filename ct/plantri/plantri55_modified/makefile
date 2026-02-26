CC=gcc
CFLAGS= -O4
LDFLAGS=
VERSION=55

all: plantri fullgen

tools: plantri_nft plantri_adj4 plantri_maxd plantri_mdcount plantri_ad \
       plantri_deg plantri_fo pccat

plantri: plantri.c
	${CC} -o plantri ${CFLAGS} plantri.c ${LDFLAGS}

plantri_s: plantri.c
	${CC} -o plantri_s ${CFLAGS} -DSPLITTEST plantri.c ${LDFLAGS}

plantri_r: plantri.c
	${CC} -o plantri_r ${CFLAGS} -DSTATS plantri.c ${LDFLAGS}

plantri_nft: plantri.c nft.c
	${CC} -o plantri_nft ${CFLAGS} '-DPLUGIN="nft.c"' plantri.c ${LDFLAGS}

plantri_adj4: plantri.c adj4.c
	${CC} -o plantri_adj4 ${CFLAGS} '-DPLUGIN="adj4.c"' \
		plantri.c ${LDFLAGS}

plantri_maxd: plantri.c maxdeg.c
	${CC} -o plantri_maxd ${CFLAGS} '-DPLUGIN="maxdeg.c"' \
		plantri.c ${LDFLAGS}

plantri_mdcount: plantri.c mdcount.c
	${CC} -o plantri_mdcount ${CFLAGS} '-DPLUGIN="mdcount.c"' \
		plantri.c ${LDFLAGS}

plantri_ad: plantri.c allowed_deg.c
	${CC} -o plantri_ad ${CFLAGS} '-DPLUGIN="allowed_deg.c"' \
		plantri.c ${LDFLAGS}

plantri_deg: plantri.c degseq.c
	${CC} -o plantri_deg ${CFLAGS} '-DPLUGIN="degseq.c"' \
		plantri.c ${LDFLAGS}

plantri_fo: plantri.c faceorbits.c
	${CC} -o plantri_fo ${CFLAGS} '-DPLUGIN="faceorbits.c"' \
		plantri.c ${LDFLAGS}

plantri_min5: plantri.c
	echo "plantri_min5 is obsolete.  Use plantri -m5."

fullgen: fullgen.c
	${CC} -o fullgen ${CFLAGS} fullgen.c ${LDFLAGS}

pccat: pcfilter.c pccat.c rng.o
	${CC} -o pccat '-DPLUGIN="pccat.c"' pcfilter.c rng.o

plantri-dist:
	mkdir plantri${VERSION}
	cp plantri.c nft.c adj4.c maxdeg.c mdcount.c allowed_deg.c \
	   degseq.c plantri-guide.txt more-counts.txt fullgen.c \
	   faceorbits.c fullgen-guide.txt LICENSE-2.0.txt \
           ${HOME}/nauty/sumlines.c makefile plantri${VERSION}
	tar cvf plantri${VERSION}.tar plantri${VERSION}
	gzip plantri${VERSION}.tar
	rm -R plantri${VERSION}
