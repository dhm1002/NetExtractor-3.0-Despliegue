'''
Este fichero implementa la lectura y conversión de una red en formato GEXF, pasada como texto, a una red en formato nx, ya que la propia librería de network
incluye un método para la conversión, pero solo pasanado la ruta del fichero gexf en nuestro equipo y no como un string.
Al utilizar los datos de dracor para las obras de teatro, he tenido que adaptar los métodos para que permitiera pasar una cadena de texto como red gexf.
La documentación de la función de networkx adaptada ha sido obtenida del siguiente enlace: 
    https://networkx.org/documentation/stable/_modules/networkx/readwrite/gexf.html#read_gexf
La única modificación realizada al fichero, ha sido la función de importación de la red en formato xml, cambiando el método 
'''
import xml.etree.ElementTree as ET
import networkx as nx

def read_gexf(path, node_type=None, relabel=False, version="1.2draft"):
        """
        Read graph in GEXF format from path.

        "GEXF (Graph Exchange XML Format) is a language for describing
        complex networks structures, their associated data and dynamics" [1]_.

        Parameters
        ----------
        path : file or string
        File or file name to read.
        File names ending in .gz or .bz2 will be decompressed.
        node_type: Python type (default: None)
        Convert node ids to this type if not None.
        relabel : bool (default: False)
        If True relabel the nodes to use the GEXF node "label" attribute
        instead of the node "id" attribute as the NetworkX node label.
        version : string (default: 1.2draft)
        Version of GEFX File Format (see http://gexf.net/schema.html)
        Supported values: "1.1draft", "1.2draft"

        Returns
        -------
        graph: NetworkX graph
            If no parallel edges are found a Graph or DiGraph is returned.
            Otherwise a MultiGraph or MultiDiGraph is returned.

        Notes
        -----
        This implementation does not support mixed graphs (directed and undirected
        edges together).

        References
        ----------
        .. [1] GEXF File Format, http://gexf.net/
        """
        reader = GEXFReader(node_type=node_type, version=version)
        G = reader(path)
        return G



class GEXF:
        versions = {}
        d = {
            "NS_GEXF": "http://www.gexf.net/1.1draft",
            "NS_VIZ": "http://www.gexf.net/1.1draft/viz",
            "NS_XSI": "http://www.w3.org/2001/XMLSchema-instance",
            "SCHEMALOCATION": " ".join(
                ["http://www.gexf.net/1.1draft", "http://www.gexf.net/1.1draft/gexf.xsd"]
            ),
            "VERSION": "1.1",
        }
        versions["1.1draft"] = d
        d = {
            "NS_GEXF": "http://www.gexf.net/1.2draft",
            "NS_VIZ": "http://www.gexf.net/1.2draft/viz",
            "NS_XSI": "http://www.w3.org/2001/XMLSchema-instance",
            "SCHEMALOCATION": " ".join(
                ["http://www.gexf.net/1.2draft", "http://www.gexf.net/1.2draft/gexf.xsd"]
            ),
            "VERSION": "1.2",
        }
        versions["1.2draft"] = d

        def construct_types(self):
            types = [
                (int, "integer"),
                (float, "float"),
                (float, "double"),
                (bool, "boolean"),
                (list, "string"),
                (dict, "string"),
                (int, "long"),
                (str, "liststring"),
                (str, "anyURI"),
                (str, "string"),
            ]

            # These additions to types allow writing numpy types
            try:
                import numpy as np
            except ImportError:
                pass
            else:
                # prepend so that python types are created upon read (last entry wins)
                types = [
                    (np.float64, "float"),
                    (np.float32, "float"),
                    (np.float16, "float"),
                    (np.float_, "float"),
                    (np.int_, "int"),
                    (np.int8, "int"),
                    (np.int16, "int"),
                    (np.int32, "int"),
                    (np.int64, "int"),
                    (np.uint8, "int"),
                    (np.uint16, "int"),
                    (np.uint32, "int"),
                    (np.uint64, "int"),
                    (np.int_, "int"),
                    (np.intc, "int"),
                    (np.intp, "int"),
                ] + types

            self.xml_type = dict(types)
            self.python_type = dict(reversed(a) for a in types)

        # http://www.w3.org/TR/xmlschema-2/#boolean
        convert_bool = {
            "true": True,
            "false": False,
            "True": True,
            "False": False,
            "0": False,
            0: False,
            "1": True,
            1: True,
        }

        def set_version(self, version):
            d = self.versions.get(version)
            if d is None:
                raise nx.NetworkXError(f"Unknown GEXF version {version}.")
            self.NS_GEXF = d["NS_GEXF"]
            self.NS_VIZ = d["NS_VIZ"]
            self.NS_XSI = d["NS_XSI"]
            self.SCHEMALOCATION = d["SCHEMALOCATION"]
            self.VERSION = d["VERSION"]
            self.version = version

class GEXFReader(GEXF):
        # Class to read GEXF format files
        # use read_gexf() function
        def __init__(self, node_type=None, version="1.2draft"):
            self.construct_types()
            self.node_type = node_type
            # assume simple graph and test for multigraph on read
            self.simple_graph = True
            self.set_version(version)

        def __call__(self, stream):

            ## ESTA ES LA ÚNICA LÍNEA QUE HE CAMBIADO RESPECTO AL CÓDIGO ORIGINAL, YA QUE AQUÍ SE HACE LA IMPORTACIÓN DEL XML, EN EL ORIGINAL MEDIANTE FICHERO Y AQUÍ
            ## POR CADENA DE TEXTO
            self.xml = ET.fromstring(stream)

            g = self.xml.find(f"{{{self.NS_GEXF}}}graph")
            if g is not None:
                return self.make_graph(g)
            # try all the versions
            for version in self.versions:
                self.set_version(version)
                g = self.xml.find(f"{{{self.NS_GEXF}}}graph")
                if g is not None:
                    return self.make_graph(g)
            raise nx.NetworkXError("No <graph> element in GEXF file.")

        def make_graph(self, graph_xml):
            # start with empty DiGraph or MultiDiGraph
            edgedefault = graph_xml.get("defaultedgetype", None)
            if edgedefault == "directed":
                G = nx.MultiDiGraph()
            else:
                G = nx.MultiGraph()

            # graph attributes
            graph_name = graph_xml.get("name", "")
            if graph_name != "":
                G.graph["name"] = graph_name
            graph_start = graph_xml.get("start")
            if graph_start is not None:
                G.graph["start"] = graph_start
            graph_end = graph_xml.get("end")
            if graph_end is not None:
                G.graph["end"] = graph_end
            graph_mode = graph_xml.get("mode", "")
            if graph_mode == "dynamic":
                G.graph["mode"] = "dynamic"
            else:
                G.graph["mode"] = "static"

            # timeformat
            self.timeformat = graph_xml.get("timeformat")
            if self.timeformat == "date":
                self.timeformat = "string"

            # node and edge attributes
            attributes_elements = graph_xml.findall(f"{{{self.NS_GEXF}}}attributes")
            # dictionaries to hold attributes and attribute defaults
            node_attr = {}
            node_default = {}
            edge_attr = {}
            edge_default = {}
            for a in attributes_elements:
                attr_class = a.get("class")
                if attr_class == "node":
                    na, nd = self.find_gexf_attributes(a)
                    node_attr.update(na)
                    node_default.update(nd)
                    G.graph["node_default"] = node_default
                elif attr_class == "edge":
                    ea, ed = self.find_gexf_attributes(a)
                    edge_attr.update(ea)
                    edge_default.update(ed)
                    G.graph["edge_default"] = edge_default
                else:
                    raise  # unknown attribute class

            # Hack to handle Gephi0.7beta bug
            # add weight attribute
            ea = {"weight": {"type": "double", "mode": "static", "title": "weight"}}
            ed = {}
            edge_attr.update(ea)
            edge_default.update(ed)
            G.graph["edge_default"] = edge_default

            # add nodes
            nodes_element = graph_xml.find(f"{{{self.NS_GEXF}}}nodes")
            if nodes_element is not None:
                for node_xml in nodes_element.findall(f"{{{self.NS_GEXF}}}node"):
                    self.add_node(G, node_xml, node_attr)

            # add edges
            edges_element = graph_xml.find(f"{{{self.NS_GEXF}}}edges")
            if edges_element is not None:
                for edge_xml in edges_element.findall(f"{{{self.NS_GEXF}}}edge"):
                    self.add_edge(G, edge_xml, edge_attr)

            # switch to Graph or DiGraph if no parallel edges were found.
            if self.simple_graph:
                if G.is_directed():
                    G = nx.DiGraph(G)
                else:
                    G = nx.Graph(G)
            return G

        def add_node(self, G, node_xml, node_attr, node_pid=None):
            # add a single node with attributes to the graph

            # get attributes and subattributues for node
            data = self.decode_attr_elements(node_attr, node_xml)
            data = self.add_parents(data, node_xml)  # add any parents
            if self.VERSION == "1.1":
                data = self.add_slices(data, node_xml)  # add slices
            else:
                data = self.add_spells(data, node_xml)  # add spells
            data = self.add_viz(data, node_xml)  # add viz
            data = self.add_start_end(data, node_xml)  # add start/end

            # find the node id and cast it to the appropriate type
            node_id = node_xml.get("id")
            if self.node_type is not None:
                node_id = self.node_type(node_id)

            # every node should have a label
            node_label = node_xml.get("label")
            data["label"] = node_label

            # parent node id
            node_pid = node_xml.get("pid", node_pid)
            if node_pid is not None:
                data["pid"] = node_pid

            # check for subnodes, recursive
            subnodes = node_xml.find(f"{{{self.NS_GEXF}}}nodes")
            if subnodes is not None:
                for node_xml in subnodes.findall(f"{{{self.NS_GEXF}}}node"):
                    self.add_node(G, node_xml, node_attr, node_pid=node_id)

            G.add_node(node_id, **data)

        def add_start_end(self, data, xml):
            # start and end times
            ttype = self.timeformat
            node_start = xml.get("start")
            if node_start is not None:
                data["start"] = self.python_type[ttype](node_start)
            node_end = xml.get("end")
            if node_end is not None:
                data["end"] = self.python_type[ttype](node_end)
            return data

        def add_viz(self, data, node_xml):
            # add viz element for node
            viz = {}
            color = node_xml.find(f"{{{self.NS_VIZ}}}color")
            if color is not None:
                if self.VERSION == "1.1":
                    viz["color"] = {
                        "r": int(color.get("r")),
                        "g": int(color.get("g")),
                        "b": int(color.get("b")),
                    }
                else:
                    viz["color"] = {
                        "r": int(color.get("r")),
                        "g": int(color.get("g")),
                        "b": int(color.get("b")),
                        "a": float(color.get("a", 1)),
                    }

            size = node_xml.find(f"{{{self.NS_VIZ}}}size")
            if size is not None:
                viz["size"] = float(size.get("value"))

            thickness = node_xml.find(f"{{{self.NS_VIZ}}}thickness")
            if thickness is not None:
                viz["thickness"] = float(thickness.get("value"))

            shape = node_xml.find(f"{{{self.NS_VIZ}}}shape")
            if shape is not None:
                viz["shape"] = shape.get("shape")
                if viz["shape"] == "image":
                    viz["shape"] = shape.get("uri")

            position = node_xml.find(f"{{{self.NS_VIZ}}}position")
            if position is not None:
                viz["position"] = {
                    "x": float(position.get("x", 0)),
                    "y": float(position.get("y", 0)),
                    "z": float(position.get("z", 0)),
                }

            if len(viz) > 0:
                data["viz"] = viz
            return data

        def add_parents(self, data, node_xml):
            parents_element = node_xml.find(f"{{{self.NS_GEXF}}}parents")
            if parents_element is not None:
                data["parents"] = []
                for p in parents_element.findall(f"{{{self.NS_GEXF}}}parent"):
                    parent = p.get("for")
                    data["parents"].append(parent)
            return data

        def add_slices(self, data, node_or_edge_xml):
            slices_element = node_or_edge_xml.find(f"{{{self.NS_GEXF}}}slices")
            if slices_element is not None:
                data["slices"] = []
                for s in slices_element.findall(f"{{{self.NS_GEXF}}}slice"):
                    start = s.get("start")
                    end = s.get("end")
                    data["slices"].append((start, end))
            return data

        def add_spells(self, data, node_or_edge_xml):
            spells_element = node_or_edge_xml.find(f"{{{self.NS_GEXF}}}spells")
            if spells_element is not None:
                data["spells"] = []
                ttype = self.timeformat
                for s in spells_element.findall(f"{{{self.NS_GEXF}}}spell"):
                    start = self.python_type[ttype](s.get("start"))
                    end = self.python_type[ttype](s.get("end"))
                    data["spells"].append((start, end))
            return data

        def add_edge(self, G, edge_element, edge_attr):
            # add an edge to the graph

            # raise error if we find mixed directed and undirected edges
            edge_direction = edge_element.get("type")
            if G.is_directed() and edge_direction == "undirected":
                raise nx.NetworkXError("Undirected edge found in directed graph.")
            if (not G.is_directed()) and edge_direction == "directed":
                raise nx.NetworkXError("Directed edge found in undirected graph.")

            # Get source and target and recast type if required
            source = edge_element.get("source")
            target = edge_element.get("target")
            if self.node_type is not None:
                source = self.node_type(source)
                target = self.node_type(target)

            data = self.decode_attr_elements(edge_attr, edge_element)
            data = self.add_start_end(data, edge_element)

            if self.VERSION == "1.1":
                data = self.add_slices(data, edge_element)  # add slices
            else:
                data = self.add_spells(data, edge_element)  # add spells

            # GEXF stores edge ids as an attribute
            # NetworkX uses them as keys in multigraphs
            # if networkx_key is not specified as an attribute
            edge_id = edge_element.get("id")
            if edge_id is not None:
                data["id"] = edge_id

            # check if there is a 'multigraph_key' and use that as edge_id
            multigraph_key = data.pop("networkx_key", None)
            if multigraph_key is not None:
                edge_id = multigraph_key

            weight = edge_element.get("weight")
            if weight is not None:
                data["weight"] = float(weight)

            edge_label = edge_element.get("label")
            if edge_label is not None:
                data["label"] = edge_label

            if G.has_edge(source, target):
                # seen this edge before - this is a multigraph
                self.simple_graph = False
            G.add_edge(source, target, key=edge_id, **data)
            if edge_direction == "mutual":
                G.add_edge(target, source, key=edge_id, **data)

        def decode_attr_elements(self, gexf_keys, obj_xml):
            # Use the key information to decode the attr XML
            attr = {}
            # look for outer '<attvalues>' element
            attr_element = obj_xml.find(f"{{{self.NS_GEXF}}}attvalues")
            if attr_element is not None:
                # loop over <attvalue> elements
                for a in attr_element.findall(f"{{{self.NS_GEXF}}}attvalue"):
                    key = a.get("for")  # for is required
                    try:  # should be in our gexf_keys dictionary
                        title = gexf_keys[key]["title"]
                    except KeyError as err:
                        raise nx.NetworkXError(f"No attribute defined for={key}.") from err
                    atype = gexf_keys[key]["type"]
                    value = a.get("value")
                    if atype == "boolean":
                        value = self.convert_bool[value]
                    else:
                        value = self.python_type[atype](value)
                    if gexf_keys[key]["mode"] == "dynamic":
                        # for dynamic graphs use list of three-tuples
                        # [(value1,start1,end1), (value2,start2,end2), etc]
                        ttype = self.timeformat
                        start = self.python_type[ttype](a.get("start"))
                        end = self.python_type[ttype](a.get("end"))
                        if title in attr:
                            attr[title].append((value, start, end))
                        else:
                            attr[title] = [(value, start, end)]
                    else:
                        # for static graphs just assign the value
                        attr[title] = value
            return attr

        def find_gexf_attributes(self, attributes_element):
            # Extract all the attributes and defaults
            attrs = {}
            defaults = {}
            mode = attributes_element.get("mode")
            for k in attributes_element.findall(f"{{{self.NS_GEXF}}}attribute"):
                attr_id = k.get("id")
                title = k.get("title")
                atype = k.get("type")
                attrs[attr_id] = {"title": title, "type": atype, "mode": mode}
                # check for the 'default' subelement of key element and add
                default = k.find(f"{{{self.NS_GEXF}}}default")
                if default is not None:
                    if atype == "boolean":
                        value = self.convert_bool[default.text]
                    else:
                        value = self.python_type[atype](default.text)
                    defaults[title] = value
            return attrs, defaults
