# this is just an initial sketch of the data structures so don't read too 
# much into them at this stage.

# basically, a Sequence is just a list of Points and a Point is just a dict
# giving values to certain Attributes.
#
# currently, Sequence assumes the Points have OFFSET_64 attribute values and
# will also make use of the DURATION_64 attribute. I'm not completely happy
# with this coupling but not sure how else to do it given Sequence needs to
# be offset aware.
#
# see datastructure_notes.txt for some of the thinking behind this whole
# approach and a bit of roadmap as to where things are headed.


# this str subclass exists as we may later add methods

class Attribute(str):
    pass


OFFSET_64 = Attribute("offset_64")
MIDI_PITCH = Attribute("midi_pitch")
DURATION_64 = Attribute("duration_64")


class Sequence(list):
    
    
    ## utility methods
    
    def last_point(self):
        if len(self) == 0:
            return Point({OFFSET_64: 0, DURATION_64: 0})
        else:
            return sorted(self, key=lambda x: x[OFFSET_64])[-1]
    
    def next_offset(self):
        point = self.last_point()
        return point[OFFSET_64] + point.get(DURATION_64, 0)
    
    
    ## operations
    
    def concatenate(self, next_seq):
        """
        concatenates two sequences to produce a new sequence
        """
        
        offset = self.next_offset()
        return Sequence(list.__add__(self, next_seq.offset_all(offset)))
    
    def repeat(self, count):
        """
        repeat sequence given number of times to produce a new sequence
        """
        
        x = Sequence(self)
        for i in range(count - 1):
            x = x + Sequence(self)
        return x
    
    def merge(self, parallel_seq):
        """
        combine the points in two sequences, putting them in offset order
        """
        
        return Sequence(sorted(list.__add__(self, parallel_seq), key=lambda x: x[OFFSET_64]))
    
    def map(self, func):
        """
        applies function to a point at a time to produce a new sequence
        """
        
        x = []
        for point in self:
            new_point = func(Point(point))
            x.append(new_point)
        return Sequence(x)
    
    
    ## operator overloading
    
    __add__ = concatenate
    __mul__ = repeat
    __floordiv__ = merge
    __or__ = map
    
    
    # @@@ this can now live elsewhere
    def offset_all(self, offset):
        
        def _(point):
            point[OFFSET_64] = point[OFFSET_64] + offset
            return point
        
        return self.map(_)


class Point(dict):
    
    def tuple(self, *attributes):
        return tuple(self.get(attribute) for attribute in attributes)
