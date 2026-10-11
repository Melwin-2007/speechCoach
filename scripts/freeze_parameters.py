import os
import json
import hashlib
from pathlib import Path

def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    os.makedirs("results", exist_ok=True)
    
    files_to_hash = [
        "configs/population_bounds.json",
        "configs/population_bounds_loo_S01.json",
        "configs/population_bounds_loo_S02.json",
        "configs/population_bounds_loo_S03.json",
        "configs/population_bounds_loo_S04.json",
        "src/speechcoach/compare/deviation.py",
        "src/speechcoach/compare/regions.py",
        "src/speechcoach/analyze.py"
    ]
    
    file_hashes = {}
    for f in files_to_hash:
        if os.path.exists(f):
            file_hashes[f] = hash_file(f)
            
    import sys
    sys.path.insert(0, "src")
    from speechcoach.compare.deviation import PARAMS, CHANNELS
    
    frozen_data = {
        "frozen": True,
        "phase": 5,
        "git_commit": "93369be3923492ef378d03be5b2d33d6a85e8b4e",
        "hashes": file_hashes,
        "params": PARAMS,
        "channels": {k: [v[0], v[1], list(v[2])] for k, v in CHANNELS.items()}
    }
    
    out_path = "results/frozen.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(frozen_data, f, indent=2)
        
    print(f"Frozen parameters and file hashes written to {out_path}:")
    print(json.dumps(frozen_data, indent=2))

if __name__ == "__main__":
    main()
