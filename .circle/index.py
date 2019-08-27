#!/usr/bin/env python

import os
import json
import yaml
import time
import argparse
import hashlib
from glob import glob
from collections import OrderedDict

from st2common.util.pack import get_pack_ref_from_metadata

EXCHANGE_NAME = "syncurity-exchange"
EXCHANGE_PREFIX = "syncurity"


def build_index(path_glob, output_path):
    result = OrderedDict({
        'packs': OrderedDict(),
        'metadata': OrderedDict([
            ('generated_ts', None),  # Timestamp of when the file has been generated
            ('hash', None)  # MD5 hash of all the content, useful when mirror the index
        ])
    })

    data_hash = hashlib.md5()

    path_glob = os.path.expanduser(path_glob)
    generator = sorted(glob(path_glob))

    counter = 0
    for filename in generator:
        with open(filename, 'r') as pack:
            pack_meta = yaml.load(pack)

        pack_name = pack_meta['name']
        pack_ref = get_pack_ref_from_metadata(metadata=pack_meta)
        sanitized_pack_name = pack_ref

        print('Processing pack: %s (%s)' % (pack_name, filename))

        pack_meta['repo_url'] = 'https://github.com/%s/%s-%s' % (
            EXCHANGE_NAME, EXCHANGE_PREFIX, sanitized_pack_name
        )

        # Note: Key in the index dictionary is ref and not a name
        result['packs'][pack_ref] = pack_meta

        # Remove any old entry for pack name when we incorrectly used name instead of ref for the
        # key
        if pack_name != pack_ref:
            result['packs'].pop(pack_name, None)

        data_hash.update(str(pack_meta))
        counter += 1

    result['metadata']['generated_ts'] = int(time.time())
    result['metadata']['hash'] = data_hash.hexdigest()

    output_path = os.path.expanduser(os.path.join(output_path, 'index.json'))
    with open(output_path, 'w') as outfile:
        json.dump(result, outfile, indent=4, sort_keys=True,
                  separators=(',', ': '))

    print('')
    print('Processed %s packs.' % (counter))
    print('Index data written to "%s".' % (output_path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate syncurity exchange index.json')
    parser.add_argument('--glob', help='Glob which points to the pack metadatafiles',
                        required=True)
    parser.add_argument('--output', help='Directory where the generated index.json file is stored',
                        required=True)
    args = parser.parse_args()

    build_index(path_glob=args.glob, output_path=args.output)
