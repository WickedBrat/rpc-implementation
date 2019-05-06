import ast
import requests
import json
import argparse
import astor


class FunctionTransformer(ast.NodeTransformer):
    def __init__(self, remote_procedures):
        self.remote_procedures = remote_procedures

    def visit_Call(self, node):
        node_id = node.func.id

        if node_id in self.remote_procedures:
            new_args = node.args[:]
            new_args.insert(0, ast.Str(s=node_id))

            new_node = ast.Call(
                func=ast.Name(id='rpc_call', ctx=ast.Load()),
                args=new_args,
                keywords=node.keywords
            )

            return new_node

        node.args = list(map(lambda child: self.visit_Call(child) if isinstance(child, ast.Call) else child, node.args))

        return node


if __name__ == '__main__':
    registry_url = "https://registry-service-provider.herokuapp.com/all-procedures"

    print("Getting Remote Procedures...")
    response = requests.get(registry_url)
    remote_procedures = json.loads(response.content)
    # remote_procedures = ['is_even', 'find_count', 'find_sum']
    print("Remote Procedures Fetched. Running Transformations...")

    parser = argparse.ArgumentParser("RPC-Transformer")
    parser.add_argument('filename', type=str, help='Filename to transform')
    parser.add_argument('--o', nargs=1, help='Write transformed code to output file')
    parser.add_argument('--norun', action='store_true', help='Does not run the transformed code')
    args = parser.parse_args()

    filepath = args.filename
    data = open(filepath).read()

    tree = ast.parse(data)
    transformer = FunctionTransformer(remote_procedures)
    tree = transformer.visit(tree)

    ast.fix_missing_locations(tree)

    if args.o:
        print("Writing Transformed Code to file: ", args.o[0])
        with open(args.o[0], "w") as f:
            f.write(astor.to_source(tree))

    if not args.norun:
        print("Transformations Done. Running transformed code...\n")
        exec(compile(tree, filename='<ast>', mode='exec'))

