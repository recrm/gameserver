from abc import abstractmethod, ABC
from expiringdict import ExpiringDict
import copy

class Games(ABC):
    def __init__(self):
        self.games = ExpiringDict(max_len=20, max_age_seconds=3600)
        self.template = self.createTemplate()

    @abstractmethod
    def createTemplate(self):
        raise NotImplementedError

    def createNew(self):
        return copy.copy(self.template)