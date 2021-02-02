''' defines activitypub collections (lists) '''
from dataclasses import dataclass, field
from typing import List

from .base_activity import ActivityObject


@dataclass(init=False)
class OrderedCollection(ActivityObject):
    ''' structure of an ordered collection activity '''
    totalItems: int
    first: str
    last: str = None
    name: str = None
    summary: str = None
    owner: str = None
    to: List[str] = field(default_factory=lambda: [])
    cc: List[str] = field(default_factory=lambda: [])
    type: str = 'OrderedCollection'


@dataclass(init=False)
class OrderedCollectionPage(ActivityObject):
    ''' structure of an ordered collection activity '''
    partOf: str
    orderedItems: List
    next: str
    prev: str
    type: str = 'OrderedCollectionPage'
