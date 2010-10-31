# coding=UTF-8

import urllib, urllib2, cookielib, re, sys, simplejson
from lxml import etree
from datetime import datetime
from decimal import Decimal

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
    def history_page(self):
        if not hasattr(self, '_history_page_cache'):
            self._history_page_cache = self.urlopen('accessAccount.do?accountAction=1').read()
        return self._history_page_cache

    def simple_property(page_name, regex):
        @property
        def p(self):
            match = re.search(regex, getattr(self, page_name))
            if match:
                return match.group(1)
        return p

    charges = simple_property('home_page', r'£(\d+\.\d\d)')
    name = simple_property('home_page', r'<span class="logonText" id="HeaderTextBorrowerName">(.*?)</span>')

    email = simple_property('user_details', r'<input type="text" name="currentEmailAddress" size="20" value="mailto:(.*?)" id="CurrentEmailAddress">')
    address = simple_property('user_details', r'<textarea name="defaultAddressDetails" cols="73" rows="2" id="defaultAddr">(.*?)</textarea>')
    telephone = simple_property('user_details', r'<input type="text" name="defaultTelephoneNo" size="15" value="(.*?)" id="defaultTelephoneNo">')

    @property
    def loans(self):
        part = self.home_page

        try:
            part = part[part.index('<Table Height="1%" Width="100%" >'):]
            part = part[:part.index('</Table>')]
        except ValueError:
            return []
        part = etree.fromstring(part, parser=etree.HTMLParser())

        items = []
        for tr in part.findall('.//tr')[1:]:
            fields = [td.find('font') for td in tr.findall('td')]
            fields = [(f.find('font') if len(f) else f) for f in fields]
            title_stmt, isbn = fields[2].text.rsplit(' - ', 1)
            items.append({
                'title_stmt': title_stmt,
                'isbn': isbn,
                'lcn': fields[3].text.strip(),
                'type': fields[4].text.strip(),
                'due': datetime.strptime(fields[5].text.strip(), '%d/%m/%Y %H:%M'),
                'renewals': int(fields[6].text.strip()),
            })

        return items

    @property
    def history(self):
        part = self.history_page

        try:
            part = part[part.index('<Table Height="1%" Width="100%" >'):]
            part = part[:part.index('</Table>')]
        except ValueError:
            return []
        part = etree.fromstring(part, parser=etree.HTMLParser())

        items = []
        for tr in part.findall('.//tr')[1:]:
            fields = [td.find('font') for td in tr.findall('td')]
            fields = [(f.find('font') if len(f) else f) for f in fields]
            title_stmt, isbn = fields[0].text.rsplit(' - ', 1)
            items.append({
                'title_stmt': title_stmt,
                'isbn': isbn,
                'lcn': fields[1].text.strip(),
                'type': fields[2].text.strip(),
                'issued': datetime.strptime(fields[3].text.strip(), '%d/%m/%Y'),
                'returned': datetime.strptime(fields[4].text.strip(), '%d/%m/%Y'),
            })

        return items

    def renew(self, lcns):
        if isinstance(lcns, basestring):
            lcns = (lcns,)

        loans = self.loans
        loans = dict((loan['lcn'], i) for i, loan in enumerate(loans))

        rows = [loans[lcn] for lcn in lcns]

        self.urlopen('accessAccount.do?%s' % urllib.urlencode((
            ('accountAction', '4'),
            ('dataType', '0'),
            ('to', '')
        ) + tuple(('loanRows', row) for row in rows)))

        del self._home_page_cache

if __name__ == '__main__':
    import pprint
    from config import INSTANCES

    tp = TalisPrism(getattr(INSTANCES, sys.argv[1]), *sys.argv[2:])
    pprint.PrettyPrinter().pprint({
        'name': tp.name,
        'email': tp.email,
        'address': tp.address,
        'telephone': tp.telephone,
        'charges': tp.charges,
        'loans': tp.loans,
        'history': tp.history,
    })

