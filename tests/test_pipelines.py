"""
Testes unitários para Pipelines
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from trf_scraper.pipelines import MongoDBPipeline
from trf_scraper.items import ProcessoItem, EnvolvidoItem, MovimentacaoItem


class TestMongoDBPipeline(unittest.TestCase):
    """Testa o pipeline de MongoDB"""
    
    def setUp(self):
        """Configura o pipeline para testes"""
        self.mongo_uri = "mongodb://admin:1234@localhost:27017/"
        self.mongo_db = "test_db"
        self.pipeline = MongoDBPipeline(self.mongo_uri, self.mongo_db)
        
        # Mock do spider
        self.spider = Mock()
        self.spider.logger = Mock()
        self.spider.crawler = Mock()
        self.spider.crawler.stats = Mock()
    
    @patch('pymongo.MongoClient')
    def test_open_spider_success(self, mock_mongo_client):
        """Testa abertura bem-sucedida da conexão"""
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        self.pipeline.open_spider(self.spider)
        
        mock_mongo_client.assert_called_once()
        mock_client.admin.command.assert_called_with('ping')
        self.assertIsNotNone(self.pipeline.client)
        self.assertIsNotNone(self.pipeline.db)
    
    @patch('pymongo.MongoClient')
    def test_open_spider_connection_failure(self, mock_mongo_client):
        """Testa falha na conexão"""
        from pymongo.errors import ConnectionFailure
        mock_mongo_client.side_effect = ConnectionFailure("Connection failed")
        
        self.pipeline.open_spider(self.spider)
        
        self.assertIsNone(self.pipeline.client)
        self.spider.logger.error.assert_called()
    
    def test_close_spider(self):
        """Testa fechamento da conexão"""
        mock_client = MagicMock()
        self.pipeline.client = mock_client
        
        self.pipeline.close_spider(self.spider)
        
        mock_client.close.assert_called_once()
    
    def test_process_item_without_connection(self):
        """Testa processamento quando não há conexão"""
        self.pipeline.client = None
        
        item = {'numero_processo': '0015648-78.1999.4.05.0000'}
        result = self.pipeline.process_item(item, self.spider)
        
        self.assertEqual(result, item)
    
    @patch('pymongo.MongoClient')
    def test_process_item_insert(self, mock_mongo_client):
        """Testa inserção de novo item"""
        # Setup
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_client.__getitem__.return_value = mock_db
        mock_db.processos = mock_collection
        
        # Mock do resultado da operação (novo documento inserido)
        mock_result = MagicMock()
        mock_result.upserted_id = "new_id_123"
        mock_collection.update_one.return_value = mock_result
        
        self.pipeline.client = mock_client
        self.pipeline.db = mock_db
        
        # Item de teste
        item = {
            'numero_processo': '0015648-78.1999.4.05.0000',
            'data_autuacao': datetime(1999, 4, 15),
            'envolvidos': [],
            'movimentacoes': []
        }
        
        # Executa
        result = self.pipeline.process_item(item, self.spider)
        
        # Verifica
        self.assertEqual(result, item)
        mock_collection.update_one.assert_called_once()
        self.spider.crawler.stats.inc_value.assert_called_with('mongodb/items_inserted')
    
    @patch('pymongo.MongoClient')
    def test_process_item_update(self, mock_mongo_client):
        """Testa atualização de item existente"""
        # Setup
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_client.__getitem__.return_value = mock_db
        mock_db.processos = mock_collection
        
        # Mock do resultado da operação (documento atualizado)
        mock_result = MagicMock()
        mock_result.upserted_id = None  # None indica update, não insert
        mock_collection.update_one.return_value = mock_result
        
        self.pipeline.client = mock_client
        self.pipeline.db = mock_db
        
        # Item de teste
        item = {
            'numero_processo': '0015648-78.1999.4.05.0000',
            'data_autuacao': datetime(1999, 4, 15),
        }
        
        # Executa
        result = self.pipeline.process_item(item, self.spider)
        
        # Verifica
        self.assertEqual(result, item)
        self.spider.crawler.stats.inc_value.assert_called_with('mongodb/items_updated')
    
    @patch('pymongo.MongoClient')
    def test_process_item_without_numero_processo(self, mock_mongo_client):
        """Testa item sem número de processo"""
        mock_client = MagicMock()
        mock_db = MagicMock()
        
        self.pipeline.client = mock_client
        self.pipeline.db = mock_db
        
        # Item sem numero_processo
        item = {
            'data_autuacao': datetime(1999, 4, 15),
        }
        
        result = self.pipeline.process_item(item, self.spider)
        
        self.assertEqual(result, item)
        self.spider.crawler.stats.inc_value.assert_called_with('mongodb/items_skipped')
    
    @patch('pymongo.MongoClient')
    def test_process_item_pymongo_error(self, mock_mongo_client):
        """Testa tratamento de erro do PyMongo"""
        from pymongo.errors import PyMongoError
        
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_client.__getitem__.return_value = mock_db
        mock_db.processos = mock_collection
        mock_collection.update_one.side_effect = PyMongoError("Database error")
        
        self.pipeline.client = mock_client
        self.pipeline.db = mock_db
        
        item = {'numero_processo': '0015648-78.1999.4.05.0000'}
        
        result = self.pipeline.process_item(item, self.spider)
        
        self.assertEqual(result, item)
        self.spider.logger.error.assert_called()
        self.spider.crawler.stats.inc_value.assert_called_with('mongodb/errors')
    
    def test_from_crawler(self):
        """Testa criação do pipeline a partir do crawler"""
        crawler = Mock()
        crawler.settings.get.side_effect = lambda key, default: {
            'MONGO_URI': 'mongodb://custom:custom@localhost:27017/',
            'MONGO_DATABASE': 'custom_db'
        }.get(key, default)
        
        pipeline = MongoDBPipeline.from_crawler(crawler)
        
        self.assertIsInstance(pipeline, MongoDBPipeline)
        self.assertEqual(pipeline.mongo_uri, 'mongodb://custom:custom@localhost:27017/')
        self.assertEqual(pipeline.mongo_db, 'custom_db')


if __name__ == '__main__':
    unittest.main()
