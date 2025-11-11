import scrapy
import re
from datetime import datetime
from itemloaders.processors import MapCompose, TakeFirst, Identity
from w3lib.html import remove_tags


def clean_cnpj(cnpj):
    if not cnpj:
        return ''
    return ''.join(filter(str.isdigit, str(cnpj)))


def clean_numero_processo(text):
    if not text:
        return None
    
    text = text.strip()
    
    text = re.sub(r'^PROCESSO\s+N[ºO°]?\s*', '', text, flags=re.IGNORECASE)
    
    return text.strip()


def clean_data_autuacao(text):
    if not text:
        return None
    
    text = text.strip()
    
    if text.upper().startswith('AUTUADO EM'):
        text = text[10:].strip()
    
    return text


def parse_date(date_string):
    if not date_string:
        return None
    
    date_string = date_string.strip()
    
    if date_string.lower().startswith('em '):
        date_string = date_string[3:].strip()
    
    date_formats = [
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y',
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return date_string

def clean_text(text):
    if not text:
        return None
    return ' '.join(text.split())

class EnvolvidoItem(scrapy.Item):
    papel = scrapy.Field(
        input_processor = MapCompose(remove_tags, clean_text),
        output_processor = TakeFirst()
    )

    nome = scrapy.Field(
        input_processor = MapCompose(remove_tags, clean_text),
        output_processor = TakeFirst()
    )

class MovimentacaoItem(scrapy.Item):
    data = scrapy.Field(
        input_processor = MapCompose(remove_tags, clean_text, parse_date),
        output_processor = TakeFirst()
    )

    texto = scrapy.Field(
        input_processor = MapCompose(remove_tags, clean_text),
        output_processor = TakeFirst()
    )

class ProcessoItem(scrapy.Item):
    numero_processo = scrapy.Field(
        input_processor = MapCompose(remove_tags, clean_text, clean_numero_processo),
        output_processor = TakeFirst()
    )
    
    numero_legado = scrapy.Field(
        input_processor = MapCompose(remove_tags, clean_text),
        output_processor = TakeFirst()
    )

    data_autuacao = scrapy.Field(
        input_processor = MapCompose(remove_tags, clean_text, clean_data_autuacao, parse_date),
        output_processor = TakeFirst()
    )

    envolvidos = scrapy.Field(
        input_processor = Identity(),
        output_processor = TakeFirst()
    )

    relator = scrapy.Field(
        input_processor = MapCompose(remove_tags, clean_text),
        output_processor = TakeFirst()
    )

    movimentacoes = scrapy.Field(
        input_processor = Identity()
    )

    url = scrapy.Field(output_processor = TakeFirst())
    data_extracao = scrapy.Field(output_processor = TakeFirst())
    

