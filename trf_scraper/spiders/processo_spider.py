from datetime import datetime
import scrapy
from scrapy.http import FormRequest
from scrapy.loader import ItemLoader

from trf_scraper.items import ProcessoItem, EnvolvidoItem, MovimentacaoItem


class ProcessoSpider(scrapy.Spider):
    
    name = "processo"
    allowed_domains = ["www5.trf5.jus.br", "cp.trf5.jus.br"]
    
    START_URL = 'http://www5.trf5.jus.br/cp/'
    FORM_ACTION_URL = 'https://cp.trf5.jus.br/cp/cp.do'
    PROCESSO_URL = 'https://cp.trf5.jus.br/processo/{}'  # Acesso direto por GET

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
    }

    def __init__(self, processos=None, cnpj=None, *args, **kwargs):
        super(ProcessoSpider, self).__init__(*args, **kwargs)
        self.processos = processos.split(',') if processos else []
        self.cnpj = cnpj

        if not self.processos and not self.cnpj:
            raise ValueError("Informe pelo menos um parâmetro: processos ou cnpj")
        
        self.logger.info(f"Spider inicializado - Processos: {len(self.processos)}, CNPJ: {bool(self.cnpj)}")
        
    def start_requests(self):
        """
        Inicia requisições:
        - Processos individuais: GET direto (mais rápido e eficiente)
        - CNPJ: POST via formulário (necessário para busca)
        """
        # Processos individuais - Acesso direto via GET
        for processo in self.processos:
            processo = processo.strip()
            if not processo:
                continue
            
            # Remove formatação do número do processo para a URL
            processo_limpo = processo.replace('-', '').replace('.', '')
            url = self.PROCESSO_URL.format(processo_limpo)
            
            self.logger.info(f"Acessando processo diretamente: {processo} -> {url}")
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_processo,
                meta={
                    'numero_busca': processo,
                    'dont_cache': True,
                },
                priority=1,
                errback=self.handle_error
            )
        
        # CNPJ - Requer formulário
        if self.cnpj:
            self.logger.info(f"Acessando formulário para busca por CNPJ: {self.cnpj}")
            
            yield scrapy.Request(
                url=self.START_URL,
                callback=self.parse_form_cnpj,
                meta={'cnpj': self.cnpj},
                priority=2,
                errback=self.handle_error
            )

    def parse_form_cnpj(self, response):
        """Processa formulário e faz busca por CNPJ"""
        cnpj = response.meta.get('cnpj')
        cnpj_limpo = self._clean_cnpj(cnpj)
        
        self.logger.info(f"Criando request para CNPJ: {cnpj_limpo}")
        
        formdata = self._build_formdata_cnpj(cnpj_limpo)
        yield FormRequest(
            url=self.FORM_ACTION_URL,
            formdata=formdata,
            callback=self.parse_lista_processos,
            meta={'dont_cache': True},
            priority=2,
            errback=self.handle_error
        )

    def parse_lista_processos(self, response):
        self.logger.info("Processando lista de processos do CNPJ...")
        
        links = response.css('a.linkar::attr(href)').getall()
        
        if not links:
            self.logger.warning(
                f"Nenhum processo encontrado na busca por CNPJ. "
                f"URL: {response.url}"
            )
            self._save_debug_html(response, 'lista_cnpj_vazia')
            return
        
        self.logger.info(f"Encontrados {len(links)} processos para o CNPJ")
        
        for link in links:
            yield response.follow(
                link,
                callback=self.parse_processo,
                errback=self.handle_error
            )

    def parse_processo(self, response):
        self.logger.info(f"Processando página do processo: {response.url}")
        
        # Debug: Check if process number is found
        has_process = response.xpath("//p[contains(., 'PROCESSO N')]").get()
        self.logger.info(f"Process header found: {has_process is not None}")
        if has_process:
            self.logger.info(f"Process header text: {has_process[:100]}")
        
        if self._is_error_page(response):
            # Extract more details about why it was detected as error
            processo_num = response.xpath("//p[contains(., 'PROCESSO N')]/text()").get()
            self.logger.error(f"Página de erro detectada: {response.url}")
            self.logger.error(f"Status code: {response.status}")
            self.logger.error(f"Processo number found in page: {processo_num}")
            self.logger.error(f"Response encoding: {response.encoding}")
            self.logger.error(f"Response body length: {len(response.body)} bytes")
            
            # Check what triggered the error
            body_text = response.text.lower()
            error_keywords = ['processo não encontrado', 'página não encontrada', 'erro ao consultar', 'consulta inválida', 'nenhum processo foi encontrado']
            found_errors = [kw for kw in error_keywords if kw in body_text]
            if found_errors:
                self.logger.error(f"Error keywords found: {found_errors}")
            else:
                self.logger.error(f"No error keywords found, but has_process_number={has_process is not None}")
            
            self._save_debug_html(response, 'erro_processo')
            return
        
        loader = ItemLoader(item=ProcessoItem(), response=response)
        
        loader.add_xpath('numero_processo', "//p[contains(., 'PROCESSO N')]/text()")
        loader.add_xpath('numero_legado', "//p[contains(., '(') and contains(., ')')]/text()")
        loader.add_xpath('data_autuacao', "//td[contains(., 'AUTUADO EM')]//div/text()")
        
        loader.add_value('url', response.url)
        loader.add_value('data_extracao', datetime.now())
        
        item = loader.load_item()
        
        item['envolvidos'] = self._extract_envolvidos(response)
        
        item['movimentacoes'] = self._extract_movimentacoes(response)
        
        if not item.get('numero_processo') and item.get('numero_legado'):
            item['numero_processo'] = item['numero_legado']
        
        if not item.get('numero_processo'):
            self.logger.warning(f"Processo sem número identificado: {response.url}")
            self._save_debug_html(response, 'processo_sem_numero')
        elif not self._validate_numero_processo(item['numero_processo']):
            self.logger.error(
                f"Número de processo inválido: {item['numero_processo']} - {response.url}"
            )
            self.crawler.stats.inc_value('validation/invalid_numero_processo')
            return
        
        yield item

    def _validate_numero_processo(self, numero):
        if not numero or not isinstance(numero, str):
            return False
        
        numero_limpo = ''.join(filter(str.isdigit, numero))
        
        return len(numero_limpo) == 20

    def _extract_envolvidos(self, response):
        envolvidos = []
        
        blocos = response.xpath("//table[.//td[contains(., 'RELATOR')]]//tr")
        
        for bloco in blocos:
            papel_text = bloco.xpath('.//td[1]//text()').getall()
            nome_text = bloco.xpath('.//td[2]//text()').getall()
            
            papel = ' '.join([t.strip() for t in papel_text if t.strip() and t.strip() != ':']).strip()
            nome = ' '.join([t.strip() for t in nome_text if t.strip()]).strip()
            
            nome = nome.lstrip(':').strip()
            
            if papel and nome:
                loader = ItemLoader(item=EnvolvidoItem())
                loader.add_value('papel', papel)
                loader.add_value('nome', nome)
                envolvidos.append(loader.load_item())
        
        self.logger.debug(f"Extraídos {len(envolvidos)} envolvidos")
        return envolvidos

    def _extract_movimentacoes(self, response):
        movimentacoes = []
        
        datas = response.xpath('//a[starts-with(@name, "mov_")]//text()').getall()
        textos = response.xpath('//td[@width="95%"]//text()').getall()
        
        for data, texto in zip(datas, textos):
            loader = ItemLoader(item=MovimentacaoItem())
            loader.add_value('data', data)
            loader.add_value('texto', texto)
            movimentacoes.append(loader.load_item())
        
        self.logger.debug(f"Extraídas {len(movimentacoes)} movimentações")
        return movimentacoes

    def _build_formdata_cnpj(self, cnpj_limpo):
        """
        Constrói formdata para busca por CNPJ.
        
        Nota: Para processos individuais, não é mais necessário usar formulário.
        Acesso direto via GET: https://cp.trf5.jus.br/processo/{numero}
        """
        return {
            'navigation': 'Netscape',
            'filtroCpfRequest': cnpj_limpo,
            'tipo': 'xmlcpf',
            'filtro': '',
            'filtroCPF2': cnpj_limpo,
            'tipoproc': 'T',
            'filtroRPV_Precatorios': '',
            'uf_rpv': 'PE',
            'numOriginario': '',
            'numRequisitorio': '',
            'numProcessExec': '',
            'uf_rpv_OAB': 'PE',
            'filtro_processo_OAB': '',
            'filtro_CPFCNPJ': '',
            'campo_data_de': '',
            'campo_data_ate': '',
            'vinculados': 'true',
            'ordenacao': 'D',
            'ordenacao cpf': 'D'
        }

    def _clean_cnpj(self, cnpj):
        if not cnpj:
            return ''
        return cnpj.replace('.', '').replace('/', '').replace('-', '').strip()

    def _is_error_page(self, response):
        if response.status >= 400:
            return True
        
        # Check if the page has the expected process structure
        has_process_number = response.xpath("//p[contains(., 'PROCESSO N')]").get()
        
        # If we found a process number, it's NOT an error page
        if has_process_number:
            return False
        
        # Only check for error indicators if no process number found
        error_indicators = [
            'processo não encontrado',
            'página não encontrada',
            'erro ao consultar',
            'consulta inválida',
            'nenhum processo foi encontrado'
        ]
        
        body_text = response.text.lower()
        return any(indicator in body_text for indicator in error_indicators)

    def _save_debug_html(self, response, prefix='debug'):
        import os
        os.makedirs('output', exist_ok=True)
        filename = f'output/{prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.logger.info(f"HTML de debug salvo: {filename}")

    def handle_error(self, failure):
        self.logger.error(f"Erro na requisição: {failure.request.url}")
        self.logger.error(f"Tipo do erro: {failure.type}")
        self.logger.error(f"Valor: {failure.value}")

        