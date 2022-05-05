"""This file holds the sample configuration parameters for the audit test logs.
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

input_files = ['data/in/testlog.txt'] # Path to input log file
parser_file = 'data/out/GeneratedParserModel.yml' # Path to output parser for AMiner
tab_string = "  "
date_format_list = ['%Y-%m-%dT%H:%M:%S.%fZ']
key_prefix_list = ['_', '+', '~', '§']
optional_dict_chars = [' ', ',', '.', ';', ':', '=', '*', '~', "'", '`', '\\\\', '\\"', '\\t', '/', '|', '!', '?', '@', '&', '#', '%', '$',
                       '§', '+', '<', '{', '[', '(', ')', ']', '}', '>']
problematic_chars = ['@']
list_element_max_num = 3
