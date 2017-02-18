#  d o c s t r i n g s
"""
A sudoku solver.
"""


#  d e p e n d e n c i e s
from itertools import combinations


#  v a r i a b l e s
sudoku_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]


#  f u n c t i o n s
def listContains(l, x):
    """
    Return 'True' if list 'l' contains 'x'.
    """
    for i in l:
        if x==i:
            return True
        
    return False

def listsOverlap(l, m):
    """
    Return 'True' if list 'l' shares at least one element with list 'm'.
    """
    for x in m:
        if listContains(l, x):
            return True

    return False


#  c l a s s e s
class sudokuSquare():
    #  p r o t e c t e d   m e t h o d s
    def __init__(self, x=0, y=0, values=sudoku_values):
        self.x = x
        self.y = y
        self.values = values
        self.conjugate = 0 # could be 2, 3, 4

    #  p u b l i c   m e t h o d s
    def zones(self, all_zones):
        """
        Return the subset of all zones that include this square.
        """
        my_zones = []
        for zone in all_zones:
            in_x = not (self.x<zone.xmin or self.x>zone.xmax) 
            in_y = not (self.y<zone.ymin or self.y>zone.ymax) 
            if in_x and in_y:
                my_zones.append(zone)
                
        return my_zones

    def location(self):
        return (self.x, self.y)
    
    def removeValues(self, known_values=[1, 2]):
        if not self.isKnown():
            old_values = self.values
            new_values = []
            for v in old_values:
                if not listContains(known_values, v):
                    new_values.append(v)
                    
            self.values = new_values

    def isKnown(self):
        if len(self.values)==1:
            return True
        else:
            return False

    def isPair(self):
        if self.conjugate==2 or self.isKnown():
            return True
        else:
            return False

    def isTriple(self):
        if self.conjugate==3 or self.isPair():
            return True
        else:
            return False

    def isQuadruple(self):
        if self.conjugate==4 or self.isTriple():
            return True
        else:
            return False


class sudokuZone():
    #  p r o t e c t e d   m e t h o d s
    def __init__(self, xmin=0, xmax=0, ymin=0, ymax=8):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def __testSquares__(self, all_squares, test=True):
        """
        Return the subset of known or unknown squares contained within this zone.
        """
        test_squares = []
        for square in self.squares(all_squares):
            if square.isKnown() is test:
                test_squares.append(square)
                
        return test_squares

    #  p u b l i c   m e t h o d s
    def squares(self, all_squares):
        """
        Return the subset of all squares contained within this zone.
        """
        my_squares = []
        for square in all_squares:
            in_x = not (square.x<self.xmin or square.x>self.xmax) 
            in_y = not (square.y<self.ymin or square.y>self.ymax) 
            if in_x and in_y:
                my_squares.append(square)
                
        return my_squares
    
    def knownSquares(self, all_squares):
        """
        Return the subset of known squares contained within this zone.
        """
        return self.__testSquares__(all_squares, test=True)
        
    def unknownSquares(self, all_squares):
        """
        Return the subset of unknown squares contained within this zone.
        """
        return self.__testSquares__(all_squares, test=False)
        
    def knownValues(self, all_squares):
        """
        Return the known values within this zone.
        """
        known_values = []
        for square in self.knownSquares(all_squares):
            known_values.append(square.values[0])

        return known_values
    
    def unknownValues(self, all_squares):
        """
        Return the unknown values within this zone.
        """
        unknown_values = []
        for square in self.unknownSquares(all_squares):
            unknown_values.append(square.values[0])

        return unknown_values
    
    def squaresAllowedValue(self, value, all_squares):
        """
        Return list of squares which could have a given value.
        """
        my_squares = self.squares(all_squares)
        allowed_squares = []
        for square in my_squares:
            if listContains(square.values, value):
                allowed_squares.append(square)

        return allowed_squares

    def valueFrequency(self, f, all_squares):
        """
        Return a dictionary of values with only 'f' possible locations: {value : [squares]}
        """
        sets = {}
        for v in sudoku_values:
            allowed_squares = self.squaresAllowedValue(v, all_squares)
            if len(allowed_squares)==f:
                sets[v] = allowed_squares

        return sets

    def pairSquares(self, all_squares):
        """
        Return a dictionary of locations with two possible values values with only two possible
        locations: {location : [a, b]}
        """
        # get list of values with only 2 possible locations, with those locations
        twos = self.valueFrequency(2, all_squares)

        # quick check : at least two such values are required for a pair
        if len(twos.keys())<2:
            return {}
        
        # prepare list of these values
        values = twos.keys()
        
        # prepare list of possible squares
        squares = []

        for k in twos.keys():
            for s in twos[k]:
                if not listContains(squares, s):
                    squares.append(s)
        
        # quick check : if there are only two values, there must be two squares 
        if len(values)==2 and len(squares)!=2:
            return {}
        
        # look for pairs
        pairs = {}
        for two_squares in combinations(squares, 2):
            for two_values in combinations(values, 2):
                square_values = []
                for this_square in two_squares:
                    square_values.append([])
                    for this_value in two_values:
                        if listContains(this_square.values, this_value): 
                            square_values[-1].append(this_value)
                
                # check two squares each have two values
                test = True
                for this_square_values in square_values:
                    test = test and len(this_square_values)==2
                    
                if not test: continue
                
                # check two values each occur in two squares
                value_tally = {}
                for this_value in two_values:
                    value_tally[this_value] = 0
                
                for this_square_values in square_values:
                    for this_value in this_square_values:
                        value_tally[this_value] += 1

                for this_value in value_tally.keys():
                    test = test and value_tally[this_value]==2
                    
                if not test: continue
                
                # new pair found
                for i in range(len(two_squares)):
                    pairs[two_squares[i].location()] = square_values[i]
            
        return pairs

    def tripleSquares(self, all_squares):
        """
        Return a dictionary of locations with two or three possible values that, combined, have only three possible
        locations: {location : [a, b(, c)]}
        """
        # get list of values with only 2, 3 possible locations, with those locations
        twos = self.valueFrequency(2, all_squares)
        threes = self.valueFrequency(3, all_squares)

        # quick check : at least three such values are required for a triple
        if (len(twos.keys()) + len(threes.keys()))<3:
            return {}
        
        # prepare list of these values
        values = twos.keys()
        for k in threes.keys():
            if not listContains(values, k):
                values.append(k)
                
        # prepare list of possible squares
        squares = []
        pairs = self.pairSquares(all_squares)
        for k in twos.keys():
            for s in twos[k]:
                if (not listContains(squares, s)) and (not listContains(pairs.keys(), s)):
                    squares.append(s)

        for k in threes.keys():
            for s in threes[k]:
                if not listContains(squares, s):
                    squares.append(s)
        
        # quick check : if there are only three values, there must be three squares 
        if len(values)==3 and len(squares)!=3:
            return {}
        
        # look for triples
        triples = {}
        for three_squares in combinations(squares, 3):
            for three_values in combinations(values, 3):
                square_values = []
                for this_square in three_squares:
                    square_values.append([])
                    for this_value in three_values:
                        if listContains(this_square.values, this_value): 
                            square_values[-1].append(this_value)
                
                # check three squares each have two or three values
                test = True
                for this_square_values in square_values:
                    test = test and (len(this_square_values)==2 or len(this_square_values)==3)

                if not test: continue
                
                # check three values each occur in two or three squares
                value_tally = {}
                for this_value in three_values:
                    value_tally[this_value] = 0
                
                for this_square_values in square_values:
                    for this_value in this_square_values:
                        value_tally[this_value] += 1

                for this_value in value_tally.keys():
                    if listContains(twos.keys(), this_value):
                        test = test and value_tally[this_value]==2
                    else:
                        test = test and value_tally[this_value]==3

                if not test: continue

                # new triple found
                for i in range(len(three_squares)):
                    triples[three_squares[i].location()] = square_values[i]
            
        return triples

    def quadrupleSquares(self, all_squares):
        """
        Return a dictionary of locations with two or three possible values that, combined, have only three possible
        locations: {location : [a, b(, c(, d))]}
        """
        # get list of values with only 2, 3, 4 possible locations, with those locations
        twos = self.valueFrequency(2, all_squares)
        threes = self.valueFrequency(3, all_squares)
        fours = self.valueFrequency(4, all_squares)

        # quick check : at least four such values are required for a quadruple
        if (len(twos.keys()) + len(threes.keys()) + len(fours.keys()))<4:
            return {}
        
        # prepare list of these values
        values = twos.keys()
        for k in threes.keys():
            if not listContains(values, k):
                values.append(k)
                
        for k in fours.keys():
            if not listContains(values, k):
                values.append(k)
                
        # prepare list of possible squares
        squares = []
        pairs = self.pairSquares(all_squares)
        for k in twos.keys():
            for s in twos[k]:
                if (not listContains(squares, s)) and (not listContains(pairs.keys(), s)):
                    squares.append(s)

        for k in threes.keys():
            for s in threes[k]:
                if not listContains(squares, s):
                    squares.append(s)
        
        for k in fours.keys():
            for s in fours[k]:
                if not listContains(squares, s):
                    squares.append(s)
        
        # quick check : if there are only four values, there must be four squares 
        if len(values)==4 and len(squares)!=4:
            return {}
        
        # look for triples
        quadruples = {}
        for four_squares in combinations(squares, 4):
            for four_values in combinations(values, 4):
                square_values = []
                for this_square in four_squares:
                    square_values.append([])
                    for this_value in four_values:
                        if listContains(this_square.values, this_value): 
                            square_values[-1].append(this_value)
                
                # check four squares each have two, three or four values
                test = True
                for this_square_values in square_values:
                    test = test and (len(this_square_values)==2 or len(this_square_values)==3 or len(this_square_values)==4)

                if not test: continue
                
                # check four values each occur in two, three or four squares
                value_tally = {}
                for this_value in four_values:
                    value_tally[this_value] = 0
                
                for this_square_values in square_values:
                    for this_value in this_square_values:
                        value_tally[this_value] += 1
                        
                for this_value in value_tally.keys():
                    if listContains(twos.keys(), this_value):
                        test = test and value_tally[this_value]==2
                    elif listContains(threes.keys(), this_value):
                        test = test and value_tally[this_value]==3
                    else:
                        test = test and value_tally[this_value]==4
                        
                if not test: continue
                
                # new quadruple found
                for i in range(len(four_squares)):
                    quadruples[four_squares[i].location()] = square_values[i]
            
        return quadruples

    
class sudokuBoard():
    """
    """
    #  p r o p e r t i e s
    size = [9, 9]
    n_squares = size[0] * size[1]
    
    #  p r o t e c t e d   m e t h o d s
    def __init__(self, given_squares):
        """
        The initialisation method. 
        """
        self.__defineZones__()
        self.__defineSquares__(given_squares)
        self.draw()
        
    def __defineZones__(self):
        """
        Create list of the zones on the board. 
        """
        self.zones = []
        for i in range(self.size[0]):
            self.zones.append(sudokuZone(xmin=i, xmax=i, ymin=0, ymax=self.size[1]))

        for j in range(self.size[1]):
            self.zones.append(sudokuZone(xmin=0, xmax=self.size[0], ymin=j, ymax=j))
            
        for i in range(0, self.size[0], 3):
            for j in range(0, self.size[1], 3):
                self.zones.append(sudokuZone(xmin=i, xmax=i+2, ymin=j, ymax=j+2))
     
    def __defineSquares__(self, given_squares):
        """
        Create list of squares on the board with location and list of possible values.
        """
        self.squares = []
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                init_values = sudoku_values
                for k in given_squares.keys():
                    if (i, j)==k:
                        init_values = given_squares[k]
                        
                self.squares.append(sudokuSquare(x=i, y=j, values=init_values))
                
    def __countKnownSquares__(self):
        """
        Return number of known squares on the board.
        """
        known = 0
        for square in self.squares:
            if square.isKnown():
                known += 1
                
        return known
    
    def __countPossibleValues__(self):
        """
        Return number of possible values for all squares on the board.
        """
        n_possible = 0
        for square in self.squares:
            n_possible += len(square.values)
                
        return n_possible
    
    def __isSolved__(self):
        if self.__countKnownSquares__()==self.n_squares:
            return True
        else:
            return False

    def __removeKnownValues__(self):
        """
        Remove known values from possible values of squares in the same zone.
        """
        for square in self.squares:
            known_values = []
            for zone in square.zones(self.zones):
                known_values.extend(zone.knownValues(self.squares))

            if not square.isKnown():
                if listsOverlap(square.values, known_values):
                    #print 'Remove known\t', square.location(), ':', square.values, '-->', 
                    square.removeValues(known_values)
                    #print square.values
            
    def __assignUniqueValues__(self):
        """
        Assign value to square if that is the only possible location within a zone.
        """
        for zone in self.zones:
            singles = zone.valueFrequency(1, self.squares)
            for v in singles.keys():
                for square in self.squares:
                    if square.location()==singles[v][0].location():
                        if not square.isKnown():
                            #print 'Assign value\t', square.location(), ':', square.values, '-->', 
                            square.values = [v]
                            square.conjugate = 1
                            #print square.values

    def __assignPairValues__(self):
        """
        For pairs of squares which must contain two values, remove other possibilities.
        """
        for zone in self.zones:
            pairs = zone.pairSquares(self.squares)
            for location in pairs.keys():
                for square in self.squares:
                    if square.location()==location:
                        if not square.isPair():
                            #print 'Assign pair\t', location, ':', square.values, '-->', 
                            square.values = pairs[location]
                            square.conjugate = 2
                            #print square.values
                            
    def __assignTripleValues__(self):
        """
        For triples of squares which must contain two or three values, remove other possibilities.
        """
        for zone in self.zones:
            triples = zone.tripleSquares(self.squares)
            for location in triples.keys():
                for square in self.squares:
                    if square.location()==location:
                        if not square.isTriple():
                            #print 'Assign triple\t', location, ':', square.values, '-->', 
                            square.values = triples[location]
                            square.conjugate = 3
                            #print square.values

    def __assignQuadrupleValues__(self):
        """
        For quadruples of squares which must contain two, three or four values, remove other possibilities.
        """
        for zone in self.zones:
            quadruples = zone.quadrupleSquares(self.squares)
            for location in quadruples.keys():
                for square in self.squares:
                    if square.location()==location:
                        if not square.isQuadruple():
                            #print 'Assign quadruple\t', location, ':', square.values, '-->', 
                            square.values = quadruples[location]
                            square.conjugate = 4
                            #print square.values

    def __assignConjugateValues__(self):
        """
        """
        self.__assignPairValues__()
        self.__assignTripleValues__()
        self.__assignQuadrupleValues__()
        
    def __removeKnownConjugates__(self):
        """
        """
        for zone in self.zones:
            squares = zone.squares(self.squares)
            known_values = []
            for square in squares:
                if square.conjugate>0:
                    known_values.extend(square.values)

            for square in squares:
                if square.conjugate==0:
                    #print 'Remove known conjugates\t', square.location(), ':', square.values, '-->', 
                    square.removeValues(known_values)
                    #print square.values
        
                        
    #  p u b l i c   m e t h o d s
    def solve(self):
        while True:
            n_known = self.__countKnownSquares__()
            while True:
                __n_known__ = self.__countKnownSquares__()
                self.__removeKnownValues__()
                self.__assignUniqueValues__()

                if __n_known__==self.__countKnownSquares__():
                    break
                
            if n_known==self.__countKnownSquares__():
                while True:
                    __n_possible__ = self.__countPossibleValues__()
                    self.__assignConjugateValues__()
                    self.__removeKnownConjugates__()
                    self.__assignUniqueValues__()
                    self.__removeKnownValues__()

                    if __n_possible__==self.__countPossibleValues__():
                        break
            
            if self.__isSolved__(): 
                self.draw()
                break

            if n_known==self.__countKnownSquares__():
                print 'Failed'
                self.draw()
                break
            
    def draw(self):
        for j in range(self.size[1]):
            print '',
            for i in range(self.size[0]):
                value = '-'
                for square in self.squares:
                    if square.location()==(i, j):
                        if square.isKnown():
                            value = square.values[0]

                print value,
            print ''

        print ''


#  m a i n   e x e c u t i o n
if __name__ == "__main__":
    easy = {(0, 1) : [2],
            (0, 5) : [7],
            (1, 2) : [6],
            (1, 6) : [4],
            (1, 8) : [2],
            (2, 1) : [4],
            (2, 2) : [9],
            (2, 3) : [1],
            (2, 6) : [3],
            (2, 7) : [8],
            (3, 0) : [3],
            (3, 4) : [4],
            (3, 6) : [6],
            (4, 3) : [7],
            (4, 5) : [5],
            (5, 2) : [7],
            (5, 4) : [1],
            (5, 8) : [9],
            (6, 1) : [5],
            (6, 2) : [3],
            (6, 5) : [6],
            (6, 6) : [8],
            (6, 7) : [1],
            (7, 0) : [4],
            (7, 2) : [8],
            (7, 6) : [7],
            (8, 3) : [2],
            (8, 7) : [9]}

    medium = {(0, 6) : [3],
              (1, 1) : [7],
              (1, 2) : [2],
              (1, 5) : [1],
              (1, 7) : [6],
              (2, 0) : [3],
              (2, 4) : [6],
              (2, 5) : [9],
              (2, 7) : [2],
              (3, 1) : [8],
              (3, 2) : [7],
              (4, 2) : [5],
              (4, 6) : [9],
              (5, 6) : [4],
              (5, 7) : [1],
              (6, 1) : [9],
              (6, 3) : [8],
              (6, 4) : [7],
              (6, 8) : [6],
              (7, 1) : [6],
              (7, 3) : [5],
              (7, 6) : [7],
              (7, 7) : [3],
              (8, 2) : [1]}
    
    hard = {(0, 1) : [2],
            (0, 6) : [4],
            (1, 0) : [4],
            (1, 3) : [7],
            (1, 7) : [9],
            (2, 2) : [6],
            (2, 4) : [2],
            (2, 8) : [7],
            (3, 3) : [3],
            (3, 8) : [5],
            (4, 0) : [9],
            (4, 4) : [7],
            (4, 8) : [6],
            (5, 0) : [1],
            (5, 5) : [2],
            (6, 0) : [6],
            (6, 4) : [4],
            (6, 6) : [1],
            (7, 1) : [5],
            (7, 5) : [6],
            (7, 8) : [9],
            (8, 2) : [3],
            (8, 7) : [8]}

    very_hard = {(1, 1) : [1],
                 (1, 4) : [8],
                 (1, 5) : [7],
                 (1, 6) : [5],
                 (2, 2) : [2],
                 (2, 5) : [6],
                 (2, 7) : [1],
                 (3, 3) : [3],
                 (3, 6) : [4],
                 (3, 7) : [9],
                 (4, 1) : [7],
                 (4, 4) : [4],
                 (4, 7) : [6],
                 (5, 1) : [4],
                 (5, 2) : [8],
                 (5, 5) : [5],
                 (6, 1) : [2],
                 (6, 3) : [8],
                 (6, 6) : [6],
                 (7, 2) : [3],
                 (7, 3) : [2],
                 (7, 4) : [9],
                 (7, 7) : [4]}

    very_very_hard = {(0, 1) : [9],
                      (0, 2) : [6],
                      (0, 3) : [7],
                      (0, 4) : [8],
                      (0, 7) : [1],
                      (1, 0) : [8],
                      (1, 6) : [5],
                      (2, 5) : [3],
                      (3, 2) : [7],
                      (3, 3) : [2],
                      (3, 8) : [9],
                      (4, 1) : [3],
                      (4, 4) : [7],
                      (4, 7) : [2],
                      (5, 0) : [9],
                      (5, 5) : [6],
                      (5, 6) : [8],
                      (6, 3) : [5],
                      (7, 2) : [4],
                      (7, 8) : [5],
                      (8, 1) : [6],
                      (8, 4) : [1],
                      (8, 5) : [2],
                      (8, 6) : [3],
                      (8, 7) : [4]}

    seven_star = {(0, 3) : [2],
                  (0, 7) : [8],
                  (1, 0) : [1],
                  (1, 2) : [7],
                  (1, 8) : [9],
                  (2, 0) : [2],
                  (2, 4) : [3],
                  (2, 6) : [1],
                  (3, 1) : [3],
                  (3, 3) : [6],
                  (3, 6) : [7],
                  (4, 1) : [4],
                  (4, 4) : [7],
                  (4, 7) : [5],
                  (5, 2) : [5],
                  (5, 5) : [4],
                  (5, 7) : [3],
                  (6, 2) : [4],
                  (6, 4) : [8],
                  (6, 8) : [3],
                  (7, 0) : [3],
                  (7, 6) : [2],
                  (7, 8) : [1],
                  (8, 1) : [6],
                  (8, 5) : [9]}
    
    #b = sudokuBoard(easy)
    b = sudokuBoard(medium)
    #b = sudokuBoard(hard)
    #b = sudokuBoard(very_hard)
    #b = sudokuBoard(very_very_hard)
    #b = sudokuBoard(seven_star)
    b.solve()
