"""
Script para executar todos os testes
"""
import unittest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Executa todos os testes do projeto"""
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_test(test_file):
    """Executa um arquivo de teste específico"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern=test_file)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Executa teste específico
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
    else:
        # Executa todos os testes
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
