from collections import deque

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import stl
import chromium

def GetSiteInstance(value):
  # Lookup the impl symbol, so the pointer can be casted to the impl and
  # data to be extracted.
  symbol = gdb.lookup_symbol("content::SiteInstanceImpl")
  if symbol[0] is None:
    raise Exception("Failed to resolve content::SiteInstanceImpl");
  site_instance = symbol[0].type.pointer()

  return value.cast(site_instance)

ProxyNodeType = "(std::pair<int const, content::RenderFrameProxyHost*> *) "
def PrintProxies(rfhm, prefix):
  proxy_hosts = rfhm['proxy_hosts_']

  hmap = stl.hash_map(proxy_hosts)
  n = hmap.next()
  while n is not None:
    node = stl.hashtable_node(n, ProxyNodeType)
    proxy = node.get_value()
    si = GetSiteInstance(proxy['site_instance_']['ptr_'])
    print prefix + "  proxy[" + str(si['id_']) + "]: " + str(proxy) + " -> " + str(si['site_']['spec_'])

    n = hmap.next()

def GetProxies(rfhm, prefix):
  # Lookup the global helper function to call and get all proxies from RFHM
  symbol = gdb.lookup_global_symbol("content::GetProxies(content::RenderFrameHostManager*)")
  proxies = symbol.value()(rfhm.address)

  v = stl.vector(proxies)
  for i in range(0, v.size):
    proxy = v.at(i)
    si = GetSiteInstance(proxy['site_instance_']['ptr_'])
    print prefix + "  proxy@" + str(proxy.address)
    print prefix + "  proxy[" + str(si['id_']) + "]: " + str(proxy) + " -> " + str(si['site_']['spec_'])


def PrintRFHM(rfhm, prefix):
  parent = rfhm['frame_tree_node_']['parent_']
  parent_addr = "NULL"
  if parent != 0:
    parent_addr = parent['render_manager_'].address

  print prefix + "RFHM[" + str(rfhm.address) + "]: child of [" + str(parent_addr) + "]"

  rfh = chromium.scoped_ptr(rfhm['render_frame_host_']).get()
  current_si = GetSiteInstance(rfh['render_view_host_']['instance_']['ptr_'])
  print prefix + "  current_rfh: " + str(rfhm['render_frame_host_']) + " site: " + str(current_si['site_']['spec_'])

  pending_rfh = chromium.scoped_ptr(rfhm['pending_render_frame_host_']).get()
  if pending_rfh != 0:
    pending_si = GetSiteInstance(pending_rfh['render_view_host_']['instance_']['ptr_'])
    print prefix + "  pending_rfh: " + str(rfhm['pending_render_frame_host_']) +  " site: " + str(pending_si['site_']['spec_'])
  else:
    print prefix + "  pending_rfh: " + str(rfhm['pending_render_frame_host_'])

  PrintProxies(rfhm, prefix)

def VisitNode(node):
  rfhm = node['render_manager_']
  PrintRFHM(rfhm, '')

class FrameTree(gdb.Command):
  """dumpft: Print out Chromium browser-side frame tree details
  """

  def __init__(self):
    self.json = False
    gdb.Command.__init__(self, "dumpft", gdb.COMMAND_OBSCURE, gdb.COMPLETE_SYMBOL)


  def invoke(self, arg, from_tty):
    arg_list = gdb.string_to_argv(arg)
    tree = gdb.parse_and_eval(arg_list[0])
    root = tree['root_']
    ptr = chromium.scoped_ptr(root).get()

    q = deque()
    ftn = ptr
    while ftn is not None:
      VisitNode(ftn)

      v = stl.vector(ftn['children_']['v_'])
      for i in range(0, v.size):
        q.append(v.at(i))

      try:
        ftn = q.pop()
      except IndexError:
        ftn = None;
        break;

FrameTree()
