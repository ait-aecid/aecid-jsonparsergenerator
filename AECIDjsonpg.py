"""This is the main program of the AECID-JSON-parsergenerator (AECID-JSON-PG). The
script analyzes log files and generates a parser model for the logdata-
anomaly-miner. Configuration parameters are located in JSONPGConfig.py
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__authors__ = ["Georg Hoeld", "Markus Wurzenberger", "Max Landauer"
               , "Wolfgang Hotwagner"]
__contact__ = "aecid@ait.ac.at"
__copyright__ = "Copyright 2021, AIT Austrian Institute of Technology GmbH"
__credits__ = ["Florian Skopik"]
__date__ = "2021/10/20"
__deprecated__ = False
__email__ = "aecid@ait.ac.at"
__license__ = "GPLv3"
__maintainer__ = "Georg Hoeld"
__status__ = "Production"
__version__ = "1.0.0"

import JSONPGConfig


# Sanitizes entry by replacing the backslashes of escape characters with double backslashes
def sanitize_entry(entry):
    if type(entry) is str:
        return_string = ''
        for i in range(len(entry)):
            if entry[i] == '\t':
                return_string += '\\t'
            elif entry[i] == '\\':
                return_string += '\\\\'
            elif entry[i] == '\"':
                return_string += '\\"'
            else:
                return_string += entry[i]
        return return_string
    return entry


# This fuction checks if word follows the format of string_format.
def follows_format(string_format, word):
    if type(word) is not str:
        return False

    # Skip next char is used to skip the wildcards of string_format.
    skip_next_char = False
    last_index = 0
    for c in string_format:
        if c == '%':
            last_index += 1
            skip_next_char = True
            continue
        elif skip_next_char:
            skip_next_char = False
            continue
        try:
            index = word[last_index:].index(c)
            int(word[last_index-1:last_index + index])
            last_index += 1 + index
        except:
            return False
    try:
        # Check if the word is fully parsed.
        if last_index != len(word):
            int(word[last_index-1:])
        return True
    except:
        return False

# This function returns the string and adds quotation marks, if the string starts with a not alphabetical character.
def add_quotation_marks(string):
    if string[0].isalpha() or (
            len(string) > 2 and string[0] == nullable_key_prefix and string[1] == optional_key_prefix and string[2].isalpha()) or (
            len(string) > 1 and string[0] == nullable_key_prefix and string[1].isalpha()) or (
            len(string) > 1 and string[0] == optional_key_prefix and string[1].isalpha()):
        return string
    else:
        return "\"" + str(string) + "\""

# This function removes all characters of char_list from the string and adds quotation marks if the string is a integer or float.
def remove_characters(string, char_list):
    if  type(string) is int or type(string) is float or ('_' in string and (string[:string.index('_')].isdigit() or (
            '.' in string and string[:string.index('.')].isdigit() and string[string.index('.') + 1:string.index('_')].isdigit()))) or (
            string.isdigit() or ('.' in string and string[:string.index('.')].isdigit() and string[string.index('.') + 1:].isdigit())):
        string = "\"" + str(string) + "\""
    elif type(string) is str:
        for i in range(len(string)-1, -1, -1):
            if string[i] in char_list:
                string = string[:i] + string[i + 1:]
    return string

# This function returns True if a dictionary is included in the object and False otherwise.
def includes_dict(obj):
    if type(obj) is dict:
        return True
    elif type(obj) is list:
        return any(includes_dict(sublist) for sublist in obj)
    else:
        return False

# This function converts all lists into tuples.
def convert_to_tuples(dictionary):
    if type(dictionary) is list:
        return_tuple = []
        for entry in dictionary:
            return_tuple.append(convert_to_tuples(entry))
        return_tuple = tuple(return_tuple)
        return return_tuple
    return sanitize_entry(dictionary)

# This function converts all tuples and sets into lists.
def convert_to_lists(dictionary):
    if type(dictionary) is set or type(dictionary) is tuple:
        return_list = []
        for entry in dictionary:
            return_list.append(convert_to_lists(entry))
        return return_list
    return dictionary

# This function receives a new dictionary and saves its values in the structure of the parser_dictionary.
# It checks if the values are optional and if the entries are lists, etc.
def fill_parser_dict(new_dict, parser_dict=None, previous_dict=None, initialize=False):
    # Initalize the parser dict.
    if initialize:
        # Differentiate between the different types for the new dictionary and recursively generate the parser dictionary.
        if type(new_dict) is dict:
            parser_dict = {}
            for key in new_dict:
                # The parser dict always has the entries following_nodes and optional. The parameter optional states if
                # the current node is optional and the subnodes of the node is situated in the entry of following_nodes.
                parser_dict[key] = {'following_nodes': None, 'optional': False, 'nullable': False, 'inconsistent': False}
                parser_dict[key]['following_nodes'] = fill_parser_dict(new_dict[key], initialize=True, previous_dict=parser_dict[key])
        elif type(new_dict) is list and len(new_dict) > 0 and includes_dict(new_dict):
            parser_dict = []
            for sub_new_dict in new_dict:
                if type(sub_new_dict) is dict:
                    parser_dict.append({})
                    for key in sub_new_dict:
                        # The parser dict always has the entries following_nodes and optional. The parameter optional states if
                        # the current node is optional and the subnodes of the node is situated in the entry of following_nodes.
                        parser_dict[-1][key] = {'following_nodes': None, 'optional': False, 'nullable': False, 'inconsistent': False}
                        parser_dict[-1][key]['following_nodes'] = fill_parser_dict(
                                sub_new_dict[key], initialize=True, previous_dict=parser_dict[-1][key])
                elif type(sub_new_dict) is list:
                    parser_dict.append([])
                    for index in range(len(sub_new_dict)):
                        # The parser dict always has the entries following_nodes and optional. The parameter optional states if
                        # the current node is optional and the subnodes of the node is situated in the entry of following_nodes.
                        parser_dict[-1].append(fill_parser_dict(sub_new_dict[index], initialize=True, previous_dict=parser_dict[-1]))
                else:
                    parser_dict.append({convert_to_tuples(sub_new_dict)})
        else:
            if type(new_dict) is list:
                parser_dict = {convert_to_tuples(new_dict)}
            else:
                parser_dict = {sanitize_entry(new_dict)}
                if new_dict == 'null':
                    previous_dict['nullable'] = True
    elif parser_dict is None:
        # Initialize the parser if the dictionary is empty.
        parser_dict = fill_parser_dict(new_dict, initialize=True)
    else:
        # Adapt the parser dictionary to the structure of the new dictionary.
        if type(parser_dict) is dict:
            if type(new_dict) is dict:
                for key in parser_dict:
                    if key not in new_dict and not parser_dict[key]['optional']:
                        # Set the parameter optional to True if the node of the parser dictionary does not appear in the new dictionary.
                        parser_dict[key]['optional'] = True
                for key in new_dict:
                    if key not in parser_dict:
                        # Add a optional node in the parser dictionary if a new node appears in new dictionary.
                        parser_dict[key] = {'following_nodes': None, 'optional': True, 'nullable': False, 'inconsistent': False}
                        parser_dict[key]['following_nodes'] = fill_parser_dict(
                                new_dict[key], initialize=True, previous_dict=parser_dict[key])
                    else:
                        # Recusively adapt the following nodes if they appear in both the parser and the new dictionary.
                        parser_dict[key]['following_nodes'] = fill_parser_dict(
                                new_dict[key], parser_dict=parser_dict[key]['following_nodes'], previous_dict=parser_dict[key])
            elif new_dict == 'null':
                previous_dict['nullable'] = True
            elif previous_dict is not None:
                previous_dict['inconsistent'] = True
        elif type(parser_dict) is list and type(new_dict) is list and includes_dict(parser_dict):
            # Recursively adapt the following nodes of the list in both the parser and the new dictionary.
            parser_dict[0] = fill_parser_dict(new_dict[0], parser_dict=parser_dict[0], previous_dict=parser_dict)
        elif type(parser_dict) is set:
            if parser_dict == {'null'} and new_dict != 'null':
                parser_dict = set()
            # Add new values of the lists of the parser dictionary.
            if type(new_dict) is list:
                if any(type(val) is not tuple for val in parser_dict):
                    previous_dict['inconsistent'] = True
                else:
                    parser_dict.add(sanitize_entry(convert_to_tuples(new_dict)))
            elif type(new_dict) is dict:
                if parser_dict == set():
                    parser_dict = fill_parser_dict(new_dict, initialize=True, previous_dict=previous_dict)
                elif previous_dict is not None:
                    previous_dict['inconsistent'] = True
            else:
                if new_dict == 'null':
                    previous_dict['nullable'] = True
                elif any(type(val) is tuple for val in parser_dict):
                    previous_dict['inconsistent'] = True
                else:
                    parser_dict.add(sanitize_entry(new_dict))

    return parser_dict

# This function returns the first two key_prefix in the list that does not appear at the beginning of any key of the parser_dict.
def generate_key_prefixes(parser_dict, key_prefix_list):
    appeared_keys = get_dictionary_keys(parser_dict)
    key_prefixes_list = []

    for key in key_prefix_list:
        if all(appeared_key[:len(key)] != key for appeared_key in appeared_keys):
            key_prefixes_list.append(key)
            if len(key_prefixes_list) == 2:
                return key_prefixes_list

    raise ValueError('Too many prefixes appear at the start of the dictionary keys. Please add characters to key_prefix_list.')

# This function returns all keys of the parser_dict.
def get_dictionary_keys(parser_dict):
    keys = []
    if type(parser_dict) is dict:
        for key in parser_dict:
            if includes_dict(parser_dict[key]):
                if type(parser_dict[key]) is dict:
                    keys += [key]
                    keys += get_dictionary_keys(parser_dict[key]['following_nodes'])
                elif type(parser_dict[key]) is list:
                    keys += [key]
                    keys += get_dictionary_keys(parser_dict[key])
    elif type(parser_dict) is list:
        for sub_parser_dict in parser_dict:
            keys += get_dictionary_keys(sub_parser_dict)
    return keys

'''
This function returns the strings of the generated parser tree in yml format.
@param dictionary dictionary of the parser tree.
@param depth current depth of the parser node.
@param end_node_string string for the definition of the end nodes in the parser.
@param tree_string string for the structure of the tree in the parser.
@param used_ids dictionary for the ids of the end nodes. Possible entries to a variable name are
['time', 'val', 'int', 'intopt', 'float', 'floatopt', 'var'].
@param self_id ID of the current node.
'''
def get_parser_tree_yml(dictionary, depth=6, end_node_string='', tree_string='', used_ids={}, self_id=''):
    if type(dictionary) is dict:
        # Add the current parser node to the tree_string.
        if 'following_nodes' in dictionary:
            # Check if inconsistencies appeared in the analysis of this node.
            if dictionary['inconsistent']:
                if tree_string[-2:] != '- ':
                    tree_string += "\n" + depth * tab_string + "# Inconsistencies appeared in the analysis of the following node!"
                else:
                    tree_string = tree_string[:-2] + "# Inconsistencies appeared in the analysis of the following node!\n" +\
                        depth * tab_string + '- '

            # Add tabs.
            if tree_string[-2:] != '- ':
                tree_string += "\n" + depth * tab_string

            # Differentiate if the node is optional and/or nullable.
            key_sting = str(self_id)
            if dictionary['optional']:
                key_sting = optional_key_prefix + key_sting
            if dictionary['nullable'] and dictionary['following_nodes'] != {'null'}:
                key_sting = nullable_key_prefix + key_sting
            tree_string += add_quotation_marks(key_sting) + ":"

            # Append the following nodes to the strings.
            [end_node_string, tree_string] = get_parser_tree_yml(dictionary['following_nodes'], depth+1, date_format_list, end_node_string,
                    tree_string, used_ids, self_id)

        elif dictionary == {}:
            tree_string += " EMPTY_OBJECT"

        else:
            # Add the keys of the dictionary as nodes.
            for key in dictionary:
                # Check if inconsistencies appeared in the analysis of this node.
                if dictionary[key]['inconsistent']:
                    if tree_string[-2:] != '- ':
                        tree_string += "\n" + depth * tab_string + "# Inconsistencies appeared in the analysis of the following node!"
                    else:
                        tree_string = tree_string[:-2] + "# Inconsistencies appeared in the analysis of the following node!\n" +\
                            depth * tab_string + '- '

                # Add tabs.
                if tree_string[-2:] != '- ':
                    tree_string += "\n" + depth * tab_string

                # Differentiate if the node is optional and/or nullable.
                key_sting = str(key)
                if dictionary[key]['optional']:
                    key_sting = optional_key_prefix + key_sting
                if dictionary[key]['nullable'] and dictionary[key]['following_nodes'] != {'null'}:
                    key_sting = nullable_key_prefix + key_sting
                tree_string += add_quotation_marks(key_sting) + ":"

                # Append the following nodes to the strings.
                [end_node_string, tree_string] = get_parser_tree_yml(dictionary[key]['following_nodes'], depth+1,
                        end_node_string, tree_string, used_ids, str(key))

    elif type(dictionary) is list and includes_dict(dictionary):
        # Add the list elements to the parser tree.
        for i in range(len(dictionary)):
            # Append the following nodes to the strings.
            if type(dictionary[i]) is dict:
                tree_string += "\n" + depth * tab_string + "- "

                [end_node_string, tree_string] = get_parser_tree_yml(dictionary[i], depth+1, end_node_string, tree_string, used_ids,
                        self_id)
            else:
                tree_string += "\n" + depth * tab_string + "# Arrays of arrays are not yet supported by the JSON parser!"

    elif type(dictionary) is set:
        # Add the elements of the lists to the tree_string.
        # Check if the name of the current node must be added to the used_ids.
        included_in_tuple = all(type(val) is tuple for val in dictionary)

        if remove_characters(self_id, problematic_chars) not in used_ids:
            used_ids[remove_characters(self_id, problematic_chars)] = {}

        # Add a time stamp end node
        if any(all(follows_format(date_format, val) for val in dictionary) for date_format in date_format_list) or (
                included_in_tuple and dictionary != {tuple([])} and
                any(all(follows_format(date_format, val[0]) for val in dictionary) for date_format in date_format_list)):
            if 'time' not in used_ids[remove_characters(self_id, problematic_chars)]:
                used_ids[remove_characters(self_id, problematic_chars)]['time'] = []

            #Find the fitting date_format
            date_format = ''
            for d_format in date_format_list:
                if (included_in_tuple and follows_format(d_format, next(iter(dictionary))[0])) or (
                        follows_format(d_format, next(iter(dictionary)))):
                    date_format = d_format
                    break

            # Add the new date format to the end nodes
            if date_format not in used_ids[remove_characters(self_id, problematic_chars)]['time']:
                end_node_string += "\n" + 4 * tab_string + "- id: " + remove_characters(str(self_id) + "_time" +
                        str(len(used_ids[remove_characters(self_id, problematic_chars)]['time'])), problematic_chars)
                end_node_string += "\n" + 5 * tab_string + "type: DateTimeModelElement"
                end_node_string += "\n" + 5 * tab_string + "name: '" + remove_characters(str(self_id) + "_time" +
                        str(len(used_ids[remove_characters(self_id, problematic_chars)]['time'])), problematic_chars) + "'"
                end_node_string += "\n" + 5 * tab_string + "date_format: '" + date_format + "'\n"
                used_ids[remove_characters(self_id, problematic_chars)]['time'].append(date_format)

            # Add the node to the tree
            if included_in_tuple:
                tree_string = "\n" + tree_string + depth * tab_string + "- " + remove_characters(str(self_id) + "_time" +
                    str(used_ids[remove_characters(self_id, problematic_chars)]['time'].index(date_format)), problematic_chars)
            else:
                tree_string += " " + remove_characters(str(self_id) + "_time" +
                    str(used_ids[remove_characters(self_id, problematic_chars)]['time'].index(date_format)), problematic_chars)

        # Add a fixed element end node.
        elif len(dictionary) == 1:
            if dictionary == {tuple([])}:
                # Check if the only entry is a empty list.
                tree_string += "\n" + depth * tab_string + '"EMPTY_ARRAY"'
            elif dictionary == {'null'}:
                # Check if the only entry is a empty list.
                tree_string += "\n" + depth * tab_string + '"NULL_OBJECT"'
            else:
                if 'val' not in used_ids[remove_characters(self_id, problematic_chars)]:
                    used_ids[remove_characters(self_id, problematic_chars)]['val'] = []

                # Check if the value has already appeared with the name of the variable, or if it must be added to the used_ids and
                # end_node_string.
                if not included_in_tuple and next(iter(dictionary)) in used_ids[remove_characters(self_id, problematic_chars)]['val']:
                    id_num = used_ids[remove_characters(self_id, problematic_chars)]['val'].index(next(iter(dictionary)))
                elif included_in_tuple and next(iter(dictionary))[0] in used_ids[remove_characters(self_id, problematic_chars)]['val']:
                    id_num = used_ids[remove_characters(self_id, problematic_chars)]['val'].index(next(iter(dictionary))[0])
                else:
                    id_num = len(used_ids[remove_characters(self_id, problematic_chars)]['val'])
                    if included_in_tuple:
                        used_ids[remove_characters(self_id, problematic_chars)]['val'].append(next(iter(dictionary))[0])
                    else:
                        used_ids[remove_characters(self_id, problematic_chars)]['val'].append(next(iter(dictionary)))
                    end_node_string += "\n" + 4 * tab_string + "- id: " + remove_characters(str(self_id) + "_str" + str(id_num),
                                                                                            problematic_chars)
                    end_node_string += "\n" + 5 * tab_string + "type: FixedDataModelElement"
                    end_node_string += "\n" + 5 * tab_string + "name: '" + remove_characters(str(self_id) + "_str" + str(id_num),
                                                                                             problematic_chars) + "'"
                    value_string = ''

                    # Remove the dictionary, if the entry is included in one.
                    if included_in_tuple:
                        value_string = str(convert_to_lists(next(iter(dictionary))[0]))
                    else:
                        value_string = str(next(iter(dictionary)))

                    # Change quotation marks if they appear in the value.
                    if "'" in value_string:
                        end_node_string += "\n" + 5 * tab_string + "args: \"" + value_string + "\"\n"
                    else:
                        end_node_string += "\n" + 5 * tab_string + "args: '" + value_string + "'\n"
                # Add the list element if the value is of type list.
                if included_in_tuple:
                    tree_string += "\n" + depth * tab_string + "- " + remove_characters(str(self_id) + "_str" + str(id_num),
                                                                                        problematic_chars)
                else:
                    tree_string += " " + remove_characters(str(self_id) + "_str" + str(id_num), problematic_chars)

        # Add a list node.
        elif len(dictionary) <= list_element_max_num:
            if 'list' not in used_ids[remove_characters(self_id, problematic_chars)]:
                used_ids[remove_characters(self_id, problematic_chars)]['list'] = []

            dictionary = convert_to_lists(dictionary)
            dictionary.sort()

            if included_in_tuple:
                reduced_dictionary = [val[0] for val in dictionary]
            else:
                reduced_dictionary = dictionary

            # Add the list element to the end_node_string if the list element has not already appeared.
            if reduced_dictionary not in used_ids[remove_characters(self_id, problematic_chars)]['list']:
                id_num = len(used_ids[remove_characters(self_id, problematic_chars)]['list'])
                used_ids[remove_characters(self_id, problematic_chars)]['list'].append(reduced_dictionary)
                end_node_string += "\n" + 4 * tab_string + "- id: " + remove_characters(str(self_id) + "_list" + str(id_num),
                                                                                        problematic_chars)
                end_node_string += "\n" + 5 * tab_string + "type: FixedWordlistDataModelElement"
                end_node_string += "\n" + 5 * tab_string + "name: '" + remove_characters(str(self_id) + "_list" + str(id_num),
                                                                                         problematic_chars) + "'"
                end_node_string += "\n" + 5 * tab_string + "args:"
                for val in reduced_dictionary:
                    end_node_string += "\n" + 5 * tab_string + "- \"" + str(val) + "\""
                end_node_string += "\n" + 5 * tab_string
            else:
                id_num = used_ids[remove_characters(self_id, problematic_chars)]['list'].index(reduced_dictionary)

            # Check if the values are all contained in a list and add the variable element to the tree_string.
            if included_in_tuple:
                tree_string += "\n" + depth * tab_string + "- " + remove_characters(str(self_id) + "_list" + str(id_num), problematic_chars)
            else:
                tree_string += " " + remove_characters(str(self_id) + "_list" + str(id_num), problematic_chars)

        # Add a integer element end node.
        elif all(type(val) is int for val in dictionary) or (included_in_tuple and all(type(val[0]) is int for val in dictionary)):
            # Check the value signs
            if (included_in_tuple and all(val[0] >= 0 for val in dictionary)) or (
                        not included_in_tuple and all(val >= 0 for val in dictionary)):
                if 'int' not in used_ids[remove_characters(self_id, problematic_chars)]:
                    used_ids[remove_characters(self_id, problematic_chars)]['int'] = None
                    end_node_string += "\n" + 4 * tab_string + "- id: " + remove_characters(str(self_id) + "_int", problematic_chars)
                    end_node_string += "\n" + 5 * tab_string + "type: DecimalIntegerValueModelElement"
                    end_node_string += "\n" + 5 * tab_string + "name: '" + remove_characters(str(self_id) + "_int",
                                                                                         problematic_chars) + "'\n"

                if included_in_tuple:
                    tree_string += "\n" + depth * tab_string + "- " + remove_characters(str(self_id) + "_int", problematic_chars)
                else:
                    tree_string += " " + remove_characters(str(self_id) + "_int", problematic_chars)
            else:
                if 'intopt' not in used_ids[remove_characters(self_id, problematic_chars)]:
                    used_ids[remove_characters(self_id, problematic_chars)]['intopt'] = None
                    end_node_string += "\n" + 4 * tab_string + "- id: " + remove_characters(str(self_id) + "_intopt", problematic_chars)
                    end_node_string += "\n" + 5 * tab_string + "type: DecimalIntegerValueModelElement"
                    end_node_string += "\n" + 5 * tab_string + "name: '" + remove_characters(str(self_id) + "_intopt",
                                                                                         problematic_chars) + "'"
                    end_node_string += "\n" + 5 * tab_string + "value_sign_type: 'optional'" + "\n"

                if included_in_tuple:
                    tree_string += "\n" + depth * tab_string + "- " + remove_characters(str(self_id) + "_intopt", problematic_chars)
                else:
                    tree_string += " " + remove_characters(str(self_id) + "_intopt", problematic_chars)

        # Add a float end node.
        elif all(type(val) is int or type(val) is float for val in dictionary) or (
                included_in_tuple and all(type(val[0]) is int or type(val[0]) is float for val in dictionary)):
            # Check the value signs
            if (included_in_tuple and all(val[0] >= 0 for val in dictionary)) or (
                        not included_in_tuple and all(val >= 0 for val in dictionary)):
                if 'float' not in used_ids[remove_characters(self_id, problematic_chars)]:
                    used_ids[remove_characters(self_id, problematic_chars)]['float'] = None
                    end_node_string += "\n" + 4 * tab_string + "- id: " + remove_characters(str(self_id) + "_float", problematic_chars)
                    end_node_string += "\n" + 5 * tab_string + "type: DecimalFloatValueModelElement"
                    end_node_string += "\n" + 5 * tab_string + "name: '" + remove_characters(str(self_id) + "_float",
                                                                                         problematic_chars) + "'"
                    end_node_string += "\n" + 5 * tab_string + "exponent_type: 'optional'" + "\n"

                if included_in_tuple:
                    tree_string += "\n" + depth * tab_string + "- " + remove_characters(str(self_id) + "_float", problematic_chars)
                else:
                    tree_string += " " + remove_characters(str(self_id) + "_float", problematic_chars)
            else:
                if 'floatopt' not in used_ids[remove_characters(self_id, problematic_chars)]:
                    used_ids[remove_characters(self_id, problematic_chars)]['floatopt'] = None
                    end_node_string += "\n" + 4 * tab_string + "- id: " + remove_characters(str(self_id) + "_floatopt", problematic_chars)
                    end_node_string += "\n" + 5 * tab_string + "type: DecimalFloatValueModelElement"
                    end_node_string += "\n" + 5 * tab_string + "name: '" + remove_characters(str(self_id) + "_floatopt",
                                                                                             problematic_chars) + "'"
                    end_node_string += "\n" + 5 * tab_string + "exponent_type: 'optional'"
                    end_node_string += "\n" + 5 * tab_string + "value_sign_type: 'optional'" + "\n"

                if included_in_tuple:
                    tree_string += "\n" + depth * tab_string + "- " + remove_characters(str(self_id) + "_floatopt", problematic_chars)
                else:
                    tree_string += " " + remove_characters(str(self_id) + "_floatopt", problematic_chars)

        # Add a variable end node.
        else:
            if 'var' not in used_ids[remove_characters(self_id, problematic_chars)]:
                used_ids[remove_characters(self_id, problematic_chars)]['var'] = []

            # Check what additional characters are needed in the variable.
            additional_chars = ''
            for char in optional_dict_chars:
                # Test if the character appears in the strings or in any string if the following node is a list.
                if any((type(val) is str and char in val) or (
                        included_in_tuple and any(type(char) is str and char in val2 for val2 in val)) for val in dictionary):
                    additional_chars += char

            # Add the variable element to the end_node_string if the variable element with the additional_chars has not already appeared.
            if additional_chars not in used_ids[remove_characters(self_id, problematic_chars)]['var']:
                id_num = len(used_ids[remove_characters(self_id, problematic_chars)]['var'])
                used_ids[remove_characters(self_id, problematic_chars)]['var'].append(additional_chars)
                end_node_string += "\n" + 4 * tab_string + "- id: " + remove_characters(str(self_id) + "_var" + str(id_num),
                                                                                        problematic_chars)
                end_node_string += "\n" + 5 * tab_string + "type: VariableByteDataModelElement"
                end_node_string += "\n" + 5 * tab_string + "name: '" + remove_characters(str(self_id) + "_var" + str(id_num),
                                                                                         problematic_chars) + "'"
                end_node_string += "\n" + 5 * tab_string + 'args: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
                end_node_string += additional_chars
                end_node_string += "\"\n"
            else:
                id_num = used_ids[remove_characters(self_id, problematic_chars)]['var'].index(additional_chars)

            # Check if the values are all contained in a list and add the variable element to the tree_string.
            if included_in_tuple:
                tree_string += "\n" + depth * tab_string + "- " + remove_characters(str(self_id) + "_var" + str(id_num), problematic_chars)
            else:
                tree_string += " " + remove_characters(str(self_id) + "_var" + str(id_num), problematic_chars)

    return end_node_string, tree_string


# Load configuration
input_files = JSONPGConfig.input_files
date_format_list = JSONPGConfig.date_format_list
key_prefix_list = JSONPGConfig.key_prefix_list
optional_dict_chars = JSONPGConfig.optional_dict_chars
problematic_chars = JSONPGConfig.problematic_chars
tab_string = JSONPGConfig.tab_string
list_element_max_num = JSONPGConfig.list_element_max_num

line_id = 0
log_line_dict = {}
parser_dict = None

# import log data and preprocess the lines
for input_file in input_files:
    print('Import ' + str(input_file) + '!')
    null = 'null'
    true = 'true'
    false = 'false'

    with open(input_file) as f:
        for line in f:
            if (line_id + 1) % 100000 == 0:
                print(str(line_id + 1) + ' lines have been imported!')

            if len(line) < 2:
                # Do not process empty log lines
                continue

            # Remove characters that should not o ccur in log data. According to RFC3164 only ascii code symbols 32-126
            # should occur in log data.
            line = ''.join([x for x in line if (31 < ord(x) < 127 or ord(x) == 9)])
            line = line.strip(' \t\n\r')

            log_line_dict[line_id] = eval(line)
            line_id += 1

    f.close()

    print('Total amount of log lines read: ' + str(line_id))

for line_id in log_line_dict:
    parser_dict = fill_parser_dict(log_line_dict[line_id], parser_dict)

key_prefixes = generate_key_prefixes(parser_dict, key_prefix_list)
optional_key_prefix = key_prefixes[0]
nullable_key_prefix = key_prefixes[1]

end_node_string = "\nParser:"

tree_string = "\n" + 4 * tab_string + "- id: json\n" + 5 * tab_string + "start: True\n" + 5 * tab_string + "type: JsonModelElement\n" +\
        5 * tab_string + "name: 'model'\n" + 5 * tab_string + "optional_key_prefix: '" + optional_key_prefix + "'\n" + 5 * tab_string +\
        "nullable_key_prefix: '" + nullable_key_prefix + "'\n" + 5 * tab_string + "key_parser_dict:"

[end_node_string, tree_string] = get_parser_tree_yml(parser_dict, depth=6, end_node_string=end_node_string,
        tree_string=tree_string)

return_string = end_node_string + tree_string + "\n"

with open(JSONPGConfig.parser_file, 'wb') as file:
    file.write(return_string.encode())

print('Parser done')
