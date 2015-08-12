#!/usr/bin/python3
from Bio import SeqIO
from Bio import SearchIO
from Bio.SeqRecord import SeqRecord
from Bio.Blast.Applications import NcbiblastnCommandline as nb
import sys

def RunBlast():
    cmd=nb(query='unknown.fasta',db='primer',task='blastn-short',evalue=0.001,outfmt=5,out=''.join([area,'-PB']))
    stdout,stderr=cmd()
    return 

def Parse():
    Out=open(''.join([area,'-PB.log']),'a')
    sys.stdout=Out
    results=list(SearchIO.parse(''.join([area,'-PB']),'blast-xml'))
    for record in results:
        if len(record)==0:
            continue
        else: 
            tophit=record[0]
            #ignore multiple hsps
        print(tophit.id,record.id,'\n',tophit)
        BlastResult[record.id]=tophit.id

#main
area=sys.argv[1].replace('.fastq','')
Out=list()
Unknown=list()
BlastResult=dict()
Sum={'cp{:03d}'.format(n+1):0 for n in range(140)}
Primer=list(SeqIO.parse(sys.argv[2],'fasta'))
Sequences=SeqIO.parse(sys.argv[1],'fastq')
all=0
for record in Sequences:
    all+=1
    Unknown.append(record)
    head=str((record.seq)[0:15])
    for p in Primer:
        if head in p.seq:
            add=[p.id[:-1],record]
            Out.append(add)
            Unknown.pop(Unknown.index(record))
            break
SeqIO.write(Unknown,'unknown.fasta','fasta')
RunBlast()
Parse()
for index,record in enumerate(Unknown):
    if record.id in BlastResult:
        add=[BlastResult[record.id][:-1],record]
        Out.append(add)
        Unknown.pop(index)
for cp in Out:
    handle=open(cp[0],'a')
    Sum[cp[0]]+=1
    SeqIO.write(cp[1],handle,'fastq')
SeqIO.write(Unknown,'unknown.fastq','fastq')
Sum['unknown']=len(Unknown)
Sum['blasted']=len(BlastResult)
Sum['all']=all
with open(''.join([area,'-devideraw.csv']),'w') as Out:
    for key,value in Sum.items():
        Out.write(' '.join([key,str(value),'\n']))