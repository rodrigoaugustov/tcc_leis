import argparse
import locale
import logging
import warnings

from scraper.pipeline import run_pipeline

locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')

logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', filename='execucao.log', encoding='utf-8', level=logging.INFO)

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()

parser.add_argument("--crawler",
                    help="run crawlers immediately",
                    action="store_true")

args = parser.parse_args()

if args.crawler:
    run_pipeline()

if __name__ == "__main__":

    run_pipeline()