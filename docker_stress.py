#! /usr/bin/python

import subprocess
import time
import logging
import sys


class ContinueCreateDockers(object):
    def __init__(self):
        self.log_file = "docker_stress_test.log"
        self.test_clients = ["wh-netclient%d" % (x+1) for x in xrange(8)]
        self.dockers = ["wh-docker-test%02d" % (x+1) for x in xrange(24)]
        self.auth_url = "http://test_url:5000/v2.0/"
        self.username = "username"
        self.password = "password"
        self.tenant = "tenant"
        self.image = "b528e0c6-4fd5-4f23-98ff-4c8638c00888"
        self.flavor = "a3a89544-ea7b-409c-a060-49e233ecf689"
        self.net = "f45a2496-808d-4224-ac97-31b28bd651f9"
        self.pre_cmd = "nova --os-auth-url %s --os-tenant-name %s " \
                       "--os-username %s --os-password %s " % \
                       (self.auth_url, self.tenant,
                        self.username, self.password)
        self.client_map = {'wh-netclient1': self.dockers[0:3],
                           'wh-netclient2': self.dockers[3:6],
                           'wh-netclient3': self.dockers[6:9],
                           'wh-netclient4': self.dockers[9:12],
                           'wh-netclient5': self.dockers[12:15],
                           'wh-netclient6': self.dockers[15:18],
                           'wh-netclient7': self.dockers[18:21],
                           'wh-netclient8': self.dockers[21:24]}

    def set_logging(self):
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(filename)s "
                            "%(levelname)s %(message)s",
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=self.log_file,
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: \
                                       %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def get_docker_ip(self, docker):
        cmd = self.pre_cmd + "list|grep %s" % docker
        status_str = subprocess.check_output(cmd, shell=True)
        return status_str.split('=')[1].split('|')[0].strip()

    def wait_docker_status(self, name):
        start_time = int(time.time())
        while True:
            post_cmd = "list |grep %s" % name
            cmd = self.pre_cmd + post_cmd
            status_str = subprocess.check_output(cmd, shell=True)
            state = status_str.split('|')[3].strip()
            if state == "ACTIVE":
                logging.debug("Create docker success: %s" % name)
                break
            elif state == "ERROR":
                logging.error("Create docker fail: %s" % name)
                raise Exception("Docker %s status is EROOR" % name)
            time.sleep(5)
            timed_out = int(time.time()) - start_time >= 300
            if timed_out:
                logging.error("Create docker %s timeout in 60s,\ "
                              "now status is %s" % (name, state))
                raise Exception("Create docker %s time, \ "
                                "now state is %s" % (name, state))

    def create_docker(self):
        n = int(self.dockers[-1][-2:]) + 1
        name = "wh-docker-test%04d" % n
        post_cmd = "boot --availability-zone wh-docker-stress-test --image " \
                   "%s --flavor %s --nic net-id=%s %s" % \
                   (self.image, self.flavor, self.net, name)
        cmd = self.pre_cmd + post_cmd
        logging.debug("create one docker instance: %s" % name)
        subprocess.check_output(cmd, shell=True)
        self.wait_docker_status(name)
        self.dockers.append(name)
        return name

    def remove_docker(self):
        docker = self.dockers[0]
        subprocess.call("echo \"remove one docker instance: %s\"" % docker,
                        shell=True)
        logging.debug("remove one docker instance: %s" % docker)
        self.dockers.remove(docker)
        return docker

    def net_stress(self, client, server):
        logging.debug("Call salt to run net stress command")
        cmd = "salt \"%s\" cmd.run \"ping -c 3 %s\"" % (client, server)
        print subprocess.check_output(cmd % client)

    def update_client_map(self, added_server, removed_server):
        for client, server in self.client_map.items():
            if removed_server in server:
                self.client_map[client].remove(removed_server)
                self.client_map[client].append(added_server)
                return client

    def continue_create_and_remove(self):
        for x in xrange(1):
            added_docker = self.create_docker()
            removed_docker = self.remove_docker()
            added_docker_ip = self.get_docker_ip(added_docker)
            client = self.update_client_map(added_docker, removed_docker)
            self.net_stress(client, added_docker_ip)
            time.sleep(5)

if __name__ == "__main__":
    A = ContinueCreateDockers()
    A.set_logging()
    A.continue_create_and_remove()
