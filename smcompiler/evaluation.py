# Need to test
# SMC Client, trusted parameter generator (for Beaver triplet scheme), secret-sharing scheme, engine for arithmetic circuits

# Must test communication (bytes sent and received) and computation costs (computation time)
# Must show
# - effect of number of parties on the costs
# - effect of number of addition operations, and separately, addition of scalars
# - effect of number of multiplication operations, and separately, scalar multiplications


from secret_sharing import Share, share_secret, reconstruct_secret, large_prime, field
from expression import Secret, Scalar

import time
from multiprocessing import Process, Queue

import random
import statistics
import time
import sys

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

from smc_party import SMCParty


def smc_client(client_id, prot, value_dict, queue, queue_sent, queue_received):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    res = cli.run()
    queue.put(res)

    print(f"Sent Bytes: {cli.sent_bytes}")
    print(f"Received Bytes: {cli.received_bytes}")
    # Add sent/received bytes to queue
    queue_sent.put(cli.sent_bytes)
    queue_received.put(cli.received_bytes)

    print(f"{client_id} has finished!")


def smc_server(args):
    run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue = Queue()
    queue_sent = Queue()
    queue_received = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue, queue_sent, queue_received)) for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    results_sent = list()
    results_received = list()
    for client in clients:
        results.append(queue.get())
        results_sent.append(queue_sent.get())
        results_received.append(queue_received.get())
    
    # print("RESULTS")
    total_sent_bytes = sum(results_sent)
    total_received_bytes = sum(results_received)
    user_sent_bytes = sum(results_sent) / len(results_sent)
    user_received_bytes = sum(results_received) / len(results_received)
    # print(f"Total sent bytes: {total_sent_bytes}")
    # print(f"Total received bytes: {total_sent_bytes}")

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results, results_sent, results_received


def suite(parties, expr):
    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    total_results = run_processes(participants, *clients)
    results = total_results[0]
    results_sent = total_results[1]
    results_received = total_results[2]

    return results, results_sent, results_received
    # for result in results:
    #     assert result == expected


def test_communication_addition(num_trials, num_additions):
    """
    
    """
    results_sent_secrets = []
    results_received_secrets = []
    results_sent_scalars = []
    results_received_scalars = []

    num_shares = num_additions + 1

    for i in range(num_trials):
        secrets = list()
        scalars = list()
        for i in range(num_shares):
            secrets.append(Secret())
        for i in range(num_shares):
            scalars.append(Scalar(i))
        
        parties = {}
        for i in range(len(secrets)):
            parties[str(i)] = {secrets[i]: i + 1}
        
        print("SECRETS")
        expression = secrets[0]
        for i in range(len(secrets) - 1):
            expression = expression + secrets[i + 1]
        results, results_sent, results_received = suite(parties, expression)
        print(results_sent)
        print(results_received)
        results_sent_secrets.append(sum(results_sent))
        results_received_secrets.append(sum(results_received))

        print("SCALARS")
        expression = scalars[0]
        for i in range(len(scalars) - 1):
            expression = expression + scalars[i + 1]
        results, results_sent, results_received = suite(parties, expression)
        print(results_sent)
        print(results_received)
        results_sent_scalars.append(sum(results_sent))
        results_received_scalars.append(sum(results_received))

    sent_secret_mean = statistics.mean(results_sent_secrets)
    sent_secret_std = statistics.stdev(results_sent_secrets)
    received_secret_mean = statistics.mean(results_received_secrets)
    received_secret_std = statistics.stdev(results_received_secrets)
    print("SENT AND RECEIVED - SECRET")
    print(sent_secret_mean)
    print(sent_secret_std)
    print(received_secret_mean)
    print(received_secret_std)

    sent_scalar_mean = statistics.mean(results_sent_scalars)
    sent_scalar_std = statistics.stdev(results_sent_scalars)
    received_scalar_mean = statistics.mean(results_received_scalars)
    received_scalar_std = statistics.stdev(results_received_scalars)
    print("SENT AND RECEIVED - SCALAR")
    print(sent_scalar_mean)
    print(sent_scalar_std)
    print(received_scalar_mean)
    print(received_scalar_std)

test_communication_addition(30, 10)
# test_suite3()


def test_communication_multiplication(num_trials, num_multiplications):
    """
    
    """
    results_sent_secrets = []
    results_received_secrets = []
    results_sent_scalars = []
    results_received_scalars = []

    num_shares = num_multiplications + 1

    for i in range(num_trials):
        secrets = list()
        scalars = list()
        for i in range(num_shares):
            secrets.append(Secret())
        for i in range(num_shares):
            scalars.append(Scalar(i))
        
        parties = {}
        for i in range(len(secrets)):
            parties[str(i)] = {secrets[i]: i + 1}
        
        print("SECRETS")
        expression = secrets[0]
        for i in range(len(secrets) - 1):
            expression = expression * secrets[i + 1]
        results, results_sent, results_received = suite(parties, expression)
        print(results_sent)
        print(results_received)
        results_sent_secrets.append(sum(results_sent))
        results_received_secrets.append(sum(results_received))

        print("SCALARS")
        expression = scalars[0]
        for i in range(len(scalars) - 1):
            expression = expression * scalars[i + 1]
        results, results_sent, results_received = suite(parties, expression)
        print(results_sent)
        print(results_received)
        results_sent_scalars.append(sum(results_sent))
        results_received_scalars.append(sum(results_received))

    sent_secret_mean = statistics.mean(results_sent_secrets)
    sent_secret_std = statistics.stdev(results_sent_secrets)
    received_secret_mean = statistics.mean(results_received_secrets)
    received_secret_std = statistics.stdev(results_received_secrets)

    print("SENT AND RECEIVED")
    print(sent_secret_mean)
    print(sent_secret_std)
    print(received_secret_mean)
    print(received_secret_std)

    sent_scalar_mean = statistics.mean(results_sent_scalars)
    sent_scalar_std = statistics.stdev(results_sent_scalars)
    received_scalar_mean = statistics.mean(results_received_scalars)
    received_scalar_std = statistics.stdev(results_received_scalars)

# test_communication_multiplication(2, 50)




############################################################################
########################### SECRET SHARING #################################
############################################################################
# Show effect of number of parties on the costs

# def test_computation_share_secret(num_trials, num_shares):
#     print(f'Number of Trials: {num_trials}')
#     print(f'Number of Shares: {num_shares}')
    
#     secret = random.choice(field)

#     results = []
#     for i in range(num_trials):

#         start = time.time()
#         shares = share_secret(secret, num_shares)
#         end = time.time()

#         elapsed_time = end - start 
#         results.append(elapsed_time)
    
#     mean = statistics.mean(results)
#     std_dev = statistics.stdev(results)

#     print("Computation Cost of share_secret: ")
#     print(f'Mean: {mean}')
#     print(f'Standard Deviation: {std_dev}')

# test_computation_share_secret(1000, 5)


# def test_computation_reconstruct_secret(num_trials, num_shares):
#     print(f'Number of Trials: {num_trials}')
#     print(f'Number of Shares: {num_shares}')
    
#     secret = random.choice(field)

#     results = []
#     for i in range(num_trials):
#         shares = share_secret(secret, num_shares)

#         start = time.time()
#         secret = reconstruct_secret(shares)
#         end = time.time()

#         elapsed_time = end - start 
#         results.append(elapsed_time)
    
#     mean = statistics.mean(results)
#     std_dev = statistics.stdev(results)

#     print("Computation Cost of reconstruct_secret: ")
#     print(f'Mean: {mean}')
#     print(f'Standard Deviation: {std_dev}')

# test_computation_share_secret(1000, 5)


# # NOTE: We do not need to test communication cost of reconstruct_secret
# # As the communication cost just looks at the number of bytes we are sending and receiving
# def test_communication_share_secret(num_shares):
#     print(f'Number of Shares: {num_shares}')
    
#     secret = random.choice(field)
#     shares = share_secret(secret, num_shares)
#     num_bytes_shares = sys.getsizeof(shares)
#     num_bytes_share = sys.getsizeof(shares[0])

#     print("Communication Cost of share_secret: ")
#     print(f'Size of all shares (Bytes): {num_bytes_shares}')
#     print(f'Size of one share (Bytes): {num_bytes_share}')

# test_communication_share_secret(5)




############################################################################
#################### ENGINE FOR ARITHMETIC CIRCUITS ########################
############################################################################

def test_computation_addition(num_trials, num_additions):
    print(f'Number of Trials: {num_trials}')
    print(f'Number of Additions: {num_additions}')

    results_secrets = []
    results_scalars = []
    for i in range(num_trials):
        secrets = []
        scalars = []
        for i in range(num_additions + 1):
            randomElement = random.choice(field)
            secrets.append(Secret(randomElement))
            scalars.append(Scalar(randomElement))
        
        start = time.time()
        sum = secrets[0]
        for i in range(len(secrets) - 1):
            sum = sum + secrets[i + 1]
        end = time.time()
        elapsed_time = end - start 
        results_secrets.append(elapsed_time)

        start = time.time()
        sum = scalars[0]
        for i in range(len(scalars) - 1):
            sum = sum + scalars[i + 1]
        end = time.time()
        elapsed_time = end - start 
        results_scalars.append(elapsed_time)

    mean = statistics.mean(results_secrets)
    std_dev = statistics.stdev(results_secrets)
    print("SECRETS - Computation Cost of Addition: ")
    print(f'Mean: {mean}')
    print(f'Standard Deviation: {std_dev}')

    mean = statistics.mean(results_scalars)
    std_dev = statistics.stdev(results_scalars)
    print("SCALARS - Computation Cost of Addition: ")
    print(f'Mean: {mean}')
    print(f'Standard Deviation: {std_dev}')

# test_computation_addition(100, 1000)


def test_computation_subtraction(num_trials, num_additions):
    print(f'Number of Trials: {num_trials}')
    print(f'Number of Additions: {num_additions}')

    results_secrets = []
    results_scalars = []
    for i in range(num_trials):
        secrets = []
        scalars = []
        for i in range(num_additions + 1):
            randomElement = random.choice(field)
            secrets.append(Secret(randomElement))
            scalars.append(Scalar(randomElement))
        
        start = time.time()
        sum = secrets[0]
        for i in range(len(secrets) - 1):
            sum = sum - secrets[i + 1]
        end = time.time()
        elapsed_time = end - start 
        results_secrets.append(elapsed_time)

        start = time.time()
        sum = scalars[0]
        for i in range(len(scalars) - 1):
            sum = sum - scalars[i + 1]
        end = time.time()
        elapsed_time = end - start 
        results_scalars.append(elapsed_time)

    mean = statistics.mean(results_secrets)
    std_dev = statistics.stdev(results_secrets)
    print("SECRETS - Computation Cost of Subtraction: ")
    print(f'Mean: {mean}')
    print(f'Standard Deviation: {std_dev}')

    mean = statistics.mean(results_scalars)
    std_dev = statistics.stdev(results_scalars)
    print("SCALARS - Computation Cost of Subtraction: ")
    print(f'Mean: {mean}')
    print(f'Standard Deviation: {std_dev}')

# test_computation_subtraction(100, 10)


def test_computation_multiplication(num_trials, num_additions):
    print(f'Number of Trials: {num_trials}')
    print(f'Number of Additions: {num_additions}')

    results_secrets = []
    results_scalars = []
    for i in range(num_trials):
        secrets = []
        scalars = []
        for i in range(num_additions + 1):
            randomElement = random.choice(field)
            secrets.append(Secret(randomElement))
            scalars.append(Scalar(randomElement))
        
        start = time.time()
        prod = secrets[0]
        for i in range(len(secrets) - 1):
            prod = prod * secrets[i + 1]
        end = time.time()
        elapsed_time = end - start 
        results_secrets.append(elapsed_time)
        
        start = time.time()
        prod = scalars[0]
        for i in range(len(scalars) - 1):
            prod = prod * scalars[i + 1]
        end = time.time()
        elapsed_time = end - start 
        results_scalars.append(elapsed_time)

    mean = statistics.mean(results_secrets)
    std_dev = statistics.stdev(results_secrets)
    print("SECRETS - Computation Cost of Multiplication: ")
    print(f'Mean: {mean}')
    print(f'Standard Deviation: {std_dev}')

    mean = statistics.mean(results_scalars)
    std_dev = statistics.stdev(results_scalars)
    print("SCALARS - Computation Cost of Multiplication: ")
    print(f'Mean: {mean}')
    print(f'Standard Deviation: {std_dev}')

# test_computation_multiplication(100, 1000)