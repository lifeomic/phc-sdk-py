"""
Query builder class to make subject search queries.
"""
from abc import abstractmethod


class BaseQueryBuilder(object):
    @abstractmethod
    def to_dict(self):
        raise NotImplementedError


class PatientFilterComponentQueryBuilder(BaseQueryBuilder):
    """
    Leaf most query builder class. E.g. PatientFilterComponentQueryBuilder().foo(eq='bar') will result
    on {"foo": "bar"} to be returned on to_dict()
    """

    def __init__(self):
        self.component_body = dict()

    def __getattr__(self, attr):
        handler = self.__global_handler
        handler.__func__.func_name = attr
        return handler

    def __global_handler(self, *args, **kwargs):
        component = {
            'operator': None,
            'value': None
        }
        for operator, value in kwargs.items():
            component['operator'] = operator
            component['value'] = value

        self.component_body[self.__global_handler.__func__.func_name] = [component]
        return self

    def to_dict(self):
        return self.component_body


class PatientFilterComponentsQueryBuilder(BaseQueryBuilder):
    """
    Property level builder class. 'observations', 'procedures' are considered as properties.
    """

    def __init__(self):
        self.key_components = dict()

    def observations(self):
        search_component = PatientFilterComponentQueryBuilder()
        self.key_components['observations'] = search_component
        return search_component

    def to_dict(self):
        key_components_dict = dict()
        for key, components in self.key_components.items():
            key_components_dict[key] = {**components.to_dict()}
        return key_components_dict


class PatientFilterQueryBuilder(BaseQueryBuilder):
    """
    Top most query for subject searches.
    """

    def __init__(self):
        self.search_components = dict()

    def patient(self):
        patient_component = PatientFilterComponentsQueryBuilder()
        self.search_components['patient'] = patient_component
        return patient_component

    def to_dict(self):
        query = {
            'query': {
                'where': {
                },
                'domain': 'filter',
                'target': 'patient'
            }
        }

        search_components_dict = dict()
        for key, component in self.search_components.items():
            search_components_dict[key] = component.to_dict()

        query['query']['where'] = search_components_dict
        return query
