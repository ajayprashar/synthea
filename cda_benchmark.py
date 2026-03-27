import os
import time
import logging
from pathlib import Path
from lxml import etree
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

# CONFIGURATION
CCDA_PATH = r"C:\synthea\output\ccda"
LOG_FILE = "parsing_results.log"
WORKERS = 14  # Safe limit to prevent SSD I/O saturation

# Setup logging to catch errors and slow files
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def process_file(file_path):
    """Production-grade parsing task"""
    start = time.perf_counter()
    try:
        # High-speed C-based parsing
        tree = etree.parse(str(file_path))
        root = tree.getroot()
        ns = {'n': 'urn:hl7-org:v3'}
        
        # Simulate common SHIE extraction tasks
        given = root.xpath("//n:patient/n:name/n:given/text()", namespaces=ns)
        family = root.xpath("//n:patient/n:name/n:family/text()", namespaces=ns)
        
        # Log any file that takes longer than 0.5s (The '15MB Outliers')
        duration = time.perf_counter() - start
        if duration > 0.5:
            logging.info(f"SLOW FILE: {file_path.name} took {duration:.2f}s")
            
        return True
    except Exception as e:
        logging.error(f"FAIL: {file_path.name} - {str(e)}")
        return False

def run_full_ingestion():
    print(f"🔍 Locating files in {CCDA_PATH}...")
    files = list(Path(CCDA_PATH).rglob("*.xml"))
    total = len(files)
    
    print(f"🚀 Processing {total:,} files. This is a full-scale stress test.")
    start_time = time.perf_counter()

    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        # The tqdm wrapper provides the real-time progress bar
        results = list(tqdm(executor.map(process_file, files), total=total, desc="Ingesting CCDAs"))
        success_count = sum(results)

    duration = time.perf_counter() - start_time
    
    print("\n" + "="*45)
    print(f"✅ FULL INGESTION COMPLETE")
    print(f"Total Time:      {duration/60:.2f} minutes")
    print(f"Final Speed:     {total / duration:.2f} files/sec")
    print(f"Success Rate:    {(success_count/total)*100:.2f}%")
    print(f"Detailed logs at: {os.path.abspath(LOG_FILE)}")
    print("="*45)

if __name__ == "__main__":
    run_full_ingestion()