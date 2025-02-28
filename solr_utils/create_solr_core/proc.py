import os
import subprocess
import rq


def create_solr_core(core_name, config_set,
                     callback_fn=None, callback_queue=None,
                     callback_timeout=180):
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
    if callback_fn and callback_queue:
        current_job = rq.get_current_job()
        redis_conn = current_job.connection
        redis_queue = rq.Queue(callback_queue, connection=redis_conn)
        job = redis_queue.enqueue_call(
                callback_fn,
                args=[{'core_name': core_name,
                       'exit_code': process.returncode,
                       'stdout': process.stdout.decode('utf-8'),
                       'stderr': process.stderr.decode('utf-8')}],
                timeout=callback_timeout)
        if not job.meta:
            job.meta = {}
        job.meta['title'] = 'SOLR Core create callback %s' % core_name
        job.save()
