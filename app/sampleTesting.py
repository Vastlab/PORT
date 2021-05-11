"""
This file is used for testing generateSamples and ORGeneratePools from OrderedPooledTesting and writing this data to
files.
"""

from OrderedPooledTesting import generateSamples, ORGeneratePools
import csv


FILENAME = 'testing.txt'
MAXPOOLSIZE = 32
MAXTESTS = 16

#Example 1
ASYMPTOMATIC = 100
SYMPTOMATIC = 20
PA = 0.01
PS = 0.2


# Example 2
ASYMPTOMATIC = 60
SYMPTOMATIC = 60
PA = 0.0166
PS = 0.0666


# Returns sample id, probability, status, poolID, RowID, ColumnID
def returnFunction(sample, pool):
    requests = {
        'SampleID': [],
        'Probability': [],
        'Status': [],
        'PoolID': [],
        'RowID': [],
        'ColumnID': []
    }
    # Create new dictionary with data from sample and pool
    for data in sample:
        requests['SampleID'].append(data['SampleID'])
        requests['Probability'].append(data['InitialProb'])
        requests['Status'].append(data['Positive'])

    for data in pool:
        requests['PoolID'].append(data['poolID'])
        requests['RowID'].append(data['rowPools'])
        requests['ColumnID'].append(data['colPools'])

    return requests


# Write a dictionary to a CSV
def writeCSV(filename, sample):
    # Defining a dictionary for the keys of csv, probably more effective method
    sample_keys = set().union(*(d.keys() for d in sample))
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sample_keys)
        writer.writeheader()
        for data in sample:
            writer.writerow(data)


# Display pools in a readable manner to compare with paper
def printPools(pools):
    # Print each pool and the length
    # Display 'x' for each item in the pool to see if it is ordered
    # print(pools)
    # Each pool is a dictionary with row and column pools
    # Print item in each row pool
    print("Samples in row pools: ")
    for pool in pools[0]['rowPools']:
        for sample in pool:
            print("x ", end='')
        print("")

    print("Samples in col pools: ")
    for pool in pools[0]['colPools']:
        for sample in pool:
            print("x ", end='')
        print("")



def main():
    # Create testing samples and generate pools
    sample = generateSamples(ASYMPTOMATIC, 1, PA)
    # Add symptomatic patient samples
    sample = sample + generateSamples(SYMPTOMATIC, 2, PS)
    genPools = ORGeneratePools(sample, MAXPOOLSIZE, MAXTESTS)

    # Used in writing to CSV this makes the first row equal to the dict keys
    # sample_keys = set().union(*(d.keys() for d in sample))

#    print("Sample Data:", sample)
#    print('Generated pools" ', genPools)

    # requests = returnFunction(sample, genPools)
    # requests_keys = set().union(*(d.keys() for d in requests))

    # Data generated from samples written to sample.csv
    #writeCSV('sample.csv', sample)
    # writeCSV('pools.csv', genPools)

    printPools(genPools)


if __name__ == "__main__":
    main()
