# NEW LIBRARIES
import pandas as pd # Pandas Python library
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer) # Sklearn Python library
from sklearn.metrics.pairwise import cosine_similarity # Imports Cosine distance measure (other possibilities:
                                                       # Euclidean and Manhattan)

from sklearn.feature_extraction import text ### The Sklearn library has stopwords of its own, which is a 
            ### frozenset that can be used with the function text.ENGLISH_STOP_WORDS. Additional items can
            ### be added to that list: text.ENGLISH_STOP_WORDS.union(additional_stopwords). 
from nltk.corpus import stopwords ### The NLTK library has its own stopwords package, too (requires 
                ### nltk downloader to be installed). 
                ### NB: Alternatively, stopwords can be removed manually in pre-processing.

import os, json, re, sys # NB: sys module allows code to introspect on the system in which its running
                         # re for regular expressions

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml")
my_stopwords_list = stopwords.words('english') + stopwords.words('french') ### Personalised stopword list 
                            ### combines English and French stopwords. 
my_stopwords_list.extend('op pp ch dun dune ibid cf iv xvi xix xviii xix'.split()) ### Adds any other stopwords.

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

def filterTfidfDictionary(dictionary, threshold, lessOrMore): # This does the filtering with the
                        # parameters dictionary, threshold and lessOrMore.
    dictionaryFilt = {} # Creates the dictionary.
    for item1, citeKeyDist in dictionary.items():
        dictionaryFilt[item1] = {} # Creates a dictionary.
        for item2, value in citeKeyDist.items():
            if lessOrMore == "less": # The 'less' argument
                if value <= threshold: # filters out items that are below the threshold.
                    if item1 != item2:
                        dictionaryFilt[item1][item2] = value
            elif lessOrMore == "more": # The 'more' argument
                if value >= threshold: # filters out items that are above the threshold.
                    if item1 != item2:
                        dictionaryFilt[item1][item2] = value
            else:
                sys.exit("`lessOrMore` parameter must be `less` or `more`") # When the argument is neither
                        # less nor more, the execution of the script stops. Prints an error message on the
                        # screen. When done right, the execution of the script will never stop, but this 
                        # safeguards against mistakes.

        if dictionaryFilt[item1] == {}: # Filtering out items from the dictionary leaves empty items. This
                                        # removes items that hold no information whatsoever.
            dictionaryFilt.pop(item1)
    return(dictionaryFilt) # Results in long json dictionary files.


def tfidfPublications(pathToMemex): # tfidfPublications is the function
    # PART 1: loading OCR files into a corpus
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, ".json") # Gets the dictionary of files with 
                        # OCR results. The .json file extension is not ideal for keeping files separated,
                        # so use a non-existent file extension instead, such as .OCRED, when generating 
                        # the corpus.
    citeKeys = list(ocrFiles.keys())#[:500] # Gets the cite keys from the dictionary, providing more
                                            # freedom for processing the information.    

    print("\taggregating texts into documents...")
    docList   = [] # Creates 2 lists: document list for documents
    docIdList = [] # and a list of Ids of the documents.

    for citeKey in citeKeys: # Loops through the citekyes
        docData = json.load(open(ocrFiles[citeKey])) # Reads every publication one after the other. 
                    # docData loads the json file.
        # IF YOU ARE ON WINDOWS, THE LINE SHOULD BE:
        # docData = json.load(open(ocrFiles[citeKey], "r", encoding="utf8"))
        
        docId = citeKey # docId is a key in the cite key
        doc   = " ".join(docData.values()) # Grabs all of the pages from the loaded json dictionary and 
                                           # merges it.

        # clean doc
        # NB: Place any text pre-processing steps here
        doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc) # word regular expression
        doc = re.sub(r'\W+', ' ', doc) # not word regular expression
        doc = re.sub('_+', ' ', doc) 
        doc = re.sub(r'\d+', ' ', doc) # digit regular expression
        doc = re.sub(' +', ' ', doc)

        # update lists
        docList.append(doc) # Updates 2 lists with ids 
        docIdList.append(docId) # and corresponding complete documents.

    print("\t%d documents generated..." % len(docList))

    # PART 2: calculate tfidf metric for all loaded publications and distances
    # Sklearn and pandas library vectorise the corpus and generate these 2 large matrixes with distances
    # and tf-idf values.
    print("\tgenerating tfidf matrix & distances...") 
    vectorizer = CountVectorizer(ngram_range=(1,1), min_df=5, max_df=0.5, stop_words=my_stopwords_list) 
                                # Functions in Sklearn have a
                                # variety of parameters. The ngram range can be changed to (1,2) to take
                                # bigrams into account. Minimum and maximum document frequency is the 
                                # filterting for the calculations. 
                                # Stopwords can also be used as parameters, i.e.: stop_words=english. 
                                # Stopwords need to be explicitly declared, stopword lists can be merged together.
                                # Min_df=5 integer exludes all the vocabulary that is used in less than 5
                                # texts in the corpus. Max_df=0.5 float is a percentage that excludes all 
                                # the vocabulary that is used in more than half of the text.
    countVectorized = vectorizer.fit_transform(docList) # Takes all of the documents and creates a vector
                        # from all of words. Each text will be mapped against that vector for words. 
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True) # Function has parameters to modify it.
                    # smooth_idf adds extra steps and fits in as a value between 0 and 1. 
    vectorized = tfidfTransformer.fit_transform(countVectorized) # Generates a sparse matrix of the tf-idf
                # values (countVectorized)
    cosineMatrix = cosine_similarity(vectorized) # Creates the matrix of the cosine similarities. 
    # NB: Matrixes as a data format speed up these calculations, but need to be converted into a dictionary.

    # PART 3: saving TFIDF values
    print("\tsaving tfidf data...")
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names())
                # Generates a data frame from the matrix in the table.
    tfidfTable = tfidfTable.transpose() # Transposes the table. The original matrix consists of 
                            # rows and columns, so it needs to be transposed so that each column is 
                            # a document and each row is information on the terms.
    print("\ttfidfTable Shape: ", tfidfTable.shape)
    tfidfTableDic = tfidfTable.to_dict() # Converts it into a dictionary

    tfidfTableDicFilt = filterTfidfDictionary(tfidfTableDic, 0.05, "more") # The filtering function takes
                        # the dictionary, takes the value for filtering (which is just 'more', an extra 
                        # switch to keep the values above or below the threshold).
    pathToSave = os.path.join(pathToMemex, "results_tfidf.dataJson") # Saves the result.
    with open(pathToSave, 'w', encoding='utf8') as f9:
        json.dump(tfidfTableDicFilt, f9, sort_keys=True, indent=4, ensure_ascii=False) # Dumps the results 
                                                                                       # into a json file.

    # PART 3: saving cosine distances
    print("\tsaving cosine distances data...")
    cosineTable = pd.DataFrame(cosineMatrix) #  Generates a data frame from the cosine matrix.
    print("\tcosineTable Shape: ", cosineTable.shape)
    cosineTable.columns = docIdList # Defines columns in cosine table.
    cosineTable.index = docIdList # Defines index in cosine table.
    cosineTableDic = cosineTable.to_dict() # Converts the data frame into a dictionary.

    tfidfTableDicFilt = filterTfidfDictionary(cosineTableDic, 0.25, "more") # Filtering function takes the
                        # cosine table dictionary and the value for filtering ("more" to keep the values above
                        # the threshold).
    pathToSave = os.path.join(pathToMemex, "results_cosineDist.dataJson") # Saves the results.
    with open(pathToSave, 'w', encoding='utf8') as f9: # Dumps the results
        json.dump(tfidfTableDicFilt, f9, sort_keys=True, indent=4, ensure_ascii=False) # into a json file.

tfidfPublications(settings["path_to_memex"])