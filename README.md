# Python SOLR Utilities

Python SOLR Utilities to workaround SOLR API shortcomings.

## Create SOLR Core

The SOLR API to create cores with configsets does not copy the configset files into the newly created core's conf folder. The only way to accomplish this is to run SOLR in Cloud Mode and copy configsets with Zookeeper and the SOLR Cloud Mode Only API endpoints.

To workaround this in SOLR Standalone, we can use Python and a REDIS Queue to execute the command `solr create -c <core name> -d <configset>` which will copy the configset files into the core's conf folder. This of course requires your SOLR server to have Python installed.

### How to use

Create a Python virtual environment:
```
python -m venv pysolr_utils_venv
```

Install requirements and this module:
```
./pysolr_utils_venv/bin/activate
cd src/pysolr_utils
pip install -r requirements.txt
pip install -e .
python setup.py develop
```

Run the REDIS Queue worker:
```
pysolr_utils_venv/bin/python src/pysolr_utils/solr_utils/create_solr_core/worker.py -r <redis url> -q <queue name> --burst
```

To have the worker run as a listener service, there are example service files included in this repo in `example_services`

Your application on another server would do something like this to create a SOLR core:
```
import rq

REDIS_QUEUE_NAME = 'my_redis_queue'
_solr_queues = {}

def create_solr_core(core_name, configset):
  global _solr_queues
  if REDIS_QUEUE_NAME in _solr_queues:
      redis_queue = _solr_queues[REDIS_QUEUE_NAME]
  else:
      redis_conn = connect_to_redis()
      redis_queue = _solr_queues[REDIS_QUEUE_NAME] = \
          rq.Queue(REDIS_QUEUE_NAME, connection=redis_conn)
  if not redis_queue:
      raise Exception("Could not connect to REDIS queue %s" % REDIS_QUEUE_NAME)
  job = redis_queue.enqueue_call(
      'solr_utils.create_solr_core.proc.create_solr_core',
      args=[core_name, configset],
      timeout=60)

create_solr_core('my_new_core', 'my_configset')
```
