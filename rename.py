from re import sub, split, match, search, findall, compile, IGNORECASE
import string

class Rename(object):
    def make_ascii(self,text):
        return text.decode('unicode_escape').encode('ascii','ignore')

    def make_unicode(self, text):
        printable = set(string.printable)
        text = filter(lambda a:a in printable, text)
        text = sub(r'(.*)\s+$', r'\1', text)
        return unicode(text).decode('unicode_escape').encode('utf-8','ignore')

    def alphanumeric(self,n):
        alphanumeric = string.digits + string.ascii_letters
        base = len(alphanumeric)
        result = ''
        n = n+base
        while n > -1:
            i = n%base
            result = alphanumeric[i] + result

            n = n/base-1

        return str(result)

    def group_to_number(self,group):
        letters = string.uppercase
        n = search(group, letters)
        if n is None:
            n = 0
        else:
            n = n.start()
        return n

    def fix_address(self,address):
        # Street -> St.
        address = sub(r'street', 'St.', address, flags=IGNORECASE)
        # ave -> Ave.
        address = sub(r'ave(\s+|$)', 'Ave.', address, flags=IGNORECASE)
        # n or s -> N. or S.
        address = sub(r'\s(n|s)\s', r' \1. ', address, flags=IGNORECASE)

        group = ''
        # removes group letter and separates in group column
        has_group = findall(r'[A-Z]\s*$', address)
        if len(has_group) > 0:
            address = sub(r'[A-Z]\s*$', '', address)
            group = has_group[0]

        # nth -> nth Ave.
        address = sub(r'(\d)(nd|rd|th)\s*$', r'\1\2 Ave.', address, flags=IGNORECASE)
        # removes trailing spaces
        address = sub(r'\s*$', '', address)

        return [
            address,
            group
        ]

    def preformat_directory(self,item):
        item = item.lower()
        item = sub(r'(-|_|\'|,)+',' ',item)

        replace = r'(\s|_)+(ave\.|street|st\.|way|block)'
        item = sub(replace,r'',item)

        add = r'(\d)(th|nd|rd)\s+'
        item = sub(add,r'\1\2',item)

        fix = r'(chestnut|franklin)\s'
        item = sub(fix,r'\1',item)

        remove = r'(\s+|\.|\(|_*\)|_$)'
        item = sub(remove,r'',item)

        return item

    def remove_slash_padding(self,item):
        return sub(r'\s+/\s+',r'/',item)

    def change_directory(self,address):
        address = self.fix_address(address)[0]
        address = address.split()
        if len(address) > 3:
            name = ''.join(address[1:3])
            name = sub(r'\.','',name)
        else:
            name = address[1]
        name = name.lower()

        try:
            number = int(address[0])
            if number > 100:
                number = str(number/100) + '00'
            else:
                number = '000'
        except ValueError:
            number = 'XXX'

        return number+'/'+name+'/'
        # return name+'/'+number+'/'


    def format_filename(self,item):
        # remove weird stuff
        item = sub(r'(\s+|-+|_+|,|\')',r'',item)
        # split by . which may be in the title and not just before extension
        parts = item.split('.')
        # lowercase the extension
        parts[-1] = '.' + parts[-1].lower()

        return ''.join(parts)

    def remove_extension(self,item):
        item = item.split('.')
        return item[0]

    def simplify_website(self,item):
        # http = match(r'^(https*://).*',item)
        # if (http):
        # else:
        #     print('-----: '+item)
        item = sub(r'(/home\.html|/)$',r'',item)
        item = sub(r'^(https*://)*(www\.)*(.*)',r'\3',item)
        # item = sub(r'*(www\.)*(.*)\/$',r'\3',item)
        return item
