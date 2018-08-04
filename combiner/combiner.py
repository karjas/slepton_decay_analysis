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
            line = '  %s' % line
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
    decays = d['decays'] if 'decays' in d else {}
    blocks = d['blocks'] if 'blocks' in d else {}
    for identifier, block in blocks.items():
        output.append('BLOCK %s' % identifier)
        for key, line in block.items():
            output.append(line)
    for particle, decay in decays.items():
        output.append(' '.join(['DECAY', particle, decay['width']]))
        for branch in decay['branches']:
            output.append(branch)

    if os.path.isfile(fpath):
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
            tmp = d[k].split()
            tmp = filter(None, tmp)
            m = tmp[1]
            d[eqMasses[k]]=" {0} {1}".format(eqMasses[k],m)
    return d

def generateMassCard(mne,mslr):
    ''' Creates a mass card with only neutralino and right handed slepton masses'''
    slrmu = '2000013'
    slre = '2000011'
    sllmu = '1000013'
    slle = '1000011'
    ne = '1000022'
    slrmuval = " {0} {1}".format(slrmu, mslr)
    slreval = " {0} {1}".format(slre, mslr)
    sllmuval = " {0} {1}".format(sllmu, mslr)
    slleval = " {0} {1}".format(slle, mslr)
    neval = " {0} {1}".format(ne, mne)
    outDict = {'blocks':{'MASS':{
        slrmu:slrmuval,
        slre:slreval,
        sllmu:sllmuval,
        slle:slleval,
        ne:neval
    }}}
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


def use_susyhit_suspect(setting):
    susyhit_path = script_relative_path('tools/susyhit')
    if setting:
        os.system('cp {0}/susyhit.in.suspect1 {0}/susyhit.in'.format(susyhit_path))
    else:
        os.system('cp {0}/susyhit.in.suspect2 {0}/susyhit.in'.format(susyhit_path))


def script_relative_path(rel_path):
    script_dir = os.path.dirname(__file__)
    return os.path.join(script_dir, rel_path)

def compute_decays(mass_dict):
    use_susyhit_suspect(False)
    sdecay_input = read_lines(script_relative_path('tools/susyhit/slhaspectrum.in.default'))
    sdecay_input[67] = mass_dict['blocks']['MASS']['2000011']
    sdecay_input[68] = mass_dict['blocks']['MASS']['2000013']
    sdecay_input[74] = mass_dict['blocks']['MASS']['1000022']
    write_lines(sdecay_input, script_relative_path('tools/susyhit/slhaspectrum.in'))
    os.system('cd %s; ./run' % script_relative_path('tools/susyhit'))
    return file2dict(script_relative_path('tools/susyhit/susyhit_slha.out'))
    

if __name__ == '__main__': 
    if len(sys.argv) < 3:
        opt = '-h'
    else:
        opt = sys.argv[2]
    if os.path.exists(default_path):
        original_dict = file2dict(default_path)
    else:
        print("Include default_card.dat in the running folder")
        sys.exit(1)

    if opt == '-h':
        print('Options :\n   <output file path> -f <input file path>\n   <output file path> -m <neutralino mass (GeV)> <slepton mass (GeV)>\n   -h This help message')
        sys.exit(1)
    elif opt == '-f':
        input_file = sys.argv[3]
        new_dict = file2dict(input_file)
    elif opt == '-m':
        m1 = sys.argv[3]
        m2 = sys.argv[4]
        mass_dict = generateMassCard(m1,m2)
        new_dict = compute_decays(mass_dict)
    else:
        print('Options :\n   <output file path> -f <input file path>\n   <output file path> -m <neutralino mass (GeV)> <slepton mass (GeV)>\n   -h This help message')
        sys.exit(1)
    # banner()
    output_file = sys.argv[1]
    merged = mergedicts(original_dict, new_dict)

    dict2file(merged, output_file)



