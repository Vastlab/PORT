"""
This file is used for testing generateSamples and ORGeneratePools from OrderedPooledTesting and writing this data to
files.
"""

from OrderedPooledTesting import generateSamples, ORGeneratePools
import csv


FILENAME = 'testing.txt'
ASYMPTOMATIC = 100
SYMPTOMATIC = 20
PA = 0.01
PS = 0.2
MAXPOOLSIZE = 32
MAXTESTS = 16

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
    writeCSV('sample.csv', sample)
    writeCSV('pools.csv', genPools)


if __name__ == "__main__":
    main()
