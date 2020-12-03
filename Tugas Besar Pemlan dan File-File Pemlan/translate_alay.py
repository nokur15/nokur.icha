def translate_alay(huruf):
    switcher = {
        "a":"4",
        "e":"3",
        "i":"1",
        "o":"0",
        "r":"2",
        "s":"5",
        "g":"6",
        "t":"+",
    }
    return switcher.get(huruf,huruf)
mau_apa = input ("masukkan kalimat= ")
mau_apa = mau_apa.lower()

if len(mau_apa)>0:
    banyak= len(mau_apa)
    count= 0
    katabaru=""
    while count<banyak :
        katabaru = katabaru + translate_alay(mau_apa[count])
        count+=1
    print (katabaru)
else:
    print ("masukkan kata")
