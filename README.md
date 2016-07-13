## CPU Pinning Nailgun Extension

This Nailgun extension allows you to override provisioning and deployment data for select machines in the cluster, to allow per-node settings for CPU pinning feature

## Installation

`setup.py install`
During the installation extension will register itself in all existing clusters and releases.

## API Reference

Nailgun REST API is extended with a new uri:
`/api/nodes/<node-id>/cpu-pinning/`

API supports GET, PUT and DELETE requests, example data for PUT request would be:
`'http://localhost:8000/api/nodes/1/cpu-pinning', headers={'X-Auth-Token': token}, data=json.dumps({'nova_cores':[1,2,3], {'vrouter_cores':[4,5,6]})`

## fuelclient commands

There are two new fuel2 commands that work with API endpoints and allow you to set, get and delete cpu pinning values for nodes, here are example uses:

`fuel2 cpu-pinning-set --node 32 --vrouter_cores 1,3 --nova_cores 18,20,22,8`

`fuel2 cpu-pinning-get --node 32`

`fuel2 cpu-pinning-del --node 32`
