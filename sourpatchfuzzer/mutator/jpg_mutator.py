from random import randint, randrange, choice
import parser, parser.jpg
import mutator
import string


class JpgMutator(mutator.Mutator):
    """
    why doesn't this work
    """
    def __init__(self, sample, min=2, max=10):
        self.jpg = sample
        mutator.Mutator.__init__(self, None, min, max)
        return

    # ======================================================
    # Filetype: jpg
    # Main strategies: mess with data and metadata fields
    # TODO: these work terribly and are not useful at all. 

    def single_mutate(self):
        output = self.jpg
        tries = randint(self.min, self.max)
        mutations = [self.mangle_data]
        for i in range(0, tries):
            if len(output.datas) > 1:
                randfield = randint(0, len(output.datas)-1)
                output.datas[randfield] = choice(mutations)(output.datas[randfield])
        return output.pack()

    def complex_mutate(self):
        output = self.jpg
        mutations = ['data','length','header']
        tries = randint(self.min, self.max)
        for i in range(0, tries):
            pick = choice(mutations)
            if pick == 'data':
                if len(output.datas) > 1:
                    randfield = randint(0, len(output.datas)-1)
                    output.datas[randfield] = self.mangle_data(output.datas[randfield])
            elif pick == 'length':
                output.lengths = self.mangle_length(output.lengths)
            else:
                output.headers = self.mangle_header(output.headers)
        return output.pack()

    # =======================================================
    # Field mutations
    def mangle_data(self,s):
        print(s)
        return super().mutate(s)

    # ======================================================
    # Structure mutations

    def mangle_length(self, size):
        randfield = randint(0, len(size)-1)
        size[randfield] = super().mutate(size[randfield])
        return size

    def mangle_header(self, headers):
        randfield = randint(0, len(headers)-1)
        if (randint(0, 10)<=5):
            headers[randfield] = super().mutate(headers[randfield])
        else: 
            headers.append(headers[randfield])
        return headers

