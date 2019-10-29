"""
Query builder class to make subject search queries.
"""
from abc import abstractmethod


class BaseQueryBuilder(object):
    @abstractmethod
    def to_dict(self):
        raise NotImplementedError


class QueryProperty(BaseQueryBuilder):
    """Leaf most query builder class. E.g. `PatientFilterComponentQueryBuilder().foo(eq='bar')` will result
    on `{"foo": "bar"}` to be returned on `to_dict()`
    """

    def __init__(self):
        self.component_body = dict()

    def __getattr__(self, attr):
        handler = self.__global_handler
        handler.__func__.func_name = attr
        return handler

    def __global_handler(self, *args, **kwargs):
        if args and len(args) > 0:
            raise NotImplementedError(
                "Property only support key value arguments!"
            )

        components = []
        for operator, value_or_values in kwargs.items():
            values = (
                value_or_values
                if type(value_or_values) is list
                else [value_or_values]
            )
            for value in values:
                components.append({"operator": operator, "value": value})

        self.component_body[
            self.__global_handler.__func__.func_name
        ] = components
        return self

    def to_dict(self):
        """Converts the query into a dictionary

        Returns
        -------
        dict
            The query as a dictionary
        """
        return self.component_body


class QueryObservationProperty(QueryProperty):
    def __init__(self):
        QueryProperty.__init__(self)

    def with_components(self, components_properties):
        """Includes component query properties

        Parameters
        ----------
        components_properties : list
            List of component query properties

        Returns
        -------
        phc.util.QueryObservationProperty
            This query property

        Raises
        ------
        TypeError
            Invalid input provided
        """
        if type(components_properties) is not list:
            raise TypeError(
                "Observation property with_components parameter must be in an array!"
            )

        self.component_body["components"] = components_properties
        return self

    def to_dict(self):
        """Converts the query into a dictionary

        Returns
        -------
        dict
            The query as a dictionary
        """
        component_body_dict = dict()
        for key, value_or_values in self.component_body.items():
            if key == "components":
                if type(value_or_values) is list:
                    component_values = []
                    for value in value_or_values:
                        component_values.append(value.to_dict())
                    component_body_dict["components"] = component_values
                else:
                    component_body_dict[
                        "components"
                    ] = value_or_values.to_dict()
            else:
                component_body_dict[key] = value_or_values
        return component_body_dict


class QueryResource(BaseQueryBuilder):
    """
    Resource level builder class. 'observations', 'procedures' are considered as resources.
    """

    def __init__(self):
        self.key_components = dict()

    def with_observations(self, observation_properties):
        """Adds obervation properties

        Parameters
        ----------
        observation_properties : list
            A list of observation properties

        Returns
        -------
        phc.util.QueryResource
            This query resource

        Raises
        ------
        TypeError
            Invalid input provided
        """
        if type(observation_properties) is not list:
            raise TypeError(
                "Resource with_observations parameter must be in an array!"
            )

        self.key_components["observations"] = observation_properties
        return self

    def to_dict(self):
        """Converts the query into a dictionary

        Returns
        -------
        dict
            The query as a dictionary
        """
        key_components_dict = dict()
        for key, components in self.key_components.items():
            components_dict = dict()
            for component in components:
                components_dict = {**components_dict, **component.to_dict()}
            key_components_dict[key] = components_dict
        return key_components_dict


class PatientFilterQueryBuilder(BaseQueryBuilder):
    """
    Top most query for subject searches.
    """

    def __init__(self):
        self.search_components = dict()

    def patient(self):
        """Construct a query to search patients.

        Returns
        -------
        phc.util.QueryResource
            The query resource
        """
        patient_component = QueryResource()
        self.search_components["patient"] = patient_component
        return patient_component

    def to_dict(self):
        """Converts the query into a dictionary

        Returns
        -------
        dict
            The query as a dictionary
        """
        query = {
            "query": {"where": {}, "domain": "filter", "target": "patient"}
        }

        search_components_dict = dict()
        for key, component in self.search_components.items():
            search_components_dict[key] = (
                component if component is dict else component.to_dict()
            )

        query["query"]["where"] = search_components_dict
        return query
