import kopf
import kubernetes
from kubernetes.client import V1ObjectMeta, V1ServiceBackendPort, V1IngressServiceBackend, V1IngressBackend, V1HTTPIngressPath, V1HTTPIngressRuleValue, V1IngressRule, V1IngressSpec, V1Ingress, V1IngressTLS

def build_ingress_name(service_name: str) -> str:
    return f"auto-ingress-{service_name}-http"

def create_ingress(service: dict, path: str):
    name = service['metadata']['name']
    namespace = service['metadata']['namespace']
    ingress_name = build_ingress_name(name)

    port = service['spec']['ports'][0]['targetPort']

    api = kubernetes.client.NetworkingV1Api()

    ingress = V1Ingress(
        metadata=V1ObjectMeta(
            name=ingress_name,
            namespace=namespace,
            annotations={
                "traefik.ingress.kubernetes.io/router.entrypoints": "web"
            }
        ),
        spec=V1IngressSpec(
            rules=[
                V1IngressRule(
                    http=V1HTTPIngressRuleValue(
                        paths=[
                            V1HTTPIngressPath(
                                path=path,
                                path_type="Prefix",
                                backend=V1IngressBackend(
                                    service=V1IngressServiceBackend(
                                        name=name,
                                        port=V1ServiceBackendPort(number=port)
                                    )
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )

    api.create_namespaced_ingress(namespace=namespace, body=ingress)


def delete_ingress(service_name: str, namespace: str):
    ingress_name = build_ingress_name(service_name)
    api = kubernetes.client.NetworkingV1Api()
    try:
        api.delete_namespaced_ingress(name=ingress_name, namespace=namespace)
    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            raise

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.posting.level = 'INFO'

@kopf.on.create('v1', 'services')
@kopf.on.update('v1', 'services')
def service_create_or_update(spec, meta, body, namespace, **_):
    annotations = meta.get('annotations', {})
    name = meta['name']
    path = annotations.get('auto-ingress')

    if path:
        create_ingress(body, path)
    else:
        delete_ingress(name, namespace)

@kopf.on.delete('v1', 'services')
def service_delete(meta, namespace, **_):
    delete_ingress(meta['name'], namespace)


