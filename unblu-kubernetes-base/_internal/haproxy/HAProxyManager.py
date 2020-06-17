#!/usr/bin/python

from kazoo.client import KazooClient
from kazoo.client import KazooState
import kazoo
import json
import logging
import time
import os
import sys
import subprocess
import signal

logging.basicConfig(format='%(asctime)s %(levelname)s %(pathname)s:%(lineno)s %(message)s',level=logging.INFO)


import signal
import time

class ExitOnSignals:
  exit = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.exit = True


workers = dict()
processes=[]
os.system("rsyslogd -i /tmp/rsyslogd.pid")
proc = subprocess.Popen("tail -F --retry /var/log/haproxy/haproxy.log",shell=True)

if len(sys.argv) != 4:
    logging.error("wrong number of arguments, please pass: zookeeper_connection_string zookeeper_worker_path backend_fallback_ipport")
    sys.exit(-1)

zookeeper_connection_string = sys.argv[1]
logging.info("zookeeper_connection_string: " + zookeeper_connection_string)

zk_path = sys.argv[2]
logging.info("zookeeper_worker_path: " + zk_path)

backend_fallback_ipport = sys.argv[3]
logging.info("backend_fallback_ipport: " + backend_fallback_ipport)


def connection_listener(state):
    if state == KazooState.LOST or state == KazooState.SUSPENDED:
        global workers
        workers=dict()
        zk.stop()
        updateConfig()
        connect()
        logging.warn("kazoo state :" + state)
    else:
        # Handle being connected/reconnected to Zookeeper
        logging.info("kazoo state changed " + str(state))



def connect():
    global zk
    while(True):
        zk = KazooClient(hosts=zookeeper_connection_string)
        zk.add_listener(connection_listener)
        try:
            zk.start()
            watch_path()
            return
        except kazoo.handlers.threading.KazooTimeoutError:
            logging.info("error while trying to connect to zookeeper.. retrying")


def updateConfig():
    acl = ""
    workers_backend = ""
    worker_backend = ""
    i = 1
    for process in processes:
        if process.poll() == None:
            for line in process.stdout:
                pass
            process.wait()
            processes.remove(process)

    use_fallback_backend=True
    for worker in workers:
        if workers[worker] == None:
            continue
        zi = str(i).zfill(3)
        acl += "    acl url_tag" + zi + " path_sub /node/" + workers[worker]["nodeId"] + "\n"
        acl += "    use_backend " + workers[worker]["nodeId"] + " if url_tag" + zi + "\n\n"
        worker_backend += "backend " + workers[worker]["nodeId"] + "\n"
        ipport = workers[worker]["endpoint"].lstrip("http://").lstrip("https://")
        worker_backend += "    server " + workers[worker]["nodeId"] + " " + ipport + " maxconn 1024\n\n"

        if not workers[worker]["acceptingNewSessions"] or not workers[worker]["healthy"] :
            workers_backend += "    #server " + workers[worker]["nodeId"] +" disabled due to not acceptingNewSessions or unhealthy state in zookeeper\n"
        else:
            use_fallback_backend=False
            workers_backend += "    server " + workers[worker]["nodeId"] + " " + ipport + " maxconn 1024\n"

        i += 1
    if use_fallback_backend:
        workers_backend += "    server worker_fallback " + backend_fallback_ipport + " maxconn 1024\n"
    configuration = """
global
    log /tmp/log local0 info
    log /tmp/log local0 notice
    maxconn 4096

defaults
    log global
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

listen stats
    bind 127.0.0.1:1936
    mode http
    stats enable
    stats hide-version  # Hide HAProxy version
    stats uri /

frontend healthz
    bind *:10253 name healthz_1
    mode http
    monitor-uri /healthz
    option dontlog-normal
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend http-in
    bind *:8080
    default_backend workers

""" + acl

    configuration += "\nbackend workers\n    balance roundrobin\n\n" + workers_backend + "\n\n" + worker_backend
    global oldconfig
    if oldconfig != configuration:
        logging.info(configuration.replace("\n", ";")) # quick hack to keep the config on one line.
        oldconfig = configuration
        logging.info("config changed, reloading haproxy")
        f = open("/usr/local/etc/haproxy/haproxy.cfg", "w")
        f.write(configuration)
        f.close()
        proc = subprocess.Popen("haproxy -n 10000 -D -f /usr/local/etc/haproxy/haproxy.cfg -p /var/run/haproxy.pid -sf $(cat /var/run/haproxy.pid)",shell=True,stdout=subprocess.PIPE)
        processes.append(proc)

def watch_path():
    while (not zk.exists(zk_path)):
        logging.info("the zk path " + zk_path + " does not exist! Waiting for it to become available")
        time.sleep(5)
    @zk.ChildrenWatch(zk_path)
    def watch_children(children):
        @zk.DataWatch(zk_path)
        def data_watch(data, stat):
            logging.info("worker path changed! " + str(data))
            if data==None and stat==None:
                print (zk_path+" disappeared, trying to recreate listener")
                watch_path()
                return False

        logging.info("Children are now: %s" % children)
        for child in children:
            if (not child in workers):
                workers[child] = None

                @zk.DataWatch(zk_path + "/" + child)
                def data_watch(data, stat):
                    if data == None and stat == None:
                        logging.debug("removing worker node data watcher ")
                        return False
                    try:
                        j = json.loads(data)
                    except ValueError:
                        logging.warn("Unable to parse JSON", exc_info=True)
                        # cannot parse data (not json)
                        return
                    nodeId = j["nodeId"]
                    workers[nodeId] = j
                    logging.debug("datawatch " + str(data))
                    updateConfig()

        workersToDelete = []
        for worker in workers:
            if workers[worker] == None:
                workersToDelete.append(worker)
            elif not worker in children:
                workersToDelete.append(worker)
        for deletableWorker in workersToDelete:
            logging.info("removing worker " + deletableWorker)
            del workers[deletableWorker]
        updateConfig()


oldconfig = ""
updateConfig()
connect()

signals = ExitOnSignals()
while not signals.exit:
    time.sleep(1)
