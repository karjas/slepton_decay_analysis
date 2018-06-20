#!/usr/bin/env python
# Script for combining two SuSpect files with valid param cards
import pprint
import pdb
import sys
import copy
import os

verbose = True
default_path = 'default_card.dat'


def vprint(*args):
    if verbose:
        for arg in args:
            sys.stdout.write(str(arg))
            sys.stdout.write(' ')
        sys.stdout.write('\n')


def yesno(question):
    print(question)
    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}
    choice = raw_input().lower()
    if choice in yes:
       return True
    elif choice in no:
       return False
    else:
       sys.stdout.write("Please respond with 'yes' or 'no'")


def read_lines(fpath):
    return open(fpath, 'r').read().strip().upper().split('\n')


def write_lines(lines, fpath):
    with open(fpath, 'w') as f:
        f.write('\n'.join(lines))


def file2dict(fpath):
    comments = []
    comment_char = '#'
    blocks = {}
    decays = {}
    # The block identifier we are currently processing in the loop
    current_identifier = False 
    # The particle decay we are currently processing in the loop
    current_particle = False 
    for line in read_lines(fpath):
        indented = False
        if len(line) > 0 and line[0] == ' ':
            indented = True
        line = ' '.join(line.strip().split())
        if indented:
            line = ' %s' % line
        splitted = line.split(comment_char, 1) # Cut away the commented part
        comment = ''
        if len(splitted) == 2:
            comment = splitted[1] 
        comments.append(comment)
        line = splitted[0]
        words = line.split()
        if len(words) == 0: # Skip empty lines
            continue
        keyword = words[0]
        if keyword == 'BLOCK':
            identifier = line.split(None, 1)[1].rstrip()
            if identifier not in blocks:
                blocks[identifier] = {}
            else:
                vprint("Warning: Block %s declared twice, merging...." % identifier)
            current_identifier = identifier
            current_particle = False
        elif keyword == 'DECAY':
            particle = words[1].rstrip()
            current_particle = particle
            current_identifier = False
            if particle in decays:
                vprint("Warning: Particle %s declared twice, overwriting...." % identifier)
            decays[particle] = {
                'width': words[2],
                'branches': set()
            }
        elif current_identifier: # If we are in a block
            splitted = line.strip().split()
            key = ' '.join(splitted[0:-1])
            blocks[current_identifier][key] = line
        elif current_particle: # If we are in a particle
            decays[current_particle]['branches'].add(line)

        output = {
            'blocks': blocks,
            'decays': decays,
        }
    return output


def dict2file(d, fpath, overwrite=False):
    output = []     # Array of lines in the output file
    decays = d['decays']
    blocks = d['blocks']
    for identifier, block in blocks.items():
        output.append('BLOCK %s' % identifier)
        for key, line in block.items():
            output.append(line)
    for particle, decay in decays.items():
        output.append(' '.join(['DECAY', particle, decay['width']]))
        for branch in decay['branches']:
            output.append(branch)

    if os.path.exists(fpath):
        if overwrite or yesno('File %s exists, overwrite? [y/n]' % fpath):
            vprint('Overwriting file %s...' % fpath)
            write_lines(output, fpath)
    else:
        write_lines(output, fpath)


def mergedicts(a, b):
    ''' Merge the dicts a and b by overwriting common values with the values in b '''
    merged = copy.deepcopy(a)
    a_blocks = a['blocks']
    b_decays = b['decays']
    b_blocks = b['blocks']

    for particle, b_decay in b_decays.items():
        merged['decays'][particle] = copy.deepcopy(b_decay)
    for identifier, b_block in b_blocks.items():
        if identifier not in a_blocks:
            merged['blocks'][identifier] = {}
        for key, line in b_block.items():
            merged['blocks'][identifier][key] = line

    return merged


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage : ./combiner.py <input file path> <output file path>')
        print('Default card file "default_card.dat" needs to be in the working directory.')
        sys.exit(1)
    nam1 = sys.argv[1]
    nam2 = sys.argv[2]
    original_dict = file2dict(default_path)
    new_dict = file2dict(nam1)
    merged = mergedicts(original_dict, new_dict)
    dict2file(merged, nam2)

