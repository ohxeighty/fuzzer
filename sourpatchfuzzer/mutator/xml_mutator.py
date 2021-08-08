from random import randint, randrange, choice, shuffle
import parser
import mutator
import string
import xml.etree.ElementTree as ET
import copy 

class XmlMutator(mutator.Mutator):
    """
    why doesn't this work
    """
    def __init__(self, sample, min=2, max=10):
        self.data = sample
        self.xml = sample # should be an ElementTree structure
        self.root = self.xml.getroot()
        mutator.Mutator.__init__(self, None, min, max)
        #print(ET.tostring(self.xml.getroot()))
        #self.tags = [x for x in self.root.iter()]
        self.tags = None

        self.mutated = None 
        return

    # ======================================================
    # Filetype: xml
    # Main strategies: 
    # TODO: implement billions of laughs
    # parse using element tree

    def single_mutate(self):
        return "TODO"
    def complex_mutate(self):
        # lol pick a random field and set it to whatever
        # we use an expensive deep copy because im lazy rn
        # and comprehension lol
        # also 1 hour to deadline :) 
        self.mutated = copy.deepcopy(self.xml)
        mutators = [self.random_child_replace_attrib]
        choice(mutators)()
        return ET.tostring(self.mutated.getroot())

    # populate one of a random child's attributes with a random string mutation
    # IF there is an attribute. otherwise replace the tag itself
    def random_child_replace_attrib(self):
        mutators = [self.field_rand_special, self.field_rand_str]
        # wow thats not expensive at all :)
        # wow we also totally dont assume anything :)
        self.tags = [x for x in self.mutated.iter()]
        random_tag = choice(self.tags)
        #print(random_tag.attrib)
        if len(random_tag.attrib):
            random_tag.attrib[choice(list(random_tag.attrib.keys()))] = choice(mutators)()
            #print(ET.tostring(self.mutated.getroot()))
            #print(random_tag.attrib)
        
    # populate with special chars + random ascii 
    def field_rand_special(self):
        special_chars = "%$;"
        return "".join(choice(string.ascii_lowercase + string.ascii_uppercase + special_chars) for i in range(30))

    def field_rand_str(self):
        return "".join(choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(30))
