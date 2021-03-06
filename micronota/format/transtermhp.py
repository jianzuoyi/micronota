# ----------------------------------------------------------------------------
# Copyright (c) 2015--, micronota development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import re

from skbio.metadata import IntervalMetadata
from skbio.io import create_format

from ..util import split, split_head


transtermhp = create_format('transtermhp')


@transtermhp.reader(None)
def _generator(fh):
    '''Parse the annotation and add it to interval metadata.

    Parameters
    ----------
    f : str
        the file path from prediction

    Yield
    -----
    tuple of str and IntervalMetadata
        seq_id and interval metadata
    '''
    p = re.compile(r'Genes are interspersed, and start the first column.')
    p2 = re.compile(r'SEQUENCE ')
    splitter = split(split_head, ignore=lambda s: not s.strip(),
                     is_head=lambda s: p2.match(s),)
    # skip the head part
    for line in fh:
        if p.match(line):
            break
    for lines in splitter(fh):
        yield _parse_record(lines)


def _parse_record(lines):
    sid = lines[0].split()[1]
    splitter = split(split_head,
                     is_head=lambda s: not s.startswith('  '))
    imd = IntervalMetadata(None)
    for gene in splitter(lines):
        if len(gene) == 1:
            # there is no terminator predicted
            continue
        gene_id = gene[0].split()[0]
        it = iter(gene[1:])
        for term in it:
            items = term.split()
            term_id = '%s_%s' % (items[0], items[1])
            hair_pin_seq = next(it)
            hair_pin_seq = '/'.join(hair_pin_seq.split())
            start, end = int(items[2]), int(items[4])
            strand = items[5]
            if strand == '-':
                start, end = end, start
            bounds = [(start, end)]
            md = {'ID': term_id, 'gene_id': gene_id,
                  'confidence': items[7], 'strand': strand,
                  'source': 'TransTermHP',
                  'sequence': hair_pin_seq,
                  'type': 'terminator'}
            imd.add(bounds, metadata=md)
    return sid, imd
