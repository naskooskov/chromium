import gdb

class vector:
  def __init__(self, v):
    self.begin = v['_M_impl']['_M_start'];
    self.end = v['_M_impl']['_M_finish'];
    self.size = self.end - self.begin
    self.item = self.begin

  def __len__(self):
    return int(self.size)

  def next(self):
    if self.item == self.end:
      #raise StopIteration
      return None
    elt = self.item.dereference()
    self.item = self.item + 1
    return elt

  def reset(self):
    self.item = self.begin

  def at(self, index):
    node = self.get(index)
    if node is not None:
      return node.dereference()
    return None

  def get(self, index):
    if index >= self.size:
      return None
    node = self.begin + index
    return node

class hash_map:
  def __init__(self, hmap):
    self.ht = hmap['_M_ht']
    self.size = hmap['_M_ht']['_M_num_elements']
    self.buckets = vector(self.ht['_M_buckets'])

  def __len__(self):
    return int(self.size)

  def reset(self):
    self.buckets.reset()

  def next(self):
    node = self.buckets.next()

    while node is not None:
      if node != 0:
        return node
      node = self.buckets.next()

    return node

  @staticmethod
  def value(node):
    return node['_M_val']['second']

  @staticmethod
  def key(node):
    return node['_M_val']['first']

  def dump(self):
    self.buckets.reset()

    node = self.next()
    while node is not None:
      print "node: %s|%s" % (node, node.type)
      node = self.next()

class hashtable_node:
  def __init__(self, node, datatype):
    self.node = node
    if self.node.type.code is not gdb.TYPE_CODE_PTR:
        raise Exception("Constructing hashtable_node with non-pointer value: %s" % (self.node.type.code))
    self.datatype = datatype
    self.next_node = self.node
    self.val_addr = None
    self.val_node = None

  """ The following two methods aren't quite working.
  def reset(self):
    print "node.reset"
    self.next_node = self.node
    return self.next_node

  def next(self):
    print "node.next"
    self.next_node = self.node['_M_next']
    return self.next_node
  """

  def get(self):
    self.val_addr = int(str(self.node), 16) + self.node.type.sizeof
    self.val_node = gdb.parse_and_eval(self.datatype + str(self.val_addr))
    return self.val_node

  def get_key(self):
    if self.val_node is None:
      self.get()
    return self.val_node['first']

  def get_value(self):
    if self.val_node is None:
      self.get()
    return self.val_node['second']

  def dump(self):
    """
    struct _Hashtable_node
    {
      _Hashtable_node* _M_next;
      _Val _M_val;
    };
    """
    if self.val_node is None:
      self.get()

    print "val_addr: %s" % (self.val_addr)
    print "val_node: %s" % (self.val_node)

#    n = self.reset()
#    while n is not None:
#      print "next: %s" % (n)
#      n = self.next()


