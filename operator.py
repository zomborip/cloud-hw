import kopf
import kubernetes
import yaml
import logging

INGRESS_CLASS_ANNOTATION = "traefik.ingress.kubernetes.io/router.entrypoints"
INGRESS_CLASS = "web"

def generate_ingress(service: dict, path: str, target_port: int):
    name = f"auto-ingress-{service['metadata']['name']}-http"
    namespace = service["metadata"]["namespace"]
    service_name = service["metadata"]["name"]

    ingress = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "annotations": {
                INGRESS_CLASS_ANNOTATION: INGRESS_CLASS
            },
        },
        "spec": {
            "rules": [{
                "http": {
                    "paths": [{
                        "path": path,
                        "pathType": "Prefix",
                        "backend": {
                            "service": {
                                "name": service_name,
                                "port": {
                                    "number": target_port
                                }
                            }
                        }
                    }]
                }
            }]
        }
    }
    return ingress

def get_http_target_port(service: dict) -> int:
    for port in service.get("spec", {}).get("ports", []):
        if port.get("name") == "http":
            return port.get("targetPort", 80)
    return 80

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.posting.level = 0

@kopf.on.create("v1", "services")
@kopf.on.update("v1", "services")
@kopf.on.resume("v1", "services")
def manage_ingress(body, spec, meta, namespace, **_):
    annotations = meta.get("annotations", {})
    path = annotations.get("auto-ingress")
    name = meta["name"]
    ingress_name = f"auto-ingress-{name}-http"

    logging.info(f"[auto-op] Service: {name}, út: {path}")

    networking = kubernetes.client.NetworkingV1Api()

    try:
        networking.read_namespaced_ingress(ingress_name, namespace)
        exists = True
        logging.info(f"[auto-op] Ingress {ingress_name} létezik.")
    except kubernetes.client.exceptions.ApiException as e:
        exists = False if e.status == 404 else (_ for _ in ()).throw(e)

    if path:
        port = get_http_target_port(body)
        logging.info(f"[auto-op] Ingress változás. port: {port}")
        ingress = generate_ingress(body, path, port)
        if exists:
            networking.patch_namespaced_ingress(ingress_name, namespace, ingress)
            logging.info(f"[auto-op] Ingress változás: {ingress_name}")
        else:
            networking.create_namespaced_ingress(namespace, ingress)
            logging.info(f"[auto-op] Ingress kész: {ingress_name}")
    elif exists:
        networking.delete_namespaced_ingress(ingress_name, namespace)
        logging.info(f"[auto-op] Törölt Ingress: {ingress_name}")

@kopf.on.delete("v1", "services")
def delete_ingress_on_service_delete(meta, namespace, **_):
    ingress_name = f"auto-ingress-{meta['name']}-http"
    networking = kubernetes.client.NetworkingV1Api()
    try:
        networking.delete_namespaced_ingress(ingress_name, namespace)
    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            raise


