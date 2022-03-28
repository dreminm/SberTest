# Тестовое задание mlops
## Описание выполненной задачи
* Обучил модель классификации [птиц](https://www.kaggle.com/datasets/gpiosenka/100-bird-species)
* Логи обучения можно посмотреть здесь [wandb](https://wandb.ai/dreminm/SberBirdsTestAssignment)
* Выполнил сервинг модели в докер контейнере с использованием torchserve
** Файлы для архивирования модели находятся в папке [model](model)
** Конфигурация и архивированная модель находятся в папке [deployment](deployment)
** Докер образ собран с использованием [репозитория](https://github.com/pytorch/serve/tree/master/kubernetes/kserve)
** Провел тестирование модели на серевере с помощью [скрипта](get_train_results_from_server.py), ответы модели в [файле](test_answers.json), Accuracy = 0.957
* Также запустил сервинг модели с помощью kserve (нативная поддержка torchserve) на кластере minikube
** Манифесты находятся [здесь](kserving/)

##Обучение модели
* [Ноутбук с кодом для обучения](TrainModel.ipynb)

## Запуск докер с torchserve
* Собираем модель
```python
torch-model-archiver --model-name final_model --version 1.0 --model-file model/final_model.py --serialized-file model/final_model.pth --handler model/handler.py --extra-files model/index_to_name.json
mv final_model.mar deployment/model-store/
```
* Строим нужный образ с помощью [скрипта](https://github.com/pytorch/serve/blob/master/kubernetes/kserve/build_image.sh) (developer с gpu)
* Запускаем контейнер
```python
docker run --rm -it --gpus all -p 8080:8080 -p 8081:8081 --name mar -v deployment/model-store:/home/model-server/model-store  -v deployment/config.properties:/home/model-server/config.properties  pytorch/torchserve:latest-gpu
```
* Получаем предсказания модели
```bash
curl -X POST http://localhost:8080/predictions/final_model -T sample.jpg
```
```python
python get_train_results_from_server.py
```
## Запуск kserve на minikube
*  Запуск minikube
```bash
minikube start
```
* Установка Kserve и зависимостей
```bash
cd kserving
bash quick_install.sh
```
* Содаем PV, PVC
```bash
kubectl apply -f create_pv.yaml
kubectl apply -f create_pvc.yaml
```
* Создаем pod для копирования модели в PVC, копируем, удаляем
```bash
kubectl apply -f copypod.yaml
kubectl exec -it model-store-pod -c model-store -- mkdir /pv/model-store/
kubectl exec -it model-store-pod -c model-store -- mkdir /pv/config/
kubectl cp ../deployment/model-store/* model-store-pod:/pv/model-store/ -c model-store
kubectl cp ../deployment/config.properties.kserve model-store-pod:/pv/config/config.properties -c model-store 
kubectl delete pod model-store-pod
```
* Поднимаем InfernceService
```bash
kubectl apply -f kserve-gpu.yaml
```