
class SubjectSearchComponent(object):

    def __init__(self):
        self.component_body = dict()

    def __getattr__(self, attr):
        handler = self.__global_handler
        handler.__func__.func_name = attr
        return handler

    def __global_handler(self, *args, **kwargs):
        self.component_body[self.__global_handler.__func__.func_name] = kwargs
        return

    def to_dict(self):
        return self.component_body


class SubjectSearchComponents(object):

    def __init__(self):
        self.key_components = dict()

    def observations(self):
        search_component = SubjectSearchComponent()
        if 'observations' not in self.key_components:
            self.key_components['observations'] = []
        self.key_components['observations'].append(search_component)
        return search_component

    def to_dict(self):
        key_components_dict = dict()
        for key, components in self.key_components.items():
            components_dict = []
            for component in components:
                components_dict.append(component.to_dict())
            key_components_dict[key] = components_dict
        return key_components_dict


class SubjectSearch(object):

    def __init__(self):
        self.search_components = dict()

    def patient(self):
        patient_component = SubjectSearchComponents()
        self.search_components['patient'] = patient_component
        return patient_component

    def to_dict(self):
        search_components_dict = dict()
        for key, component in self.search_components.items():
            search_components_dict[key] = component.to_dict()
        return search_components_dict
