#!/usr/bin/env python3

import sys
import os
from os import path
import subprocess
from subprocess import call, check_output

class bcolors:
    PINK = '\033[95m'
    OKBLUE = '\033[36m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_with_color(text):
    text = text.\
           replace("{info}", bcolors.OKBLUE).\
           replace("{error}", bcolors.FAIL).\
           replace("{warning}", bcolors.WARNING).\
           replace("{ok}", bcolors.OKGREEN).\
           replace("{pink}", bcolors.PINK)
    text = "\n".join([x for x in text.split("\n")])
    print(text + bcolors.ENDC)

def format_with_color(text):
    text = text.\
           replace("{info}", bcolors.OKBLUE).\
           replace("{error}", bcolors.FAIL).\
           replace("{warning}", bcolors.WARNING).\
           replace("{ok}", bcolors.OKGREEN).\
           replace("{pink}", bcolors.PINK)
    text = "\n".join([x for x in text.split("\n")])
    return text + bcolors.ENDC

def delete_rc(options, service_name, version):
    return call(["kubectl", options.split()[0], options.split()[1], "delete", "rc", "{}-{}".format(service_name, version)])

def create_pod(options, yaml):
    return call(["kubectl", options.split()[0], options.split()[1], "create", "-f", yaml])

def push_image(service_name, version):
    return call(["gcloud", "docker", "--", "push", "eu.gcr.io/optimal-life-112611/{}:{}".format(service_name, version)])

def is_pod_up(options, service_name):
    pods = str(check_output(["kubectl", options.split()[0], options.split()[1], "get", "pods"]))
    return service_name in pods

def service_exists(options, service_name):
    services = str(check_output(["kubectl", options.split()[0], options.split()[1], "get", "services"]))
    return service_name in services

def create_service(service_name, version):
    return call(['kubectl', 'expose', 'rc', '{}-{}'.format(service_name, version), '--name={}'.format(service_name), '--port=80', '--target-port=80', '--selector=app={}'.format(service_name)])

def create_image():
    result = subprocess.Popen("./create_docker.sh")
    result.communicate()[0]
    return result.returncode

def rolling_update(options, service_name, version_old, yaml):
    return call(["kubectl", options.split()[0], options.split()[1], "rolling-update", "{}-{}".format(service_name, version_old), "-f", yaml])

def restart_rc(options, service_name, version, yaml):
    # kubectl {options} delete rc {service_name}-{version} &&
    if delete_rc(options, service_name, version) != 0:
        print_with_color("{{error}}[ERROR] Error al intentar borrar {{warning}}{}-{}".format(service_name, version))
        # kubectl {options} create -f {yaml}
    create_pod(options, yaml)

def create_and_push(service_name, version):
    if create_image() == 0:
        print_with_color("{{info}}[INFO] Publicando la imagen eu.gcr.io/optimal-life-112611/{}:{}".format(service_name, version))
        if push_image(service_name, version) != 0:
            print_with_color("{error}[ERROR] Error al publicar la imagen")
    else:
        print_with_color("{error}[ERROR] Fallo al crear el docker image")
        sys.exit(8)

def check_service_and_create(options, service_name, version):
    print_with_color("{{info}}[INFO] Comprobando si existe el servicio para {}".format(service_name))
    if service_exists(options, service_name):
        print_with_color("{{info}}[INFO] Existe el servicio para {{warning}}{}".format(service_name))
        sys.exit(0)
    else:
        print_with_color("{{info}}[INFO] No existe el servicio para {{warning}}{}".format(service_name))
        print_with_color("{{info}}[INFO] Creando el servicio para {{warning}}{}".format(service_name))
        if create_service(service_name, version) != 0:
            print_with_color("{error}[ERROR] No se pudo crear el servicio")
            sys.exit(11)

try:
    from update_version import update_version_main, rollback
except:
    print_with_color("{error}[ERROR] No update_version file")
    exit(2)

if len(sys.argv) < 4:
    print_with_color("{error}[ERROR] Tiene que haber al menos 3 argumentos")
    print_with_color("{{error}}[ERROR] ./{} [ pre | pro ] [ service name ] [ major | minor | patch | restart | redeploy ] [ yaml ]".format(os.path.basename(__file__)))
    sys.exit(1)

operation = sys.argv[3].lower()
if operation != "major" and operation != "minor" and operation != "patch" and operation != "restart" and operation != "redeploy":
    print_with_color("{error}[ERROR] El tercer argumento debe de ser: major, minor, patch, restart.")
    exit(1)

# check version file
if not path.isfile(".version"):
    print_with_color("{error}[ERROR] No existe el archivo '.version'. Por favor, cree un archivo .version con la version actual del servicio (Ex. echo 0.0.0 > .version)")
    sys.exit(2)

# check yaml
yaml = sys.argv[4]
if not path.isfile(yaml):
    print_with_color("{{error}}[ERROR] No existe el yaml {{warning}}{}".format(sys.argv[3]))
    sys.exit(3)

service_name = sys.argv[2]
version = open(".version").readline().strip()
    
# check pre or prod
type_version = sys.argv[1].lower()
if type_version == "pre":
    options = "--context gke_optimal-life-112611_europe-west1-b_gennion-prod-gce-cluster"
    inp = format_with_color("{{info}}[INFO] Publicando {{warning}}{0}{{info}} a {{warning}}{1}{{info}}\n[INFO] Estas seguro de querer publicar a {{warning}}{1}{{info}} [y/N]: ".format(service_name, type_version.upper()))
elif type_version == "pro":
    options = "--context gke_optimal-life-112611_europe-west1-d_gennion-live-gce-cluster"
    inp = format_with_color("{{info}}[INFO] Publicando {{error}}{0}{{info}} a {{error}}{1}{{info}}\n[INFO] Estas seguro de querer publicar a {{error}}{1}{{info}} [y/N]: ".format(service_name, type_version.upper()))
else:
    print_with_color("{error}[ERROR] El primer parametro debe de tener los valores: {{warning}}PRE {{error}}o {{warning}}PRO")
    sys.exit(4)

resp = input(inp).lower()

# Case yes
if resp == "yes" or resp == "y":
    # case redeploy
    if sys.argv[3].lower() == "redeploy":
        if not path.isfile("create_docker.sh"):
            print_with_color("{error}[ERROR] No existe el archivo 'create_docker.sh' necesario para crear la imagen del docker")
            sys.exit(6)

        # Crear docker image
        create_and_push(service_name, version)
        restart_rc(options, service_name, version, yaml)

        # Comprobar si existe service y crearlo si es necesario
        check_service_and_create(options, service_name, version)

    # case restart
    if sys.argv[3].lower() == "restart":
        # kubectl {options} delete rc {service_name}-{version} &&
        if delete_rc(options, service_name, version) != 0:
            print_with_color("{{error}}[ERROR] Error al intentar borrar {{warning}}{}-{}".format(service_name, version))
            sys.exit(5)
        # kubectl {options} create -f {yaml}
        create_pod(options, yaml)
    else:
        print_with_color("{info}[INFO] Subiendo version")
        if not path.isfile("update_version.py"):
            print_with_color("{error}[ERROR] No existe el programa 'update_version.py' necesario para subir la version.")
        else:
            if not path.isfile(".version_old"):
                version_old_old = None
            else:
                version_old_old = open(".version_old").readline()
            update_version_main(sys.argv[3])
        if not path.isfile("create_docker.sh"):
            print_with_color("{error}[ERROR] No existe el archivo 'create_docker.sh' necesario para crear la imagen del docker")
            sys.exit(6)
        else:
            version_old = open(".version_old").readline()
            version = open(".version").readline()

            # Create docker image
            if create_image() == 0:
                print_with_color("{{info}}[INFO] Publicando la imagen eu.gcr.io/optimal-life-112611/{}:{}".format(service_name, version))
                if push_image(service_name, version) != 0:
                    # rollback
                    rollback(version_old_old)

                if is_pod_up(options, service_name):
                    print_with_color("{{info}}[INFO] Haciendo el rolling update para {{warning}}{}-{}".format(service_name, version))
                    if rolling_update(options, service_name, version_old, yaml) != 0:
                        # rollback
                        rollback(version_old_old)
                        sys.exit(9)
                else:
                    print_with_color("{{info}}[INFO] Creando {{warning}}{}-{}".format(service_name, version))
                    if create_pod(options, yaml) != 0:
                        # rollback
                        rollback(version_old_old)
                        sys.exit(10)

                print_with_color("{{info}}[INFO] Comprobando si existe el servicio para {}".format(service_name))
                if service_exists(options, service_name):
                    print_with_color("{{info}}[INFO] Existe el servicio para {{warning}}{}".format(service_name))
                    sys.exit(0)
                else:
                    print_with_color("{{info}}[INFO] No existe el servicio para {{warning}}{}".format(service_name))
                    print_with_color("{{info}}[INFO] Creando el servicio para {{warning}}{}".format(service_name))
                    if create_service(service_name, version) != 0:
                        print_with_color("{error}[ERROR] No se pudo crear el servicio")
                        sys.exit(11)
            else:
                print_with_color("{error}[ERROR] Fallo al crear el docker image")
                # rollback
                rollback(version_old_old)
                sys.exit(8)
else:
    print_with_color("{info}[INFO] Cancelando despliegue, Yay! {pink}(つ◕_◕)つ")
