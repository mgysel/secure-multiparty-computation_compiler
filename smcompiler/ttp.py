"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

import collections
from typing import (
    Dict,
    Set,
    Tuple,
    List,
)

from communication import Communication
from secret_sharing import(
    share_secret,
    Share,
)

import random

# Feel free to add as many imports as you want.

large_prime = (2 ** 17) - 1
field = list(range(large_prime))

class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        # Changed from Set to List for consistency with the protocol spec object and because it was useful 
        self.participant_ids: List[str] = list()
        self.already_shared_operations: Dict[str, Tuple[List[Share], List[Share], List[Share]]] = dict()


    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.append(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """

        res_tuple = ()
        clientIndex = self.participant_ids.index(client_id) 
        if(op_id in self.already_shared_operations):
            for valueShares in self.already_shared_operations[op_id]:
                res_tuple += (valueShares[clientIndex],)
        
        else:
            a = random.choice(field)
            b = random.choice(field)
            c = a * b

            aShares = share_secret(a, len(self.participant_ids))
            bShares = share_secret(b, len(self.participant_ids))
            cShares = share_secret(c, len(self.participant_ids))
            
            self.already_shared_operations[op_id] = (aShares, bShares, cShares)

            res_tuple += (aShares[clientIndex], bShares[clientIndex], cShares[clientIndex])

        return res_tuple

    # Feel free to add as many methods as you want.
