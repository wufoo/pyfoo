try:
    import urllib.request as urllib_request
    import urllib.parse as urllib_parse
    from urllib.parse import urlencode
except:
    import urllib as urllib_request
    from urllib import urlencode
    import urllib2 as urllib_parse

import json

try:
    from collections import UserList, UserDict

except:
    from UserList import UserList
    from UserDict import UserDict

BOOLEAN_FIELDS = ('IsAccountOwner', 'IsRequired', 'IsPublic', 'CreateForms', 
        'CreateReports', 'CreateThemes', 'AdminAccess', 'Success')

class WufooObject(object):
    def __init__(self, api, json_object):
        super(WufooObject, self).__init__()
        self.api = api
        for key in list(json_object.keys()):
            if isinstance(json_object[key], list):
                sub_list = []
                for sub_json in json_object[key]:
                    sub_object = WufooObject(api, sub_json)
                    sub_list.append(sub_object)
                setattr(self, key, sub_list)
            else:
                if key in BOOLEAN_FIELDS:
                    boolean_value = str(json_object[key]) == '1'
                    setattr(self, key, boolean_value)
                else:
                    setattr(self, key, json_object[key])

class SearchParameter(object):
    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value
        
class Entry(UserDict):
    def __init__(self, fields=None, form=None):
        #super(Entry, self).__init__(data=fields)
        if fields:
            self.data = fields
        else:
            self.data = {}
        self.form = form
        if 'LastUpdated' not in self:
            self['LastUpdated'] = None
        if 'LastUpdatedBy' not in self:
            self['LastUpdatedBy'] = None
    
    @property
    def comments(self):
        if not hasattr(self, '_comments'):
            comments_json = self.form.api.make_call('https://%s.wufoo.com/api/v3/forms/%s/comments.json?entryId=%s' % (self.form.api.account, self.form.Hash, self['EntryId']))
            self._comments = [Comment(self.form.api, comment) for comment in comments_json['Comments']]
        return self._comments
        
         
class Field(WufooObject):
    def __init__(self, api, json_object):
        super(Field, self).__init__(api, json_object)
        if not hasattr(self, 'IsRequired'):
            self.IsRequired = False
            
        if hasattr(self, 'SubFields'):
            self.ID = None
            self.Type = None
        else:
            self.SubFields = []

        if hasattr(self, 'Choices'):
            [setattr(choice, 'Score', None) for choice in self.Choices if not hasattr(choice, 'Score')]
        else:
            self.Choices = []


class Form(WufooObject):
    def search_entries(self, parameters):
        output = {}
        for index in range(len(parameters)):
            param = parameters[index]
            output['Filter%s' % (index + 1)] = "%s__%s__%s" % (param.field, param.operator, param.value)
        filter_string = urlencode(output).replace('__', '+')
        return self.get_entries(filter_string=filter_string)

    def get_entries(self, page_start=0, page_size=100, sort_field='DateCreated', sort_direction='DESC', filter_string=None):
        url = "%s?system=true&pageStart=%s&pageSize=%s&sort=%s&sortDirection=%s" % (self.LinkEntries, page_start, page_size, sort_field, sort_direction)
        if filter_string:
            url = "%s&%s" % (url, filter_string)
        entries_json = self.api.make_call(url)
        entries = [Entry(fields=entry, form=self) for entry in entries_json['Entries']]
        return entries
    
    def get_field(self, title):
        field = [field for field in self.fields if field.Title == title]
        if len(field) > 1:
            return field
        elif len(field) > 0:
            return field[0]
        else:
            return None
    
    @property
    def fields(self):
        if not hasattr(self, '_fields'):
            fields_json = self.api.make_call(self.LinkFields)
            self._fields = [Field(self.api, field) for field in fields_json['Fields']]
        return self._fields
        
    @property
    def entry_count(self):
        #if not hasattr(self, '_entry_count'):
        fields_json = self.api.make_call(self.LinkEntriesCount)
        try:
            self._entry_count = int(fields_json['EntryCount'])
        except:
            self._entry_count = 0
        return self._entry_count
        
    @property
    def comments(self):
        if not hasattr(self, '_comments'):
            comments_json = self.api.make_call('https://%s.wufoo.com/api/v3/forms/%s/comments.json' % (self.api.account, self.Hash))
            self._comments = [Comment(self.api, comment) for comment in comments_json['Comments']]
        return self._comments
        
    def add_entry(self, entry):
        post_params = {}
        for field in self.fields:
            if field.Title in entry:
                post_params[field.ID] = entry[field.Title]
            elif field.ID in entry:
                post_params[field.ID] = entry[field.ID]
        url = 'https://%s.wufoo.com/api/v3/forms/%s/entries.json' % (self.api.account, self.Hash)
        response_json = self.api.make_call(url, post_params=post_params)
        response_status = WufooObject(self.api, response_json)
        if response_status.Success:
            entry['EntryId'] = response_status.EntryId
        return response_status
    
    def add_web_hook(self, hook_url, handshake_key=None, send_metadata=True):
        post_params = {'url': hook_url, 'handshakeKey': handshake_key, 'metadata': str(send_metadata).lower()}
        url = 'https://%s.wufoo.com/api/v3/forms/%s/webhooks.json' % (self.api.account, self.Hash)
        response_json = self.api.make_call(url, post_params=post_params, method='PUT')
        return response_json['WebHookPutResult']['Hash']

    def delete_web_hook(self, webhook_hash):
        post_params = {'hash': webhook_hash}
        url = 'https://%s.wufoo.com/api/v3/forms/%s/webhooks/%s.json' % (self.api.account, self.Hash, webhook_hash)
        response_json = self.api.make_call(url, post_params=post_params, method='DELETE')
        return response_json['WebHookDeleteResult']['Hash']
    
    def get_link_url(self):
        return "http://%s.wufoo.com/forms/%s/" % (self.api.account, self.Hash)
    
    def get_javascript_embed_url(self):
        params = {'hash': self.Hash, 'account': self.api.account}
        script_code = """<script type="text/javascript">var host = (("https:" == document.location.protocol) ? "https://secure." : "http://");document.write(unescape("%%3Cscript src='" + host + "wufoo.com/scripts/embed/form.js' type='text/javascript'%%3E%%3C/script%%3E"));</script>
<script type="text/javascript">
var %(hash)s = new WufooForm();
%(hash)s.initialize({
'userName':'%(account)s', 
'formHash':'%(hash)s', 
'autoResize':true,
'height':'607'});
%(hash)s.display();
</script>""" % params
        return script_code

    def get_iframe_embed_url(self):
        params = {'account': self.api.account, 'hash': self.Hash, 'title': self.Name}
        return """<iframe height="607" allowTransparency="true" frameborder="0" scrolling="no" style="width:100%%;border:none"  src="http://%(account)s.wufoo.com/embed/%(hash)s/"><a href="http://%(account)s.wufoo.com/forms/%(hash)s/" title="%(title)s" rel="nofollow">Fill out my Wufoo form!</a></iframe>""" % params

class Report(WufooObject):
    @property
    def entries(self, page=None, count=None):
        if not hasattr(self, '_entries'):
            entries_json = self.api.make_call(self.LinkEntries)
            self._entries = [Entry(fields=entry, form=self) for entry in entries_json['Entries']]
        return self._entries
        
    def get_entries(self, page_start=0, page_size=100):
        url = "%s?system=true&pageStart=%s&pageSize=%s" % (self.LinkEntries, page_start, page_size)
        entries_json = self.api.make_call(url)
        entries = [Entry(fields=entry, form=self) for entry in entries_json['Entries']]
        return entries
        
    @property
    def fields(self):
        if not hasattr(self, '_fields'):
            fields_json = self.api.make_call(self.LinkFields)
            self._fields = [Field(self.api, field) for field in list(fields_json['Fields'].values())]
        return self._fields
        
    @property
    def widgets(self):
        if not hasattr(self, '_widgets'):
            widgets_json = self.api.make_call(self.LinkWidgets)
            self._widgets = [Widget(self.api, widget) for widget in widgets_json['Widgets']]
        return self._widgets
    
    def get_link(self):
        return 'https://%s.wufoo.com/reports/%s/' % (self.api.account, self.Hash)
    
    @property
    def entry_count(self):
        #if not hasattr(self, '_entry_count'):
        fields_json = self.api.make_call(self.LinkEntriesCount)
        try:
            self._entry_count = int(fields_json['EntryCount'])
        except:
            self._entry_count = 0
        return self._entry_count
        
class User(WufooObject):
    def get_big_image_url(self):
        return self.ImageUrlSmall
    def get_small_image_url(self):
        return self.ImageUrlBig
  
class Widget(WufooObject):
    def get_embed_code(self):
        if hasattr(self, 'Hash'):
            return '<script type="text/javascript">var host = (("https:" == document.location.protocol) ? "https://" : "http://");document.write(unescape("%%3Cscript src=\'" + host + "%s.wufoo.com/scripts/widget/embed.js?w=%s\' type=\'text/javascript\'%%3E%%3C/script%%3E"));</script>' % (self.api.account, self.Hash)
        else:
            return None
            
class Comment(WufooObject):
    pass
        
class PyfooAPI(object):
    def __init__(self,
        account=None,
        api_key=None,
        email=None,
        password=None,
        integration_key=None,
        test_json_dir=None):

        self.account = account
        self.api_key = api_key
        self.test_json_dir = test_json_dir
        if email and password:
            url = 'https://wufoo.com/api/v3/login.json'
            data = {'email': email, 'password': password, 'integrationKey': integration_key}
            if account:
                data['subdomain'] = account
                
            response = self.make_call(url, data, 'POST')
            self.api_key = response['ApiKey']
            self.account = response['Subdomain']
            
    def make_call(self, url, post_params=None, method=None):
        password_mgr = urllib_request.HTTPPasswordMgrWithDefaultRealm()
        if self.account:
            top_level_url = "https://%s.wufoo.com/api/v3" % self.account
        else:
            top_level_url = "https://wufoo.com/api/v3"
        password_mgr.add_password(None, top_level_url, self.api_key, "footastic")
        handler = urllib_request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib_request.build_opener(handler)
        urllib_request.install_opener(opener)
        
        if post_params:
            data = urllib_parse.urlencode(post_params)
            request = urllib_request.Request(url, data=data)
            if method:
                request.get_method = lambda: method
            response = opener.open(request)
        else:
            response = opener.open(url)
        
        json_string = response.read()        
        
        post_params_string = ''
        if post_params:
            post_params_string = ''.join(list(post_params.keys()))

        if self.test_json_dir:
            with open(os.path.join(
                    self.test_json_dir,
                    '%s%s.json' % (url.replace('/', '_'),
                post_params_string)
                ), 'w' ) as test_script:
                test_script.write(json_string)
                test_script.close()

        try:
            json_object = json.loads(json_string.decode('utf8'))
            
        except Exception as ex:
            print(url)
            print(json_string)
            
            raise ex
        return json_object

    # Users
    @property
    def users(self):
        if not hasattr(self, '_users'):
            users_json = self.make_call('https://%s.wufoo.com/api/v3/users.json' % self.account)
            self._users = [User(self, user_dict) for user_dict in users_json['Users']]
        return self._users

    # Forms
    @property
    def forms(self):
        if not hasattr(self, '_forms'):
            forms_json = self.make_call('https://%s.wufoo.com/api/v3/forms.json' % self.account)
            self._forms = [Form(self, form_dict) for form_dict in forms_json['Forms']]
        return self._forms
    
    # Reports
    @property
    def reports(self):
        if not hasattr(self, '_reports'):
            reports_json = self.make_call('https://%s.wufoo.com/api/v3/reports.json' % self.account)
            self._reports = [Report(self, report_dict) for report_dict in reports_json['Reports']]
        return self._reports
    
