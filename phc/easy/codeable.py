import os
import re
import pandas as pd
from phc import Session
from phc.services import Fhir
from phc.easy.util import (join_underscore, without_keys, concat_dicts,
                           prefix_dict_keys)


def system_to_column(system):
    "Convert system name (potentially URL) to a readable column name"
    (new_string, _) = re.subn(r'https?:\/\/', '', system)
    return new_string.replace('.', '_').replace('/', '_')


def tags_to_dict(tags):
    "Convert list of system codes to flat dictionary"
    return {system_to_column(tag['system']): tag['code'] for tag in tags}


def coding_to_dict(value):
    "Convert dictionary of system and code to flat dictionary"
    return {
        system_to_column(code_dict['system']): code_dict['code']
        for code_dict in value['coding']
    }


def coding_to_str(value):
    "Convert dictionary of system and code to a period-delimited string"
    return '|'.join([
        f"{system_to_column(code_dict['system'])}.{code_dict['code']}"
        for code_dict in value['coding']
    ])


def type_and_value_to_dict(codeable):
    "Convert dictionary of type and value to flat dictionary"
    return {coding_to_str(codeable['type']): codeable['value']}


def value_concept_to_dict(codeable):
    "Convert dictionary of a codeable concept to flat dictionary"
    return coding_to_dict(codeable['valueCodeableConcept'])


def value_string_to_dict(codeable):
    "Convert dictionary of url and valueString to flat dictionary"
    return {system_to_column(codeable['url']): codeable['valueString']}


def value_with_extras_to_dict(codeable):
    system = system_to_column(codeable['system'])
    attrs = {
        f"{system}_{key}": value
        for key, value in codeable.items() if key not in ['system', 'value']
    }
    return {**attrs, system: codeable['value']}


def tag_codeable_to_dict(codeable_dict):
    codeable_dicts = codeable_dict['tag']

    return {
        **prefix_dict_keys(without_keys(codeable_dict, ['tag']), 'tag'),
        **concat_dicts(map(generic_codeable_to_dict, codeable_dicts),
                       prefix='tag')
    }


def generic_codeable_to_dict(codeable_dict, prefix=''):
    "Convert any type of dictionary that contains code data to a flat dictionary"

    def prefixer(dictionary):
        return prefix_dict_keys(dictionary, prefix)

    if 'type' in codeable_dict and 'value' in codeable_dict:
        return prefixer(type_and_value_to_dict(codeable_dict))

    if 'valueCodeableConcept' in codeable_dict:
        return prefixer(value_concept_to_dict(codeable_dict))

    if 'valueString' in codeable_dict:
        return prefixer(value_string_to_dict(codeable_dict))

    if 'system' in codeable_dict and 'code' in codeable_dict:
        return prefixer(
            {system_to_column(codeable_dict['system']): codeable_dict['code']})

    if 'system' in codeable_dict and 'value' in codeable_dict:
        return prefixer(value_with_extras_to_dict(codeable_dict))

    if 'tag' in codeable_dict:
        return prefixer(tag_codeable_to_dict(codeable_dict))

    keys = codeable_dict.keys()

    if len(keys) == 1 and 'url' in codeable_dict:
        return prefixer(
            {'url': system_to_column(codeable_dict['url'])})

    print('Unknown codeable type', codeable_dict)

    return {}


def expand_url_dict(codeable_dict, prefix=''):
    if 'url' not in codeable_dict.keys():
        return {}

    prefix = join_underscore([prefix, system_to_column(codeable_dict['url'])])

    return concat_dicts([
        expand_extension(codeable_dict, prefix),
        {
            join_underscore([prefix, k]): v
            for k, v in without_keys(codeable_dict,
                                     ['url', 'extension']).items()
        }
    ])


def expand_extension(codeable_dict, prefix=''):
    extensions = codeable_dict.get('extension', [])

    return concat_dicts([
        concat_dicts([
            expand_extension(nested_codeable_dict, prefix),
            expand_url_dict(nested_codeable_dict, prefix)
        ]) for nested_codeable_dict in extensions
    ])


def expand_codeable_column(codeable_col):
    "Convert a pandas dictionary column with codeable data to a data frame"

    def codeable_values(codeables):
        if type(codeables) is list:
            return codeables
        elif type(codeables) is dict and type(codeables.get('tag')) is list:
            return codeables.get('tag')
        elif type(codeables) is dict:
            return [codeables]
        else:
            return []

    values = [
        concat_dicts([
            generic_codeable_to_dict(codeable, index)
            for index, codeable in enumerate(codeable_values(codeables))
        ]) for codeables in codeable_col.values
    ]

    return pd.DataFrame(values)
