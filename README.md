# Code for  Pooled Ordered Rectangular Testing
Based on paper PORT: Pooled Ordered Rectangular Testing for Improved Public Health Screening  by Terrance E. Boult, Yanyan Zhuang  which  will appear in the 2021 IEEE 9th International Conference on Healthcare Informatics (ICHI). Thanks to supporting project members K. Paulson  C. M. Vander Zanden, A. Nashikkar, N. Windesheim, and S. Zhou   for their contributions/discussions. Espeically K. Paulson and N. Windesheim who both worked on the code development and testing. 

# Installation instructions

```git clone https://github.com/Vastlab/PORT.git```

From the root of the cloned repository:

```
docker build -t $name .
docker run -dp 5000:80 $name
```

The flask container should now be running at http://localhost:5000. The docker application runs on port 5000 by default, to run on a different port you must change the port references in the file PORT/app/templates/upload.html. 

# Usage instructions

Some example files exist on the "examples" page of the now running docker container. You can download these files to test that the application is functioning properly, download from either the webpage or upload a copy from the repository at: ```app/static/downloads/```. Example files also exist at the root of this repository under `examples` this includes examples from the paper and a file with more samples that will give multiple pools in the result.

![paperexamples](https://user-images.githubusercontent.com/75324494/117877932-6bcbf580-b262-11eb-8767-30731768ed54.PNG)

These files should then be uploaded on the tool page. 

![submissionexample](https://user-images.githubusercontent.com/75324494/117878073-96b64980-b262-11eb-8d46-395472d22c05.PNG)

A file containing the ordered pools will be automatically downloaded once you hit submit. If the uploaded file contained large amounts of samples this download could take some time.

When uploading files containing samples they should have the following information: "CurrentProb, Positive, SampleID, InitialProb, UserKey, ProviderID, numTest" 
When the file is uploaded it should look something like this:

![sampleExamples](https://user-images.githubusercontent.com/75324494/117878735-4b506b00-b263-11eb-86ff-6ba08d5d427a.PNG)

Prior to the start of each pool the file will designate what type of testing is to be completed: Single, Ordered Rectangular (PORT), or Individual. An example pool file is located at PORT/examples/largeSamplePools.csv

After testing has been completed on the samples in an ordered rectangular pool our tool also creates a list of the necessary individual tests to be completed. To use this tool upload an excel file containing only the sample names from the tested pool. There should be no other information included in the file, it should look something like this:

![tool2](https://user-images.githubusercontent.com/75324494/117879358-1d1f5b00-b264-11eb-9478-cfae493d2f85.PNG)

When you submit the file you must select the positive rows and columns in a space separated list. Such as Positive Rows: "12 14 15" and Positive Columns: "1 4 5". When you submit this information and the previous csv or excel file a txt file will be automatically downloaded with the samples that need individual testing.

![tool2ex](https://user-images.githubusercontent.com/75324494/117879932-c0707000-b264-11eb-936b-3300f71c8e67.PNG)

![indTests](https://user-images.githubusercontent.com/75324494/117880097-f150a500-b264-11eb-90f3-c26f0dd48d9d.PNG)
