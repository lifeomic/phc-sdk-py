from phc.web.base_client import BaseClient


class DataLakeQuery(object):
    def __init__(self, dataset_id, query, output_file_name):
        self.__dataset_id = dataset_id
        self.__query = query
        self.__output_file_name = output_file_name

    def to_request_dict(self):
        return {
            "query": self.__query,
            "datasetId": self.__dataset_id,
            "outputFileName": self.__output_file_name,
        }
