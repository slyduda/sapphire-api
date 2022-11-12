Mutli = TypeVar('Multi', list[Any])
URI = TypeVar('URI', str)
TEL = TypeVar('TEL', URI, str)
x_name = type('x-')
iana_token = type('iana-token')
media_type = 'application/pgp-keys' | 'text/calendar'
type_param_tel = "text" | "voice" | "fax" | "cell" | "video" | "pager" | "textphone" | iana_token | x_name
type_param_kind = 'individual' | 'group' | 'org' | 'location' | x_name | iana_token

class VCardNProperty(NamedTuple):
    family: list[str]
    given: list[str]
    additional: list[str]
    prefixes: list[str]
    suffixes: list[str]


class VCardAddressProperty(NamedTuple):
    pobox: list[str]
    ext: list[str]
    street: list[str]
    locality: list[str]
    region: list[str]
    code: list[str]
    country: list[str]


class VCardOrgProperty(NamedTuple):
    name: str
    primary: str | None
    secondary: str | None


v_card_outline = {
    'SOURCE': URI,
    'KIND': type_param_kind,
    'XML': str,
    'FN': str,
    'N': VCardNProperty, 
    'NICKNAME': Mutlti[list[str] | tuple[str, list[str]]], 
    'PHOTO':  tuple[media_type, URI] | URI, 
    'BDAY': datetime | str,
    'ANNIVERSARY': datetime | str,
    'GENDER': tuple[str | None, str, None],
    'ADR': Mutli[VCardAddressProperty | tuple[str, VCardAddressProperty]],
    'TEL': Mutli[TEL | tuple[type_param_tel, TEL]], 
    'EMAIL': Mutli[str | tuple[str, str]],
    'IMPP': Mutli[URI], 
    'LANG': Mutli[str],

    'TZ': str,
    'GEO': URI,

    'TITLE': str,
    'ROLE': str,
    'LOGO': str,
     
    'ORG': '', 
    'MEMBER': Mutlti[URI],
    'RELATED': Mutli[URI, str],
     
    'CATEGORIES': list[str], 
    'NOTE': str,
    'PRODID': str,
    'REV': datetime,
    'SOUND': URI,
    'UID': UUID,
    'CLIENTPIDMAP': Mutli[tuple[int, UUID]],
    'URL': Mutli[URI],
    'VERSION': int,
    'KEY': Mutli[str | tuple[media_type, URI]],

    'FBURL': Mutli[tuple[media_type, URI]],
    'CALADRURI': Mutli[URI],
    'CALURI': Mutli[URI],

    'X-PRONOUNS': Multi[list[str]],
    'X-SOCIALPROFILE': Multi[tuple[str, URI]],
}