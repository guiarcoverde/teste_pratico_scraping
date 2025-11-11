from scrapy import signals
from scrapy.http import HtmlResponse
import logging
from datetime import datetime
import time


class ResponseTimeMiddleware:
    """
    Mid-level use case: Track response times for monitoring.
    Useful for identifying slow endpoints and optimization.
    """
    
    def process_request(self, request, spider):
        request.meta['start_time'] = time.time()
    
    def process_response(self, request, response, spider):
        if 'start_time' in request.meta:
            elapsed = time.time() - request.meta['start_time']
            spider.logger.debug(f"Response time: {elapsed:.2f}s - {request.url}")
            
            if elapsed > 10:
                spider.logger.warning(
                    f"Slow response ({elapsed:.2f}s): {request.url}"
                )
        
        return response


class CustomUserAgentMiddleware:
    """
    Mid-level use case: Rotate user agents to avoid blocks.
    More sophisticated than default UserAgentMiddleware.
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
        self.current = 0
    
    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.user_agents[self.current]
        self.current = (self.current + 1) % len(self.user_agents)


class ErrorLoggingMiddleware:
    """
    Mid-level use case: Centralized error logging with context.
    Saves failed URLs to a file for later retry.
    """
    
    def __init__(self):
        self.failed_urls = []
    
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s
    
    def process_exception(self, request, exception, spider):
        self.failed_urls.append({
            'url': request.url,
            'exception': str(exception),
            'timestamp': datetime.now().isoformat()
        })
        
        spider.logger.error(
            f"Failed request: {request.url} - {exception}"
        )
    
    def spider_closed(self, spider):
        if self.failed_urls:
            import os
            os.makedirs('logs', exist_ok=True)
            filename = f'logs/failed_urls_{spider.name}_{datetime.now():%Y%m%d_%H%M%S}.txt'
            with open(filename, 'w') as f:
                for item in self.failed_urls:
                    f.write(f"{item['url']}\n")
            
            spider.logger.warning(
                f"Saved {len(self.failed_urls)} failed URLs to {filename}"
            )


class CaptchaDetectionMiddleware:
    """
    Mid-level use case: Detect when site returns captcha/block page.
    Pauses spider to avoid wasting requests.
    """
    
    def process_response(self, request, response, spider):
        captcha_indicators = [
            b'captcha',
            b'robot',
            b'blocked',
            b'access denied'
        ]
        
        body_lower = response.body.lower()
        
        if any(indicator in body_lower for indicator in captcha_indicators):
            spider.logger.critical(
                f"CAPTCHA/Block detected on {request.url}! "
                f"Consider adding delays or proxies."
            )
            
            spider.crawler.engine.close_spider(spider, 'captcha_detected')
        
        return response