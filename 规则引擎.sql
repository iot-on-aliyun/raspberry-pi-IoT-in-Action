SELECT 
deviceName() as deviceName, 
timestamp('yyyy-MM-dd') as time, 
items.gender.value as gender,
items.glass.value as glass,
items.age.value as age
FROM 
"/a1*****E/+/thing/event/property/post"