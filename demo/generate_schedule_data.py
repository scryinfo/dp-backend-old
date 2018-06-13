import random
import pandas as pd
from datetime import tzinfo, timedelta, datetime
import csv

df=pd.read_csv('/home/chuck/scry3/publisher/demo/data/routes.dat',names=['airline','airlineId','origin','originId','destination','destinationId','Codeshare','stops','equipment'])

data=df[['airline','equipment','origin','destination']].values.tolist()

#flight_route=0
airline=''
data2=[]
flight_number=''
flight_route=''
i=''


data2=[]

for i in data:
    if i[0]!=airline:
        flight_route=0
        airline=i[0]
    flight_route+=1
    n=str(flight_route)
    flight_number=airline+(3-len(n))*'0'+n

#    print(flight_number)
    d=random.randint(10,15)
    h=random.randint(0,23)
    m=random.randint(0,11)*5

    h2=h+random.randint(2,8)
    m2=m+random.randint(0,12)*5
    d2=d

    if m2>=60:
        m2=m2-60
        h2=h2+1

    if h2>=24:
        h2=h2-24
        d2=d2+1


    departureTime=datetime(2018, 6, d,h,m).isoformat()
    arrivalTime=datetime(2018, 6, d2,h2,m2).isoformat()

    i.insert(0,flight_number)
    i.append(departureTime)
    i.append(arrivalTime)
    data2.append(i)



csvfile = open('schedule.csv', 'w')
csvwriter = csv.writer(csvfile)
for item in data2:
    csvwriter.writerow(item)
csvfile.close()
