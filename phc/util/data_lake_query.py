class DataLakeQuery(object):
    """Represents a data lake query

    Parameters
    ----------
    project_id : str
        The project ID
    query: dict
        The query parameters
    output_file_name: str
        The name of the file where the results should be stored.
    """

    def __init__(self, project_id, query, output_file_name):
        self.__dataset_id = project_id
        self.__query = query
        self.__output_file_name = output_file_name

    def to_request_dict(self):
        """Converts the query into a query request dictionary.

        Returns
        -------
        dict
            A dictionary that can be sent in a query request.
        """
        return {
            "query": self.__query,
            "datasetId": self.__dataset_id,
            "outputFileName": self.__output_file_name,
        }
