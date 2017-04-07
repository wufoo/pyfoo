import unittest
import os, sys
import json

try:
    import urllib.request as urllib_request

except:
    import urllib as urllib_request


from pyfoo import PyfooAPI, Entry, SearchParameter

account = 'apprabbit'
api_key = 'C0BN-5BYC-I30C-U95X'

def test_make_call(url, post_params=None, method=None ):
    post_params_string = ''
    if post_params:
        post_params_string = ''.join(list(post_params.keys()))
    path = 'test_scripts/%s%s.json' % (url.replace('/', '_'), post_params_string)    
    
    try:
        test_script = open(path)
        json_object = json.load(test_script)
        test_script.close()
    except IOError as ex:
        api = PyfooAPI(account, api_key)
        json_object = api.make_call(url, post_params, method)
        print(ex)
        print('*** Using the regular API ***')
    return json_object
    
def get_test_api():
    test_api = PyfooAPI(account, api_key, test_json_dir='test_scripts')
    test_api.make_call = test_make_call
    return test_api
    
class TestForms(unittest.TestCase):
    def test_form_link_url(self):
        api = get_test_api()
        self.assertEqual('http://apprabbit.wufoo.com/forms/m7x3k1/', api.forms[1].get_link_url());

    def test_form_javascript_embed_url(self):
        javascript_code = """<script type="text/javascript">var host = (("https:" == document.location.protocol) ? "https://secure." : "http://");document.write(unescape("%3Cscript src='" + host + "wufoo.com/scripts/embed/form.js' type='text/javascript'%3E%3C/script%3E"));</script>
<script type="text/javascript">
var m7x3k1 = new WufooForm();
m7x3k1.initialize({
'userName':'apprabbit', 
'formHash':'m7x3k1', 
'autoResize':true,
'height':'607'});
m7x3k1.display();
</script>"""
        api = get_test_api()
        self.assertEqual(javascript_code, api.forms[1].get_javascript_embed_url());

    def test_form_iframe_embed_url(self):
        api = get_test_api()
        iframe_code = """<iframe height="607" allowTransparency="true" frameborder="0" scrolling="no" style="width:100%;border:none"  src="http://apprabbit.wufoo.com/embed/m7x3k1/"><a href="http://apprabbit.wufoo.com/forms/m7x3k1/" title="Order Form" rel="nofollow">Fill out my Wufoo form!</a></iframe>"""
        self.assertEqual(iframe_code, api.forms[1].get_iframe_embed_url());

    def test_forms_getter(self):
        api = get_test_api()
        self.assertEqual(2, len(api.forms))
        self.assertEqual('Contact Form', api.forms[0].Name)

    def test_form_entries_getter(self):
        api = get_test_api()
        entries = api.forms[0].get_entries()
        self.assertEqual(3, len(entries))
        self.assertEqual(3, api.forms[0].entry_count)
        self.assertEqual('Robert Smith', entries[0]['Field1'])

    def test_form_entries_sorting_getter(self):
        api = get_test_api()
        entries = api.forms[0].get_entries(sort_field='EntryId', sort_direction='ASC')
        self.assertEqual('Mark Ransom', entries[0]['Field1'])
        entries = api.forms[0].get_entries(sort_field='EntryId', sort_direction='DESC')
        self.assertEqual('Robert Smith', entries[0]['Field1'])

    def test_form_fields_getter(self):
        api = get_test_api()
        entries = api.forms[0].get_entries()
        self.assertEqual(3, len(entries))
        self.assertEqual('Robert Smith', entries[0]['Field1'])

    def test_form_fields_and_entries_match(self):
        api = get_test_api()
        entry = api.forms[0].get_entries()[0]
        fields = api.forms[0].fields
        for field in fields:
            if field.ID not in ('LastUpdated',):
                if field.SubFields:
                    for subfield in field.SubFields:
                        self.assertTrue(subfield.ID in entry)
                else:
                    self.assertTrue(field.ID in entry)
            if field.Choices:
                self.assertEqual(3, len(field.Choices))
                self.assertEqual('Client', field.Choices[0].Label)
                self.assertEqual(None, field.Choices[0].Score)
       
class TestSearchingEntries(unittest.TestCase):
    def test_search_comments_and_email(self):
        api = get_test_api()
        comment_field = [field for field in api.forms[0].fields if field.Title == 'Comments'][0]
        parameters = [SearchParameter(comment_field.ID, 'Contains', 'Test'),]
        entries = api.forms[0].search_entries(parameters=parameters)
        self.assertEqual(2, len(entries))

        email_field = [field for field in api.forms[0].fields if field.Title == 'Email'][0]
        parameters.append(SearchParameter(email_field.ID, 'Contains', 'gmail'))
        entries = api.forms[0].search_entries(parameters=parameters)
        self.assertEqual(1, len(entries))
        
class TestGetEntriesPager(unittest.TestCase):
    def test_get_entries_page(self):
        api = get_test_api()
        entries = api.forms[0].get_entries()
        self.assertEqual(3, len(entries))
        entries = api.forms[0].get_entries(page_start=0, page_size=2)
        self.assertEqual(2, len(entries))
        entries = api.forms[0].get_entries(page_start=2, page_size=2)
        self.assertEqual(1, len(entries))
        

class TestAddEntries(unittest.TestCase):
    def test_add_entry(self):
        api = get_test_api()
        entry = Entry()
        entry['Title'] = "Test Entry"
        entry['Details'] = 'This is a new test entry'
        entry['Type'] = 'Active'
        entry['Cost'] = '123456'
        api.forms[1].add_entry(entry)
        self.assertTrue('EntryId' in entry)
            
    def test_fail_adding_entry(self):
        api = get_test_api()
        entry = Entry()
        entry['Details'] = 'This is a new test entry'
        entry['Type'] = 'Active'
        entry['Cost'] = '123456'
        response = api.forms[1].add_entry(entry)
        self.assertFalse(response.Success)
        self.assertEqual('Field1', response.FieldErrors[0].ID)



class TestWebHooks(unittest.TestCase):
    def test_add_web_hook(self):
        api = get_test_api()
        response = api.forms[1].add_web_hook("http://www.apprabbit.com", "gobblygook", False)
        self.assertEqual("v3v0m7", response)
         
    def test_delete_web_hook(self):
        api = get_test_api()
        add_response = api.forms[0].add_web_hook("http://www.apprabbit.com", "delete", False)
        delete_response = api.forms[0].delete_web_hook(add_response)
        self.assertEqual(delete_response, add_response)
        
class TestComments(unittest.TestCase):
    def test_comments_getter(self):
        api = get_test_api()
        self.assertEqual(3, len(api.forms[0].comments))

    def test_form_entry_comments_getter(self):
        api = get_test_api()
        entry = api.forms[0].get_entries()[2]
        self.assertEqual(2, len(entry.comments))

       
class TestReports(unittest.TestCase):
    def test_reports_getter(self):
        api = get_test_api()
        self.assertEqual(2, len(api.reports))
        self.assertEqual('Untitled Report', api.reports[1].Name)

    def test_report_entries_getter(self):
        api = get_test_api()
        entries = api.reports[1].get_entries()
        self.assertEqual(3, len(entries))
        self.assertEqual(3, api.reports[1].entry_count)
        self.assertEqual('Mark Ransom', entries[0]['Field1'])

    """ Report Entries don't appear to support filters, paging, or sorting
    def test_report_paged_entries_getter(self):
        api = get_test_api()
        entries = api.reports[0].get_entries(page_start=1, page_size=2)
        self.assertEqual(1, len(entries))
    """
    def test_report_fields_getter(self):
        api = get_test_api()
        fields = api.reports[0].fields
        details_field = [field for field in fields if field.Title == 'Details'][0]
        first_entry = api.reports[0].get_entries()[0]
        self.assertFalse(details_field.ID in first_entry)

        type_field = [field for field in fields if field.Title == 'Type'][0]
        self.assertTrue(type_field.ID in first_entry)
        
    def test_report_fields_and_entries_match(self):
        api = get_test_api()
        entry = api.reports[1].get_entries()[0]
        fields = api.reports[1].fields
        for field in fields:
            if field.SubFields:
                for subfield in field.SubFields:
                    self.assertTrue(subfield.ID in entry)
            else:
                if field.IsRequired:
                    self.assertTrue(field.ID in entry)
                
    def test_report_widgets_getter(self):
        api = get_test_api()
        widgets = api.reports[1].widgets
        self.assertEqual(1, len(widgets))
        self.assertEqual('fieldChart', widgets[0].Type)

    def test_report_widget_code_getter(self):
        api = get_test_api()
        widget = api.reports[1].widgets[0]
        self.assertEqual('<script type="text/javascript">var host = (("https:" == document.location.protocol) ? "https://" : "http://");document.write(unescape("%3Cscript src=\'" + host + "apprabbit.wufoo.com/scripts/widget/embed.js?w=JlLuLGXrZ8sGfSR6D2lwuslashIQwuBey8dw1CIWDhDIJyLHRJQY=\' type=\'text/javascript\'%3E%3C/script%3E"));</script>', widget.get_embed_code())
           
    def test_report_widget_link_getter(self):
        api = get_test_api()
        report = api.reports[0]
        self.assertEqual('https://apprabbit.wufoo.com/reports/m5p8q8/', report.get_link())           
            
class TestUsers(unittest.TestCase):       
    def test_users_getter(self):
        api = get_test_api()
        self.assertEqual(1, len(api.users))
        self.assertEqual('apprabbit', api.users[0].User)

    def test_users_image_urls(self):
        api = get_test_api()
        user = api.users[0]
        if sys.version[0] == '3':
            response = urllib_request.urlopen(user.get_big_image_url())
            self.assertEqual(200, response.code)
            self.assertEqual('image/png', response.headers.get_content_type())
            response = urllib_request.urlopen(user.get_small_image_url())
            self.assertEqual(200, response.code)
            self.assertEqual('image/png', response.headers.get_content_type())

        if sys.version[0] == '2':
            response = urllib_request.urlopen(user.get_big_image_url())
            self.assertEqual(200, response.code)
            self.assertEqual('image/png', response.headers.type)
            response = urllib_request.urlopen(user.get_small_image_url())
            self.assertEqual(200, response.code)
            self.assertEqual('image/png', response.headers.type)


""" 
class TestLogin(unittest.TestCase):       
    def test_login(self):
        api = PyfooAPI(email="email", password="password", integration_key="integration_key")
        self.assertTrue(api.api_key)
        self.assertTrue(api.account)
"""
                
if __name__ == '__main__':
    unittest.main()

