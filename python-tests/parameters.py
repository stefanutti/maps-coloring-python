import argparse

parser = argparse.ArgumentParser(description='4ct args')

group_input = parser.add_mutually_exclusive_group(required=False)
group_input.add_argument("-r", "--random", help="Random graph: dual of a triangulation of N vertices", type=int, default=100)
group_input.add_argument("-i", "--input", help="Input edgelist filename (networkx)")
group_input.add_argument("-p", "--planar", help="Load a planar embedding of the graph G.faces() - Automatically saved at each run: input_planar_file.serialized")
parser.add_argument("-o", "--output", help="Output edgelist filename (networkx)", required=False)

print(parser.parse_args())
# Namespace(input=None, output=None, planar=None, random=100)
print(parser.parse_args("-r 77".split()))
# Namespace(input=None, output=None, planar=None, random=77)
print(parser.parse_args("-o some/path".split()))
# Namespace(input=None, output='some/path', planar=None, random=100)
print(parser.parse_args("-i some/path".split()))
# Namespace(input='some/path', output=None, planar=None, random=100)
print(parser.parse_args("-i some/path -o some/other/path".split()))
# Namespace(input='some/path', output='some/other/path', planar=None, random=100)
print(parser.parse_args("-r 42 -o some/other/path".split()))
# Namespace(input=None, output='some/other/path', planar=None, random=42)
