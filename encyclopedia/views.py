import re

from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from random import randint, randrange
from markdown2 import markdown
from django import forms

from . import util

result = randrange(100)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
		"header" : "All Pages"
    })	
	
def entry(request, title): 
    entries =  util.get_entry(title.lower())
    if entries is None: 	
        return render(request, "encyclopedia/index.html", {
            "message": "No such title exist -> Please try again." ,
			"header" : "Error: Wrong Entry"
		})
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown(util.get_entry(title))
        })
   
   
def edit(request, title): 
    if request.method == "GET":
        if title is not None:
            content = util.get_entry(title)            
            return render(request, "encyclopedia/edit.html", {
                "title": title,                
				"edit_content": EditContent(initial = {'content': content})				
            }) 
			
    if request.method == "POST":	    
        edit_content = EditContent(request.POST)		
        if edit_content.is_valid():            			
            captcha = int(edit_content.cleaned_data["captcha"])
			
            if captcha != result:
                return render(request, "encyclopedia/index.html", {
                    "message": "The entry is incorrect -> Please try again.",
					"header": "Error: Wrong Captcha"
                })	            
            new_description = edit_content.cleaned_data["content"]
            util.save_entry(title, new_description)
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "content": markdown(util.get_entry(title))
            })        
        else:
            return render(request, "encyclopedia/index.html", {
                "message": "The entry is invalid(Access Denied) -> Please try again.",
				 "header": "Error: Wrong Entry"
            })
			

def create(request):
    if request.method == "POST":
        new_content = NewContent(request.POST)
        if new_content.is_valid():           
            captcha = int(new_content.cleaned_data["captcha"])
            if captcha != result:
                return render(request, "encyclopedia/index.html", {
                    "message": "Unable to create new entry -> Please try again.",					
					"header": "Error: Wrong Captcha"
                })
            else:				
                saved_title = [entry.lower() for entry in util.list_entries()]
                title = new_content.cleaned_data["title"].lower()
            if title in saved_title:
                return render(request, "encyclopedia/index.html", {
                    "message": "Unable to create new entry -> Please try again.",
					"header": "Error: Entry Already Exist"
                })            
            util.save_entry(title, new_content.cleaned_data["content"])
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "content": markdown(util.get_entry(title))
            })
       
        else:
            return render(request, "encyclopedia/create.html", {
            "new_content": NewContent()
        })
    else:
        return render(request, "encyclopedia/create.html", {
            "new_content": NewContent()
            })
    
def random(request):
    entries = util.list_entries()
    title = entries[randint(0, len(entries)-1)]
    return redirect("entry", title=title)
	
	
def search(request):
    query = request.GET.get('q').strip()
    entries = [entry.lower() for entry in util.list_entries()]	
    if query.lower() in entries:
        return redirect("entry", title=query)	
    _, filenames = default_storage.listdir("entries")    
    return render(request, "encyclopedia/search.html", 
	    {"entries": list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md") 
				and query in filename.lower())), "query": query})
	
	
class EditContent(forms.Form):    
    content = forms.CharField(label="[Edit page by using Markdown language]", widget=forms.Textarea)	
    captcha = forms.IntegerField(label="Captcha: Enter the value shown here: "+ str(result))
	
	
class NewContent(forms.Form):
    title = forms.CharField(label="Title",
            widget=forms.TextInput(attrs={'placeholder': "Enter title"}) #Title widget
        )
    content = forms.CharField(
        label="Enter content in markdown",
        widget=forms.Textarea(attrs={'placeholder': "Enter content"})) #Content widget
    captcha = forms.IntegerField(label="Captcha: Enter the value shown here: "+ str(result))
