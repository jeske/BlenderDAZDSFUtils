import itertools, copy

from . import dsf_data

class geom_creator (object):
  """class to create dsf-geometry items from meshes.
  """
  def __init__ (self):
    """create an instance. This constructor should set some default arguments.
    """
    pass
  @classmethod
  def get_vertices (self, msh):
    """get the vertices object from the mesh.
    """
    vs = [[v.co.x, v.co.y, v.co.z] for v in msh.vertices]
    jdata = {
      'count': len (vs),
      'values': vs
    }
    return jdata

  @classmethod
  def get_face_groups (self, obj):
    """returns two objects: the polygon_groups-block of the dsf
       and a list containing the group-indices (one for each face).
       obj is the mesh object (which holds the groups).
    """
    msh = obj.data
    def get_common_group (vidxs):
      """get the smallest group index that is a common group index of
         all vertexes whose indices are given in vidxs.
         If there is no common index, return 0.
      """
      # list of group-objects, one for each vertex
      groups = [msh.vertices[vidx].groups for vidx in vidxs]
      # create a list of lists of group-indices
      group_idxs = [[vg.group for vg in vgroups] for vgroups in groups]
      # build the intersection of all groups
      intersection = set (group_idxs.pop ())
      for group in group_idxs:
        intersection.intersection_update (group)
      if len (intersection) == 0:
        return 0
      else:
        return min (intersection)
    # pgroups is the list of group indices to use, one for each face.
    pgroups = [get_common_group (poly.vertices) for poly in msh.polygons]
    if len (obj.vertex_groups) == 0:
      group_names = ['default']
    else:
      group_names = [group.name for group in obj.vertex_groups]
    jdata = {
      'count': len (obj.vertex_groups),
      'values': group_names
    }
    return (jdata, pgroups)

  @classmethod
  def get_face_materials (self, obj):
    """returns two objects: the polygon_material_groups as an object
       and a list of material indices, one for each face.
    """
    msh = obj.data
    def get_material_name (material):
      """get a sensible name for the material
      """
      if material is None:
        return 'default'
      else:
        return material.name
    mgroups = [poly.material_index for poly in msh.polygons]
    if len (msh.materials) == 0:
      material_names = ['default']
    else:
      material_names = [get_material_name (mat) for mat in msh.materials]
    jdata = {
      'count': len (material_names),
      'values': material_names
    }
    return (jdata, mgroups)

  @classmethod
  def create_face_data (self, obj):
    """create the polygon data of the object.
       this returns a dictionary with the keys:
       polygon_groups, polygon_material_groups, polylist
    """
    msh = obj.data
    (pg_jdata, pg_idxs) = self.get_face_groups (obj)
    (pm_jdata, pm_idxs) = self.get_face_materials (obj)
    assert len (pg_idxs) == len (pm_idxs) == len (msh.polygons)
    def create_poly_tuple (g, m, vs):
      return [g, m] + vs
    poly_vidx_list = [list (poly.vertices) for poly in msh.polygons]
    polylist_jdata ={
      'count': len (msh.polygons),
      'values': list (map (create_poly_tuple, pg_idxs, pm_idxs, poly_vidx_list))
    }
    vertices = self.get_vertices (msh)
    jdata = {
      'vertices': vertices,
      'polygon_groups': pg_jdata,
      'polygon_material_groups': pm_jdata,
      'polylist': polylist_jdata
    }
    return jdata

  def create_geometry (self, obj):
    """create a geometry_library entry from a mesh.
       The geometry is given a name derived from the mesh data object
       (by appending a '-mesh').
       @parameter msh a blender mesh object (e.g. created from to_mesh).
    """
    geom_lib = {
      'type': 'polygon_mesh',
      'name': obj.data.name,
      'id': obj.data.name + '-mesh'
    }
    geom_lib.update (self.create_face_data (obj))
    # required contents:
    # id, name, type, vertices, polygon_groups, polygon_material_groups,
    # polylist, default_uv_set (if available),
    # extra (optional): geometry_channels (for subdivision)
    return geom_lib

class node_creator (object):
  """class to create node entries, in particular: node entries for
     geometry objects.
  """
  def __init__ (self):
    """create an instance. This constructor should set some default arguments.
    """
    pass
  def create_node (self, obj):
    """create the node-library entry for the object.
       The node is given an id by appending '-node' to the meshes data name.
    """
    id_data = {
      'id': obj.name + '-node',
      'name': obj.name,
      'label': obj.name,
      'rotation_order' : "XYZ",
    }
    node_lib = copy.deepcopy (dsf_data.node_entry)
    node_lib.update (id_data)
    return node_lib
