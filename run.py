# -*- coding:utf-8 -*-

import requests
from bs4 import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import Tkinter as tk
import tkMessageBox
import pandas as pd
import getpass
import os


baseurl = "http://www.whatclinic.com"
current_url_normal = ""
driver = webdriver.PhantomJS(service_args=['--load-images=no'])
driver.get(baseurl)
headers = {'User-Agent': 'Mozilla/5.0'}
total_number_of_doctors = 0
total_num = 0
i = 0
counter = 0
n = 0

def search_tool():
    global current_url_normal
    if counter == 0:
        while True:
            clinicname = clinicname_box.get()
            locationname = locationname_box.get()
            if len(clinicname) == 0 or len(locationname) == 0:
                yazi["text"] = "Bütün alanları eksiksiz doldur."
                window.update()
            else:
                break
        clinic = driver.find_element_by_id("treatment_inputbox")
        location = driver.find_element_by_id("country_inputbox")
        clinic.send_keys(clinicname, Keys.TAB)
        location.send_keys(locationname, Keys.TAB)
        driver.find_element_by_id("myHeader_mySearchBox_ButtonFind").click()
        current_url_normal = driver.current_url
        return driver.current_url
    else:
        return current_url_normal


def page_number_change():
    global counter
    yazi["text"] = str(counter) + " of " + str(total_num + 1) + "\nSayfalar İnceleniyor.."
    window.update()
    link = str(search_tool()) + "#page=" + str(counter - 1)
    counter += 1
    return link


def page_source():
    yazi["text"] = "Sayfa Kaynak Kodları Okunuyor.."
    window.update()
    currenturl = str(page_number_change())
    driver.get(currenturl)
    html_source = driver.page_source
    soupall = BeautifulSoup(html_source, "html.parser")
    return soupall


def total_page_number():
    global total_number_of_doctors
    global total_num
    if counter == 0:
        soupall = page_source()
        for ii in soupall.find_all("div", class_="result_count"):
            link = ii.renderContents()
            linklist = link.split()
            total_number_of_doctors = int(linklist[5])
            total_num = (int(int(linklist[5]) / 12.9))
            return total_num
    else:
        pass

def source_link_finder():
    yazi["text"] = "Sayfa Linkleri Oluşturuluyor.."
    window.update()
    all_list = []
    numb_link_list = []
    link_list = []
    soupall = page_source()
    for link in soupall.find_all("a", class_="text-elipse nocss-brochure-link"):
        link_render = baseurl + str(link.get("href"))
        link_list.append(link_render)
    for ii in soupall.find_all("a", class_="jq_phoneLink thickbox"):
        link = ii.get("href")
        link_all = baseurl + str(link)
        numb_link_list.append(link_all)
    all_list.append(link_list)
    all_list.append(numb_link_list)
    return all_list


def all_link_list_creator():
    yazi["text"] = "Doktor Linkleri Oluşturuluyor.."
    window.update()
    normal_link_list = []
    direct_link_list = []
    all_link_list2 = []

    page_number = int(total_page_number()) + 1
    page_counter = 0

    while page_counter < page_number:
        all_link_list = source_link_finder()
        normal_link_list += all_link_list[0]
        direct_numbers = all_link_list[1]

        if len(direct_numbers) != 0:
            direct_link_list += direct_numbers
        page_counter += 1

    all_link_list2.append(normal_link_list)

    if len(direct_link_list) != 0:
        all_link_list2.append(direct_link_list)

    return all_link_list2


def phone_number_link_creator(pagesource):
    """"span class onclick icerisinde bulunan linki ceker"""
    soup = BeautifulSoup(pagesource, "html.parser")
    soup_special = soup.select_one("span.pseudoLink")
    data = (soup_special).encode("utf-8")
    show_number_btn_link = data.split()
    number_page = show_number_btn_link[3]
    return number_page[1:-2].replace("amp;","")

def doctor_name(pagesource):
    soup = BeautifulSoup(pagesource, "html.parser")
    for i in soup.find_all("h1"):
        return i.renderContents()

def doctor_name_direct_links(soup):
    for i in soup.find_all("h2"):
        for z in i.find_all("label"):
            return z.renderContents()

def start_info():
    return str(total_number_of_doctors) + " adet doktor veya sağlık kuruluşu bulundu.\n" \
                                       "İsim soyisim veya kuruluş adı ve numaralar kayıt edilmeye" \
                                        " başlandı."

def finish_message():
    tkMessageBox.showinfo("WhatClinic.com Bot", "İşlem Başarıyla Tamamlandı.")

def take_number():
    global counter
    link_list = all_link_list_creator()
    name_list = []
    phone_number_list = []
    nn = 1
    yazi["text"] = "Aramaya başlanıyor.."
    window.update()
    yazi["text"] = start_info()
    window.update()
    for i in link_list[0]:
        doctor_links = requests.get(i)
        source = doctor_links.text
        number_links = requests.get(phone_number_link_creator(source),headers=headers)
        source2 = number_links.text
        soup = BeautifulSoup(source2, "html.parser")
        phone_number = soup.select_one("span.phone_number").renderContents()
        name_list.append(str(doctor_name(source)))
        phone_number_list.append(str(phone_number))
        write = "\n" + str(doctor_name(source)) + " - " + str(phone_number)
        nn += 1
        yazi["text"] = "(" + str(nn - 1) + " of " + str(total_number_of_doctors) + ") " + write
        window.update()
    if len(link_list[1]) != 0:
        window.update()
        for z in link_list[1]:
            window.update()
            direct_links = requests.get(z)
            source3 = direct_links.text
            soup3 = BeautifulSoup(source3, "html.parser")
            phone_number3 = soup3.select_one("span.phone_number").renderContents()
            write2 = "\n" + str(doctor_name_direct_links(soup3)) + " - " + str(phone_number3)
            name_list.append(str(doctor_name_direct_links(soup3)))
            phone_number_list.append(str(phone_number3))
            yazi["text"] = "(" + str(nn - 1) + " of " + str(total_number_of_doctors) + ")" + write2
            nn += 1
            window.update()
    computer_username = getpass.getuser()
    system_harddrive_name = os.getenv("SystemDrive")
    if desktop.get() == 1:
        desktop_path = os.path.join(system_harddrive_name, "\\Users", computer_username, "Desktop")
        df = pd.DataFrame({"İsim": name_list, "Numara": phone_number_list})
        writer = pd.ExcelWriter(desktop_path + "\\" + clinicname_box.get().title() + ".xlsx")
        df.to_excel(writer, sheet_name="Sheet1", index=False)
        writer.save()
    if current_path.get() == 1:
        newpath = 'Numbers'
        if not os.path.exists(newpath):
            os.mkdir(newpath)
        else:
            pass
        df = pd.DataFrame({"İsim": name_list, "Numara": phone_number_list})
        writer = pd.ExcelWriter(newpath + "\\" + clinicname_box.get().title() + ".xlsx")
        df.to_excel(writer, sheet_name="Sheet1", index=False)
        writer.save()
    if desktop.get() == 0 and desktop.get() == 0:
        yazi["text"] = "Lütfen kaydedilecek bir dizin seç."

    finish_message()
    if (int(total_number_of_doctors) - nn) != 0:
        yazi["text"] = "Aynı isme veya telefon numarasına sahip " + str((int(total_number_of_doctors) - (nn - 1))) + \
            " adet sağlık kuruluşu veya doktor atlandı.\n" \
        + str(nn-1) + " adet numara başarıyla kaydedildi!"
    counter = 0

def iletisim_sayfasi():
    mail = "Mail: ertgrlkutluer@gmail.com"
    window_iletisim = tk.Toplevel()
    window_iletisim.iconbitmap("bot_ico.ico")
    window_iletisim.geometry("250x75+170+170")
    yazi_iletisim = tk.Text(window_iletisim, height=1)
    yazi_iletisim.insert(1.0, mail)
    yazi_iletisim.configure(bg=window_iletisim.cget('bg'), relief="flat")
    yazi_iletisim.configure(state="disabled")
    yazi_iletisim.pack()
    yazi_program_version = tk.Label(window_iletisim, text = "v1.0")
    yazi_program_version.pack()
    btn_in_iletisim = tk.Button(window_iletisim,text = "Çıkış", command = window_iletisim.destroy)
    btn_in_iletisim.pack()


window = tk.Tk()
window.geometry("450x150+150+150")
window.title("WhatClinic.com Bot v1.1")
window.iconbitmap("bot_ico.ico")
window.resizable(width=False, height=False)

yazi = tk.Label(text = "Lütfen Gerekli Bilgileri Girin")
yazi.pack()

clinicname_entry = tk.Label(text = "Klinik Adı")
clinicname_entry.place(relx = 0.05, rely = 0.30)
clinicname_box = tk.Entry()
clinicname_box.place(relx = 0.23, rely = 0.30)

locationname_entry = tk.Label(text = "Lokasyon")
locationname_entry.place(relx = 0.05, rely = 0.50)
locationname_box = tk.Entry()
locationname_box.place(relx = 0.23, rely = 0.50)

desktop = tk.IntVar()
desktop.set(1)
current_path = tk.IntVar()
current_path.set(0)

save_place = tk.Label(text = "Dosya Nereye Kaydedilsin?")
save_place.place(relx = 0.59, rely = 0.23)

desktop_checkbox = tk.Checkbutton(text = "Masaüstü", variable = desktop)
desktop_checkbox.place(relx = 0.66, rely = 0.37)

current_path_checkbox = tk.Checkbutton(text = "Programın Bulunduğu Dizin",variable = current_path)
current_path_checkbox.place(relx = 0.55, rely = 0.51)

gonder = tk.Button(text="Başlat",height = 1, width = 15, command = take_number)
gonder.place(relx = 0.08, rely = 0.75)

cikis = tk.Button(text="Çıkış",height = 1, width = 10, command = window.quit)
cikis.place(relx = 0.55, rely = 0.75)

iletisim_buton = tk.Button(text = "İletişim",height = 1, width = 10,command = iletisim_sayfasi)
iletisim_buton.place(relx = 0.75, rely = 0.75)

window.mainloop()

driver.quit()
