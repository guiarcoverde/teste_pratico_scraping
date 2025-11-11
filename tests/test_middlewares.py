"""
Testes unitários para Middlewares
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from scrapy.http import HtmlResponse, Request
from scrapy import signals
import time

from trf_scraper.middlewares import (
    ResponseTimeMiddleware,
    CustomUserAgentMiddleware,
    ErrorLoggingMiddleware,
    CaptchaDetectionMiddleware
)


class TestResponseTimeMiddleware(unittest.TestCase):
    """Testa o middleware de tempo de resposta"""
    
    def setUp(self):
        """Configura o middleware"""
        self.middleware = ResponseTimeMiddleware()
        self.spider = Mock()
        self.spider.logger = Mock()
    
    def test_process_request_adds_start_time(self):
        """Testa que process_request adiciona start_time"""
        request = Request('http://example.com')
        
        self.middleware.process_request(request, self.spider)
        
        self.assertIn('start_time', request.meta)
        self.assertIsInstance(request.meta['start_time'], float)
    
    def test_process_response_logs_time(self):
        """Testa que process_response loga o tempo"""
        request = Request('http://example.com')
        request.meta['start_time'] = time.time() - 2  # 2 segundos atrás
        
        response = HtmlResponse(
            url='http://example.com',
            request=request,
            body=b'<html></html>'
        )
        
        result = self.middleware.process_response(request, response, self.spider)
        
        self.assertEqual(result, response)
        self.spider.logger.debug.assert_called()
    
    def test_process_response_warns_slow_response(self):
        """Testa warning para respostas lentas"""
        request = Request('http://example.com')
        request.meta['start_time'] = time.time() - 11  # 11 segundos atrás
        
        response = HtmlResponse(
            url='http://example.com',
            request=request,
            body=b'<html></html>'
        )
        
        self.middleware.process_response(request, response, self.spider)
        
        self.spider.logger.warning.assert_called()
    
    def test_process_response_without_start_time(self):
        """Testa resposta sem start_time"""
        request = Request('http://example.com')
        response = HtmlResponse(
            url='http://example.com',
            request=request,
            body=b'<html></html>'
        )
        
        result = self.middleware.process_response(request, response, self.spider)
        
        self.assertEqual(result, response)
        self.spider.logger.debug.assert_not_called()


class TestCustomUserAgentMiddleware(unittest.TestCase):
    """Testa o middleware de User-Agent"""
    
    def setUp(self):
        """Configura o middleware"""
        self.middleware = CustomUserAgentMiddleware()
        self.spider = Mock()
    
    def test_process_request_sets_user_agent(self):
        """Testa que process_request define User-Agent"""
        request = Request('http://example.com')
        
        self.middleware.process_request(request, self.spider)
        
        self.assertIn('User-Agent', request.headers)
    
    def test_process_request_rotates_user_agents(self):
        """Testa rotação de User-Agents"""
        request1 = Request('http://example.com/1')
        request2 = Request('http://example.com/2')
        request3 = Request('http://example.com/3')
        
        self.middleware.process_request(request1, self.spider)
        ua1 = request1.headers.get('User-Agent')
        
        self.middleware.process_request(request2, self.spider)
        ua2 = request2.headers.get('User-Agent')
        
        self.middleware.process_request(request3, self.spider)
        ua3 = request3.headers.get('User-Agent')
        
        # Deve rotacionar
        self.assertIsNotNone(ua1)
        self.assertIsNotNone(ua2)
        self.assertIsNotNone(ua3)


class TestErrorLoggingMiddleware(unittest.TestCase):
    """Testa o middleware de log de erros"""
    
    def setUp(self):
        """Configura o middleware"""
        self.middleware = ErrorLoggingMiddleware()
        self.spider = Mock()
        self.spider.logger = Mock()
        self.spider.name = 'test_spider'
    
    def test_process_exception_logs_error(self):
        """Testa que exceções são logadas"""
        request = Request('http://example.com')
        exception = Exception("Test error")
        
        self.middleware.process_exception(request, exception, self.spider)
        
        self.assertEqual(len(self.middleware.failed_urls), 1)
        self.spider.logger.error.assert_called()
    
    def test_process_exception_stores_url(self):
        """Testa que URL é armazenada"""
        request = Request('http://example.com/test')
        exception = Exception("Test error")
        
        self.middleware.process_exception(request, exception, self.spider)
        
        failed_url = self.middleware.failed_urls[0]
        self.assertEqual(failed_url['url'], 'http://example.com/test')
        self.assertIn('exception', failed_url)
        self.assertIn('timestamp', failed_url)
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=MagicMock)
    def test_spider_closed_saves_failed_urls(self, mock_open, mock_makedirs):
        """Testa salvamento de URLs falhadas"""
        request = Request('http://example.com')
        exception = Exception("Test error")
        self.middleware.process_exception(request, exception, self.spider)
        
        self.middleware.spider_closed(self.spider)
        
        mock_makedirs.assert_called_once_with('logs', exist_ok=True)
        mock_open.assert_called_once()
        self.spider.logger.warning.assert_called()
    
    @patch('os.makedirs')
    def test_spider_closed_no_failed_urls(self, mock_makedirs):
        """Testa quando não há URLs falhadas"""
        self.middleware.spider_closed(self.spider)
        
        mock_makedirs.assert_not_called()
        self.spider.logger.warning.assert_not_called()
    
    def test_from_crawler(self):
        """Testa criação do middleware a partir do crawler"""
        crawler = Mock()
        crawler.signals = Mock()
        
        middleware = ErrorLoggingMiddleware.from_crawler(crawler)
        
        self.assertIsInstance(middleware, ErrorLoggingMiddleware)
        crawler.signals.connect.assert_called_once()


class TestCaptchaDetectionMiddleware(unittest.TestCase):
    """Testa o middleware de detecção de CAPTCHA"""
    
    def setUp(self):
        """Configura o middleware"""
        self.middleware = CaptchaDetectionMiddleware()
        self.spider = Mock()
        self.spider.logger = Mock()
        self.spider.crawler = Mock()
        self.spider.crawler.engine = Mock()
    
    def test_process_response_normal(self):
        """Testa resposta normal (sem CAPTCHA)"""
        request = Request('http://example.com')
        response = HtmlResponse(
            url='http://example.com',
            body=b'<html><body>Normal content</body></html>'
        )
        
        result = self.middleware.process_response(request, response, self.spider)
        
        self.assertEqual(result, response)
        self.spider.logger.critical.assert_not_called()
    
    def test_process_response_captcha_detected(self):
        """Testa detecção de CAPTCHA"""
        request = Request('http://example.com')
        response = HtmlResponse(
            url='http://example.com',
            body=b'<html><body>Please solve this CAPTCHA</body></html>'
        )
        
        self.middleware.process_response(request, response, self.spider)
        
        self.spider.logger.critical.assert_called()
        self.spider.crawler.engine.close_spider.assert_called_with(
            self.spider, 
            'captcha_detected'
        )
    
    def test_process_response_robot_detected(self):
        """Testa detecção de mensagem de robot"""
        request = Request('http://example.com')
        response = HtmlResponse(
            url='http://example.com',
            body=b'<html><body>We detected robot behavior</body></html>'
        )
        
        self.middleware.process_response(request, response, self.spider)
        
        self.spider.logger.critical.assert_called()
        self.spider.crawler.engine.close_spider.assert_called()
    
    def test_process_response_blocked(self):
        """Testa detecção de bloqueio"""
        request = Request('http://example.com')
        response = HtmlResponse(
            url='http://example.com',
            body=b'<html><body>Access blocked</body></html>'
        )
        
        self.middleware.process_response(request, response, self.spider)
        
        self.spider.logger.critical.assert_called()
        self.spider.crawler.engine.close_spider.assert_called()


if __name__ == '__main__':
    unittest.main()
