# Software Engineering Lab

Name: GURUBELLI YEKAMBAR ESHWAR RAO

SRN: PES2UG24CS173

| Folder | Lab |
| --- | --- |
| [Lab 1](Lab/Lab%201) | Requirements and UML |
| [Lab 2](Lab/Lab%202) | Submission and screenshots |
| [Lab 3](Lab/Lab%203) | Architecture and design |
| [Lab 4](Lab/Lab%204) | Reaction Time Tester |
| [Lab 5](Lab/Lab%205) | Static analysis |
| [Lab 6](Lab/Lab%206) | Code and branch coverage |
| [Lab 7](Lab/Lab%207) | Fuzz testing |

Project: [SprintFlow](https://github.com/Darshanpawar7/SE-SRS)

Install test dependencies with `python3 -m pip install -r requirements.txt`.

Run the tests separately from each lab folder:

- Lab 6: `python3 -m pytest -q CodeCoverageTest_warranty_claims_application.py BranchCoverageTest_warranty_claims_application.py --cov=warranty_claims --cov-branch`
- Lab 7: `python3 -m pytest -q test_warranty_claims.py`
