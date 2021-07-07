import re
RE_NONTERMINAL = re.compile(r'(<[^<>]*>)')

"""
A set of valid inputs to a program is called a "language"
Grammars are the middle ground between regex and Turing machines. (please do not ask me to elaborate)
A grammar is good at expressing the syntactical structure of an input. We use so-called context-free grammars

# wtf is a grammar
A grammar consists of a start symbol and expansion rules which dictate how symbols can be expanded. e.g.
For example. the following is a grammar for a sequence of two digits:
```wtf
<start> ::= <digit><digit>
<digit> ::= 0|1|2|3|4|5|6|7|8|9
```
Symbols on the left are like variable declarations. <start> is replaced by <digit><digit>, and <digit> can be replaced by 0-9

e.g. arithmetics:
<start>   ::= <expr>
<expr>    ::= <term> + <expr> | <term> - <expr> | <term>
<term>    ::= <term> * <factor> | <term> / <factor> | <factor>
<factor>  ::= +<factor> | -<factor> | (<expr>) | <integer> | <integer>.<integer>
<integer> ::= <digit><integer> | <digit>
<digit>   ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
We can do something like this using lists and strings
"""
# An example of some grammars:
DIGIT_GRAMMAR = {
    "<start>": ["0","1","2","3","4","5","6","7","8","9"]   
}
EXPR_GRAMMAR = {
    "<start>": ["<expr>"],
    "<expr>": ["<term> + <expr>", "<term> - <expr>", "<term>"],
    "<term>": ["<factor> * <term>", "<factor> / <term>", "<factor>"],
    "<factor>": ["+<factor>","-<factor>","(<expr>)","<integer>.<integer>","<integer>"],
    "<integer>": ["<digit><integer>", "<digit>"],
    "<digit>": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
}
URL_GRAMMAR = {
    "<start>":
        ["<url>"],
    "<url>":
        ["<scheme>://<authority><path><query>"],
    "<scheme>":
        ["http", "https", "ftp", "ftps"],
    "<authority>":
        ["<host>", "<host>:<port>", "<userinfo>@<host>", "<userinfo>@<host>:<port>"],
    "<host>":  # Just a few
        ["cispa.saarland", "www.google.com", "fuzzingbook.com"],
    "<port>":
        ["80", "8080", "<nat>"],
    "<nat>":
        ["<digit>", "<digit><digit>"],
    "<digit>":
        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    "<userinfo>":  # Just one
        ["user:password"],
    "<path>":  # Just a few
        ["", "/", "/<id>"],
    "<id>":  # Just a few
        ["abc", "def", "x<digit><digit>"],
    "<query>":
        ["", "?<params>"],
    "<params>":
        ["<param>", "<param>&<params>"],
    "<param>":  # Just a few
        ["<id>=<id>", "<id>=<nat>"],
}
"""
nonterminals: the stuff that isn't the brackets
The basic algorithm is:
- start with start symbol
- pick random symbol to expand
- pick random possible expansion of the symbol
- replace and repeat

This is simple, inefficient, and all round terrible.
Syntactically, these inputs will always be valid - making them good candidates as seeds for mutation!

# extending grammars
to extend grammars, make a deep copy before adding more on

# other possibly needed tools:
- validating grammars
- shortcuts in grammar expression
- escaping delimiters (use "left-angle"=["<"])
can be referenced from the book -- i am not copying down the code for it

# Problems with the basic algorithm:
- infinite strings
- inefficient
Instead, we can use a derivation tree.
A node is a pair (SYMBOL, CHILDREN)
- Start with start symbol
- Traverse tree to find nonterminal symbol without symbol, S
- Expand S from grammar, add expansion as a child of S
"""

def all_terminals(tree):
    (symbol, children) = tree
    if children is None:
        return symbol # this is a nonterminal symbol 
    if len(children) == 0:
        return symbol # terminal symbol
    
    return ''.join([all_terminals(c) for c in children])

def tree_to_string(tree):
    """
    Print our tree
    """
    symbol, children, *_ = tree
    if children:
        return ''.join(tree_to_string(c) for c in children)
    else:
        return '' if is_nonterminal(symbol) else symbol

def is_nonterminal(s): # Remember: nonterminal symbol is one that can be expanded into terminal symbols
    return re.match(RE_NONTERMINAL, s)

def exp_string(expansion):
    """
    Returns the string to be expanded
    """
    if isinstance(expansion, str):
        return expansion
    return expansion[0]

def expand_to_children(expansion):
    """
    takes an expansion string and decomposes to a list of derivation trees
    """
    expansion = exp_string(expansion) # set the e
    assert isinstance(expansion, str)

    if expansion == "":
        return [("", [])]

    strings = re.split(RE_NONTERMINAL, expansion)
    return [(s, None) if is_nonterminal(s) else (s, []) for s in strings if len(s) > 0]

"""
One of the key features of grammar based fuzzing is control. We can determine how large our input gets.
By representing everything as a tree, we get access to the ability to measure the cost of expansions:
- the minimum cost of all expansions
- the sum of all expansions. if a particular nonterminal is encountered more than once, this is infinite
Using these, we can create two functions: 
1. expand to max cost
2. expand with min cost
We desire an input of random length with a min and max length. Hence, a desirable expand_tree function will look like this:
1. expand nodes with max cost until a minimum threshold
2. expand randomly until a maximum threshold
3. close expansion with min cost
"""

derivation_tree = ("<start>",[("<expr>",[("<expr>", None),(" + ", []),("<term>", None)])])
print(expand_to_children(("+<term>", ["extra_data"])))
### TODO: expansion code proper