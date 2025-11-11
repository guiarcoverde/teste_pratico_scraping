class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017/'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'trf5_processos')
        )
    
    def open_spider(self, spider):
        try:
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure

            self.client = MongoClient(
                self.mongo_uri,
                maxPoolSize=50,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            self.db = self.client[self.mongo_db]

            self.client.admin.command('ping')
            spider.logger.info("Conexão com MongoDB estabelecida com sucesso.")
            
            self.db.processos.create_index('numero_processo', unique=True)
            spider.logger.info("Índice 'numero_processo' garantido no MongoDB.")
            
        except ImportError:
            spider.logger.warning(
                "pymongo não instalado. Use: pip install pymongo"
            )
            self.client = None
        except ConnectionFailure:
            spider.logger.error(
                f"Falha ao conectar ao MongoDB: {self.mongo_uri}"
            )
            self.client = None
    
    def close_spider(self, spider):
        if self.client:
            self.client.close()
            spider.logger.info("Conexão com MongoDB fechada.")
    
    def process_item(self, item, spider):
        if not self.client:
            return item
        
        try:
            from datetime import datetime
            from scrapy.utils.serialize import ScrapyJSONEncoder
            from pymongo.errors import PyMongoError
            
            item_dict = dict(item)
            
            encoder = ScrapyJSONEncoder()
            item_json = encoder.encode(item_dict)
            import json
            item_dict = json.loads(item_json)
            
            numero_processo = item_dict.get('numero_processo')
            
            if numero_processo:
                result = self.db.processos.update_one(
                    {'numero_processo': numero_processo},
                    {
                        '$set': item_dict,
                        '$setOnInsert': {'created_at': datetime.now()},
                        '$currentDate': {'updated_at': True}
                    },
                    upsert=True
                )
                
                if result.upserted_id:
                    spider.logger.info(f"Processo inserido: {numero_processo}")
                    spider.crawler.stats.inc_value('mongodb/items_inserted')
                else:
                    spider.logger.info(f"Processo atualizado: {numero_processo}")
                    spider.crawler.stats.inc_value('mongodb/items_updated')
            else:
                spider.logger.warning("Processo sem número - não foi salvo no MongoDB")
                spider.crawler.stats.inc_value('mongodb/items_skipped')
                
        except PyMongoError as e:
            spider.logger.error(f"Erro do MongoDB: {e}")
            spider.crawler.stats.inc_value('mongodb/errors')
        except Exception as e:
            spider.logger.error(f"Erro inesperado ao salvar no MongoDB: {e}")
            spider.crawler.stats.inc_value('mongodb/errors')
        
        return item
    

        