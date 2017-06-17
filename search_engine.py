# Sorting pages according to their ranks
def quicksort(pages,ranks):
    if not pages or len(pages)<=1:
        return pages
    else:
        worse=[]
        better=[]
        pivot=ranks[pages[0]]
        for page in pages[1:]:
            if ranks[page]<=pivot:
                worse.append(page)
            else:
                better.append(page)
            return quicksort(better,ranks)+[pages[0]]+quicksort(worse,ranks)
        
#Perform a search action on a keyword
def ordered_search(index, ranks, keyword):
    pages=lookup(index,keyword)
    return quicksort(pages,ranks)

#Checks whether a link redirects to itself (within kth branch)
def is_reciprocal_link(graph,source,destination,k):
    if k==0:
        if source==destination:
            return True
        return False
    if source in graph[destination]:
        return True
    for node in graph[destination]:
        if is_reciprocal_link(graph,source,node,k-1):
            return True
    return False

#Computes the ranks of each page in the graph
def compute_ranks(graph,k):
    d = 0.8 # damping factor
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                        if not is_reciprocal_link(graph,node,page,k):
                                newrank=newrank+d*(ranks[node]/len(graph[node]))
            newranks[page] = newrank
        ranks = newranks
    return ranks

#The web crawler, which return the web index and the graph (a dictionary where
#each key is a <url> and the value is [a list of pages it links to]
def crawl_web(seed): 
    tocrawl = [seed]
    crawled = []
    graph = {}  
    index = {} 
    while tocrawl: 
        page = tocrawl.pop()
        if page not in crawled:
            content = get_page(page)
            add_page_to_index(index, page, content)
            outlinks = get_all_links(content)
            graph[page] = outlinks 
            union(tocrawl, outlinks)
            crawled.append(page)
    return index, graph

#gets the webpage at a given <url>
def get_page(url):
    try:
        import urllib
        return urllib.urlopen(url).read()
    except:
        return None

#traverses the links on a webpage    
def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1: 
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

#gets all the links on a webpage
def get_all_links(page):
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links

#unio of two lists
def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

#adds a webpage (keywords and url of the page) to the index
def add_page_to_index(index, url, content):
    words = content.split()
    for word in words:
        add_to_index(index, word, url)

#adds keywords and urls associated with them to the index        
def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

#returns a list of urls associated with a keyword
def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None
    
#performs a multi-keyword search    
def multi_keyword_search(index,rank,string):
    keys=string.split()
    search_list=[]
    for word in keys:
        for elem in index[word]:
            for x in search_list:
                if elem[0]== x[0]:
                    x[1]+=1
                else:
                    search_list.append(elem)
    return quicksort(search_list,ranks)

#Creating the index   
index, graph = crawl_web('https://www.dmoz.org/')
ranks = compute_ranks(graph,3)
