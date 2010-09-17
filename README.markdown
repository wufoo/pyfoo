Pyfoo is a Python wrapper for the Wufoo API.

You can use the wrapper with either an API Key or an email address, password, and integration key.

###Example usage:

	api = PyfooAPI('your_account', 'your_api_key_here')
	or
	api = PyfooAPI(email='email@email.com', password='password', integration_key='your_integration_key')


Once you have created an instance of the PyfooAPI you can access forms, reports, fields, and entries.
The Entry class is a dictionary of field values, all other classes have fields corrosponding with the fields returned
by the Wufoo api, for example the Form class has Name, Description, Url, and RedirectMessage properties,
along with all of the other properties returned by the API.  This allows you to reference the Wufoo API
documentation directly when accessing class properties, or a simple dir(form) will also give you a list
of all of the available properties.


###Here are some examples:

	api = PyfooAPI('your_account', 'your_api_key_here')
	for form in api.forms:
	    print '%s (%s)' % (form.Name, form.entry_count)

	for report in api.reports:
	    print '%s (%s)' % (report.Name, report.entry_count)

	for user in api.users:
	    print '%s (%s)' % (report.Name, report.entry_count)

	contact_form = api.forms[0]
	email_field = contact_form.get_field('Email')    
	entries = contact_form.get_entries() # By default this returns 100 entries sorted by DateCreated descending
	for entry in entries: 
	    print entry[email_field.ID]

	entry = entries[0]
	for field in contact_form.fields:
	    if field.SubFields:
	        for subfield in field.SubFields:
	            print '%s: %s' % (subfield.Label, entry[subfield.ID])
	    else:
	        print '%s: %s' % (field.Title, entry[field.ID])



###PyfooAPI Class Documentation:    

	class PyfooAPI(account, api_key) or
	class PyfooAPI(email=None, password=None, integration_key=None)
	    Propreties:
	        forms
	        reports
	        users


	class Form()
	    Methods:
	        add_entry(Entry())
	        add_web_hook(hook_url, handshake_key=None, send_metadata=True)
	        delete_web_hook(self, webhook_hash)
	        get_entries(page_start=0, page_size=100, sort_field='DateCreated', sort_direction='DESC')
	        get_iframe_embed_url()
	        get_javascript_embed_url()
	        get_link_url()
	        search_entries([SearchParameter(), SearchParameter(), ...])
	        get_field(title)
        
	    Properties:
	        comments
	        entry_count
	        fields

 
	class Entry()
	    Properties:    
	        comments


	class Report()
	    Methods:
	        get_entries(page_start=0, page_size=100)
	        get_link()

	    Propreties:
	        entries
	        entry_count
	        fields
	        widgets


	class User()
	    Methods:
	        get_big_image_url(self)
	        get_small_image_url(self)
     
     
	class Widget()
	    Methods:
	        get_embed_code(self)
    
	class SearchParameter(field, operator, value)
	class Comment()
	class Field()



