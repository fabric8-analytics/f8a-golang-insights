"""Preprocessing of the collected raw manifests to generate our list of manifests."""
import os
import warnings
import json
import subprocess

warnings.filterwarnings('ignore')


def run_mercator(man_file_name):  # pragma: no cover
    """Run the mercator commmand line tool and return its o/p."""
    completed = subprocess.Popen(["mercator",
                                  man_file_name],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    mercator_output = completed.stdout.read()
    return json.loads(mercator_output)


# Parser for Glide manifests
def parse_glide_yaml(mercator_op):  # pragma: no cover
    """Parse glide.yaml files and get the manifests as a JSON."""
    cur_manifest_lock = mercator_op['items'][0]['result'].get('_dependency_tree_lock_file', {}).get(
            'import', [])
    cur_manifest = mercator_op['items'][0]['result'].get('import', [])

    cur_manifest_list = []
    if not cur_manifest:
        cur_manifest_list = [mercator_op['items'][0]['result']['package']]

    if cur_manifest_lock:
        cur_manifest = cur_manifest_lock

    for package in cur_manifest:
        if 'subpackages' not in package:
            try:
                if 'name' in package:
                    cur_manifest_list.append(package['name'])
                elif 'package' in package:
                    cur_manifest_list.append(package['package'])
                else:
                    raise Exception
            except Exception:
                print(package)
        else:
            try:
                for sub_pkg_name in package['subpackages']:
                    if 'name' in package:
                        cur_manifest_list.append(os.path.join(package['name'], sub_pkg_name))
                    else:
                        cur_manifest_list.append(os.path.join(package['package'], sub_pkg_name))
            except Exception:
                print(package)
    return cur_manifest_list


# Parser for Gopkg toml
def parse_gopkg_toml(mercator_op):  # pragma: no cover
    """Parse Gopkg.toml files and get the manifests as a JSON."""
    try:
        cur_manifest_lock = mercator_op['items'][0]['result'].get('_dependency_tree_lock_file',
                                                                  {}).get('packages', [])
        cur_manifest = mercator_op['items'][0]['result']['constraint']
    except Exception:
        print(mercator_op['items'][0]['result'])
        return []
    if cur_manifest_lock:
        cur_manifest = cur_manifest_lock

    cur_manifest_list = []
    for package in cur_manifest:
        cur_manifest_list.append(package['name'])
    return cur_manifest_list


# Parser for godeps.json
def parse_godeps(mercator_op):  # pragma: no cover
    """Parse Gopkg.toml files and get the manifests as a JSON."""
    if type(mercator_op) is str:
        try:
            mercator_op = json.loads(mercator_op)
        except Exception:
            print(mercator_op)
            return []

    packages_set = set(mercator_op.get("Packages", []))
    try:
        dep_set = mercator_op.get('Deps', [])

        if not dep_set:
            return []

    except Exception:
        print(mercator_op)
    if not packages_set:
        packages_set = set([dep['ImportPath'] for dep in dep_set])

    if './...' in packages_set:
        packages_set.remove('./...')
    return list(packages_set)


def main():  # pragma: no cover
    """Pre-processing logic."""
    manifests_glide = []
    with open(
            '~/f8a/mercator-go/manifests_kube/schemakube_ecosystem_glide_yaml.json') \
            as f:
        content = f.read()
    json_content = json.loads(content)
    if not os.path.exists('/tmp/current_workdir'):
        os.makedirs('/tmp/current_workdir')
    for record in json_content:
        with open('/tmp/current_workdir/glide.yaml', 'w') as temp_manifest:
            temp_manifest.write(record['content'])
        manifests_glide.append(parse_glide_yaml(run_mercator('/tmp/current_workdir/glide.yaml')))

    print(len(manifests_glide))

    with open('manifests_glide.json', 'w') as f:
        f.write(json.dumps(manifests_glide))

    manifests_dep = []
    with open(
            '~/f8a/mercator-go/manifests_kube/schemakube_ecosystem_gopkg_toml.json') \
            as f:
        content = f.read()
    json_content = json.loads(content)
    if not os.path.exists('/tmp/current_workdir'):
        os.makedirs('/tmp/current_workdir')
    for record in json_content:
        with open('/tmp/current_workdir/Gopkg.toml', 'w') as temp_manifest:
            temp_manifest.write(record['content'])
        manifests_dep.append(parse_gopkg_toml(run_mercator('/tmp/current_workdir/Gopkg.toml')))

    print(len(manifests_dep))

    manifests_godeps = []
    with open(
            '~/f8a/mercator-go/manifests_kube/schemakube_ecosystem_godeps.json') \
            as f:
        content = f.read()
    json_content = json.loads(content)
    if not os.path.exists('/tmp/current_workdir'):
        os.makedirs('/tmp/current_workdir')
    for record in json_content:
        man_norm = parse_godeps(record['content'])
        if man_norm:
            manifests_godeps.append(man_norm)

    print(len(manifests_godeps))

    manifests_all = manifests_dep + manifests_godeps + manifests_glide

    with open('golang_manifests.json', 'w') as f:
        f.write(json.dumps(manifests_all))

    for idx, manifest in enumerate(manifests_all):
        manifest_new = []
        for package in manifest:
            if not package.startswith('./'):
                manifest_new.append(package)
        manifests_all[idx] = manifest_new

    # Elimiate duplicates
    manifest_list_new = []

    for idx, manifest in enumerate(manifests_all):
        manifest = set(manifest)
        duplicate = False
        for man_c in manifest_list_new:
            if manifest == man_c:
                duplicate = True
                break
        if not duplicate:
            manifest_list_new.append(manifest)
    print(len(manifest_list_new))

    manifest_list_new = [list(manifest) for manifest in manifest_list_new]
    with open('golang_manifests_unique.json', 'w') as f:
        f.write(json.dumps(manifest_list_new))

    package_set = set()

    for manifest in manifest_list_new:
        package_set = package_set.union(set(manifest))

    print(len(package_set))

    # Create an ingestion list based on the packages present in the training set.
    with open('package_to_ingest.txt', 'w') as f:
        for package in package_set:
            f.write(str(package) + '\n')
