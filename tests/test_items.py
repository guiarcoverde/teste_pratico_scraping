"""
Testes unitários para Items e processadores de dados
"""
import unittest
from datetime import datetime
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse

from trf_scraper.items import (
    ProcessoItem, 
    EnvolvidoItem, 
    MovimentacaoItem,
    clean_numero_processo,
    clean_data_autuacao,
    clean_cnpj,
    parse_date,
    clean_text
)


class TestCleanFunctions(unittest.TestCase):
    """Testa funções de limpeza de dados"""
    
    def test_clean_numero_processo_with_prefix(self):
        """Testa remoção do prefixo 'PROCESSO Nº'"""
        result = clean_numero_processo("PROCESSO Nº 0015648-78.1999.4.05.0000")
        self.assertEqual(result, "0015648-78.1999.4.05.0000")
    
    def test_clean_numero_processo_variants(self):
        """Testa variações do prefixo"""
        test_cases = [
            ("PROCESSO NO 0015648-78.1999.4.05.0000", "0015648-78.1999.4.05.0000"),
            ("PROCESSO N° 0015648-78.1999.4.05.0000", "0015648-78.1999.4.05.0000"),
            ("processo n 0015648-78.1999.4.05.0000", "0015648-78.1999.4.05.0000"),
        ]
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                result = clean_numero_processo(input_val)
                self.assertEqual(result, expected)
    
    def test_clean_numero_processo_without_prefix(self):
        """Testa número sem prefixo"""
        result = clean_numero_processo("0015648-78.1999.4.05.0000")
        self.assertEqual(result, "0015648-78.1999.4.05.0000")
    
    def test_clean_numero_processo_none(self):
        """Testa valor None"""
        result = clean_numero_processo(None)
        self.assertIsNone(result)
    
    def test_clean_data_autuacao_with_prefix(self):
        """Testa remoção do prefixo 'AUTUADO EM'"""
        result = clean_data_autuacao("AUTUADO EM 15/04/1999")
        self.assertEqual(result, "15/04/1999")
    
    def test_clean_data_autuacao_without_prefix(self):
        """Testa data sem prefixo"""
        result = clean_data_autuacao("15/04/1999")
        self.assertEqual(result, "15/04/1999")
    
    def test_clean_cnpj(self):
        """Testa limpeza de CNPJ"""
        test_cases = [
            ("12.345.678/0001-90", "12345678000190"),
            ("12345678000190", "12345678000190"),
            ("", ""),
            (None, ""),
        ]
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                result = clean_cnpj(input_val)
                self.assertEqual(result, expected)
    
    def test_parse_date_full_datetime(self):
        """Testa parsing de data/hora completa"""
        result = parse_date("11/11/2025 14:30:45")
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2025)
        self.assertEqual(result.month, 11)
        self.assertEqual(result.day, 11)
    
    def test_parse_date_short_datetime(self):
        """Testa parsing de data/hora sem segundos"""
        result = parse_date("11/11/2025 14:30")
        self.assertIsInstance(result, datetime)
    
    def test_parse_date_only_date(self):
        """Testa parsing apenas de data"""
        result = parse_date("15/04/1999")
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 1999)
    
    def test_parse_date_with_em_prefix(self):
        """Testa parsing com prefixo 'Em'"""
        result = parse_date("Em 15/04/1999")
        self.assertIsInstance(result, datetime)
    
    def test_parse_date_invalid(self):
        """Testa data inválida"""
        result = parse_date("invalid date")
        self.assertEqual(result, "invalid date")
    
    def test_clean_text(self):
        """Testa limpeza de texto"""
        test_cases = [
            ("  texto  com   espaços  ", "texto com espaços"),
            ("texto\nnormal", "texto normal"),
            ("texto\t\ttab", "texto tab"),
            (None, None),
        ]
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                result = clean_text(input_val)
                self.assertEqual(result, expected)


class TestProcessoItem(unittest.TestCase):
    """Testa ProcessoItem e seus processadores"""
    
    def setUp(self):
        """Cria um HTML response mock para testes"""
        html = """
        <html>
            <body>
                <p>PROCESSO Nº 0015648-78.1999.4.05.0000</p>
                <p>(99.05.15648-8)</p>
                <td>AUTUADO EM 15/04/1999</td>
            </body>
        </html>
        """
        self.response = HtmlResponse(
            url='http://example.com',
            body=html.encode('utf-8')
        )
    
    def test_processo_item_loader(self):
        """Testa ItemLoader para ProcessoItem"""
        loader = ItemLoader(item=ProcessoItem(), response=self.response)
        
        loader.add_xpath('numero_processo', "//p[contains(., 'PROCESSO')]/text()")
        loader.add_xpath('numero_legado', "//p[contains(., '(')]/text()")
        loader.add_xpath('data_autuacao', "//td[contains(., 'AUTUADO')]/text()")
        
        item = loader.load_item()
        
        self.assertEqual(item['numero_processo'], '0015648-78.1999.4.05.0000')
        self.assertEqual(item['numero_legado'], '(99.05.15648-8)')
        self.assertIsInstance(item['data_autuacao'], datetime)
    
    def test_processo_item_url_and_data_extracao(self):
        """Testa campos URL e data_extracao"""
        loader = ItemLoader(item=ProcessoItem(), response=self.response)
        
        test_url = "https://cp.trf5.jus.br/cp/cp.do"
        test_date = datetime.now()
        
        loader.add_value('url', test_url)
        loader.add_value('data_extracao', test_date)
        
        item = loader.load_item()
        
        self.assertEqual(item['url'], test_url)
        self.assertEqual(item['data_extracao'], test_date)


class TestEnvolvidoItem(unittest.TestCase):
    """Testa EnvolvidoItem"""
    
    def test_envolvido_item_loader(self):
        """Testa ItemLoader para EnvolvidoItem"""
        html = """
        <html>
            <body>
                <td>APTE</td>
                <td>MARIA MARLENE GOMES MARQUES</td>
            </body>
        </html>
        """
        response = HtmlResponse(url='http://example.com', body=html.encode('utf-8'))
        
        loader = ItemLoader(item=EnvolvidoItem(), response=response)
        loader.add_xpath('papel', '//td[1]/text()')
        loader.add_xpath('nome', '//td[2]/text()')
        
        item = loader.load_item()
        
        self.assertEqual(item['papel'], 'APTE')
        self.assertEqual(item['nome'], 'MARIA MARLENE GOMES MARQUES')
    
    def test_envolvido_item_clean_whitespace(self):
        """Testa limpeza de espaços extras"""
        html = """
        <html>
            <body>
                <td>  Advogado/Procurador  </td>
                <td>  JALES  DE  SENA  RIBEIRO  </td>
            </body>
        </html>
        """
        response = HtmlResponse(url='http://example.com', body=html.encode('utf-8'))
        
        loader = ItemLoader(item=EnvolvidoItem(), response=response)
        loader.add_xpath('papel', '//td[1]/text()')
        loader.add_xpath('nome', '//td[2]/text()')
        
        item = loader.load_item()
        
        self.assertEqual(item['papel'], 'Advogado/Procurador')
        self.assertEqual(item['nome'], 'JALES DE SENA RIBEIRO')


class TestMovimentacaoItem(unittest.TestCase):
    """Testa MovimentacaoItem"""
    
    def test_movimentacao_item_loader(self):
        """Testa ItemLoader para MovimentacaoItem"""
        html = """
        <html>
            <body>
                <a name="mov_1">11/11/2025 14:30:00</a>
                <td width="95%">Baixa Definitiva - Processo Migrado para o PJe.</td>
            </body>
        </html>
        """
        response = HtmlResponse(url='http://example.com', body=html.encode('utf-8'))
        
        loader = ItemLoader(item=MovimentacaoItem(), response=response)
        loader.add_xpath('data', '//a[@name="mov_1"]/text()')
        loader.add_xpath('texto', '//td[@width="95%"]/text()')
        
        item = loader.load_item()
        
        self.assertIsInstance(item['data'], datetime)
        self.assertEqual(item['texto'], 'Baixa Definitiva - Processo Migrado para o PJe.')


if __name__ == '__main__':
    unittest.main()
