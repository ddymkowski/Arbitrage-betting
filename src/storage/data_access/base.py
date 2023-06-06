from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    def add_bulk(self):
        pass

    @abstractmethod
    def get_bulk_by_insertion_timestamp(self):
        pass

    @abstractmethod
    def delete_bulk(self):
        pass