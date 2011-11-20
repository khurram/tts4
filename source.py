import sys
from math import sqrt

def savetofile(filename, data):
    f = open(filename, 'w')
    try:
        for person in data:
            f.write("%.8f " % person[1] + person[0] + '\n')    
    finally:
        f.close()
        
def getoutgoing(filename):
    f = open(filename, 'r')
    # Store email sender as key to a list of receivers
    emaildict = {}
    for line in f:
        email = line.strip().split(None, 2)[1:3]
        if email[0] != email[1]:
            emaildict.setdefault(email[0], []).append(email[1])
    return emaildict

def getlenoutgoing(outgoingemails):
    outgoingcount = {}
    for key in outgoingemails.keys():
        outgoingcount[key] = len(outgoingemails[key])
    return outgoingcount

def getingoing(filename):
    f = open(filename, 'r')
    # Store email receiver as key to a list of senders
    emaildict = {}
    for line in f:
        email = line.strip().split(None, 2)[1:3]
        # filter out A->A emails as we don't need them
        if email[0] != email[1]:
            emaildict.setdefault(email[1], []).append(email[0])
    return emaildict

def getall(outgoingemails, ingoingemails):
    nodes = {}
    for key in outgoingemails.keys():
        nodes[key] = 1
    for key in ingoingemails.keys():
        nodes[key] = 1
    return nodes

def getdangling(senders, receivers):
    return dict([(key, True)
        for key in set(senders.keys()+receivers.keys())
        if (key in receivers and key not in senders)
    ])

def getpagerank(nodes, ingoingemails, outgoingcount):
    initialpagerank = {}
    pagerank = {}
    nodecount = len(nodes)
    iterations = 10
    damping = 0.8

    # Initialise pageranks
    for node in nodes.keys():        if not ingoingemails.has_key(node):            ingoingemails[node] = ()        initialpagerank[node] = 1.0 / nodecount
 
    # Calculate pagerank for remaining iterations
    while iterations > 0:        for node in nodes.keys():
            sumgame = 0 
            for sender in ingoingemails[node]:                if outgoingcount.has_key(sender):                    sumgame += initialpagerank[sender] / outgoingcount[sender]
 
            pagerank[node] = ((1 - damping) / nodecount) + (damping * sumgame)

        # Update pageranks            
        for node in pagerank.keys():            initialpagerank[node] = pagerank[node]
 
        iterations -= 1
    return pagerank

def gethits(nodes, ingoingemails, outgoingemails, hubs, authority):
    iterations = 10
    
    # Initialise Hub and Authority scores to 1 for each node
    for node in nodes.keys():
        authority[node] = 1
        hubs[node] = 1
    
    # Calculate Hub and Authority scores for remaining iterations
    while iterations > 0:
        norm = 0

        # Update Authority scores
        for node in nodes.keys():
            if not ingoingemails.has_key(node):
                ingoingemails[node] = ()
            authority[node] = 0
            
            for sender in ingoingemails[node]:
                authority[node] += hubs[sender]
            norm += authority[node] * authority[node]
        
        norm = sqrt(norm)
        
        # Normalise Authority scores
        for node in nodes.keys():
            authority[node] = authority[node] / norm
            
        norm = 0
        
        # Update Hub scores
        for node in nodes.keys():
            if not outgoingemails.has_key(node):
                outgoingemails[node] = ()
            hubs[node] = 0
            
            for receiver in outgoingemails[node]:
                    hubs[node] += authority[receiver]
            norm += hubs[node] * hubs[node]
        
        norm = sqrt(norm)
        
        # Normalise Hub scores
        for node in nodes.keys():
            hubs[node] = hubs[node] / norm

        iterations -= 1
 
if __name__ == '__main__':

    emails = sys.argv[1]

    outgoingemails = getoutgoing(emails)
    outgoingcount = getlenoutgoing(outgoingemails)
    print len(outgoingemails), "Senders"
    
    ingoingemails = getingoing(emails)
    print len(ingoingemails), "Receivers"
    
    dangling = getdangling(outgoingemails, ingoingemails)
    print len(dangling), "Dangling Nodes"

    nodes = getall(outgoingemails, ingoingemails)
    nodecount = len(nodes)
    print nodecount, "Total Nodes"
    
    finalpagerank = getpagerank(nodes, ingoingemails, outgoingcount)
    
    pageranktopten = sorted(finalpagerank.items(), key=lambda(k,v):(v,k))[-10:]
    savetofile("pr.txt", pageranktopten)
    
    hubs = {}
    authority = {}
    gethits(nodes, ingoingemails, outgoingemails, hubs, authority)
    
    hubstopten = sorted(hubs.items(), key=lambda(k,v):(v,k))[-10:]
    savetofile("hubs.txt", hubstopten)
    
    authoritytopten = sorted(authority.items(), key=lambda(k,v):(v,k))[-10:]
    savetofile("auth.txt", authoritytopten)
