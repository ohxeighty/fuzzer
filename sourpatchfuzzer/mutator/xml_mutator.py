from random import randint, randrange, choice
import parser
import mutator
import string


class XmlMutator(mutator.Mutator):
    """
    why doesn't this work
    """
    def __init__(self, sample, min=2, max=10):
        self.xml = sample # should be an ElementTree structure
        mutator.Mutator.__init__(self, None, min, max)
        return

    # ======================================================
    # Filetype: xml
    # Main strategies: 
    # TODO: implement billions of laughs
    # parse using element tree

    def single_mutate(self):
        return "TODO"
    def complex_mutate(self):
        return "TODO"
