#!/usr/bin/env python
import configparser
import os
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import IBus
home_dir = os.environ['HOME']
data_dir = "/usr/share/ibus-sharada-braille/braille"


#Key code map #{30:"a",31:"s",32:"d",33:"f",34:"g",35:"h",36:"j",37:"k",38:"l",39:";"}

class ibus_sharada_braille_preferences():
	def __init__ (self,file_list=None):
		self.guibuilder = Gtk.Builder()
		self.guibuilder.add_from_file("/usr/share/ibus-sharada-braille-preferences/ui.glade")
		self.window = self.guibuilder.get_object("window")
		self.combobox_default_languge = self.guibuilder.get_object("combobox_default_languge")
		self.box_general = self.guibuilder.get_object("box_general")		


		
		self.config = configparser.ConfigParser()
		self.default_key_dict = { "dot-1":33,"dot-2":32,"dot-3":31,"dot-4":36,"dot-5":37,"dot-6":38,"punctuation_key":39,"capitol_switch_key":34,"letter_deletion_key":35,"switch_between_languages":119,"list_switch_key":56,"abbreviation_key":30 }
		
		if (self.config.read("{}/isb.cfg".format(home_dir)) == []):
			self.config.add_section('cfg')
			self.checked_languages = ["english-en","hindi-hi"]
			self.reset_keys_and_shorcuts(None,None)
			self.config.set('cfg',"simple-mode",str(0))
			self.config.set('cfg',"default-language",str(0))
			default_language = 0;
			self.key_dict = self.default_key_dict.copy()
		else:
			self.checked_languages = self.config.get('cfg',"checked_languages").split(",")
			self.key_dict = {}
			default_language = int(self.config.get('cfg',"default-language"))
			for key in self.default_key_dict.keys():
				self.key_dict[key] =  int(self.config.get('cfg',key))			
			
		self.checked_languages_liststore = Gtk.ListStore(str)
		for item in self.checked_languages:
			self.checked_languages_liststore.append([item]);
			
		self.combobox_default_languge.set_model(self.checked_languages_liststore)
		renderer_text = Gtk.CellRendererText()
		self.combobox_default_languge.pack_start(renderer_text, True)
		self.combobox_default_languge.add_attribute(renderer_text, "text", 0)
		self.combobox_default_languge.show()
		self.combobox_default_languge.set_active(default_language)
		
		#Create checkbuttons for each available language
		self.available_languages = []
		print(self.checked_languages)
		for item in open("{}/languages.txt".format(data_dir)):
			widget = Gtk.CheckButton.new_with_label(item[:-1])

			self.available_languages.append(item[:-1])
			if item[:-1] in self.checked_languages:
				widget.set_active(True) 
			widget.connect("clicked",self.language_toggled)
			self.box_general.pack_start(widget,0,0,0);
			widget.show()						
		self.box_general.show()

		self.set_keys_and_shortcuts_to_ui(None,None)
		
		#Set Simple mode checkbox
		checkbutton_simple_mode = self.guibuilder.get_object("checkbutton_simple_mode")
		checkbutton_simple_mode.set_active(int(self.config.get('cfg',"simple-mode")))
		
		self.guibuilder.connect_signals(self)
		self.window.show()
	
	def combobox_default_languge_changed(self,widget,data=None):
		self.config.set('cfg',"default-language",str(int(widget.get_active())))
	
	def simple_mode_toggled(self,widget,data=None):
		self.config.set('cfg',"simple-mode",str(int(widget.get_active())))
		
	
	def reset_keys_and_shorcuts(self,widget,data=None):
		self.reset_keys_and_shorcuts_config(None,None)
		self.set_keys_and_shortcuts_to_ui(None,None)

	def reset_keys_and_shorcuts_config(self,widget,data=None):
		for key,value in self.default_key_dict.items():
			self.config.set('cfg',key,str(value))
		self.key_dict = self.default_key_dict.copy()
			
	def set_keys_and_shortcuts_to_ui(self,widget,data=None):
		for item in self.key_dict.keys():
			widget = self.guibuilder.get_object(item)
			hardware_keycode = int(self.config.get('cfg',item))
			map = Gdk.Keymap.get_default()
			var1, var2, var3 = map.get_entries_for_keycode(hardware_keycode+8)
			text = IBus.keyval_to_unicode(var3[0])
			widget.set_text(text)		
		
	def key_press(self,widget,event):
		hardware_keycode = int(event.hardware_keycode)-8
		if (hardware_keycode != 15):
			widget_name = Gtk.Buildable.get_name(widget)		
			if self.key_dict[widget_name] != hardware_keycode:
				if hardware_keycode in self.key_dict.values():
					widget.set_text("None")
					self.key_dict[widget_name] = None;
				else:
					self.key_dict[widget_name] = hardware_keycode
					self.config.set('cfg',widget_name,str(hardware_keycode))
					widget.set_text(event.string)
	
	def language_toggled(self,widget,data=None):
		label = widget.get_label()
		if (widget.get_active()):
			if (label not in self.checked_languages):
				self.checked_languages.append(label)
		else:
			if (label in self.checked_languages):
				if (len(self.checked_languages) > 2):
					self.checked_languages.remove(label)
				else:
					widget.set_active(True)
		print(self.checked_languages)
		
		self.checked_languages_liststore = Gtk.ListStore(str)
		for item in self.checked_languages:
			self.checked_languages_liststore.append([item]);
		self.combobox_default_languge.set_model(self.checked_languages_liststore)
		self.combobox_default_languge.set_active(0)
		self.combobox_default_languge.show()
	
	def close(self,widget,data=None):
		Gtk.main_quit()

	def apply(self,widget,data=None):
		file = open("{}/isb.cfg".format(home_dir),"w")
		self.config.set('cfg',"checked_languages",str(','.join(self.checked_languages)))
		self.config.write(file)
		file.close()
		Gtk.main_quit()
		
ibus_sharada_braille_preferences()
Gtk.main()
