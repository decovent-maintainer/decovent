class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        if other == None:
            return False
        if self.x == other.x and self.y == other.y:
            return True
        return False
    def __repr__(self):
        return 'Point(x=%s, y=%s)' % (self.x, self.y)
    
def check_error(e, h):
    e_success, e_result, e_class, e_meth = e
    
    if e_success is False:
        raise e_result    
    
    for h_success, h_result, h_class, h_meth in h:
        if h_success is False:
            if not isinstance(h_success, tuple):
                raise h_result
            raise h_result[1]