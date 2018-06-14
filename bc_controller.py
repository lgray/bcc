#!/usr/bin/python

################################################################################
#Copyright (c) 2018 BlockCollider Foundation
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
################################################################################

# author: meanphysicist
# This script requires you have python2.7.
# The docker package ( [sudo] pip install docker).
# and docker must be running on your computer!

import argparse
import docker

parser = argparse.ArgumentParser(description='Command (multiple) block collider instances.')
parser.add_argument('command', help='the command to execute to BC Miner: start, stop, restart, install, purge')
parser.add_argument('--forever', default=False, action='store_true', help='instruct docker to run BC forever if it exits of its own accord')
parser.add_argument('--nproc', type=int, default=1, help='total number of processors available for mining')
parser.add_argument('--nprocpergroup', type=int, default=1, help='number of processors per docker instance')
parser.add_argument('--walletkey', default='', help='The BC wallet key that you want to collect NRG into')
parser.add_argument('--repo',default='blockcollider/bcnode', help='The BC docker repository, change only if you know what you are doing')
parser.add_argument('--tag',default='latest',help='The BC docker tag, change only if you know what you are doing')

class BlockColliderDocker(object):
    def __init__(self, **kwargs):
        self._docker = docker.from_env()
        self._nproc  = kwargs['nproc']
        self._nprocpergroup = kwargs['nprocpergroup']        
        self._nodename = 'bcnode'
        self._repo = kwargs['repo']
        self._tag = kwargs['tag']
        
        #do we want docker to keep on truckin'?
        self._forever = False
        if kwargs['forever']:
            self._forever = True
            
        #where do we send NRG to?
        self._walletkey = None
        if kwargs['walletkey'] != '':
            self._walletkey = kwargs['walletkey']

        if kwargs['command'] != 'install':
            try:
                self._bcnode = self._docker.images.get('%s:%s'%(self._repo,self._tag))
            except docker.errors.ImageNotFound as err:
                raise Exception('image "%s:%s" not found! please do "python bc_controller.py install" first'%(self._repo,
                                                                                                              self._tag))
        
        self._containers = self._docker.containers.list()
        
        
    def start(self):
        if self._walletkey is None:
            raise Exception('Starting BlockColliderDocker requires that you provide a wallet key!')
        print 'starting bcnode using %d processors with %d per container'%(self._nproc,self._nprocpergroup)
        restart_dict = {}
        if self._forever:
            restart_dict = {'Name': 'on-failure'}
        for iproc in xrange(0,self._nproc,self._nprocpergroup):
            container_name = 'bcc_%s_%d'%(self._nodename,iproc)
            print 'starting container: %s'%(container_name)
            self._docker.containers.run('%s:%s'%(self._repo,self._tag),
                                        './lib/cli/main.js start --ws --rovers --ui --node --miner-key %s'%(self._walletkey),
                                        name=container_name,
                                        ports = {'3000/tcp':3000+iproc,
                                                 '9090/tcp':9090+iproc},
                                        cpuset_cpus='%d-%d'%(iproc,iproc+self._nprocpergroup),
                                        restart_policy = restart_dict,
                                        detach=True)
            
        
    def stop(self):
        for inst in self._containers:
            if self._nodename in inst.name:
                print 'stopping container : %s'%inst.name
                inst.stop()
        self._docker.containers.prune()

    def restart(self):
        self.stop()
        self.start()
    
    def install(self):
        self._bcnode = self._docker.images.pull(self._repo,self._tag)
        

    def purge(self):
        self.stop()
        self._docker.images.remove(image = '%s:%s'%(self._repo,self._tag))

    def listImages(self):
        installed = self._docker.images.list()
        if len(installed) > 0:
            print 'installed images:'
            for i,inst in enumerate(installed):
                if 'blockcollider' in inst.attrs['RepoTags'][0]:
                    print '\t%d : %s'%(i+1,inst.attrs['RepoTags'][0])
        else:
            print 'no blockcollider repository images installed'

    def listContainers(self):
        running = self._docker.containers.list()
        if len(running) > 0:
            print 'running containers:'
            for i,inst in enumerate(running):   
                if 'bcc' in inst.name:
                    print '\t%d : %s'%(i+1,inst.name)
        else:
            print 'no running containers'

def bind_commands(bc):
    commands = {}
    commands['start'] = bc.start
    commands['stop'] = bc.stop
    commands['restart'] = bc.restart
    commands['install'] = bc.install
    commands['purge'] = bc.purge
    commands['listContainers'] = bc.listContainers
    commands['listImages'] = bc.listImages
    return commands

if __name__ == "__main__":
    args = parser.parse_args()
    todo = args.command
    
    bc = BlockColliderDocker(**vars(args))
    
    commands = bind_commands(bc)
    
    if todo not in commands.keys():
        print 'command %s is not accepted!'%todo
        valid_cmds = ' '.join(commands.keys())
        print 'valid commands: %s'%valid_cmds
        exit(1)
    
    commands[todo]()
