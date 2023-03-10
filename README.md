# Modular decomposition algorithm

Rough implementation of O(n+m*log(n)) time algorithm for finding the modular decomposition of a given graph.
Based on [this](https://doi.org/10.46298/dmtcs.274) [1] algorithm of McConnell and Spinrad (2000). This implementation
might not have the same time complexity though, since it makes some calls to networkx and uses built in `deque` rather than custom-built doubly-linked lists. I don't have good control over the time complexity of these calls in comparison to what McConnell and Spinrad uses in their proofs. Need to think about it, and possibly re-build parts.

## How to use this code

It suffices to import the function `modularDecomposition` from the file `modularDecomp`, if you just want a modular decomposition of a Networkx-graph. It simply takes an instance of `nx.Graph` and returns a modular decomposition tree T as a `nx.Digraph`. The nodes in T will be frozensets (since they need to be hashable) corresponding to the strong modules of the graph. Each inner node of T has an attribute `'MDlabel'` set to one of the strings `'0'`, `'1'` or `'p'` for series, parallel resp. prime nodes. Obtain these by, say, `T.nodes[v]['MDlabel']`. Note that  `modularDecomposition` will, as a side-effect, add some vertex attributes to your input graph (namely 'cell' and 'cellIdx'). You can remove them if you'd like.

See also the file `paperExGraph.py` for example of use plus a small function for fast end easy visualization of your MD-tree.

## How does it work?

Refer to [1] for a full description of the algorithm but here's a very brief summary:

We're decomposing G=(V, E). Pick some vertex v and find the partition P(G,v) consisting of {v} and all inclusion-maximal modules not containing v. It turns out the quotient graph G/P(G,v) has nice enough structure so that an MD can be found efficiently using just some priority-rules while calculating P(G,v). The MD of G/P(G,v) has the modules of P(G,v) as leafs. We find an MD of each module of P(G,v) recursively, and attach as a subtree in the MD of G/P(G,v).

## How finished is this implementation?

Well. Not so much. But it works as far as I'm aware'(and if it has bugs you'll notice – it's easier to verify that a given labeled tree is an MD of a graph than it is to calculate it). We'll see how much I'll improve it.
