#! /usr/bin/python

import subprocess
import time
import logging
import sys


class ContinueCreateDockers(object):
    def __init__(self):
        self.log_file = "docker_stress_test.log"
        self.test_clients = ["wh-netclient%02d" % (x+1) for x in xrange(8)]
        self.dockers = ["wh-docker-test%04d" % (x+1) for x in xrange(24)]
        self.dockers_info = []

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

    def create_init_dockers(self):
        for d in self.dockers:
            logging.debug("Create docker: %s" % d)
            try:
                cmd = 'ifconfig en0|grep "inet *\.*\.*\.* "|awk \'{print $2}\''
                ip = subprocess.check_output(cmd, shell=True)
                self.dockers_info.append((d, str(ip).strip('\n')))
            except subprocess.CalledProcessError, error:
                logging.error("Create test docker fail, error:%s" % str(error))
                sys.exit(1)

    def create_docker(self):
        n = int(self.dockers[-1][-4:]) + 1
        name = "wh-docker-test%04d" % n
        subprocess.call("echo \"create one docker instance:%s\"" % name,
                        shell=True)
        logging.debug("create one docker instance: %s" % name)
        self.dockers.append(name)

    def check_created_docker_ip(self):
        logging.debug("Check docker\'s ip if pingable")
        subprocess.call("echo \"Check created docker ip if pingable\"")

    def remove_docker(self):
        docker = self.dockers[0]
        subprocess.call("echo \"remove one docker instance: %s\"" % docker,
                        shell=True)
        logging.debug("remove one docker instance: %s" % docker)
        self.dockers.remove(docker)

    def continue_create_and_remove(self):
        for x in xrange(1):
            self.remove_docker()
            self.create_docker()
            time.sleep(5)

if __name__ == "__main__":
    A = ContinueCreateDockers()
    A.set_logging()
    A.create_init_dockers()
    A.continue_create_and_remove()
    print A.dockers_info
