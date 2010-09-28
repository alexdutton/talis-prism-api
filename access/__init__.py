import urllib, urllib2, cookielib, re
from lxml import etree
from datetime import datetime

class TalisPrism(object):
    _USER_AGENT = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.8) Gecko/20100215 Solaris/10.1 (GNU)'

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        
        self.login(username, password)

    def urlopen(self, url, *args, **kwargs):
        request = urllib2.Request(self.base_url+url, *args, **kwargs)
        request.headers['User-Agent'] = self._USER_AGENT
        return self.opener.open(request)

    def login(self, username, password):
        login_page = self.urlopen('accessAccount.do')
        login_page = self.urlopen('logon.do', data=urllib.urlencode({
            'hasLoaded': 'no',
            'talissession': '',
            'LoginSubmit': 'Logon',
            'hidden_username': username,
            'hidden_password': password,
        }))

        content = login_page.read()

        if 'Your login details have not been recognised by the system.' in content:
            raise ValueError("Your details have not been recognised.")

        self._home_page_cache = content

    @property
    def home_page(self):
        if not hasattr(self, '_home_page_cache'):
            self._home_page_cache = self.urlopen('accessAccount.do').read()
        return self._home_page_cache

    @property
    def user_details(self):
        if not hasattr(self, '_user_details_cache'):
            self._user_details_cache = self.urlopen('userDetails.do').read()
        return self._user_details_cache

    @property
    def fines(self):
        return None

    @property
    def name(self):
        match = re.search('<span class="logonText" id="HeaderTextBorrowerName">(.*?)</span>', self.home_page)
        if match:
            return match.group(1)

    @property
    def email(self):
        match = re.search('<input type="text" name="currentEmailAddress" size="20" value="mailto:(.*?)" id="CurrentEmailAddress">', self.user_details)
        if match:
            return match.group(1)

    @property
    def address(self):
        match = re.search('<textarea name="defaultAddressDetails" cols="73" rows="2" id="defaultAddr">(.*?)</textarea>', self.user_details)
        if match:
            return match.group(1)

    @property
    def telephone(self):
        match = re.search('<input type="text" name="defaultTelephoneNo" size="15" value="(.*?)" id="defaultTelephoneNo">', self.user_details)
        if match:
            return match.group(1)

    @property
    def loans(self):
        part = self.home_page
        part = part[part.index('<Table Height="1%" Width="100%" >'):]
        part = part[:part.index('</Table>')]
        part = etree.fromstring(part, parser=etree.HTMLParser())

        items = []
        for tr in part.findall('.//tr')[1:]:
            fields = [td.find('font') for td in tr.findall('td')]
            title_stmt, isbn = fields[2].text.rsplit(' - ', 1)
            items.append({
                'title_stmt': title_stmt,
                'isbn': isbn,
                'lcn': fields[3].text.strip(),
                'type': fields[4].text.strip(),
                'due': datetime.strptime(fields[5].text.strip(), '%d/%m/%Y %H:%M'),
            })

        return items


tp = TalisPrism('http://www.library.northamptonshire.gov.uk/TalisPrism/', '1000930016', '9999')
print tp.name
print tp.email
print tp.address
print tp.telephone
print tp.loans

