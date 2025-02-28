import os
import subprocess

def create_solr_core(core_name, config_set):
    solr_home = os.environ.get('SOLR_HOME', '/var/solr/data')
    config_set = f'{solr_home}/configsets/{config_set}'
    process = subprocess.run(
        ['solr', 'create', '-c', core_name, '-d', config_set],
        capture_output=True,
        timeout=60)
    if process.stdout:
        print(process.stdout.decode('utf-8'))
    if process.stderr:
        print(process.stderr.decode('utf-8'))
