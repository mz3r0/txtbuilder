# -*- coding: utf-8 -*-

import re
import random

MAX_LINES = 1000000
EMPTY_STRING = ''
DEFAULT_CALL_FUNCTIONS = True # TODO review upon release of RR feature
REMOVE_TRAILING_NEWLINES = False
UTF8SIG = 'utf-8-sig'
FLAG_SET_SORTED_RANDOM_DEFAULT = 0
SYMBL_USR_PRMPT = '~'
SYMBL_SET_PRMPT = '@'

# TXTB FUNCTIONS USED IN STATIC MEMBERS

def txtb_strip(data=EMPTY_STRING):
    return data.strip()


def txtb_to_caps(data=EMPTY_STRING):
    return data.upper()


def txtb_to_lower(data=EMPTY_STRING):
    return data.lower()


def txtb_precede_minus(data=EMPTY_STRING):
    result = EMPTY_STRING
    if data:
        split = data.split('\n')
        split[0] = '- ' + split[0].title()
        result = '\n'.join(split)
    return result


def txtb_audiosurf_gamemode(data=EMPTY_STRING):
    if data == 'none' or data == EMPTY_STRING:
        return 'None'
    result = EMPTY_STRING
    tmp = data.split()
    if len(tmp) > 1:
        for part in tmp:
            result += f'[as-{part}]'
        result = result.strip()
    else:
        result = f'[as-{data}]'
    return result


def txtb_rpl_newline(data=EMPTY_STRING):
    return data.replace('\n ', '\n')


def txtb_str_title(data=EMPTY_STRING):
    return data.title()


class TXTB:
    charmap = {
        's': ' ',  # Space
        't': '\t',  # Tab
        'n': '\n'  # Newline
    }

    function_map = {
        'strip': txtb_strip,
        'rpl_newline': txtb_rpl_newline,
        'caps': txtb_to_caps,
        'lower': txtb_to_lower,
        'linktitle': txtb_precede_minus,
        'title': txtb_str_title,
        'gametag': txtb_audiosurf_gamemode
    }

    section_separator = '%%'
    data_separator = '%'
    set_separator = '#'

    def __init__(self, input_name):
        """Prepare data and syntax, tokenization"""
        self.data = list()      # Text used as building blocks
        self.tokens = list()    # Syntax as a list of tokens to interpret
        self.set_index = dict() # index_in_data -> list_of_set_items
        self.set_index_by_name = dict() # set_name -> index_in_data

        ds = TXTB.data_separator
        ss = TXTB.set_separator

        with open(input_name, 'r', encoding=UTF8SIG) as fin:
            all_lines = fin.readlines(MAX_LINES)

        # Preprocess input text
        found_section_separator = False
        lines_containing_data = [EMPTY_STRING]
        current_line = 0
        lines_containing_syntax = list()
        for line in all_lines:
            if line.startswith(ds + ' ') or line.startswith(ds + '\n'):
                lines_containing_data.append(EMPTY_STRING)
                current_line += 1
                continue
            elif line.startswith(TXTB.section_separator):
                found_section_separator = True
                continue
            if found_section_separator:
                lines_containing_syntax.append(line)
            else:
                lines_containing_data[current_line] += line

        for line in lines_containing_syntax:
            self.tokens.extend(line.strip().split(' ')) # Trailing newline is preserved

        self.data = lines_containing_data

        if REMOVE_TRAILING_NEWLINES:
            for i in range(len(self.data)):
                self.data[i] = self.data[i].strip()

        set_items_indices = [i for i, data_item in enumerate(self.data) if data_item[0] == ss]
        for i in set_items_indices:
            set_name, set_items = TXTB.get_set_data(self.data[i])
            self.set_index[i] = set_items
            self.set_index_by_name[set_name] = i

    @staticmethod
    def get_set_data(data_item):
        """Return the set name and its items as a list"""
        line1, rest = data_item.split('\n', 1)
        set_name = line1.split(TXTB.set_separator)[1]

        the_set = {set_item.strip()
                   for line in rest.split('\n')
                   for set_item in line.split(',')
                   if set_item}  # TODO optimize this if possible

        set_items = list(the_set)   # Convert back to list, no duplicates

        if FLAG_SET_SORTED_RANDOM_DEFAULT == 0:
            set_items.sort()

        elif FLAG_SET_SORTED_RANDOM_DEFAULT == 1:
            random.shuffle(set_items)

        return set_name, set_items

    def generate_txt(self, output_name):
        """Interpret syntax and write to file"""
        fout = open(output_name, 'w', encoding=UTF8SIG)

        seq_type = EMPTY_STRING     # Also acts as a flag
        seq_tokens = list()         # Sequence tokens

        for t in self.tokens:
            if t[0] in [SYMBL_USR_PRMPT,SYMBL_SET_PRMPT]:
                if seq_type:
                    if seq_type == t[0]:
                        seq_type = EMPTY_STRING
                else:
                    seq_type = t[0]

                seq_tokens.append(t)  # Start/End

                if len(seq_tokens) > 1 and seq_type == EMPTY_STRING:
                    self.handle_sequence(seq_tokens, fout)
                    seq_tokens.clear()

                continue

            if seq_type:
                seq_tokens.append(t)
                continue

            # In any other case, just interpret each token
            fout.write(TXTB.interpret(t, self.data))
        fout.close()

    def handle_sequence(self, seq_tokens, file_out):
        """Handles user prompts and set prompts"""
        t_first = seq_tokens[0]
        t_middle = seq_tokens[1:-1]
        t_last = seq_tokens[-1]

        if t_first[0] == SYMBL_USR_PRMPT:
            user_prompt = ' '.join(t_middle)
            if t_first.find('.') != -1:
                user_prompt = TXTB.transform(user_prompt, t_first)
            user_input = input(f'{user_prompt}: ')
            file_out.write(TXTB.transform(user_input, t_last))
        elif t_first[0] == SYMBL_SET_PRMPT:
            for line in TXTB.combinations(t_middle, self.set_index, self.set_index_by_name):
                file_out.write(line + '\n')

    @staticmethod
    def transform(target_text, token_with_functions):
        """Prepare functions to be applied on target text - Intermediate step"""
        function_names = token_with_functions.split('.')[1:]
        if not function_names:
            return target_text
        result = TXTB.call_functions_on(target_text, function_names)
        return result

    @staticmethod
    def call_functions_on(target_text, functions):
        """Call functions with target text as an argument"""
        for f in functions:  # Does f exist in the dict keys?
            if f in TXTB.function_map:
                target_text = TXTB.function_map[f](target_text)
            else:
                print('Call not found: ' + f)  # TODO THROW EXCEPTION
        return target_text

    @staticmethod
    def interpret(token, data_section, call_functions=DEFAULT_CALL_FUNCTIONS):
        """
        Interprets a syntax token. Examples: 'arbitraryText.caps' and '3.strip'
        Tokens SYMBL_USR_PRMPT and SYMBL_SET_PRMPT never make it here.
        DEFAULT_CALL_FUNCTIONS is True.
        """
        atom = token.split('.')[0]

        if atom in TXTB.charmap:  # Character Sheet token?
            t = TXTB.charmap[atom]
        elif atom.isnumeric():  # Index token?
            if int(atom) < len(data_section):
                t = data_section[int(atom)]
            else:
                print('OUT OF BOUNDS IN DATA LIST')
                t = EMPTY_STRING  # TODO THROW EXCEPTION
        else:
            t = atom  # Raw insertion

        if call_functions:
            return TXTB.transform(t, token) # TODO figure what this does

        return t

    @staticmethod
    def count_iterations(limits):
        counter = [0] * len(limits)
        i = 0

        while i != len(counter):
            if i:
                counter[i] += 1
                if counter[i] == limits[i]:
                    counter[i] = 0
                    i += 1
                    continue
                i = 0

            yield counter
            counter[0] += 1

            if counter[i] == limits[i]:
                counter[i] = 0
                i += 1

    @staticmethod
    def combinations(tokens, set_index, set_index_by_name):
        """
        Interprets tokens as a template, inserts set items and yields all combinations.
        """
        template = ' '.join(tokens)
        ss = TXTB.set_separator

        # Token order is preserved throughout
        token_mods = list()
        nr_of_replacements = list()
        token_replacement = [[t,None] for t in tokens if t[0] == ss]

        for pair in token_replacement:
            token = pair[0]
            modifiers = list()
            _, set_reference, modifiers_maybe = token.split(ss)
            if set_reference.isnumeric():
                index = int(set_reference)
            else:
                index = set_index_by_name[set_reference]

            set_items = set_index[index]

            pair[1] = set_items
            set_len = len(set_items)

            if len(modifiers_maybe) > 1:
                modifiers = modifiers_maybe.split('.')[1:]

            if modifiers:
                first_modifier = modifiers[0]
                if first_modifier.isnumeric() and int(first_modifier) <= len(set_items):
                    set_len = int(first_modifier)
                    modifiers = modifiers[1:]  # Only function names

            nr_of_replacements.append(set_len)
            token_mods.append(modifiers)

        for indices in TXTB.count_iterations(nr_of_replacements):
            combination = template
            generator = zip(*zip(*token_replacement),indices,token_mods)
            for token, set_items, item_index, modifiers in generator:
                set_item = set_items[item_index]

                # Apply modifiers
                set_item = TXTB.call_functions_on(set_item,modifiers)

                combination = combination.replace(token,set_item)
            yield combination
