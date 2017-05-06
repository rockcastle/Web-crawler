import re
import requests
from bs4 import BeautifulSoup as bs
import json
import shutil
import argparse
import sys

class product_search():
    def __init__(self,*args, **kwargs):
        super(product_search, self).__init__()
        #test_sayfa = "http://www.hepsiburada.com/gunes-gozlugu-c-1120745?sayfa=2"
        with open("product.json","w") as f:
            f.write("{}")
            f.close()
        try:
            p_args = argparse.ArgumentParser(description='Hepsiburadadan aranılan ürününlinkini verip istenilen sayfa sayısı kadar ürünlerin özelliklerinin json formatında listelenmesi')
            p_args.add_argument("-l",action='store', dest='Link',help="http://www.hepsiburada.com/gunes-gozlugu-c-1120745?sayfa=",type=str)
            p_args.add_argument("-c",action='store', dest='max_sayi',help="Çalıştırılacak sayfa sayısı",type=int)
            args = p_args.parse_args()
            if args.max_sayi <=1:
                args.max_sayi=2
            for i in range(1,int(args.max_sayi)):
                #self.ul = "http://www.hepsiburada.com/gunes-gozlugu-c-1120745?sayfa="+ str(i)  # "#http://www.hepsiburada.com/bilgisayarlar-c-2147483646?sayfa=1"http://www.hepsiburada.com/hawk-hw-1383-01-unisex-gunes-gozlugu-p-HBV0000004B4R"
                self.ul = str(args.Link) + str(i)
                self.padi = self.ul.split("/")
                self.d_adi= self.padi[len(self.padi)-1].split("-")[0]+"_"+self.padi[len(self.padi)-1].split("-")[1]
                self.hb = "http://www.hepsiburada.com"
                self.r = requests.get(self.ul)
                if self.r.status_code == 200:
                    #with open("product.json","w") as f:
                    #    f.write("{}")
                    #    f.close()
                    self.soap = bs(self.r.text, "html.parser")
                    self.get_product_links()
                    self.f_json = {}
                    # print(i)
            else:
                print("Hata: " + str(self.r.url))
        except:
            pass

    def get_product_links(self):
        try:
            #print(self.soap)
            sp = self.soap("ul", {'class': re.compile('^product-list results-container')})[0]
            #lnk = "http://www.hepsiburada.com/bottega-veneta-b-v-0020s-001-kadin-gunes-gozlugu-p-HBV000000484B" #No need this
            for i in sp("a"):
                ln = i.get("href")
                if ln.startswith("/"):
                    self.hb += ln
                    # print(self.hb)
                    self.get_product_detail(self.hb)
                self.hb = "http://www.hepsiburada.com"
        except:
            pass

    def get_product_detail(self, lnk):
        try:
            r2 = requests.get(lnk)
            if r2.status_code == 200:
                self.prc = {}
                self.soap2 = bs(r2.text, "html.parser")
                self.pName = self.soap2.html.head.title.get_text()

                pSpec = self.soap2("div",{"id": "tabProductDesc", "class": "list-item-detail product-detail box-container"})[0]("table")

                pOrijinalPrice = self.soap2("del", {"id": "originalPrice"})[0].get_text()
                pNewP = self.soap2("span", {"class": "price"})[0]["content"]
                yuzdeIndirimOranı = round(100 * (1 - (int(float(pNewP)) / int(pOrijinalPrice.split(" ")[0].split(",")[0]))))
                self.prc.update({"OrjinalFiyat": pOrijinalPrice, "indirimliFiyat": pNewP, "indirimOrani": yuzdeIndirimOranı})
                sy = 0
                with open("product.json") as f:
                    self.data = json.load(f)
                    f.close()
                for i in pSpec:
                    for k in i("div", {"id": "productDescriptionContent"}):
                        self.dsc = k.get_text().strip()
                    for l in i("div", {"id": "productTechSpecContainer"}):
                        self.tech = l.get_text().strip()
                        self.dsctech = self.tech.split("\n")
                        while True:
                            try:
                                self.dsctech.remove("")
                            except ValueError:
                                break
                        sy += 1
                self.stch = {}
                d = 0
                while d < len(self.dsctech):
                    if self.dsctech[d] == "Diğer":
                        self.dsctech.remove(self.dsctech[d])
                        #d += 1
                        pass
                    else:
                        self.stch.update({self.dsctech[d]: self.dsctech[d + 1]})
                        d += 2
                self.f_json = {self.pName: {"pDiscription": self.dsc, "dcsTech": self.stch, "pPrice": self.prc}}

                self.data.update(self.f_json)
                with open("product.json", "w") as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
                shutil.copy("product.json",self.d_adi+".json")

        except:
            pass


if __name__ == "__main__":
    product_search(sys.argv[1:])
