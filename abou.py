#!/usr/bin/env python
#-*- coding:utf-8 -*-
import gtk
def hakkinda():
	hakkinda = gtk.AboutDialog()	
	hakkinda.set_title(program_name)
	hakkinda.set_program_name(program_name)
	hakkinda.set_version(version) 
	hakkinda.set_copyright(copyright)
	hakkinda.set_icon_from_file(icon)
	hakkinda.set_license(lisans)
	hakkinda.set_website(website)
	hakkinda.set_authors(authors)
	logo = gtk.gdk.pixbuf_new_from_file_at_size(icon, 148, 148)
	hakkinda.set_logo(logo)	
	
	hakkinda.show_all()
	if  hakkinda.run() == gtk.RESPONSE_CANCEL:     
		hakkinda.destroy()
lisans = """ 
Grub_On özgür bir yazılımdır, onu Özgür Yazılım
Vakfı'nın yayınladığı GNU Genel Kamu Lisansı'nın 2.
sürümü veya (tercihinize bağlı) daha sonraki sürümleri
altında dağıtabilir ve/veya değiştirebilirsiniz.


Grub_On  faydalı olacağı umut edilerek dağıtılmaktadır,
fakat HİÇBİR GARANTİSİ YOKTUR; hatta ÜRÜN DEĞERİ
ya da BİR AMACA UYGUNLUK gibi garantiler de
vermez. Lütfen GNU Genel Kamu Lisansı'nı daha fazla
ayrıntı için inceleyin. """

website = "http://launchpad.net/grub-on"

copyright = "UGT"

icon = "./grub_on.png"

program_name = "Grub-On"

version = "1.1"

authors = ["hitokiri  <aaANILaa@gmail.com>","Enes Ateş <atesenes67@gmail.com>","Utku Demir <utdemir@gmail.com>"] 
