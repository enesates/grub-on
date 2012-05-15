#!/usr/bin/env python
#! coding:utf-8 -*-
 
import parser
import abou

import gtk ,pango
import subprocess
import re
import sys
import os
import gtksourceview2 as edit
 


DefaultGrubConfig=parser.DefaultGrubConfig()
DefaultGrubConfig.path="/etc/default/grub"
DefaultGrubConfig.read()

GrubCfgConfig=parser.GrubCfgConfig()
GrubCfgConfig.path="/boot/grub/grub.cfg"
GrubCfgConfig.read()

programPath = "/usr/share/grub-on"
BACKUP_PATH = programPath+"/backup/"
#BACKUP_PATH="/home/user/" # uncomment this for using another backup path

GRUB_UPDATE_COMMAND="update-grub"
class Gui(gtk.Window):

	def __init__(self):
		gtk.Window.__init__(self)
		self.set_title("Grub-on")
		self.connect("delete-event",gtk.main_quit)
		self.set_icon_from_file("./grub_on.png")
        
		self.builder = gtk.Builder()
		self.builder.add_from_file("./ui.glade")
		self.box = self.builder.get_object("vbox1")
		self.add(self.box)  
        
		kontak = [self.up,self.down,self.setDefault,self.append,self.remove,self.backup,self.restore,self.reset,self.save,self.abou,self.undo,self.help ]
        
		for x in range(1,13) :
			buton = "button%s" %(x)
			buton = self.builder.get_object(buton)
			buton.connect("clicked", kontak[x -1] )
        	
		self.store = gtk.TreeStore(gtk.gdk.Pixbuf,str)
		self.treeview = self.builder.get_object("treeview1")
		self.treeview.set_model(self.store)
		self.treeview.connect("cursor-changed",self.active_item)

		self.col = gtk.TreeViewColumn()

		self.render_pix = gtk.CellRendererPixbuf()
		self.col.pack_start(self.render_pix, expand=False)
		self.col.add_attribute(self.render_pix, 'pixbuf',0)
	
		self.render_text = gtk.CellRendererText()
		self.render_text.set_property("weight",pango.WEIGHT_BOLD)
		self.col.pack_start(self.render_text, expand=True)
		self.col.add_attribute(self.render_text, 'text',1)

		self.treeview.append_column(self.col)
		self.treeview.set_headers_visible(False)
	
		self.sw = self.builder.get_object("scrolledwindow2")
		self.edit = edit.View()	
		self.edit.set_wrap_mode(gtk.WRAP_CHAR)	
		self.buffer =  edit.Buffer()
		self.edit.set_buffer(self.buffer)
		self.buffer.connect("changed",self.change_row)
		self.sw.add(self.edit)
        
		lm = edit.LanguageManager()
		self.buffer.set_data('languages-manager', lm)
		manager = self.buffer.get_data('languages-manager') 
		lang = "application/x-shellscript"
		language = manager.guess_language(content_type=lang)
		self.buffer.set_language(language) 	
	 
	
		self.adj = self.builder.get_object("adjustment1")
		self.adj.connect("value-changed" ,  self.setTimeout)
		self.home = self.box.render_icon(gtk.STOCK_HOME,gtk.ICON_SIZE_LARGE_TOOLBAR,None)
	    
		self.buffer2 = self.builder.get_object("textbuffer1")
	    	self.tview = self.builder.get_object("textview1")
		self.tview.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))

		
		self.text = None
		self.refresh()
		self.undo()
    
	def command(self,code): 

 		self.buffer2.insert_at_cursor("$" + code+"\n")
		if os.system(code + " 2> /tmp/pipe") !=0:
			print "hata"
		out = open("/tmp/pipe").read()	
		self.buffer2.insert_at_cursor(out  )
		tag = self.buffer2.create_tag(foreground= gtk.gdk.color_parse("#D5D5D5") )
		start, end = self.buffer2.get_bounds()
		self.buffer2.apply_tag(tag, start, end )
 		del out

		    
	def refresh(self,data=None):	
		treeselection = self.treeview.get_selection()
		model, iter  = treeselection.get_selected()

		expose = None
		try:
			expose = int(model.get_path(iter) [0] )
		except:
			pass

	    	self.store.clear()
		val = int(DefaultGrubConfig.settings["GRUB_TIMEOUT"])
		self.adj.set_value(val)
 		try:
			for i  in GrubCfgConfig.entries:  
				self.store.append(None, [None,i["name"]] )
		
			default=int(DefaultGrubConfig.settings["GRUB_DEFAULT"]) 
			model[default][0] = self.home
 
			if not expose :
				treeselection.select_path(0) 
			else:
				treeselection.select_path(expose) 
			self.treeview.emit("cursor-changed")
		except:
			return	
			
	def undo(self,data=None):
		DefaultGrubConfig.read()
		GrubCfgConfig.read()
		self.refresh()
	
	def reset(self,data=None):	
		self.command( GRUB_UPDATE_COMMAND  )
		DefaultGrubConfig.read()
		GrubCfgConfig.read()
		self.refresh()      
         
	def append(self,data=None):
		GrubCfgConfig.entries.append({"name":"New Startup Entry", "content": "menuentry 'New Startup Entry' {\n set root=(hd0,4) \n }"})
		self.refresh()   
                   
	def save(self,data=None):	
		DefaultGrubConfig.write()
		self.command( GRUB_UPDATE_COMMAND  )
		GrubCfgConfig.write()
		self.refresh() 
        
	def backup(self,data=None):	
	    self.command("cp {0} {1}".format(GrubCfgConfig.path, BACKUP_PATH) )
	    self.command("cp {0} {1}".format(DefaultGrubConfig.path, BACKUP_PATH) )
	    self.refresh()
		
	def restore(self,data=None):	
		self.command("cp {0}/grub {1}".format(BACKUP_PATH, DefaultGrubConfig.path)   )
		self.command("cp {0}/grub.cfg {1}".format(BACKUP_PATH, GrubCfgConfig.path)  )
	 
		DefaultGrubConfig.read()
		GrubCfgConfig.read()
		self.refresh()
		
	def setTimeout(self, timeout): 
	    	timeout = timeout.get_value() 
		DefaultGrubConfig.settings["GRUB_TIMEOUT"]= int(timeout)
	     #   self.refresh()
		
	def remove(self,data=None):	
	    	treeselection = self.treeview.get_selection()
		model, iter  = treeselection.get_selected()  
		try:
			try:pos = int(model.get_path(iter) [0] )
			except:return
			default = int(DefaultGrubConfig.settings["GRUB_DEFAULT"])
			if pos < default:
				DefaultGrubConfig.settings["GRUB_DEFAULT"] = default - 1
			if pos == default :
				DefaultGrubConfig.settings["GRUB_DEFAULT"] = 0
		except IndexError:
			return   
				 
		del GrubCfgConfig.entries[pos]
		self.refresh() 
           
	def up(self,data=None):
		treeselection = self.treeview.get_selection()
		model, iter  = treeselection.get_selected()  
		try:pos = int(model.get_path(iter) [0] )
		except:return
		npos = pos -1
		if pos > 0:  
			try:riter = model.get_iter(  npos )
			except :return
			model.swap( iter ,riter)       
			 
			entry=GrubCfgConfig.entries[pos]
			del GrubCfgConfig.entries[pos]
			GrubCfgConfig.entries.insert(npos , entry)        
			if npos==int(DefaultGrubConfig.settings["GRUB_DEFAULT"]):
					DefaultGrubConfig.settings["GRUB_DEFAULT"]= pos
				
	def down(self,data=None):
		treeselection = self.treeview.get_selection()
		model, iter  = treeselection.get_selected()  
		try:pos = int(model.get_path(iter) [0] )
		except:return
		npos = pos +1    
		try:riter = model.get_iter(  npos  )    
		except : return
		else:model.swap(  iter ,riter)       
	 
		entry=GrubCfgConfig.entries[pos]
		del GrubCfgConfig.entries[pos]
		GrubCfgConfig.entries.insert(  npos,entry)
		if  npos == int(DefaultGrubConfig.settings["GRUB_DEFAULT"]):
				DefaultGrubConfig.settings["GRUB_DEFAULT"]=  pos 
					
	def setDefault(self, data=None): 
		treeselection = self.treeview.get_selection()
		model, iter  = treeselection.get_selected()  
		try:pos = int(model.get_path(iter) [0] )
		except:return
		DefaultGrubConfig.settings["GRUB_DEFAULT"]= pos
		self.refresh()
		treeselection.select_path(pos)        
        
	def change_row(self, data=None):
		treeselection = self.treeview.get_selection()
		model, iter  = treeselection.get_selected()  

		try:pos = int(model.get_path(iter) [0] )
		except:return

		start, end = self.buffer.get_bounds()
		konu= self.buffer.get_slice(start, end)
		GrubCfgConfig.entries[pos]["content"]= konu
		try:
			newName=re.findall("menuentry ['\"](.*?)['\"]", konu )[0]
			if self.text == newName:
				return
			GrubCfgConfig.entries[pos]["name"]=newName
			self.text = newName
			model[pos][1]  = newName

		except IndexError:
			pass
			
	def active_item(self,widget):
		treeselection = widget.get_selection()
		model, item  = treeselection.get_selected() 
		try:path = model.get_path(item)[0]
		except:return
		text = GrubCfgConfig.entries[path]["content"] 
		self.buffer.begin_not_undoable_action()
		self.buffer.set_text(text)
	 	self.buffer.end_not_undoable_action()
 	
	def abou(self,data=None):
		abou.hakkinda()
	
	def help(sef,data=None):
	    os.system("yelp /usr/share/gnome/help/grubon/grub-on.xml 2> /dev/null   & ")
    
if not os.getuid()==0:
	subprocess.Popen(["gksudo", os.path.abspath(sys.argv[0])])
	sys.exit(0) 
Gui().show_all()
gtk.main()        
