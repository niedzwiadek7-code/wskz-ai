import base64
import quopri


def parse_body(item: dict) -> str:
    content = item.get('Content', {})
    cte = (content.get('Headers', {}).get('Content-Transfer-Encoding') or ['7bit'])[0].lower()
    body = content.get('Body', '')
    if cte == 'quoted-printable':
        return quopri.decodestring(body).decode('utf-8')
    if cte == 'base64':
        return base64.b64decode(body).decode('utf-8')
    return body
