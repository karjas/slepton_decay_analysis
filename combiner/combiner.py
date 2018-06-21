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
    yes = ['yes','y','ye', '']
    no = ['no','n']
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
           # print(keyword)
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

def combineMasses(d): 
    '''A function to set required masses as equal for MadGraph5''' 
    #List of masses that need to be equal
    eqMasses={'1000012':'1000014','2000001':'2000003', '1000001':'1000003','2000011':'2000013','1000011':'1000013','1000002':'1000004','2000002':'2000004'} 
    for k in eqMasses.keys():
        if k in d.keys():
            tmp = d[k].split(" ")
            tmp = filter(None, tmp)
            m = tmp[1]
            d[eqMasses[k]]=" {0} {1}".format(eqMasses[k],m)
    return d

def generateMassCard(mne,mslr):
    ''' Creates a mass card for -m option with only neutralino and right handed slepton masses'''
    slr = '2000013'
    ne = '1000022'
    slrval = " {0} {1}".format(slr, mslr)
    neval = " {0} {1}".format(ne, mne)
    outDict = {'blocks':{'MASS':{slr:slrval,ne:neval}}}
    return outDict

def mergedicts(a, b):
    ''' Merge the dicts a and b by overwriting common values with the values in b '''
    merged = copy.deepcopy(a)
    a_blocks = a['blocks']
    b_blocks = b['blocks']

    if 'decays' in b.keys():
        b_decays = b['decays']
        for particle, b_decay in b_decays.items():
            merged['decays'][particle] = copy.deepcopy(b_decay)
    
    for identifier, b_block in b_blocks.items():
        if identifier not in a_blocks:
            merged['blocks'][identifier] = {}
        for key, line in b_block.items():
            merged['blocks'][identifier][key] = line
    
    if 'MASS' in merged['blocks'].keys():
        merged['blocks']['MASS'] = combineMasses(merged['blocks']['MASS'])
    return merged


def banner():
    ban =    '''
 __       __  ________  __        ______    ______   __       __  ________        ________   ______  
|  \  _  |  \|        \|  \      /      \  /      \ |  \     /  \|        \      |        \ /      \ 
| $$ / \ | $$| $$$$$$$$| $$     |  $$$$$$\|  $$$$$$\| $$\   /  $$| $$$$$$$$       \$$$$$$$$|  $$$$$$\\
| $$/  $\| $$| $$__    | $$     | $$   \$$| $$  | $$| $$$\ /  $$$| $$__             | $$   | $$  | $$
| $$  $$$\ $$| $$  \   | $$     | $$      | $$  | $$| $$$$\  $$$$| $$  \            | $$   | $$  | $$
| $$ $$\$$\$$| $$$$$   | $$     | $$   __ | $$  | $$| $$\$$ $$ $$| $$$$$            | $$   | $$  | $$
| $$$$  \$$$$| $$_____ | $$_____| $$__/  \| $$__/ $$| $$ \$$$| $$| $$_____          | $$   | $$__/ $$
| $$$    \$$$| $$     \| $$     \\\\$$    $$ \$$    $$| $$  \$ | $$| $$     \         | $$    \$$    $$
 \$$      \$$ \$$$$$$$$ \$$$$$$$$ \$$$$$$   \$$$$$$  \$$      \$$ \$$$$$$$$          \$$     \$$$$$$ 
                                                                                                     
                                                                                                     
                                                                                                     
           ______    ______   __       __  _______   ______  __    __  ________  _______                
          /      \  /      \ |  \     /  \|       \ |      \|  \  |  \|        \|       \               
         |  $$$$$$\|  $$$$$$\| $$\   /  $$| $$$$$$$\ \$$$$$$| $$\ | $$| $$$$$$$$| $$$$$$$\\              
         | $$   \$$| $$  | $$| $$$\ /  $$$| $$__/ $$  | $$  | $$$\| $$| $$__    | $$__| $$              
         | $$      | $$  | $$| $$$$\  $$$$| $$    $$  | $$  | $$$$\ $$| $$  \   | $$    $$              
         | $$   __ | $$  | $$| $$\$$ $$ $$| $$$$$$$\  | $$  | $$\$$ $$| $$$$$   | $$$$$$$\\              
         | $$__/  \| $$__/ $$| $$ \$$$| $$| $$__/ $$ _| $$_ | $$ \$$$$| $$_____ | $$  | $$              
          \$$    $$ \$$    $$| $$  \$ | $$| $$    $$|   $$ \| $$  \$$$| $$     \| $$  | $$              
           \$$$$$$   \$$$$$$  \$$      \$$ \$$$$$$$  \$$$$$$ \$$   \$$ \$$$$$$$$ \$$   \$$              
                                                                                                     
'''
    print(ban)




if __name__ == '__main__':
   # print(len(sys.argv))
    banner()
    
    if len(sys.argv) == 1:
        opt = '-h'
    else:
        opt = sys.argv[1]
    if os.path.exists(default_path):
        original_dict = file2dict(default_path)
    else:
        print("Include default_card.dat in the running folder")
        sys.exit(1)

    if opt == '-h':
        print('Options :\n\t -f <input file path> <output file path>\n\t -m <output file path> <neutralino mass (GeV)> <slepton mass (GeV)\n\t -h This help message')
        sys.exit(1)
    elif opt == '-f':
        nam1 = sys.argv[2]
        nam2 = sys.argv[3]
        new_dict = file2dict(nam1)
    elif opt == '-m':
        nam2 = sys.argv[2]
        m1 = sys.argv[3]
        m2 = sys.argv[4]
        new_dict = generateMassCard(m1,m2)
        #print(original_dict['blocks']['MASS'])
    else:
        print('Options :\n\t -f <input file path> <output file path>\n\t -m <output file path> <neutralino mass (GeV)> <slepton mass (GeV)\n\t -h This help message')
        sys.exit(1)
    merged = mergedicts(original_dict, new_dict)

    dict2file(merged, nam2)



