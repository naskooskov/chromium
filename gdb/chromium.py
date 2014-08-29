class scoped_ptr:
  def __init__(self, ptr):
    self.scoped_ptr = ptr
    if not str(ptr.type).startswith("scoped_ptr<"):
      raise Exception("Variable type doesn't seem to be scoped_ptr: %s" % ptr.type)

  def get(self):
    ptr = self.scoped_ptr['impl_']['data_']['ptr']
    return ptr


