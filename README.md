kubectl --kubeconfig $PWD/config.yaml apply -f pv.yaml
kubectl --kubeconfig $PWD/config.yaml apply -f pvc.yaml
docker build -t pvrsaikumar/cs695:dindserver . --file ./Dind_Dockerfile
docker push pvrsaikumar/cs695:dindserver
kubectl --kubeconfig $PWD/config.yaml apply -f nodeport.yaml
kubectl --kubeconfig $PWD/config.yaml apply -f clusterip.yaml
kubectl --kubeconfig $PWD/config.yaml apply -f server.yaml
