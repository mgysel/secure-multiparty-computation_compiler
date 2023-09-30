"""
Secret sharing scheme.
"""

from typing import List
import random

large_prime = (2 ** 17) - 1
field = list(range(large_prime))
#print(f"***** LARGE PRIME: {large_prime}")

class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, bn):
        # Adapt constructor arguments as you wish
        # TODO: Create field for secret sharing (Zq)
        # What size field?
            # https://crypto.stackexchange.com/questions/88931/should-the-field-size-in-shamir-secret-sharing-scheme-be-larger-than-secret
                # In practice, often use GF(2^k) where k = 8, 16, 32
            # https://moodle.epfl.ch/mod/forum/discuss.php?d=76221#p149940
                # As for the size of p, there is no one general answer. As a bit of a hint, notice that once the result of your computation, e.g., a * b, exceeds p, you get a wraparound (the result is a * b mod p). This could matter a lot for the correctness of your application, depending on the application.
        self.bn = bn

    def __repr__(self):
        # Helps with debugging.
        return f"{self.__class__.__name__}({repr(self.bn)})"

    def __add__(self, other):
        return Share((self.bn + other.bn) % large_prime)

    def __sub__(self, other):
        return Share((self.bn - other.bn) % large_prime)

    def __mul__(self, other):
        return Share((self.bn * other.bn) % large_prime)


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    # raise NotImplementedError("You need to implement this method.")

    # sample s(0), s(1), ..., s(n-1) elem of Zq uniformly at random
    secret_shares = []
    sum_secret_shares = 0
    for i in range(num_shares - 1):
        s_i = random.choice(field)
        sum_secret_shares += s_i
        secret_shares.append(Share(s_i))

    #print("*** SECRET SHARES BEFORE UPDATE")
    #for share in secret_shares:
        #print(share.bn)

    # set s(0) = s - sum(s(i) mod q)
    s_0 = (secret - sum_secret_shares) % large_prime
    secret_shares.insert(0, Share(s_0))

    #print(f"S0: {s_0}")

    return secret_shares

def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    # To recreate secret, sum all shares mod q
    sum_shares = 0
    for share in shares:
        sum_shares += share.bn

    secret = sum_shares % large_prime
    return secret


# Feel free to add as many methods as you want.
'''
secret = random.choice(field)
print("***** SECRET")
print(f"{secret}")

secret_shares = share_secret(secret, 2)
print("***** SECRET SHARES")
for share in secret_shares:
    print(f"This Share: {share.bn}")

reconstructed_secret = reconstruct_secret(secret_shares)
print("***** RECONSTRUCTED SECRET")
print(reconstructed_secret)
'''