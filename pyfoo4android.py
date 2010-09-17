import android
import os
from pyfoo import PyfooAPI

def get_key_and_account():
    key, account = None, None
    if os.path.exists('/sdcard/key.txt'):
        try:
            f = open('/sdcard/key.txt')
            key, account = f.readlines()
        except: 
            pass
    if not key:
        result = droid.getInput('API Key', 'Please enter your API Key')
        key = result.result
        result = droid.getInput('App Name', 'Please enter your account name (the "account" part of http://account.wufoo.com)')
        account = result.result
        f = open('/sdcard/key.txt', 'w')
        f.write('%s\n%s' % (key, account))
        f.close()

    key = key.strip()
    account = account.strip()
    return key, account

def get_entry_details(entry):
    output = []
    for field in entry.form.fields:
        if field.SubFields:
            output.append(field.Title)
            for subfield in field.SubFields:
                if entry.has_key(subfield.ID):
                    output.append("\t%s: %s" % (subfield.Label, entry[subfield.ID]))
        else:
            if entry.has_key(field.ID):
                output.append("%s: %s" % (field.Title, entry[field.ID]))
    return output


droid = android.Android()

key, account = get_key_and_account()
api = PyfooAPI(account, key)

droid.dialogCreateSpinnerProgress('Loading Forms')
droid.dialogShow()
forms = api.forms
droid.dialogDismiss()

droid.dialogCreateAlert('Select a Form')
droid.dialogSetItems([form.Name for form in forms])
droid.dialogSetNegativeButtonText('Cancel')
droid.dialogShow()
response = droid.dialogGetResponse()
form = forms[response.result['item']]

droid.dialogCreateSpinnerProgress('Loading Entries')
droid.dialogShow()
entries = form.entries
droid.dialogDismiss()

droid.dialogCreateAlert('Select an Entry')
droid.dialogSetItems([entry['DateCreated'] for entry in entries])
droid.dialogSetNegativeButtonText('Cancel')
droid.dialogShow()
response = droid.dialogGetResponse()
entry = entries[response.result['item']]

droid.dialogCreateSpinnerProgress('Loading Entry Details')
droid.dialogShow()
details = "\n".join(get_entry_details(entry))
droid.dialogDismiss()

droid.dialogCreateAlert('Entry Details', details)
droid.dialogShow()
response = droid.dialogGetResponse

