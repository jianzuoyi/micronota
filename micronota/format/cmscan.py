from skbio.io import create_format
from skbio.metadata import IntervalMetadata

from ..util import split, SplitterID


cmscan = create_format('cmscan')


@cmscan.reader(None)
def _generator(fh):
    splitter = split(SplitterID(lambda s: s.split()[2]),
                     ignore=lambda s: s.startswith('#'))
    for lines in splitter(fh):
        yield _parse_record(lines)


def _parse_record(lines):
    '''Return interval metadata'''
    imd = IntervalMetadata(None)
    seq_id = lines[0].split()[2]
    for line in lines:
        bounds, md = _parse_line(line)
        imd.add(bounds, metadata=md)
    return seq_id, imd


def _parse_line(line):
    items = line.split()
    fam_id = items[1]
    md = {'source': 'Rfam', 'ncRNA_class': items[0], 'db_xref': fam_id}
    if fam_id in {'RF00001', 'RF00177', 'RF02541', 'RF01959',
                  'RF02540', 'RF00001', 'RF00002', 'RF01960', 'RF02543'}:
        md['type'] = 'rRNA'
        if fam_id == 'RF00001':
            md['product'] = '5s_rRNA'
        elif fam_id in {'RF00177', 'RF01959'}:
            md['product'] = '16s_rRNA'
        elif fam_id in {'RF02541', 'RF02540'}:
            md['product'] = '23s_rRNA'
    else:
        md['type'] = 'ncRNA'

    strand = items[9]
    md['strand'] = strand
    if strand == '+':
        start = int(items[7]) - 1
        end = int(items[8])
    elif strand == '-':
        start = int(items[8]) - 1
        end = int(items[7])
    else:
        raise ValueError('Unknown strand for the ncRNA: %s' % line)
    return [(start, end)], md

