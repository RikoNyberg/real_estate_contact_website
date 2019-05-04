# real_estate_contact_crawler

Contact information crawler that is gathering all Finnish real estate agent contacts from the following real estate companies:

```
kiinteistomaailma
huom
op
reimax
sp
skv
huoneistokeskus
openmarket
```


## Run the website:
On a linux server that has a docker installed you can just run the following commands in the /gym_class_booking folder and you are up and running :D

```
$ docker run -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome

$ docker build -t contact_crawler .

$ docker run --rm --network host --name my_contact_crawler contact_crawler
```

```
$ docker build -t contacts .
$ docker run -d -p 5000:5000 contacts
```