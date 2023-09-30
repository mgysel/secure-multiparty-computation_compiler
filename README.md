# Advanced Topics on Privacy-Enhancing Technologies Project 2 - Secure Multiparty Computation Compiler

## Description

In this project, we developed a SMC framework, which allows users to compute a shared expression using different operations (addition, subtraction, and multiplication), scalar values, and the participants' secrets, without having to send them to a third party to do the computation. An in-depth discussion including the threat model, implementation details, and performance evaluation can be found in `SMCompiler_report.pdf`.

## Implementation

* expression.py - File where we defined how to represent our expressions and handle the operations between them
* secret_sharing.py - File where we implemented the secret sharing scheme (Additive Secret Sharing)
* ttp.py - File with the code to generate the Beaver Triplets for the multiplication operations
* smc_party.py - File where we run the SMC protocol
* test_integration.py - File for the integration tests
* test_expression.py - File where we tested the expressions and their representation
* test_ttp.py - File to test the trusted third party (not used)
* test_secret_sharing.py - File to test the secret sharing scheme (not used)

## Run & Test

As it stands, the current way to run the framework is by creating a use-case, placing it in the test_integration.py
and running the test command, in order to simulate the behavior of the framework for the given test case.
 
To test the framework, one needs to run the following command in the smcompiler directory:
```
python3 -m pytest
```

If the intended is just to run the integration tests, for example, then the command should be:
```
python3 -m pytest test_integration.py
```

## Performance

To test the system's performance, one must be in the smcompiler directory and run the command:
```
python3 evaluation.py
```

Note: Some performance tests are heavy since they consider cases where the system is given a large number of operations/parties

## References

https://github.com/spring-epfl/CS-523-public/blob/master/smcompiler/README.md
