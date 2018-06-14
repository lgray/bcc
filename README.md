# bcc
BlockCollider Controller

This is a little wrapper for running instances of the BlockCollider docker distribution.
Should work on windows, mac, linux.

# Requirements
python 2.7

docker_py package -> [sudo] pip install docker

an active running docker installation

# Usage

N.B. -> replace my wallet key with yours, unless you're a very generous person

`python bc_controller.py install` -- install the 'latest' repository 

`python bc_controller.py install --tag=0.5.0` -- install the last 'testnet' repository (useful for testing this script)


`python bc_controller.py start --tag=0.5.0 --walletkey=0xf34fa87db39d15471bebe997860dcd49fc259318` -- start the testnet block collider

`python bc_controller.py start --walletkey=0xf34fa87db39d15471bebe997860dcd49fc259318` -- start the mainnet block collider (from latest repository)

`python bc_controller.py stop --tag=0.5.0` -- stop all block collider container instances and remove them

`python bc_controller.py restart --tag=0.5.0 --walletkey=0xf34fa87db39d15471bebe997860dcd49fc259318` -- stop and then start the test net again`

`python	bc_controller.py restart --walletkey=0xf34fa87db39d15471bebe997860dcd49fc259318` -- stop and then start the mainnet again

`python bc_controller.py start --tag=0.5.0 --walletkey=0xf34fa87db39d15471bebe997860dcd49fc259318 --nproc=2` -- start the testnet miner twice for two separate processors

`python bc_controller.py start --walletkey=0xf34fa87db39d15471bebe997860dcd49fc259318 --nproc=2` -- start the mainnet block collider (from latest repository) twice on two separate processors

`python bc_controller.py purge --tag=0.5.0` -- remove the testnet miner

`python bc_controller.py purge` -- remote the mainnet launcher

`python bc_controller.py --help` -- get more information about options