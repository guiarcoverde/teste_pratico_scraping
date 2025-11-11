"""
Testes de integração end-to-end

NOTA: Estes testes requerem MongoDB rodando e podem fazer requisições reais
ao site do TRF5. Use com cuidado em ambientes de CI/CD.
"""
import unittest
from unittest.mock import patch, Mock
from scrapy.http import HtmlResponse, Request
from scrapy.utils.test import get_crawler
from twisted.internet import defer
from scrapy.utils.project import get_project_settings

from trf_scraper.spiders.processo_spider import ProcessoSpider
from trf_scraper.pipelines import MongoDBPipeline


class TestIntegrationProcessoSpider(unittest.TestCase):
    """Testes de integração do spider"""
    
    def setUp(self):
        """Configura o ambiente de teste"""
        self.settings = get_project_settings()
        self.settings['MONGO_URI'] = "mongodb://admin:1234@localhost:27017/"
        self.settings['MONGO_DATABASE'] = "test_trf5"
    
    def test_spider_with_processo_number(self):
        """Testa spider com número de processo - acesso direto via GET"""
        spider = ProcessoSpider(processos="00156487819994050000")
        
        # start_requests agora retorna Request direto, não mais FormRequest
        requests = list(spider.start_requests())
        
        # Verifica que foi criado um Request
        self.assertEqual(len(requests), 1)
        self.assertIn('00156487819994050000', requests[0].url)
        self.assertEqual(requests[0].callback.__name__, 'parse_processo')
    
    def test_spider_parse_processo_integration(self):
        """Testa parsing completo de um processo"""
        spider = ProcessoSpider(processos="00156487819994050000")
        
        # HTML real simplificado de um processo
        html = """
        <html>
            <body>
                <p>PROCESSO Nº 0015648-78.1999.4.05.0000</p>
                <p>(99.05.15648-8)</p>
                <table>
                    <tr>
                        <td>AUTUADO EM</td>
                        <td><div>15/04/1999</div></td>
                    </tr>
                </table>
                <table>
                    <tr>
                        <td>RELATOR</td>
                        <td>:</td>
                    </tr>
                    <tr>
                        <td>APTE</td>
                        <td>: MARIA MARLENE GOMES MARQUES</td>
                    </tr>
                    <tr>
                        <td>Advogado/Procurador</td>
                        <td>: JALES DE SENA RIBEIRO - CE006397</td>
                    </tr>
                </table>
                <a name="mov_1">2021-09-11 16:50:00</a>
                <td width="95%">Baixa Definitiva - Processo Migrado para o PJe .</td>
            </body>
        </html>
        """
        
        response = HtmlResponse(
            url='https://cp.trf5.jus.br/cp/cp.do',
            body=html.encode('utf-8'),
            encoding='utf-8'
        )
        
        # Parse
        results = list(spider.parse_processo(response))
        
        # Verificações
        self.assertEqual(len(results), 1)
        item = results[0]
        
        self.assertIn('numero_processo', item)
        self.assertIn('envolvidos', item)
        self.assertIn('movimentacoes', item)
        self.assertIn('url', item)
        
        # Verifica estrutura dos envolvidos
        if item['envolvidos']:
            self.assertIsInstance(item['envolvidos'], list)
        
        # Verifica estrutura das movimentações
        if item['movimentacoes']:
            self.assertIsInstance(item['movimentacoes'], list)


class TestIntegrationPipeline(unittest.TestCase):
    """Testes de integração do pipeline"""
    
    @patch('pymongo.MongoClient')
    def test_pipeline_full_flow(self, mock_mongo_client):
        """Testa fluxo completo do pipeline"""
        # Setup com MagicMock para suportar __getitem__
        from unittest.mock import MagicMock
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.processos = mock_collection
        
        mock_result = Mock()
        mock_result.upserted_id = "new_id"
        mock_collection.update_one.return_value = mock_result
        
        # Pipeline
        pipeline = MongoDBPipeline(
            mongo_uri="mongodb://admin:1234@localhost:27017/",
            mongo_db="test_db"
        )
        
        spider = Mock()
        spider.logger = Mock()
        spider.crawler = Mock()
        spider.crawler.stats = Mock()
        
        # Open spider
        pipeline.open_spider(spider)
        
        # Process item
        item = {
            'numero_processo': '0015648-78.1999.4.05.0000',
            'numero_legado': '(99.05.15648-8)',
            'data_autuacao': '15/04/1999',
            'envolvidos': [
                {'papel': 'APTE', 'nome': 'MARIA MARLENE'}
            ],
            'movimentacoes': [
                {'data': '2021-09-11 16:50:00', 'texto': 'Baixa Definitiva'}
            ]
        }
        
        result = pipeline.process_item(item, spider)
        
        # Close spider
        pipeline.close_spider(spider)
        
        # Verificações
        self.assertEqual(result, item)
        mock_collection.update_one.assert_called_once()
        mock_client.close.assert_called_once()


class TestIntegrationDataFlow(unittest.TestCase):
    """Testa fluxo completo de dados"""
    
    def test_item_to_dict_conversion(self):
        """Testa conversão de Item para dict"""
        from trf_scraper.items import ProcessoItem, EnvolvidoItem
        from scrapy.loader import ItemLoader
        from scrapy.http import HtmlResponse
        
        html = """
        <html>
            <body>
                <p>PROCESSO Nº 0015648-78.1999.4.05.0000</p>
            </body>
        </html>
        """
        
        response = HtmlResponse(
            url='http://example.com',
            body=html.encode('utf-8')
        )
        
        loader = ItemLoader(item=ProcessoItem(), response=response)
        loader.add_xpath('numero_processo', "//p/text()")
        loader.add_value('url', 'http://example.com')
        
        item = loader.load_item()
        item_dict = dict(item)
        
        self.assertIsInstance(item_dict, dict)
        self.assertIn('numero_processo', item_dict)
        self.assertEqual(item_dict['numero_processo'], '0015648-78.1999.4.05.0000')


if __name__ == '__main__':
    unittest.main()
