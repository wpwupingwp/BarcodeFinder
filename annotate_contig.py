#!/usr/bin/python3

import sys
from Bio import SeqIO
from Bio import SearchIO
from Bio.Blast.Applications import NcbiblastnCommandline as nb
from Bio.SeqRecord import SeqRecord
from multiprocessing import cpu_count
from os import makedirs
from os.path import exists
from subprocess import call


def get_gene():
    # Edit it when necessary
    wanted_gene_list = [
        'accD', 'atpA', 'atpB', 'atpE', 'atpF', 'atpH', 'atpI', 'ccsA',
        'cemA', 'clpP', 'infA', 'matK', 'ndhA', 'ndhB', 'ndhC', 'ndhD',
        'ndhE', 'ndhF', 'ndhG', 'ndhH', 'ndhI', 'ndhJ', 'ndhK', 'petA',
        'petB', 'petD', 'petG', 'petL', 'petN', 'psaA', 'psaB', 'psaC',
        'psaI', 'psaJ', 'psbA', 'psbB', 'psbC', 'psbD', 'psbE', 'psbF',
        'psbH', 'psbI', 'psbJ', 'psbK', 'psbL', 'psbM', 'psbN', 'psbT',
        'psbZ', 'rbcL', 'rpl14', 'rpl16', 'rpl2', 'rpl20', 'rpl22',
        'rpl23', 'rpl32', 'rpl33', 'rpl36', 'rpoA', 'rpoB', 'rpoC1',
        'rpoC2', 'rps11', 'rps12', 'rps14', 'rps15', 'rps16', 'rps18',
        'rps19', 'rps2', 'rps3', 'rps4', 'rps7', 'rps8', 'rrn16',
        'rrn23', 'rrn4.5', 'rrn5', 'ycf1', 'ycf2', 'ycf3', 'ycf4'
    ]
    fragment = list()
    genomes = SeqIO.parse(sys.argv[1], 'gb')
    for genome in genomes:
        for feature in genome.features:
            if feature.type != 'gene' or 'gene' not in feature.qualifiers:
                continue
            position = list()
            if feature.location_operator != 'join':
                position.append([
                    int(feature.location.start),
                    int(feature.location.end)
                ])
            else:
                for i in feature.sub_features:
                    position.append([
                        int(i.location.start),
                        int(i.location.end)
                    ])
            for n, frag in enumerate(position):
                name = str(feature.qualifiers['gene'][0]).replace(' ', '_')
                if name not in wanted_gene_list:
                    continue
                sequence = str(genome.seq[frag[0]:frag[1]])
                if n > 0:
                    name = '-'.join([name, str(n + 1)])
                fragment.append([name, sequence])
    return fragment


def generate_query(fragment):
    handle = open('fragment.fasta', 'w')
    for gene in fragment:
        handle.write(''.join([
            '>', gene[0], '\n',
            gene[1], '\n'
        ]))
    handle.close()
    return 'fragment.fasta'


def blast(query_file, contig_file):
    xml_file = 'out/BlastResult.xml'
    call('makeblastdb -in {0} -out {1} -dbtype nucl'.format(contig_file,
                                                            contig_file),
         shell=True)
    cmd = nb(
        num_threads=cpu_count(),
        query=query_file,
        db=contig_file,
        task='blastn',
        evalue=0.001,
        outfmt=5,
        out=xml_file
    )
    stdout, stderr = cmd()
    return xml_file


def parse(xml_file):
    parse_result = list()
    blast_result = SearchIO.parse(xml_file, 'blast-xml')
    for record in blast_result:
        if len(record) == 0:
            continue
        else:
            tophit = record[0]
        parse_result.append([tophit[0][0].hit.id, tophit[0][0].query.id])
    # {contig.id:gene}
    return dict(parse_result)


def output(parse_result, contig_file, mode):
    contigs = SeqIO.parse(contig_file, 'fasta')
    annotated_contig = contig_file.split(sep='.')[0]
    handle = open(''.join([
        'out/',
        annotated_contig,
        '_annotated.fasta'
    ]), 'a')
    for contig in contigs:
        if contig.id in parse_result:
            gene = parse_result[contig.id]
            new_seq = SeqRecord(
                id='|'.join([gene, contig.id]),
                description='',
                seq=contig.seq
            )
            SeqIO.write(new_seq, handle, 'fasta')
            if mode == '2':
                minimum_length = 200
                if len(contig.seq) <= minimum_length:
                    continue
                gene_file = '-'.join([annotated_contig, gene])
                handle_gene = open(gene_file, 'a')
                SeqIO.write(new_seq, handle_gene, 'fasta')
    handle.close()


def main():
    """
    This program will annotate contigs from assembly according to given
    genbank file, which describes a complete chloroplast genome. The genbank
    file may contains single or several genomes.
    Edit wanted_gene list in get_cds(). If you want to annotate 
    mitochrondria contigs.
    Usage:
    python3 annotate_contig.py genbank_file contig_file mode
    Mode:
        1. Query contig against coding genes, then every contig will be
        annotated by gene name.
        2. Query contig in a whole genome. It only judge if contig was belong to
        genome of given genbank file. Also, contig less than 200bp will be
        droped. You can edit 'minimum_length' in output.
    The final result is 'out/contig_file_annotated.fasta'.
    On default, it use Nicotiana.gb which was placed in current path."""
    print(main.__doc__)
    if not exists('out'):
        makedirs('out')
    mode = sys.argv[3]
    if mode not in ['1', '2']:
        raise ValueError('Bad command!\n')
    contig_file = sys.argv[2]
    if mode == '1':
        fragment = get_gene()
        query_file = generate_query(fragment)
    else:
        query_file = sys.argv[1].replace('.gb', '.fasta')
        SeqIO.convert(sys.argv[1], 'gb', query_file, 'fasta')
    xml_file = blast(query_file, contig_file)
    parse_result = parse(xml_file)
    output(parse_result, contig_file, mode)


if __name__ == '__main__':
    main()
