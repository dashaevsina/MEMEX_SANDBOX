import os, yaml, json, random

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml")

###########################################################
# FUNCTIONS ###############################################
###########################################################

# generate search pages and TOC
def formatSearches(pathToMemex):
    with open(settings["template_search"], "r", encoding="utf8") as f1:
        indexTmpl = f1.read()
    dof = functions.dicOfRelevantFiles(pathToMemex, ".searchResults")

    toc = []
    for file, pathToFile in dof.items():
        searchResults = []
        data = json.load(open(pathToFile))
        
        # collect toc
        template = "<tr> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td></tr>"

        linkToSearch = os.path.join("searches", file+".html")
        pathToPage = '<a href="%s"><i>read</i></a>' % linkToSearch
        searchString = '<div class="searchString">%s</div>' % data.pop("searchString")
        timeStamp = data.pop("timestamp")
        tocItem = template % (pathToPage, searchString, len(data), timeStamp)
        toc.append(tocItem)

        # generate the results page
        keys = sorted(data.keys(), reverse=True)
        for k in keys:
            searchResSingle = []
            results = data[k]
            temp = k.split("::::")
            header = "%s (pages with results: %d)" % (temp[1], int(temp[0]))
            for page, excerpt in results.items():
                pdfPage = int(page)
                linkToPage = '<a href="../%s"><i>go to the original page...</i></a>' % excerpt["pathToPage"]
                searchResSingle.append("<li><b><hr>(pdfPage: %d)</b><hr> %s <hr> %s </li>" % (pdfPage, excerpt["result"], linkToPage))
            searchResSingle = "<ul>\n%s\n</ul>" % "\n".join(searchResSingle)
            searchResSingle = generalTemplate.replace("@ELEMENTHEADER@", header).replace("@ELEMENTCONTENT@", searchResSingle)
            searchResults.append(searchResSingle)
        
        searchResults = "<h2>SEARCH RESULTS FOR: <i>%s</i></h2>\n\n" % searchString + "\n\n".join(searchResults)
        with open(pathToFile.replace(".searchResults", ".html"), "w", encoding="utf8") as f9:
            f9.write(indexTmpl.replace("@MAINCONTENT@", searchResults))

    toc = searchesTemplate.replace("@TABLECONTENTS@", "\n".join(toc))
    return(toc)