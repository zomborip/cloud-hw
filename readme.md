# Cloud - K8S Homework

## AWS Setup:

Be kell lépni az [**Academy Learner Lab**](https://awsacademy.instructure.com/courses/111116/modules/items/10438056)-ba

Fel kell installálni a [**Labor K3S Stack**-et *(k3s-multinode)*](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://vitmac12-resources.s3.amazonaws.com/k3s-multinode.template&stackName=k3s-multinode) 

Be kell lépni két terminálba. Az *output* segítségével

## Setup & Virtual env

A virtuális környezet inicializálásához:

```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```

Lehet, hogy fog egy *sudo apt install-t* kérni

Másoljuk át a helyes K3S Login fileokat:
```bash
cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
```

A követelmények installálásához:

```bash
pip install -r requirements.txt
```

Le kell ellenőrizni, hogy biztosan be legyen állítava a megfelelő környezeti változó:

```bash
export KUBECONFIG=~/.kube/config
```

## Futtatás és tesztelés

Ehheza folyamathoz több terminálablakra lesz szükségünk. Az egyikben az auto-ingress script fut, a másikban pedig a Kubernetes parancsokat tudjuk kiadni

### Futtatás

Az auto-ingress script elindítása:
```bash
kopf run operator.py
```

### Teszteslés

Egy másik terminál ablakban teszteljük a test scriptekkel a dolgokat.

Teszt deployment init:
```bash
kubectl apply -f test-deployment.yaml
```

Test service init:
```bash
kubectl apply -f test-service.yaml
```

A szolgáltatás tesztelése:
```bash
curl http://[ingress-ip]/aaa
```
Itt az *\[ingrees-ip\]* az egy IP cím, amit a következőképpen lehet megtudni:
```bash
kubectl get ingress -A
```








