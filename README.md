------------------------------------------------------------------------------------------------------
ATELIER API-DRIVEN INFRASTRUCTURE
------------------------------------------------------------------------------------------------------
L’idée en 30 secondes : **Orchestration de services AWS via API Gateway et Lambda dans un environnement émulé**.  
Cet atelier propose de concevoir une architecture **API-driven** dans laquelle une requête HTTP déclenche, via **API Gateway** et une **fonction Lambda**, des actions d’infrastructure sur des **instances EC2**, le tout dans un **environnement AWS simulé avec LocalStack** et exécuté dans **GitHub Codespaces**. L’objectif est de comprendre comment des services cloud serverless peuvent piloter dynamiquement des ressources d’infrastructure, indépendamment de toute console graphique.Cet atelier propose de concevoir une architecture API-driven dans laquelle une requête HTTP déclenche, via API Gateway et une fonction Lambda, des actions d’infrastructure sur des instances EC2, le tout dans un environnement AWS simulé avec LocalStack et exécuté dans GitHub Codespaces. L’objectif est de comprendre comment des services cloud serverless peuvent piloter dynamiquement des ressources d’infrastructure, indépendamment de toute console graphique.
  
-------------------------------------------------------------------------------------------------------
Séquence 1 : Codespace de Github
-------------------------------------------------------------------------------------------------------
Objectif : Création d'un Codespace Github  
Difficulté : Très facile (~5 minutes)
-------------------------------------------------------------------------------------------------------
RDV sur Codespace de Github : <a href="https://github.com/features/codespaces" target="_blank">Codespace</a> **(click droit ouvrir dans un nouvel onglet)** puis créer un nouveau Codespace qui sera connecté à votre Repository API-Driven.
  
---------------------------------------------------
Séquence 2 : Création de l'environnement AWS (LocalStack)
---------------------------------------------------
Objectif : Créer l'environnement AWS simulé avec LocalStack  
Difficulté : Simple (~5 minutes)
---------------------------------------------------

Dans le terminal du Codespace copier/coller les codes ci-dessous etape par étape :  

**Installation de l'émulateur LocalStack**  
```
sudo -i mkdir rep_localstack
```
```
sudo -i python3 -m venv ./rep_localstack
```
```
sudo -i pip install --upgrade pip && python3 -m pip install localstack && export S3_SKIP_SIGNATURE_VALIDATION=0
```
```
localstack start -d
```
**vérification des services disponibles**  
```
localstack status services
```
**Réccupération de l'API AWS Localstack** 
Votre environnement AWS (LocalStack) est prêt. Pour obtenir votre AWS_ENDPOINT cliquez sur l'onglet **[PORTS]** dans votre Codespace et rendez public votre port **4566** (Visibilité du port).
Réccupérer l'URL de ce port dans votre navigateur qui sera votre ENDPOINT AWS (c'est à dire votre environnement AWS).
Conservez bien cette URL car vous en aurez besoin par la suite.  

Pour information : IL n'y a rien dans votre navigateur et c'est normal car il s'agit d'une API AWS (Pas un développement Web type UX).

---------------------------------------------------
Séquence 3 : Exercice
---------------------------------------------------
Objectif : Piloter une instance EC2 via API Gateway
Difficulté : Moyen/Difficile (~2h)
---------------------------------------------------  
Votre mission (si vous l'acceptez) : Concevoir une architecture **API-driven** dans laquelle une requête HTTP déclenche, via **API Gateway** et une **fonction Lambda**, lancera ou stopera une **instance EC2** déposée dans **environnement AWS simulé avec LocalStack** et qui sera exécuté dans **GitHub Codespaces**. [Option] Remplacez l'instance EC2 par l'arrêt ou le lancement d'un Docker.  

**Architecture cible :** Ci-dessous, l'architecture cible souhaitée.   
  
![Screenshot Actions](API_Driven.png)   
  
---------------------------------------------------  
## Processus de travail (résumé)

1. Installation de l'environnement Localstack (Séquence 2)
2. Création de l'instance EC2
3. Création des API (+ fonction Lambda)
4. Ouverture des ports et vérification du fonctionnement

---------------------------------------------------
Séquence 4 : Documentation  
Difficulté : Facile (~30 minutes)
---------------------------------------------------
**Complétez et documentez ce fichier README.md** pour nous expliquer comment utiliser votre solution.  
Faites preuve de pédagogie et soyez clair dans vos expliquations et processus de travail.  
Réponse :
## Objectif

Cet atelier a pour objectif de concevoir une architecture API-driven permettant de piloter une infrastructure via des appels HTTP.

Une requête HTTP envoyée à une API déclenche une fonction Lambda qui exécute des actions sur une instance EC2 dans un environnement AWS simulé avec LocalStack.

---

## Architecture

L’architecture mise en place repose sur les composants suivants :

- API Gateway : point d’entrée HTTP
- Lambda : logique métier (start / stop)
- EC2 : ressource pilotée
- LocalStack : simulation AWS

Flux :

Client → API Gateway → Lambda → EC2

---

## Mise en place de l’environnement

### Installation de LocalStack

```bash
python3 -m venv rep_localstack
pip install localstack
Configuration du token
export LOCALSTACK_AUTH_TOKEN=YOUR_TOKEN
Lancement
localstack start -d
Vérification
curl http://localhost:4566/_localstack/health
Configuration AWS CLI
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
Création de l’instance EC2
AMI_ID=$(aws --endpoint-url=http://localhost:4566 ec2 describe-images \
  --owners amazon \
  --query "Images[0].ImageId" \
  --output text)

aws --endpoint-url=http://localhost:4566 ec2 run-instances \
  --image-id "$AMI_ID" \
  --instance-type t2.micro

Récupération de l’instance :

aws --endpoint-url=http://localhost:4566 ec2 describe-instances \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text
Création de la Lambda
Code
import json
import boto3
import os

INSTANCE_ID = os.environ.get("INSTANCE_ID")

ec2 = boto3.client(
    "ec2",
    endpoint_url="http://localhost.localstack.cloud:4566",
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

def lambda_handler(event, context):
    path = event.get("rawPath") or event.get("path", "")

    if path.endswith("/start"):
        ec2.start_instances(InstanceIds=[INSTANCE_ID])
        return {"statusCode": 200, "body": json.dumps({"action": "start", "instance_id": INSTANCE_ID})}

    if path.endswith("/stop"):
        ec2.stop_instances(InstanceIds=[INSTANCE_ID])
        return {"statusCode": 200, "body": json.dumps({"action": "stop", "instance_id": INSTANCE_ID})}

    return {"statusCode": 400, "body": json.dumps({"error": "invalid route"})}
Déploiement
zip lambda.zip lambda_function.py
aws --endpoint-url=http://localhost:4566 iam create-role \
  --role-name lambda-ec2-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'
aws --endpoint-url=http://localhost:4566 lambda create-function \
  --function-name ec2-controller \
  --runtime python3.12 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda.zip \
  --role arn:aws:iam::000000000000:role/lambda-ec2-role \
  --environment Variables="{INSTANCE_ID=YOUR_INSTANCE_ID}"
Création de l’API Gateway
API_ID=$(aws --endpoint-url=http://localhost:4566 apigatewayv2 create-api \
  --name ec2-api \
  --protocol-type HTTP \
  --query "ApiId" \
  --output text)
INTEGRATION_ID=$(aws --endpoint-url=http://localhost:4566 apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:us-east-1:000000000000:function:ec2-controller \
  --payload-format-version 2.0 \
  --query "IntegrationId" \
  --output text)
Routes
aws --endpoint-url=http://localhost:4566 apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "GET /start" \
  --target "integrations/$INTEGRATION_ID"
aws --endpoint-url=http://localhost:4566 apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "GET /stop" \
  --target "integrations/$INTEGRATION_ID"
Stage
aws --endpoint-url=http://localhost:4566 apigatewayv2 create-stage \
  --api-id $API_ID \
  --stage-name dev \
  --auto-deploy
Tests
Start
curl "http://localhost:4566/restapis/$API_ID/dev/_user_request_/start"
Stop
curl "http://localhost:4566/restapis/$API_ID/dev/_user_request_/stop"
Résultat
{"action":"start","instance_id":"i-..."}
{"action":"stop","instance_id":"i-..."}
Conclusion

Cet atelier démontre qu’il est possible de piloter dynamiquement une infrastructure via des API HTTP en s’appuyant sur des services serverless.

L’utilisation de LocalStack permet de reproduire un environnement AWS complet en local, facilitant le développement et les tests.

Cette approche API-driven permet une automatisation avancée des infrastructures et s’intègre parfaitement dans des architectures modernes orientées microservices et cloud.


---------------------------------------------------
Evaluation
---------------------------------------------------
Cet atelier, **noté sur 20 points**, est évalué sur la base du barème suivant :  
- Repository exécutable sans erreur majeure (4 points)
- Fonctionnement conforme au scénario annoncé (4 points)
- Degré d'automatisation du projet (utilisation de Makefile ? script ? ...) (4 points)
- Qualité du Readme (lisibilité, erreur, ...) (4 points)
- Processus travail (quantité de commits, cohérence globale, interventions externes, ...) (4 points) 
