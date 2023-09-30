"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import collections
import json
from typing import (
    Dict,
    Set,
    Tuple,
    Union
)

from communication import Communication
from expression import (
    Expression,
    Secret,
    Scalar,
    AddOp,
    MultOp,
    SubOp
)
from protocol import ProtocolSpec
from secret_sharing import(
    reconstruct_secret,
    share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
        ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict
        self.beaver_triplets_multiplication = {}
        self.multiplication_counter = 0
        self.sent_bytes = 0
        self.received_bytes = 0


    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """

        # Variable with the Secret used in the expression and the number of shares multiplications
        exprInfo = self.retrieve_expr_info(self.protocol_spec.expr)
        exprSecrets = exprInfo[0]
        exprSharesMults = exprInfo[1]

        numParticipants = len(self.protocol_spec.participant_ids)

        for i in range(exprSharesMults):
            beaverTriplets = self.comm.retrieve_beaver_triplet_shares(str(i))
            self.beaver_triplets_multiplication[i] = beaverTriplets

        ownSecrets = []
        ownShares = {}
        for secret in self.value_dict:
            ownSecrets.append(secret)
            ownShares[secret] = share_secret(self.value_dict[secret], numParticipants)

        myShares = []
        for exprSecret in exprSecrets:
            # If this expression secret is mine I want to send its respective share to the respective participant, and store my share of it
            if(exprSecret in ownSecrets):
                for i in range(numParticipants):
                    if(self.protocol_spec.participant_ids[i] != self.client_id):
                        receiver_id = self.protocol_spec.participant_ids[i]
                        self.comm.send_private_message(receiver_id, str(exprSecret.id)+"_owner", json.dumps(self.client_id))
                        self.comm.send_private_message(receiver_id, self.client_id+"_to_"+receiver_id+"_"+str(exprSecret.id), json.dumps(ownShares[exprSecret][i].bn))
            
                    else:
                        self.value_dict[exprSecret] = ownShares[exprSecret][i].bn

            # If this expression secret is not mine I want to retrieve my share of it
            elif(exprSecret not in self.value_dict):
                shareOwnerBytes = self.comm.retrieve_private_message(str(exprSecret.id)+"_owner")
                shareOwner = json.loads(shareOwnerBytes)

                shareValueBytes = self.comm.retrieve_private_message(shareOwner+"_to_"+self.client_id+"_"+str(exprSecret.id))
                shareValue = json.loads(shareValueBytes)
                
                self.value_dict[exprSecret] = shareValue
        
        finalShare = self.process_expression(self.protocol_spec.expr)

        # Share own final share with all the other participants
        self.comm.publish_message(self.client_id+"_final_share", json.dumps(finalShare.bn))

        # Retrieve other participants final shares
        allShares = [] 
        for sender_id in self.protocol_spec.participant_ids:
            if(sender_id != self.client_id):

                shareValueBytes = self.comm.retrieve_public_message(sender_id, sender_id+"_final_share")
                shareValue = json.loads(shareValueBytes)
                
                allShares.append(Share(shareValue))
            
            else:
                allShares.append(finalShare)
            
        self.sent_bytes = self.comm.sent_bytes
        self.received_bytes = self.comm.received_bytes

        return reconstruct_secret(allShares)


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ) -> Share:

        if isinstance(expr, AddOp):
            leftSide = self.process_expression(expr.a)
            rightSide = self.process_expression(expr.b)
            
            # If we are adding a constant, only the participant in the first position adds the constant
            if(isinstance(expr.a, Scalar) and self.protocol_spec.participant_ids.index(self.client_id) != 0):
                return rightSide
            elif(isinstance(expr.b, Scalar) and self.protocol_spec.participant_ids.index(self.client_id) != 0):
                return leftSide
            else:
                return leftSide + rightSide
        
        elif isinstance(expr, MultOp):
            leftSide = self.process_expression(expr.a)
            rightSide = self.process_expression(expr.b)
            
            if(isinstance(expr.a, Scalar) or isinstance(expr.b, Scalar)):
                return leftSide * rightSide
            
            else:
                # Retrieve each of the random values shares for this multiplication
                aShareValue = self.beaver_triplets_multiplication[self.multiplication_counter][0]
                bShareValue = self.beaver_triplets_multiplication[self.multiplication_counter][1]
                cShareValue = self.beaver_triplets_multiplication[self.multiplication_counter][2]

                aShare = Share(aShareValue)
                bShare = Share(bShareValue)
                cShare = Share(cShareValue)

                # publish [leftSide - a] share
                self.comm.publish_message(self.client_id+"_leftSide-a_share_mult"+str(self.multiplication_counter), json.dumps((leftSide-aShare).bn))

                # publish [rightside - b] share
                self.comm.publish_message(self.client_id+"_rightSide-b_share_mult"+str(self.multiplication_counter), json.dumps((rightSide-bShare).bn))

                allLeftSideSubAShares = []
                allRightSideSubBShares = []
                for sender_id in self.protocol_spec.participant_ids:
                    if(sender_id != self.client_id):

                        leftSideSubAValueBytes = self.comm.retrieve_public_message(sender_id, sender_id+"_leftSide-a_share_mult"+str(self.multiplication_counter))
                        leftSideSubAValue = json.loads(leftSideSubAValueBytes)
                        allLeftSideSubAShares.append(Share(leftSideSubAValue))

                        rightSideSubBValueBytes = self.comm.retrieve_public_message(sender_id, sender_id+"_rightSide-b_share_mult"+str(self.multiplication_counter))
                        rightSideSubBValue = json.loads(rightSideSubBValueBytes)
                        allRightSideSubBShares.append(Share(rightSideSubBValue))
                    
                    else:
                        allLeftSideSubAShares.append(leftSide-aShare)
                        allRightSideSubBShares.append(rightSide-bShare)

                
                leftSideSubAValue = reconstruct_secret(allLeftSideSubAShares)
                rightSideSubBValue = reconstruct_secret(allRightSideSubBShares)

                leftSideSubAValueAsShare = Share(leftSideSubAValue)
                rightSideSubBValueAsShare = Share(rightSideSubBValue)
                
                self.multiplication_counter += 1

                decrement = Share(0)
                # Only the participant in the first position subtracts the (leftSide-a) * (rightSide-b) factor
                if(self.protocol_spec.participant_ids.index(self.client_id) == 0):
                    decrement = leftSideSubAValueAsShare * rightSideSubBValueAsShare

                return cShare + leftSide * rightSideSubBValueAsShare + rightSide * leftSideSubAValueAsShare - decrement

        elif isinstance(expr, SubOp):
            leftSide = self.process_expression(expr.a)
            rightSide = self.process_expression(expr.b)
            return leftSide - rightSide

        elif isinstance(expr, Secret):
            for secret in self.value_dict:
                if(secret.id == expr.id):
                    return Share(self.value_dict[secret])

        elif isinstance(expr, Scalar):
            return Share(expr.value)
        
    # This function retrieves the instances of the secrets in the expression, as well as the number of multiplications between shares
    def retrieve_expr_info(self, expr: Expression) -> (Set[Secret], int):
        if isinstance(expr, AddOp) or isinstance(expr, SubOp):
            leftSide = self.retrieve_expr_info(expr.a)
            rightSide = self.retrieve_expr_info(expr.b)
            
            return (leftSide[0] + rightSide[0], leftSide[1] + rightSide[1]) 
        
        elif isinstance(expr, MultOp):
            leftSide = self.retrieve_expr_info(expr.a)
            rightSide = self.retrieve_expr_info(expr.b)
            increment = 0
            if(not isinstance(expr.a, Scalar) and not isinstance(expr.b, Scalar)):
                increment = 1
            return (leftSide[0] + rightSide[0], leftSide[1] + rightSide[1] + increment) 

        elif isinstance(expr, Secret):
            return ([expr], 0)

        elif isinstance(expr, Scalar):
            return ([], 0)

    # Feel free to add as many methods as you want.
