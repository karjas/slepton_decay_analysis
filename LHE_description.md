# Description of LHE dataformat

Here is the collected list of parameters present in the Les Houches Event -format. The values are gathered from the [standard fromat accord](https://arxiv.org/abs/hep-ph/0609017)

## I) Init information

Gives the information on the event and the file as whole

### a) First line, process independent information


IDBMUP(1) IDBMUP(2) EBMUP(1)  EBMUP(2)  PDFGUP(1) PDFGUP(2) PDFSUP(1) PDFSUP(2) IDWTUP  NPRUP


| Name | Description |
| --- | --- |
IDBMUP(1) | Incoming beam 1 identity 
IDBMUP(2) | Incoming beam 2 identity
EBMUP(1) | Incoming beam 1 energy (GeV)
EBMUP(2) | Incoming beam 2 energy (GeV)
PDFGUP(1) | PDF set used (Parton Distribution Function)
PDFGUP(2) | PDF set used (Parton Distribution Function)
PDFSUP(1) | PDF set used (Parton Distribution Function)
PDFSUP(2) | PDF set used (Parton Distribution Function)
IDWTUP | Weighting strategy
NPRUP | Number of separately identified processes

### b) NPRUP lines, one for each process IPR in the range 1 through NPRUP: 

XSECUP(IPR) XERRUP(IPR) XMAXUP(IPR) LPRUP(IPR)|

| Name | Description |
|---|---|
XSECUP(IPR) | Cross-section information
XERRUP(IPR) | Cross-section information
XMAXUP | Cross-section information
LPRUP | Integer label

## II) Event data blocks (one for each event)
### a) One line containing common event information

NUP IDPRUP  XWGTUP  SCALUP  AQEDUP  AQCDUP

| Name | Description |
| --- | --- |
NUP | Number of particles in the event
IDPRUP | Some kind of identification..?
XWGTUP | Event weight
SCALUP | Event scale
AQEDUP | \(\alpha\)_{em} ???
AQCDUP | \(\alpha\)_s ???

##### b) NUP lines for each particle I in the range 1 through NUP

IDUP(I) ISTUP(I)  MOTHUP(1,I) MOTHUP(2,I) ICOLUP(1,I) ICOLUP(2,I) PUP(1,I)  PUP(2,I)  PUP(3,I)  PUP(4,I)  PUP(5,I)  VTIMUP(I) SPINUP(I)

|Name | Description|
|---|---|
IDUP(I) | ID of particle I
ISTUP(I) | [Particle status](http://home.thep.lu.se/~torbjorn/pythia81html/ParticleProperties.html)
MOTHUP(1,I) | Mother 1, [Explanation for 2 mothers](http://home.thep.lu.se/~torbjorn/pythia81html/ParticleProperties.html)
MOTHUP(2,I) | Mother 2
ICOLUP(1,I) | Colour ???
ICOLUP(2,I) | Colour ???
PUP (1,I) | px (PUP is 4-momentum + mass)
PUP (2,I) | py 
PUP (3,I) | pz
PUP (4,I) | E
PUP (5,I) | m
VTIMUP(I) | Proper lifetime
SPINUP(I) | Spin
