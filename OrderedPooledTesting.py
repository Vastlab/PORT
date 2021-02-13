"""
*
* NOTICE: This software was produced as independent effort and under C-time (CIVIC)
* in support of open source community of Safe Paths and to help the greater community.

* Author1: Keith Paulson
* kpaulso2@uccs.edu
* kpaulson@mitre.org

* Author2: Terrance Boult
* tboult@uccs.edu

* NOTE: The first author’s affiliation with The MITRE Corporation is provided for identification purposes only,
* and is not intended to convey or imply MITRE’s concurrence with, or support for, the positions, opinions,
* or viewpoints expressed by the author.
* ** Need to update disclaimer for software vice publication.  Will be licensed under MIT license once approved.
*
* (c) 2020 The MITRE Corporation. All Rights Reserved.
* Applied for Public Release Open Source Contribution Case No:  20-01673
* Pending Approval/Under Review will be released under MIT License
*
* (c) 2020 University of Colorado.  All Rights Reserved.


* PROJECT: SAFE PATH forked to support UCCS COVID-19
*
* FILE:Sample_pool.py
* AUTHOR: Keith Paulson
* DESCRIPTION: Initial sample pooling application.  This is an MVP that focuses on the ability to create pools
*              The following should represent minimal viable product.  It works with both combinational matrix
*              and binary search patterns to optimize finding definitive test results in a single round, when possible
* 1) generateSamples - creates data of samples on defined format
* 2) generateTruth - creates truth data (infected/not) for samples
* 3) generatePools - generates pools for execution of all samples  <-- We are here....
* 4) generatePlates - generates plate for testing
* 5) runPlate - runs test on a Plate
* Get results, rinse and repeat as needed.
"""
import uuid
import random
import numpy as np

from typing import Dict, List, Any, Union
from operator import itemgetter

TBdebug=0
#TBdebug=0  #No debug info


# TODO shift things to libraries or __init__
# TODO shift to Object / Class oriented style if people like better
# TODO use PEP8 standards, mixing  j-standards in naming conventions
def decision(probability):
    return random.random() < probability


def generateTruth(samples):
    """
          generates truth data is sample infected
          :param samples: samples to generate truth for
          :return: truth
          """
    truth = [{'SampleID': sample['SampleID'],
              'Truth': decision(sample['CurrentProb'])} for sample in samples]
    return truth


def generateSamples(countSamples, ProviderID, infectionRate):
    """
       generates samples to be used.
       :type countSamples: int
       :param countSamples: How many samples generated
       :param ProviderID: The ID of the provider
       :param infectionRate: the rate of infection
       :return: samples
       """
    # Password is likely hashed or something in testing providers system
    # We would need to develop protocol of exchange.
    # Most likely end user would scan bar code / QR code from provider into system
    # This would locally be used to pull results without linking
    # the person to the sample.
    samples = [{
#        'SampleID': "i"+str(index)+"-"+str(infectionRate)+"-"+uuid.uuid4().hex,
                'SampleID': "i"+str(index)+"-"+str(infectionRate),
        'ProviderID': ProviderID,
        'UserKey': uuid.uuid4().hex,
        'InitialProb': infectionRate,
        'CurrentProb': infectionRate,
        'numTest': 1,
        'Positive': "Unknown"} for index in range(countSamples)]


    # Check each sample if there is an override
    # need to make more pythonesque later

    for index in range(0, countSamples-1):
        if checkIR(samples[index]['InitialProb'],
                   samples[index]['SampleID'],
                   samples[index]['ProviderID'],
                   samples[index]['UserKey']) != samples[index]['InitialProb']:
            samples[index]['InitialProb']=checkIR(samples[index]['InitialProb'],
                                                  samples[index]['SampleID'],
                                                  samples[index]['ProviderID'],
                                                  samples[index]['UserPass'])
            samples[index]['CurrentProb'] = samples[index]['InitialProb']
    if(TBdebug>0):
        print("Generated ",len(samples)," samples");
    return samples



def checkIR(ir, user, password, provider):
    # for now just return IR
    """
              generates overrides to be used.
              :param ir: Current infection rate
              :param user: SampleID
              :param password: Hash or some validation
              :param provider ID
              :return: updated_ir
              """
    # TODO API to lookup provider location and IR if null or enmumaration
    # TODO API to lookup in SAFEPATH if user permitted 
    return ir

import pdb
import math
def mceil(x):
    "My ceiling type function for easy chagen to ceil or not"
    return math.ceil(x)
#    return (x)


def ExpectedSinglePoolCost(samples,maxPoolSize):
    """
           Estiamte expected cost for single pool testing of the next few items  minimies cost even if its a single item

           :param cnt: total actual samples used
           :param samples:  the actual samples 

           :return: list with expected total cost if this per-item applied everywhere, and the number of items in single pool

           """
    minval = 1000
    cnt=1
    mincnt = 1;
    rowsum =0
    tcost = 0
    if(maxPoolSize > 8): maxPoolSize=8
    sprob = samples[0]['CurrentProb']    
    for sample in  samples:
        if(sample['CurrentProb'] != sprob):
            break
        ecost = 1/cnt + (1-pow((1-sprob),cnt))
        if(ecost < minval):
            minval = ecost
            mincnt = cnt;
        if(TBdebug > 3):        print("IN single", cnt, ecost, minval, mincnt, sample['CurrentProb'])
        cnt += 1
        if(cnt >= maxPoolSize):
            break
        #estimate  per sample average cost
    return [minval, mincnt]

    
    


def ExpectedORCost(prob,nrows,ncols,cnt,nsamples):
    """
           Estiamte expected cost of an Ordered Ragged pool, based on formula in paper XXXX
    TC(r,c) = r + c + \left({\sum_{i=1}^r \Big( 1-\prod_{k=1}^c(1-p_{i*c+k})\Big) }\right) *
    \left({\sum_{i=1}^c \Big( 1-\prod_{k=1}^r(1-p_{i+k*r})\Big) }\right)

           :param prob: 2d array of probility for the cnt samples
           :param nrows: number of rows in array
           :param ncols: number of colums in array
           :param cnt: total actual samples used
           :param nsamples:  the total number of samples

           :return: expected total cost if this per-item applied everywhere

           """

#    if ((nrows < 2) or  (ncols < 2)):
#        return 1    
    
    expectrows = 0
    if((TBdebug > 2) and (nrows == 6) and (ncols == 20)  ):
        print ("Prob for ", nrows,ncols,"shape", np.shape(prob)," prod= ",prob);
    for row in range( 0, nrows,1):
        colprod = 1
        for col in range( 0, ncols,1):        
            colprod *= (1-prob[row][col])
            if((TBdebug > 4) and (nrows == 5) and (ncols == 20)  ):
                print (" include prob ", prob[row][col]," for ", row,col," prod= ",colprod);            
        if((TBdebug > 5) and (nrows == 6) and (ncols == 19)  ):
            print ("OR for", nrows,ncols," 1-cprod= ",1-colprod);
        expectrows +=  (1-colprod)
    if((TBdebug > 2) and (nrows == 6) and (ncols == 19)  ):
        print ("erows", nrows,ncols," 1-cprod= ",expectrows);

    expectcols = 0    
    for col in range( 0, ncols,1):        
        rowprod = 1
        for row in range( 0, nrows,1):
            rowprod *= (1-prob[row][col])
            if((TBdebug > 4) and (nrows == 6) and (ncols == 19)  ):
                print (" include prob ", prob[row][col]," for ", row,col," rprod= ",rowprod);            
        if((TBdebug > 4) and (nrows == 6) and (ncols == 19)  ):
            print ("OR for", nrows,ncols," 1-cprod= ",1-rowprod);
        expectcols +=  (1-rowprod)
    if((TBdebug > 2) and (nrows == 6) and (ncols == 19)  ):
        print ("ecols", nrows,ncols," 1-cprod= ",expectcols);
        
#we add +1 since we are using 0 based rows/columns so have one more expeced
#    tcost = (nrows+1 + ncols+1 + mceil(expectrows+1)* mceil(expectcols+1))
#    print ("OR Ecost ",cnt,nrows+1,ncols+1,mceil(expectrows+1), mceil(expectcols+1),tcost,tcost/cnt,tcost/cnt*nsamples)
#    ncols += 1
    tcost = (nrows  + ncols  + mceil((expectrows))* mceil(expectcols+1))
    if(TBdebug > 2):    print ("OR for", nrows,ncols," Ecost= ",tcost, "cnt=", cnt, "int rows,cols", mceil(expectrows), mceil(expectcols+1),tcost,tcost/cnt,tcost/cnt*nsamples)
    return tcost
    
    
    

def ORGeneratePools(samples, maxPoolSize, maxTests):
    """
           generates optimized Ordered ragged pools  
           :param samples: Current samples requested
           :param maxPoolSize: The maximum pool size
           :param maxTests: ??
           :return: pools
           """
    if(TBdebug > 0):        print("Doring Ordered Rectangle with ", len(samples)," samples")
#    pdb.set_trace()    
#    return;
    sortedsamples =     sorted(samples, key=itemgetter('CurrentProb'),reverse=True)
#    sortedsamples =     sorted(samples, key=itemgetter('SampleID'),reverse=True)      #simulate random order
#    maxsum = 1.0
#uncomment so maxsum=0, to ignore maxsum for rows.. formula's don't see right yet     
    maxsum = 0.0    
    startpos = 0;
    pools = []
    endpos =  len(sortedsamples)
    nsamples = endpos
    mincnt=1
    while(startpos < endpos):
        minval = nsamples*10;
        minlocal = 10000;        
        minc=minr=-1;
        if(TBdebug > 2):        print("Start search between ", startpos,endpos)
#        if(startpos < 10):
#            pdb.set_trace()
#       if prob is > .333  ordered is not more efficient so don't bother and let it fall abck to individual testing
        if(sortedsamples[startpos]['CurrentProb'] < .333):
             for nr in range( 2, maxPoolSize,1):
                 for nc in range( 2, maxPoolSize,1):
                     prob = np.zeros((nr,nc))
                     rowsum=0
                     col=0
                     row=0
                     cnt=0;
                     for row in range( 0, nr,1):
#                         cnt -= 1                         
                         for col in range( 0, nc,1):
                             if(startpos+cnt < endpos):
                                 sample = sortedsamples[startpos+cnt]
                             else:
                                 row=nr
                                 col=nc
                                 break; 
                             prob[row][col] = sample['CurrentProb']
                             cnt += 1

# older code from when we were testing if rowsum mattered.. it does not
#                      for sample in sortedsamples[startpos:endpos]:
#                          if (col < nc):
#                              rowsum += sample['CurrentProb']
#                              if (maxsum >0 and rowsum >= maxsum):
#                                  if(row > nr):
#                                      if((TBdebug > 2) ):                                 
#                                          print("row too full ", row, col, prob[row][col],cnt,rowsum,maxsum)                                     
#                                      break                        
#                                  row += 1
#                                  rowsum = sample['CurrentProb']
#                              prob[row][col] = sample['CurrentProb']
#                              cnt += 1
# #                             if(TBdebug > 3):
#                              if((TBdebug > 2) and (nr == 7) and (nc == 20)  ):                                 
#                                  print("Fill ", row, col, prob[row][col],cnt,rowsum,maxsum)
# #                             if((TBdebug > 2) and (nr == 7) and (nc == 20) and (row == 5) and (col==14) ):
# #                                 pdb.set_trace();

#                              col += 1
#                          else:
#                              #if we filled this rectangle as full as it goes, so break from loop over using samples
#                              row += 1
#                              if(row >= nr):
#                                  row -= 1;
#                                  break
#                              rowsum = sample['CurrentProb']
#                              col = 0
#                              prob[row][col] = sample['CurrentProb']
#                              if((TBdebug > 2) and (nr == 7) and (nc == 20)  ):                                 
#                                  print("rFill ", row, col, prob[row][col],cnt,rowsum,maxsum)
#                              cnt += 1

                     if((TBdebug > 2) and (nr == 6) and (nc == 20)  ):                                 
                         print("Filled  ", nr, nc, "cnt", cnt,  "shape", np.shape(prob), "prob =", prob)
                                 
                     #when here we have a fillled prob matrix so can compute expected cost of this design.
                     tcost = ExpectedORCost(prob,nr,nc,cnt,nsamples)
                     ecost = tcost/cnt*nsamples
                     if(TBdebug > 2):                             
                                 print("rT/Ecost ", tcost," ", ecost,"for  row, col",nr,nc,cnt,nsamples)                     
                     if(ecost < minval):
                         if(TBdebug > 2):                             
                                 print("New min  ", ecost," ", math.ceil(tcost),"for  row, col",nr,nc,cnt,nsamples)                                              
                         minval = ecost
                         minlocal = math.ceil(tcost)
                         minr = nr
                         minc = nc
                         mincnt = cnt;

        scost = ExpectedSinglePoolCost(sortedsamples[startpos:endpos],maxPoolSize)
        if(TBdebug > 1):
            print("single pool returns", scost )
            print ("OR Min " ,minlocal, "at ", minr,minc,"Expected=", minval,"Cnt = ", mincnt, "per-item", minlocal / (mincnt))
        if( (scost[0] <  minlocal / (mincnt))
            or ( minlocal / mincnt > 1 )
            or minr < 0 
        ):
            if(TBdebug > 0):            print("single wins with ", scost, minlocal / (mincnt+1) )
            #if single pool cost is > 1, then run as indivisual
            if(scost[0] > .97) :
                if(TBdebug > 1): print("IndTesting", scost, minlocal / (mincnt+1) )
                sprob =  sortedsamples[startpos]['CurrentProb']
                mincnt = 0
                #If this  probability needs to be independetely tested,  collect all samples at this prob
                for sample in sortedsamples[startpos:endpos]:
                    if(sample['CurrentProb'] == sprob):
                        pools.append({'type': "IND",
                                      'poolID': uuid.uuid4().hex,
                                      'Pool': [sample['SampleID']],
                                      'PoolTest': 1,
                                      'ExpectedCost': 1,
                                      'SampleTest': 1
                        })
                        mincnt += 1                        
                    else:
                        break;
            else:
            #do single pool
                mincnt = scost[1];
                poolit=[]
                for sample in sortedsamples[startpos:startpos+mincnt]:
                        poolit.append(sample['SampleID'])                
                pools.append({'type': 'SINGLE',
                              'poolID': uuid.uuid4().hex,
                              'rowPools': poolit,
                              'colPools': False,
                              'Pool': poolit,
                              'PoolTest': 0,
                              'ExpectedCost': mincnt,
                              'SampleTest': mincnt
                              })
            startpos += mincnt;                
        else:
            if(TBdebug > 0): print("OR wins. Doing design with ", minr,minc )            
            #Have minimum expected cost design, now use it to compute sample pool row and coluns
            prob = np.zeros((minr,minc))
            rowsum=0
            col=0
            row=0
            cnt = 0
            rows = []
            cols = []
            poolit = []
            rows = [[] for _ in range(minr)]
            cols = [[] for _ in range(minc)]


            for sample in sortedsamples[startpos:endpos]:
                if (col < minc):
                    rowsum += sample['CurrentProb']
                    #if row has too high an expected value then jump to next row, rows are initally zero so pre and post are zero
                    if (maxsum >0 and rowsum > maxsum):
                        rowsum = 0;
                        row += 1
                        if(row >= minr):
                            break                    
                    rows[row].append(sample['SampleID'])
                    cols[col].append(sample['SampleID'])
                    poolit.append(sample['SampleID'])
                    col += 1
                    cnt += 1
                else:   
                    row += 1
                    #if we filled this rectangle as full as it goes, so break from loop over using samples
                    if(row >= minr):
                        break
                    col = 0
                    rows[row].append(sample['SampleID'])
                    cols[col].append(sample['SampleID'])
                    poolit.append(sample['SampleID'])
                    rowsum = sample['CurrentProb']
                    cnt += 1                
            #filled in rows, columns so update the pools
    #        pdb.set_trace()
            pools.append({'type': "ORCOMBO",
                          'poolID': uuid.uuid4().hex,
                          'rowPools': rows,
                          'colPools': cols,
                          'Pool': poolit,
                          'PoolTest': len(rows) + len(cols),
                          'ExpectedCost': minlocal,
                          'SampleTest': cnt
            })
            #advance in the sorted list, as we may not have used all point yet
            startpos += cnt;
    if(TBdebug > 2):    print("Restart with ", startpos)
    return pools
                 

                        



def generatePools(samples, maxPoolSize, maxTests):
    """
           generates pools to be used.
           :param samples: Current samples requested
           :param maxPoolSize: The maximum pool size
           :return: pools
           """
    # TODO: update to reflect real saddle points and prob distros
    #        these are reasonable first pass assumptions
    # The following logic is applied
    # Combinational Pools pools established first -- under 11.1111% rates
    # This allows 3 x 3 square with 1 positive
    # Please note: binary pools are **always** more computationally efficient.
    # Combo pools are easier to pipet.
    # Pipetting think of each pool  as row/columns in a square.
    combMaxRate = float(1.00 / 9.00)
    #    and  3 or more tests remain possible for sample
    combMaxRound = maxTests - 3
    comb = []

    # Binary Search / Halving pools second -- under 21% rates
    # This allows 50% hinge with 3 pool size.
    binMaxRate = .21
    #    and  2 or more tests remain possible for sample
    binMaxRound = maxTests - 2
    bin_P = []
    # Individual Pools last above bin rates
    #    or only 1 test remains for sample.

    ind = []
    # This can be made more efficient, but ok for now
    # This is logic for combo squares
    # It should be broken out to its own function
    minsquare = 3
    combMaxRate = float(1.00 / float(minsquare * minsquare))
    cursquare = minsquare
    for sample in samples:
        if sample['CurrentProb'] < combMaxRate and sample['numTest'] <= combMaxRound:
            comb.append(sample)
            comb = sorted(comb, key=itemgetter('CurrentProb'))
        elif sample['CurrentProb'] < binMaxRate and sample['numTest'] <= binMaxRound:
            bin_P.append(sample)
            bin_P = sorted(bin_P, key=itemgetter('CurrentProb'))
        elif sample['CurrentProb'] >= binMaxRate or sample['numTest'] > binMaxRound:
            ind.append(sample)
    pools = []

    popCount = cursquare * cursquare
    count = 0
    combopool = []
    neg_prob = 1.0
    trivial_estimate = 0.0
    # we keep adding to square while probaility is less than 1 and pool size threshold not met
    while (len(comb) > popCount - count and cursquare <= maxPoolSize):
        # I can generally make rectangles up to the square size.
        while count < popCount and trivial_estimate < 1:
            item = comb.pop(0)
            neg_prob *= (1.0 - item['CurrentProb'])
            trivial_estimate += item['CurrentProb']
            combopool.append(item)
            count += 1
        # I permit jagged rectangle with a caveat, I don't want to add a row / column with less than 3 items
        while ((count-1) % cursquare < 2 and len(comb)>0):
            # I decide to expand these even if trivial prob says no
            item = comb.pop(0)
            neg_prob *= (1.0 - item['CurrentProb'])
            trivial_estimate += item['CurrentProb']
            combopool.append(item)
            count += 1
        # This makes assumptions that are not 100% valid.  That is there are no major prob jumps.
        cursquare += 1
        # I want to have each added column with at least
        if (trivial_estimate < 1.0 and cursquare <= maxPoolSize):
            # I make assumption based on trivial estimated probability I can expand my rectangle to next largest square.
            popCount = cursquare * cursquare
        else:
            # We have our maximum square create the pools
            # TODO add backtrack to previous square if prob too high to address assumption
            cursquare -= 1
            if (len(combopool) != cursquare*cursquare):
                # we have a rectangle
                cursquare -= 1

            # TODO change this as it is a bad practice, but is easier to understand
            count = 0
            rows = []
            cols = []
            poolit = []
            # we populate the square
            while count < cursquare:
                rows.append([])
                cols.append([])
                count += 1
            count = cursquare * cursquare
            # and now the rectangle
            while (count < len(combopool)):
                rows.append([])
                count += cursquare
            count=0
            for item in combopool:
                col = int(count % cursquare)
                row = int(count / cursquare)
                rows[row].append(item['SampleID'])
                cols[col].append(item['SampleID'])
                poolit.append(item['SampleID'])
                count += 1

            pools.append({'type': "COMBO",
                          'poolID': uuid.uuid4().hex,
                          'rowPools': rows,
                          'colPools': cols,
                          'Pool': poolit,
                          'PoolTest': len(rows) + len(cols),
                          'SampleTest': len(combopool),
                          'AllNeg_Prob': neg_prob,
                          'Possion': trivial_estimate
                          }
                         )
            # reset and get next one
            count = 0
            trivial_estimate = 0.0
            neg_prob = 1.0
            combopool = []
            cursquare = minsquare
            popCount = cursquare * cursquare
    # Combinational pools will target identification of 1 negative results in a square
    # Combinational pools will **cost** two rounds of testing per sample
    # Binary Search will target identification of 50% negative results
    # Create Binary Pools
    # Left-over Comb pools are added to binary
    bin_P = comb + bin_P
    count = 0
    binpool = []
    neg_prob = 1.0
    curbin = 0
    minbin = 4

    while len(bin_P) > minbin - count and curbin < maxPoolSize:
        item = bin_P.pop(0)
        neg_prob *= (1.0 - item['CurrentProb'])
        binpool.append(item)
        count += 1
        # This makes assumptions that are not 100% valid.  That is there are no major prob jumps.
        curbin += 1
        if not((neg_prob * float(1 - item['CurrentProb'])) > .50 and (len(bin_P) > 1) and curbin < maxPoolSize):
            # We have our maximum bin pool
            myPool = []
            for item in binpool:
                myPool.append(item['SampleID'])
            pools.append({'type': "BIN",
                          'poolID': uuid.uuid4().hex,
                          'Pool': myPool,
                          'PoolTest': 1,
                          'SampleTest': len(myPool)
                          }
                         )
            # reset and get next one
            count = 0
            curbin = 0
            binpool = []
            neg_prob = 1.0

    # Individual
    ind = bin_P + ind
    for item in ind:
        pools.append({'type': "IND",
                      'poolID': uuid.uuid4().hex,
                      'Pool': [item['SampleID']],
                      'PoolTest': 1,
                      'SampleTest': 1}
                     )

    return pools
def CurrentWell(well, MaxCols, MaxRows):
    col = (well % MaxCols) - 1
    row = int((well-1) / MaxCols)
    if col < 0:
        col = MaxCols - 1
    return (col, row)

# TODO generate plate is an ideal candidate for dynamic program
# Knapsack
# Integer weights (pool size) and value = weight (so we maximize value when all wells filled)


def generatePlates(pools, plateWellCount, maxPlate):
    """
        generates plates to be used.
               :param pools: Current pools
               :param plateWellCount: Count of Wells on Plate
               :return: PLATES
    """
    # TODO control behavior of testing
    # COMBO must run two RNA Sequence test
    # per pool
    comboTest = 2
    # BINARY must run two RNA Sequence test
    # per pool
    binaryTest = 2
    # Indvidual must run 2 RMA Sequence test
    # and one verification test
    # per pool
    indTest = 3
    # Reserve plate requires positive / negative samples
    # on each plate as controls
    ctrlTest = 2


    # Well count on plates
    # 96 is 12 x 8
    # 348 is also an option
    # 24 x 16
    if plateWellCount == 96:
        MaxCols = 12
        MaxRows =8
    elif plateWellCount == 348:
        MaxCols = 24
        MaxRows = 16
    else:
        # I have no idea so just make three very long row.
        MaxCols=plateWellCount / 3
        MaxRows=3
    myPlates=[]
   # Easiest to operate with different pools
    (combo, binary, ind) = separatePools(pools)
    # We are humans deal
    plate = 1
    well = 1

    myplate = [[{} for i in range(MaxRows)] for j in range(MaxCols)]

    if(TBdebug < 1): print(myplate)
    # TODO Routine for storing samples on plates
    #      This would be useful but we need data from providers
    # TODO handle maxPlate:  this is exhaustive
    for pool in combo:
        fit=True
        if well == 1:
            (col,row)=CurrentWell(well,MaxCols,MaxRows)
            ctrl= 0
            while ctrl < ctrlTest:
                (col, row) = CurrentWell(well, MaxCols, MaxRows)
                myplate[col][row]={
                    'pool_type': "CTRL_POS",
                    'pool_id': 'CTRL_POS',
                    'pool_row': False,
                    'pool_pos': 0,
                    'test_type': 0}
                well+= 1
                (col, row)=CurrentWell(well, MaxCols, MaxRows)
                myplate[col][row] = {'pool_type': 'CTRL_NEG',
                                     'pool_id': 'CTRL_NEG',
                                     'pool_row': False,
                                     'pool_pos': 0,
                                     'test_type': 1}
                ctrl+= 2
                well+= 1
        (col, row) = CurrentWell(well, MaxCols, MaxRows)
        if well + (pool['PoolTest'] * comboTest) <= plateWellCount:
            pool_type=pool['type']
            pool_id=pool['poolID']
            pool_row=True
            pool_pos=0
            # We can populate on single plate
            for element in pool['rowPools']:
                ctrl = 0
                while ctrl < comboTest:
                    (col, row) = CurrentWell(well, MaxCols, MaxRows)
                    myplate[col][row] = {'pool_type': pool_type,
                                         'pool_id': pool_id,
                                         'pool_row': pool_row,
                                         'pool_pos': pool_pos,
                                         'test_type': ctrl}
                    well += 1
                    ctrl += 1
                pool_pos += 1

            pool_row = False
            pool_pos = 0
            for element in pool['colPools']:
                ctrl = 0
                while ctrl < comboTest:
                    (col, row) = CurrentWell(well, MaxCols, MaxRows)
                    myplate[col][row] = {'pool_type': pool_type,
                                         'pool_id': pool_id,
                                         'pool_row': pool_row,
                                         'pool_pos': pool_pos,
                                         'test_type': ctrl}
                    well += 1
                    ctrl += 1
                pool_pos += 1

            if well == plateWellCount:
                myPlates.append(myplate)
                plate += 1
                well = 1
                myplate = [[{} for i in range(MaxRows)] for j in range(MaxCols)]

        else:
            fit=False
            while len(binary) > 0 and well + binaryTest <= plateWellCount:
                bin_pool=binary.pop()
                ctrl=0
                while ctrl < binaryTest:
                    (col, row) = CurrentWell(well, MaxCols, MaxRows)
                    myplate[col][row] = {'pool_type': bin_pool['type'],
                                         'pool_id': bin_pool['poolID'],
                                         'pool_row': False,
                                         'pool_pos': 0,
                                         'test_type': ctrl}

                    well += 1
                    ctrl += 1

            while len(ind) > 0 and well+indTest <= plateWellCount:
                ind_pool=ind.pop()
                ctrl = 0
                while ctrl < indTest:
                    (col, row) = CurrentWell(well, MaxCols, MaxRows)
                    myplate[col][row] = {'pool_type': ind_pool['type'],
                                         'pool_id': ind_pool['poolID'],
                                         'pool_row': False,
                                         'pool_pos': 0,
                                         'test_type': ctrl}
                    well += 1
                    ctrl += 1
            myPlates.append(myplate)
            plate += 1
            well = 1
            myplate = [[{} for i in range(MaxRows)] for j in range(MaxCols)]
    while (len(binary) > 0 ):
        if well == 1:
            (col, row) = CurrentWell(well, MaxCols, MaxRows)
            ctrl = 0
            while ctrl < ctrlTest:
                (col, row) = CurrentWell(well, MaxCols, MaxRows)
                myplate[col][row] = {
                    'pool_type': "CTRL_POS",
                    'pool_id': 'CTRL_POS',
                    'pool_row': False,
                    'pool_pos': 0}
                well += 1
                (col, row) = CurrentWell(well, MaxCols, MaxRows)
                myplate[col][row] = {'pool_type': 'CTRL_NEG',
                                     'pool_id': 'CTRL_NEG',
                                     'pool_row': False,
                                     'pool_pos': 0}
                ctrl += 2
                well += 1
        (col, row) = CurrentWell(well, MaxCols, MaxRows)
        if well + binaryTest <= plateWellCount:
            pool=binary.pop()
            pool_type = pool['type']
            pool_id = pool['poolID']
            pool_row = False
            pool_pos = 0
            ctrl = 0
            while ctrl < binaryTest:
                (col, row) = CurrentWell(well, MaxCols, MaxRows)
                myplate[col][row] = {'pool_type': pool['type'],
                                     'pool_id': pool['poolID'],
                                     'pool_row': False,
                                     'pool_pos': 0,
                                     'test_type': ctrl}

                well += 1
                ctrl += 1
            if well == plateWellCount:
                myPlates.append(myplate)
                plate += 1
                well = 1
                myplate = [[{} for i in range(MaxRows)] for j in range(MaxCols)]
        else:
            myPlates.append(myplate)
            plate += 1
            well = 1
            myplate = [[{} for i in range(MaxRows)] for j in range(MaxCols)]
    while (len(ind) > 0 ):
        if well == 1:
            (col, row) = CurrentWell(well, MaxCols, MaxRows)
            ctrl = 0
            while ctrl < ctrlTest:
                (col, row) = CurrentWell(well, MaxCols, MaxRows)
                myplate[col][row] = {
                    'pool_type': "CTRL_POS",
                    'pool_id': 'CTRL_POS',
                    'pool_row': False,
                    'pool_pos': 0}
                well += 1
                (col, row) = CurrentWell(well, MaxCols, MaxRows)
                myplate[col][row] = {'pool_type': 'CTRL_NEG',
                                     'pool_id': 'CTRL_NEG',
                                     'pool_row': False,
                                     'pool_pos': 0}
                ctrl += 2
                well += 1
        (col, row) = CurrentWell(well, MaxCols, MaxRows)
        if well + indTest <= plateWellCount:
            pool=ind.pop()
            pool_type = pool['type']
            pool_id = pool['poolID']
            pool_row = False
            pool_pos = 0
            ctrl = 0
            while ctrl < indTest:
                (col, row) = CurrentWell(well, MaxCols, MaxRows)
                myplate[col][row] = {'pool_type': pool['type'],
                                     'pool_id': pool['poolID'],
                                     'pool_row': False,
                                     'pool_pos': 0,
                                     'test_type': ctrl}

                well += 1
                ctrl += 1
            if well == plateWellCount:
                myPlates.append(myplate)
                plate += 1
                well = 1
                myplate = [[{} for i in range(MaxRows)] for j in range(MaxCols)]
        else:
            myPlates.append(myplate)
            plate += 1
            well = 1
            myplate = [[{} for i in range(MaxRows)] for j in range(MaxCols)]
    if well > 1:
        myPlates.append(myplate)
        plate += 1

    return myPlates





def separatePools(pools):
    binary= []
    combo= []
    ind= []
    for pool in pools:
        if pool['type'] == 'COMBO':
            combo.append(pool)
        elif pool['type'] == 'ORCOMBO':
            combo.append(pool)
        elif pool['type'] == 'BIN':
            binary.append(pool)
        elif pool['type'] == 'SINGLE':
            binary.append(pool)            
        elif pool['type'] == 'IND':
            ind.append(pool)
    return (combo,binary,ind)

def notCompletedTest(samples):

    return False


def updateSamples():
    return ()


def runPlate():
    return ()


def displaySampleMetrics():
    return ()


def displayPoolMetrics(pools, current_round,truthdict):
    print("Round ", current_round)
    countCOMBO = 0
    countORCOMBO = 0
    countSINGLE = 0        
    countBIN = 0
    countIND = 0
    countUNK = 0
    countSample = 0
    countPool = 0
    ExpectedCost = 0
    for pool in pools:
        if pool['type'] == "COMBO":
            countCOMBO += 1
        elif pool['type'] == "ORCOMBO":
            ExpectedCost += pool['ExpectedCost']           
            countORCOMBO += 1
        elif pool['type'] == "SINGLE":
            ExpectedCost += pool['ExpectedCost']           
            countSINGLE += 1
        elif pool['type'] == "IND":
            ExpectedCost += 1
            countIND += 1
        elif pool['type'] == "BIN":
            countBIN += 1
        else:
            countUNK += 1
        countPool += pool['PoolTest']
        countSample += pool['SampleTest']
        
        
    print("===========================")
    print("\t Combination Matrices Pools: ", countCOMBO)
    print("\t Ordered Rectangular Pools: ", countORCOMBO)
    print("\t Single Pools: ", countSINGLE)        
    print("\t Binary Search Pools: ", countBIN)
    print("\t Individual: ", countIND)
    if countUNK > 0:
        print("\t Unknown: ", countUNK)
    if pool['type'] == "ORCOMBO" or pool['type'] == "SINGLE":
        actual=ActualORCost(pools,truthdict)
        print("\t Total OR Pooled Testing:  expected cost ", ExpectedCost, "and actual cost", actual, "for ", countSample, " samples for actual per sample saving of ",countSample/actual )        
    else:
        print("\t Total Pooled Testing: ", countPool, " for ", countSample, " samples")

    return ()


def displayPlatesMetrics():
    return ()


def displayResults():
    return ()

def ActualORCost(pools,truthdict):
    cnt = 0;
    for pool in pools:
        rowcnt=0
        colcnt=0
        if(pool['type'] == "ORCOMBO"):
            for row in pool["rowPools"]:
                ispos=False;
                for sampleid in row:
                    ispos = ispos or truthdict[sampleid]
                if(ispos): rowcnt += 1;
            for col in pool["colPools"]:
                ispos=False;
                for sampleid in col:
                    ispos = ispos or truthdict[sampleid]
                if(ispos): colcnt += 1;            
            poolcost = len(pool["rowPools"]) + len(pool["colPools"])
            indcost = rowcnt * colcnt
            cnt += poolcost + indcost
        elif (pool['type'] == "SINGLE"):
            poolcost = 1
            ispos=False;
            for sampleid in pool["rowPools"]:
                ispos = ispos or truthdict[sampleid]            
            if (ispos): indcost = pool["SampleTest"]
            else: indcost = 0
            cnt += poolcost + indcost
        elif(pool['type'] == "IND"):
            poolcost = 0
            indcost = pool["SampleTest"]            
            cnt +=  indcost
                
#        print("Pool id",pool["poolID"], pool["PoolTest"], pool["ExpectedCost"],pool["SampleTest"]," actual costs",  poolcost, indcost, poolcost+ indcost,  cnt)

#    print("Actual ORPool random sample cost", cnt)
    return cnt;


# I think I will use in future
# import json
# import pandas as pd
# import numpy as np
# import sqlalchemy
# import requests



def OR_main():
 ###########################################################
 #  Welcome to main ()
 # TODO: data-frames (pandas) are more efficient but I hate using with functions
 # TODO: convert to flask application and microservices (json returns)
 # TODO: integrate with database - MariaDB (sqlalchemy)
 Largetesting=False
 Largetesting=True
 if Largetesting:
     countSamples = 2405
     infectionRate = 0.05
     ProviderID = 1
     samples = generateSamples(countSamples, ProviderID, infectionRate)
     countSamples = 1400
     infectionRate = 0.004
     ProviderID = 2
     samples = samples + generateSamples(countSamples, ProviderID, infectionRate)
     countSamples = 100
     infectionRate = 0.12
     samples = samples + generateSamples(countSamples, ProviderID, infectionRate)
     countSamples = 1000
     infectionRate = 0.08
     ProviderID = 4
     samples = samples + generateSamples(countSamples, ProviderID, infectionRate)
 else:
     #TBtest data
     countSamples = 110
     infectionRate = 0.01
     ProviderID = 1
     samples = generateSamples(countSamples, ProviderID, infectionRate)
     countSamples = 10
     infectionRate = 0.4
     ProviderID = 2
     samples = samples + generateSamples(countSamples, ProviderID, infectionRate)


 # TODO: account for probability breaks/backtrack in samples of combo approach
 # TODO: allow variable infection rates, provider data, and include test error (inconclusive results)
 # TODO: consider number of unique RNA tests (2) required for positive and RNA validation test (1)
 # TODO: add unit test / integration test, etc.
 # TODO: create requirements and build files
 # TODO: MD documentation
 # TODO: too much to think about
 # TODO: Toggle for IND confirmation of positive results.
 # This is a cheat to make faster, should be eliminated once DB in place
 sample2index = {}
 counter = 0
 for i in samples:
     sample2index[i['SampleID']] = counter
     counter += 1

 # TODO: permit override of infection rate that is we guess wrong in samples
 truth = generateTruth(samples)
 truth2index = {}
 counter = 0
 # This is a cheat to make faster, and only used for testing
 for i in truth:
     truth2index[i['SampleID']] = counter
     counter += 1

 #TB: make a dict so we can lookup truth by string
 truthdict  = {truth[i].get('SampleID'): truth[i].get('Truth') for i in range(0, len(truth), 1)}    

 #print(truth)
 # This is the maximum times a sample can be tested. It reflects approximate number of tests possible post-RNA extract
 maxTests = 6
 # An additional 6 RNA extracts can be performed
 # This is the maximum size of pool or those tests that can be combined and still have detection correct
 # Higher numbers theoretically possible with extra cycles during RNA extract
 maxPoolSize = 32
 current_round = 1
 # Well count on plates
 plateWellCount = 96
 # 96 is 12 x 8
 # 348 is also an option
 # 24 x 16
 # maxPlate limits return to this number of plates 0 is infinite
 # TODO add a storage plate option this would allow a plate to store individual samples in addition to pools
 maxPlate = 0
 print("GENERATING samples for testinng ")
 if(TBdebug>8):    
     pools = ORGeneratePools(samples, maxPoolSize, maxTests)
 else: 
     pools = generatePools(samples, maxPoolSize, maxTests)



 displayPoolMetrics(pools, current_round,truthdict)

 # I force all tests for a pool onto a single plate
 plates = generatePlates(pools, plateWellCount, maxPlate)
 plate=plates.pop()
 result = runPlate()
 while notCompletedTest(samples):
     pools = generatePools(samples, maxPoolSize, maxTests)
     displayPoolMetrics(pools, current_round)

     plates = generatePlates(pools, plateWellCount,maxPlate)
     displayPlatesMetrics(plates, current_round)
     current_plate = 1
     for plate in plates:
         displaySampleMetrics(current_round, current_plate, samples)
         result = runPlate(plate, truth, samples, pools, current_round, current_plate)
         displayResults(result, current_plate, current_round)
         samples = updateSamples(samples, plate, pools, result)
         current_plate += 1

     displaySampleMetrics(current_round, current_plate, samples)
     current_round += 1




